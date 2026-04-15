--[[

    inline-code – make sure inline code (i.e. single-backtick) doesn't change
    the font sizing. Headings get a dedicated macro so monospace can be tuned
    separately there without affecting body inline code.

--]]

local function escape_latex_code(text)
    text = text:gsub("([{}$%%#&_])", "\\%1")
    text = text:gsub("~", "\\textasciitilde{}")
    text = text:gsub("%^", "\\textasciicircum{}")
    text = text:gsub("\\", "\\textbackslash{}")
    return text
end

function Header(el)
    if not FORMAT:match("latex") then
        return nil
    end

    return el:walk({
        Code = function(code)
            return pandoc.RawInline("latex", "\\headinginlinecode{" .. escape_latex_code(code.text) .. "}")
        end
    })
end

function Code(el)
    if FORMAT:match("latex") then
        return pandoc.RawInline("latex", "\\inlinecode{" .. escape_latex_code(el.text) .. "}")
    end
end
