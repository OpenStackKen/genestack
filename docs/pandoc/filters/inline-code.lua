--[[
  inline-code.lua

  Pandoc's default LaTeX output for inline code is not sufficient for literals
  that contain TeX-special characters such as `#` once other escaping has
  already happened in the surrounding writer pipeline. Render inline code spans
  explicitly for LaTeX so characters like `#`, `$`, `\`, `{`, and `}` are
  always treated as literal text.
--]]

local function escape_latex_code(text)
  local function escape_lua_pattern(literal)
    return (literal:gsub("([^%w])", "%%%1"))
  end

  local placeholders = {
    ["\\"] = "\1",
    ["{"] = "\2",
    ["}"] = "\3",
    ["$"] = "\4",
    ["%"] = "\5",
    ["#"] = "\6",
    ["&"] = "\7",
    ["_"] = "\8",
    ["~"] = "\11",
    ["^"] = "\12",
  }

  local replacements = {
    ["\1"] = "\\textbackslash{}",
    ["\2"] = "\\{",
    ["\3"] = "\\}",
    ["\4"] = "\\$",
    ["\5"] = "\\%",
    ["\6"] = "\\#",
    ["\7"] = "\\&",
    ["\8"] = "\\_",
    ["\11"] = "\\textasciitilde{}",
    ["\12"] = "\\textasciicircum{}",
  }

  for literal, token in pairs(placeholders) do
    text = text:gsub(escape_lua_pattern(literal), token)
  end

  for token, escaped in pairs(replacements) do
    text = text:gsub(token, function()
      return escaped
    end)
  end

  return text
end

if FORMAT:match("latex") then
  function Code(el)
    return pandoc.RawInline("latex", "\\inlinecode{" .. escape_latex_code(el.text) .. "}")
  end
end
