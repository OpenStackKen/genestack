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

local function latex_escape_path(path)
  return path
    :gsub("\\", "/")
    :gsub("([%%{}])", "\\%1")
end

local function run_mmdc(source_path, output_path, output_format)
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
    "--outputFormat",
    shell_escape(output_format),
  }, " ")

  local ok, _, code = os.execute(command)
  if not ok or code ~= 0 then
    error("mermaid-cli failed for " .. output_path)
  end
end

function CodeBlock(el)
  if not FORMAT:match("latex") then
    return nil
  end

  if not el.classes:includes("mermaid") then
    return nil
  end

  -- Always render Mermaid as PNG for the PDF pipeline. This is simpler than
  -- trying to preserve SVG text through LaTeX's SVG conversion stack, and it
  -- avoids the `foreignObject` label problem entirely because Mermaid bakes the
  -- label text into raster output.
  local digest = pandoc.sha1("mermaid-png-v1\n" .. el.text)
  local output_path = mermaid_cache .. "/" .. digest .. ".png"
  if not file_exists(output_path) then
    ensure_parent_directory(output_path)
    local source_path = mermaid_cache .. "/" .. digest .. ".mmd"
    write_file(source_path, el.text)
    run_mmdc(source_path, output_path, "png")
    os.remove(source_path)
  end

  local latex = table.concat({
    "\\begin{figure}[H]",
    "\\centering",
    "\\includegraphics[width=0.85\\linewidth,height=\\textheight,keepaspectratio,alt={Mermaid diagram}]{" .. latex_escape_path(output_path) .. "}",
    "\\end{figure}",
  }, "\n")

  return pandoc.RawBlock("latex", latex)
end

function Meta(meta)
  if meta.mermaid_cache_dir then
    mermaid_cache = stringify(meta.mermaid_cache_dir)
  end
end
