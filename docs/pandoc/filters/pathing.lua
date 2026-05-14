local stringify = pandoc.utils.stringify

local guide_slug = ""
local docs_root = os.getenv("GENESTACK_DOCS_ROOT") or "."
local site_base_url = "/"

local function read_meta_string(meta, key, fallback)
  local value = meta[key]
  if not value then
    return fallback
  end
  return stringify(value)
end

local function file_exists(path)
  local handle = io.open(path, "rb")
  if handle then
    handle:close()
    return true
  end
  return false
end

local function slugify(text)
  local lowered = text:lower()
  lowered = lowered:gsub("[^%w%s%-_/]", "")
  lowered = lowered:gsub("_", "-")
  lowered = lowered:gsub("%s+", "-")
  lowered = lowered:gsub("%-+", "-")
  return lowered:gsub("^%-", ""):gsub("%-$", "")
end

local function split_target(target)
  local path, fragment = target:match("^([^#]*)(#.*)$")
  if path then
    return path, fragment
  end
  return target, ""
end

local function anchor_for_site_path(path)
  local trimmed = path:gsub("^/", ""):gsub("/$", "")
  trimmed = trimmed:gsub("/", "-")
  return slugify(trimmed)
end

local function fragment_anchor(path, fragment)
  if fragment == "" then
    return "#" .. anchor_for_site_path(path)
  end
  local base = anchor_for_site_path(path)
  local suffix = fragment:gsub("^#", "")
  return "#" .. base .. "--" .. slugify(suffix)
end

local function is_same_guide(path)
  return path == "/" .. guide_slug .. "/" or path:match("^/" .. guide_slug .. "/")
end

local function resolve_root_relative_asset(target)
  local relative = target:gsub("^/", "")
  local candidates = {
    docs_root .. "/content/" .. relative,
    docs_root .. "/" .. relative,
  }
  for _, candidate in ipairs(candidates) do
    if file_exists(candidate) then
      return candidate
    end
  end
  return target
end

function Meta(meta)
  guide_slug = read_meta_string(meta, "guide_slug", "")
  docs_root = read_meta_string(meta, "docs_root", docs_root)
  site_base_url = read_meta_string(meta, "site_base_url", "/")
end

function Link(el)
  if not el.target:match("^/") or el.target:match("^//") then
    return nil
  end

  local path, fragment = split_target(el.target)
  if is_same_guide(path) then
    el.target = fragment_anchor(path, fragment)
    return el
  end

  if site_base_url ~= "/" then
    el.target = site_base_url:gsub("/$", "") .. el.target
    return el
  end

  return nil
end

function Image(el)
  if not el.src:match("^/assets/") then
    return nil
  end

  el.src = resolve_root_relative_asset(el.src)
  return el
end
