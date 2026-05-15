--[[
  Pandoc filter for Obsidian callouts

  Note: Remember to leave one blank line between the callout title and content

--]]

local function logMessage(level, message)
    -- Check if we're logging
    if logging then
      -- Basic logging to console
      print(string.format("[%s] %s: %s", os.date("%Y-%m-%d %H:%M:%S"), level, message))
    end
end

-- Should we use logging?
logging = false
logMessage("INFO","In Callout filter...")

function table.contains(table, element)
    for _, value in pairs(table) do
        if value == element then
            return true
        end
    end
    return false
end


-- Transform callout type to Titlecase
function titlecase(str)
    lowerText = string.lower(str)
    return (lowerText:gsub("^%l", string.upper))
end


-- Check if the callout type is in a list
function has_value(tab, val)
    val = titlecase(val)
    for index, value in ipairs(tab) do
        if value == val then
            return true
        end
    end
    return false
end


-- Parse callout title
function get_raw_tex(para)
    para.content = para.content:walk {
        Math = function(el) return "$" .. elem.text .. "$" end,
        Emph = function(el) return "\\textit{" .. pandoc.utils.stringify(elem.content) .. "}" end,
        Strong = function(el) return "\\textbf{" .. pandoc.utils.stringify(elem.content) .. "}" end,
        Code = function(el) return "\\textit{" .. elem.text .. "}" end
    }
    return para
end

-- Check for empty string
function isempty(s)
    return s == nil or s == ''
end

local function escape_latex_text(text)
    text = text:gsub('\\', '\\textbackslash{}')
    text = text:gsub('([{}$%%#&_])', '\\%1')
    text = text:gsub('~', '\\textasciitilde{}')
    text = text:gsub('%^', '\\textasciicircum{}')
    return text
end

local function latex_from_blocks(blocks)
    local tex = pandoc.write(pandoc.Pandoc(blocks), "latex")
    tex = tex:gsub("%s+$", "")
    return tex
end

local function extract_callout_footnotes(blocks)
    local footnotes = {}
    local rewritten = {}

    local function replace_note_with_mark(note)
        table.insert(footnotes, latex_from_blocks(note.content))
        return pandoc.RawInline("latex", "\\footnotemark{}")
    end

    for _, block in ipairs(blocks) do
        table.insert(rewritten, block:walk({
            Note = replace_note_with_mark
        }))
    end

    return rewritten, footnotes
end


-- Process BlockQuote/Callout
function BlockQuote(elem)
  
    logMessage("INFO", "Callout found:")
    
    -- Get callout type
    callout_type=pandoc.utils.stringify( elem.content[1].content[1] )
    callout_type = callout_type:match("^%[%!([A-Za-z0-9%-]*)%][-]?")
    -- Check for empty type
    if isempty(callout_type) then
        callout_type = "Blank"
        logMessage("INFO", "    Type is blank.")
    else
        callout_type = titlecase(callout_type)
        logMessage("INFO", "    Type: " .. callout_type)
        -- Remove the callout type so we can get the title
        table.remove(elem.content[1].content, 1)
        table.remove(elem.content[1].content, 1)
    end
  
    -- Get callout title
    callout_title = ""

    if not (callout_type == "Blank") then
        logMessage("INFO", "    Type isn't Blank!")
        item=1
        title=( elem.content[1].content[item] )
        if title then
            titletype=title.t
        else
            callout_title = titlecase(callout_type)
            titletype=false
        end 
            
        if titletype then
            while not titletype == "Str" do
                title=( elem.content[1].content[item] )
                titletype=title.t
                item=item+1 
            end
            logMessage("INFO", "    Title: " .. pandoc.utils.stringify(title))
            callout_title = pandoc.utils.stringify(elem.content[1])           
            table.remove(elem.content,1)   
        else
            logMessage("INFO", "    Title: (NO TITLE)")
        end
    end
    
    fmt = titlecase(pandoc.utils.stringify(FORMAT))      
    if fmt == 'Latex'
    then
        callout_title = escape_latex_text(callout_title)
        -- remove blockquote tag and get content
        callout = elem.content
        callout, callout_footnotes = extract_callout_footnotes(callout)
        
        -- Callout types
        if has_value({ "Blank" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\begin{quote}\n\\sffamily\n\\itshape"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{quote}"))
        elseif has_value({ "Note" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\noteTitle{\\noteIcon " .. callout_title .. "}\n\\begin{note-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{note-box}"))
        elseif has_value({ "Info" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\infoTitle{\\infoIcon " .. callout_title .. "}\n\\begin{info-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{info-box}"))
        elseif has_value({ "Todo" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\todoTitle{\\todoIcon " .. callout_title .. "}\n\\begin{todo-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{todo-box}"))
        elseif has_value({ "Abstract" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\abstractTitle{\\abstractIcon " .. callout_title .. "}\n\\begin{abstract-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{abstract-box}"))
        elseif has_value({ "Tip" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\tipTitle{\\tipIcon " .. callout_title .. "}\n\\begin{tip-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{tip-box}"))
        elseif (has_value({ "Faq" }, callout_type)) or (has_value({ "Question" }, callout_type)) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\questionTitle{\\questionIcon " .. callout_title .. "}\n\\begin{question-box}"))
             -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{question-box}"))
        elseif has_value({ "Warning" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\warningTitle{\\warningIcon " .. callout_title .. "}\n\\begin{warning-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{warning-box}"))
        elseif has_value({ "Failure" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\failTitle{\\failIcon " .. callout_title .. "}\n\\begin{failure-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{failure-box}"))
        elseif has_value({ "Danger" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\dangerTitle{\\dangerIcon " .. callout_title .. "}\n\\begin{danger-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{danger-box}"))
        elseif has_value({ "Bug" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\bugTitle{\\bugIcon " .. callout_title .. "}\n\\begin{bug-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{bug-box}"))
        elseif has_value({ "Example" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\exampleTitle{\\exampleIcon " .. callout_title .. "}\n\\begin{example-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{example-box}"))
        elseif has_value({ "Success" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\successTitle{\\successIcon " .. callout_title .. "}\n\\begin{success-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{success-box}"))
        elseif has_value({ "Quote" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\quoteTitle{\\quoteIcon " .. callout_title .. "}\n\\begin{quote-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{quote-box}"))
        elseif has_value({ "Command" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\commandTitle{\\commandIcon " .. callout_title .. "}\n\\begin{command-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{command-box}"))
        elseif has_value({ "Output" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\outputTitle{\\outputIcon " .. callout_title .. "}\n\\begin{output-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{output-box}"))
        elseif has_value({ "Genestack" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\genestackTitle{\\genestackIcon " .. callout_title .. "}\n\\begin{genestack-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{genestack-box}"))
        elseif has_value({ "Blank" }, callout_type) then
            -- insert element in front
            table.insert(callout, 1, pandoc.RawBlock("latex", "\\renewcommand\\quoteTitle{\\quoteIcon}\n\\begin{quote-box}"))
            -- insert element at the back
            table.insert(callout, pandoc.RawBlock("latex", "\\end{quote-box}"))   
        end

        for _, footnote_tex in ipairs(callout_footnotes) do
            table.insert(callout, pandoc.RawBlock("latex", "\\footnotetext{" .. footnote_tex .. "}"))
        end
    end 
    return callout
end
