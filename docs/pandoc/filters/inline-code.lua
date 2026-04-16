--[[
  inline-code.lua

  Pandoc's default LaTeX output for inline code is not sufficient for literals
  that contain TeX-special characters such as `#` once other escaping has
  already happened in the surrounding writer pipeline. Render inline code spans
  explicitly for LaTeX so characters like `#`, `$`, `\`, `{`, and `}` are
  always treated as literal text.
--]]

local function escape_latex_code(text)
  text = text:gsub("\\", "\\textbackslash{}")
  text = text:gsub("([{}$%%#&_])", "\\%1")
  text = text:gsub("~", "\\textasciitilde{}")
  text = text:gsub("%^", "\\textasciicircum{}")
  return text
end

if FORMAT:match("latex") then
  function Code(el)
    return pandoc.RawInline("latex", "\\inlinecode{" .. escape_latex_code(el.text) .. "}")
  end
end

