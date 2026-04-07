local stringify = pandoc.utils.stringify
local mermaid_cache = "./pdf/.cache/mermaid"
local docs_root = os.getenv("GENESTACK_DOCS_ROOT") or "."
local puppeteer_config = docs_root .. "/pandoc/puppeteer-config.json"

local function file_exists(path)
  local handle = io.open(path, "rb")
  if handle then
    handle:close()
    return true
  end
  return false
end

local function ensure_parent_directory(path)
  local parent = path:match("^(.*)/[^/]+$")
  if parent and parent ~= "" then
    os.execute(string.format('mkdir -p "%s"', parent))
  end
end

local function shell_escape(value)
  return "'" .. value:gsub("'", [["'"']]) .. "'"
end

local function write_file(path, text)
  local handle = assert(io.open(path, "w"))
  handle:write(text)
  handle:close()
end

function CodeBlock(el)
  if not FORMAT:match("latex") then
    return nil
  end

  if not el.classes:includes("mermaid") then
    return nil
  end

  local digest = pandoc.sha1(el.text)
  local output_path = mermaid_cache .. "/" .. digest .. ".pdf"
  if not file_exists(output_path) then
    ensure_parent_directory(output_path)
    local source_path = mermaid_cache .. "/" .. digest .. ".mmd"
    write_file(source_path, el.text)
    local command = table.concat({
      "mmdc",
      "--quiet",
      "--input",
      shell_escape(source_path),
      "--output",
      shell_escape(output_path),
      "--puppeteerConfigFile",
      shell_escape(puppeteer_config),
      "--theme",
      shell_escape("default"),
      "--backgroundColor",
      shell_escape("transparent"),
    }, " ")
    local ok, _, code = os.execute(command)
    os.remove(source_path)
    if not ok or code ~= 0 then
      error("mermaid-cli failed for " .. output_path)
    end
  end

  return pandoc.Para({pandoc.Image({pandoc.Str("Mermaid diagram")}, output_path)})
end

function Meta(meta)
  if meta.mermaid_cache_dir then
    mermaid_cache = stringify(meta.mermaid_cache_dir)
  end
end
