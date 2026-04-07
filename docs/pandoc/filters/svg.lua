--[[

    svg.lua

    Handle remote SVG assets that LaTeX cannot consume directly.

    The immediate use case is Asciinema poster images written in Markdown as:

      [![asciicast](https://asciinema.org/a/706976.svg)](https://asciinema.org/a/706976)

    Pandoc's LaTeX writer can emit remote SVGs as `\includesvg{https://...}`,
    which fails because the svg package expects a local file that Inkscape can
    open. This filter localizes those poster SVGs into the docs PDF cache and
    rewrites the embed into:

    1. a local screenshot image that LaTeX can include, and
    2. a separate hyperlink to the remote recording for interactive viewing.

--]]

local path = require 'pandoc.path'
local stringify = pandoc.utils.stringify

-- Keep cache layout aligned with the docs PDF build filesystem. The builder
-- already mounts the docs root into the Pandoc container and exports
-- GENESTACK_DOCS_ROOT for filters that need to write deterministic artifacts.
local docs_root = os.getenv('GENESTACK_DOCS_ROOT') or '.'
local cache_dir_rel = 'pdf/.cache/remote-svg'
local link_label = 'View recording on asciinema.org'

-- Match Asciinema poster SVG URLs and capture the cast id.
local function asciinema_cast_id(url)
  return url:match('^https?://asciinema%.org/a/([%w%-_]+)%.svg$')
end

-- Convert the poster SVG URL into the normal browser URL for the recording.
local function default_view_url(svg_url)
  return svg_url:gsub('%.svg$', '')
end

-- Pandoc filters can run repeatedly during one process. Memoize localized
-- assets so repeated embeds in a single document don't refetch or rewrite the
-- same cache file.
local localized_svg_cache = {}

local function ensure_directory(dirpath)
  pandoc.pipe('mkdir', {'-p', dirpath}, '')
end

local function write_file(filepath, content)
  local file = assert(io.open(filepath, 'wb'))
  file:write(content)
  file:close()
end

-- Fetch a remote SVG via Pandoc's mediabag support and write it into the docs
-- PDF cache. Using `mediabag.fetch` lets Pandoc handle the HTTP retrieval
-- rather than adding an external downloader dependency to the filter.
local function localize_remote_svg(svg_url)
  if localized_svg_cache[svg_url] then
    return localized_svg_cache[svg_url]
  end

  local cast_id = asciinema_cast_id(svg_url)
  if not cast_id then
    return nil
  end

  local relative_path = path.join({cache_dir_rel, 'asciinema-' .. cast_id .. '.svg'})
  local absolute_path = path.join({docs_root, relative_path})

  local existing = io.open(absolute_path, 'rb')
  if existing then
    existing:close()
    localized_svg_cache[svg_url] = relative_path
    return relative_path
  end

  local mime_type, contents = pandoc.mediabag.fetch(svg_url)
  if not mime_type or not contents then
    error('svg.lua: unable to fetch remote SVG ' .. svg_url)
  end

  if not tostring(mime_type):match('image/svg') then
    error('svg.lua: expected SVG content for ' .. svg_url .. ', got ' .. tostring(mime_type))
  end

  ensure_directory(path.directory(absolute_path))
  write_file(absolute_path, contents)
  localized_svg_cache[svg_url] = relative_path
  return relative_path
end

local function build_view_link(target)
  return pandoc.Link(link_label, target)
end

local function localized_image(original_image)
  local local_src = localize_remote_svg(original_image.src)
  if not local_src then
    return nil
  end

  -- Preserve the original identifier, classes, attributes, caption, and title.
  return pandoc.Image(
    original_image.caption,
    local_src,
    original_image.title,
    original_image.attr
  )
end

local function rewrite_linked_asciinema_poster(inlines)
  if #inlines ~= 1 then
    return nil
  end

  local outer = inlines[1]
  if outer.t ~= 'Link' or #outer.content ~= 1 or outer.content[1].t ~= 'Image' then
    return nil
  end

  local image = outer.content[1]
  if not asciinema_cast_id(image.src) then
    return nil
  end

  local screenshot = localized_image(image)
  if not screenshot then
    return nil
  end

  local view_url = outer.target ~= '' and outer.target or default_view_url(image.src)
  return {
    pandoc.Para({screenshot}),
    pandoc.Para({build_view_link(view_url)}),
  }
end

-- The Asciinema embeds in this docs tree are authored as paragraphs containing
-- a single `Link(Image(...))`. Rewriting at the block level lets us replace the
-- entire linked image with two separate blocks: a local screenshot and a plain
-- hyperlink for the remote recording.
function Para(para)
  return rewrite_linked_asciinema_poster(para.content)
end

function Plain(plain)
  return rewrite_linked_asciinema_poster(plain.content)
end
