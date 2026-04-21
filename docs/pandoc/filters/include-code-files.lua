--- include-code-files.lua – filter to include code from source files
---
--- This is intentionally compatible with Pandoc's upstream include-code-files
--- filter contract:
---   - include
---   - start-line / startLine
---   - end-line / endLine
---   - dedent
---
--- The local extension is path resolution for a controlled repo-root-relative
--- subset, so authors can write include paths such as:
---   - bin/install-neutron.sh
---   - scripts/generate_product_matrix.py
---   - docs/scripts/mkpdf.sh
---   - manifests/grafana/azure-client-secret.yaml
---   - etc/keystone/mapping.json
--- without exposing the entire repository tree.

local docs_root = os.getenv("GENESTACK_DOCS_ROOT") or "."
local repo_root = os.getenv("GENESTACK_REPO_ROOT") or ""

local function file_exists(path)
  local handle = io.open(path, "rb")
  if handle then
    handle:close()
    return true
  end
  return false
end

local function join_paths(base, relative)
  if base:sub(-1) == "/" then
    return base .. relative
  end
  return base .. "/" .. relative
end

local function dedent(line, n)
  return line:sub(1, n):gsub(" ", "") .. line:sub(n + 1)
end

local function resolve_include_path(raw_path)
  local candidates = { raw_path }

  local normalized = raw_path:gsub("^source%-snippets/", "")
  local allowed_prefixes = {
    "bin/",
    "scripts/",
    "base%-helm%-configs/",
    "ansible/",
    "recovery/",
    "manifests/",
    "etc/",
    "%.github/workflows/",
    "docs/scripts/",
  }

  for _, prefix in ipairs(allowed_prefixes) do
    if normalized:match("^" .. prefix) then
      table.insert(candidates, join_paths(docs_root, normalized))
      if repo_root ~= "" then
        table.insert(candidates, join_paths(repo_root, normalized))
      end
      break
    end
  end

  for _, candidate in ipairs(candidates) do
    if file_exists(candidate) then
      return candidate
    end
  end

  return raw_path
end

local function transclude(cb)
  if not cb.attributes.include then
    return nil
  end

  local content = ""
  local include_path = resolve_include_path(cb.attributes.include)
  local fh = io.open(include_path)
  if not fh then
    io.stderr:write("Cannot open file " .. cb.attributes.include .. " | Skipping includes\n")
  else
    local number = 1
    local start = 1

    for _, pascal in pairs({ "startLine", "endLine" }) do
      local hyphen = pascal:gsub("%u", "-%0"):lower()
      if cb.attributes[hyphen] then
        cb.attributes[pascal] = cb.attributes[hyphen]
        cb.attributes[hyphen] = nil
      end
    end

    if cb.attributes.startLine then
      cb.attributes.startFrom = cb.attributes.startLine
      start = tonumber(cb.attributes.startLine)
    end

    for line in fh:lines("L") do
      if cb.attributes.dedent then
        line = dedent(line, tonumber(cb.attributes.dedent))
      end
      if number >= start then
        if not cb.attributes.endLine or number <= tonumber(cb.attributes.endLine) then
          content = content .. line
        end
      end
      number = number + 1
    end
    fh:close()
  end

  cb.attributes.include = nil
  cb.attributes.startLine = nil
  cb.attributes.endLine = nil
  cb.attributes.dedent = nil

  return pandoc.CodeBlock(content, cb.attr)
end

return {
  { CodeBlock = transclude }
}
