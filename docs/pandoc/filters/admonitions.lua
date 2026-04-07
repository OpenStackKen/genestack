local stringify = pandoc.utils.stringify

local titles = {
  NOTE = "Note",
  TIP = "Tip",
  INFO = "Info",
  IMPORTANT = "Important",
  WARNING = "Warning",
  EXAMPLE = "Example",
  GENESTACK = "Genestack",
}

local kinds = {
  NOTE = "note",
  TIP = "tip",
  INFO = "info",
  IMPORTANT = "important",
  WARNING = "warning",
  EXAMPLE = "example",
  GENESTACK = "genestack",
}

local function latex_escape(text)
  local replacements = {
    ["\\"] = "\\textbackslash{}",
    ["{"] = "\\{",
    ["}"] = "\\}",
    ["#"] = "\\#",
    ["$"] = "\\$",
    ["%"] = "\\%",
    ["&"] = "\\&",
    ["_"] = "\\_",
    ["^"] = "\\textasciicircum{}",
    ["~"] = "\\textasciitilde{}",
  }
  return (text:gsub("[\\{}#$%%&_~%^]", replacements))
end

local function build_open(kind, title)
  return pandoc.RawBlock("latex", "\\begin{GenestackAdmonition}{" .. kind .. "}{" .. latex_escape(title) .. "}")
end

function BlockQuote(el)
  if not FORMAT:match("latex") then
    return nil
  end

  if #el.content == 0 then
    return nil
  end

  local first = el.content[1]
  if first.t ~= "Para" and first.t ~= "Plain" then
    return nil
  end

  local first_text = stringify(first)
  local marker, trailing = first_text:match("^%[!([A-Za-z0-9_-]+)%]%s*(.*)$")
  if not marker then
    return nil
  end

  marker = marker:upper()
  local kind = kinds[marker] or "note"
  local title = trailing ~= "" and trailing or titles[marker] or marker

  local blocks = {build_open(kind, title)}
  if trailing ~= "" then
    table.insert(blocks, pandoc.Para({pandoc.Str(trailing)}))
  end

  for index = 2, #el.content do
    table.insert(blocks, el.content[index])
  end
  table.insert(blocks, pandoc.RawBlock("latex", "\\end{GenestackAdmonition}"))
  return blocks
end
