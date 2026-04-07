--[[

    Convert alternate checkbox syntax to inline tcboxes.

-- ]]

local function logMessage(level, message)
    -- Check if we're logging
    if logging then
      -- Basic logging to console
      print(string.format("[%s] %s: %s", os.date("%Y-%m-%d %H:%M:%S"), level, message))
    end
end

-- Should we use logging?
logging = false
logMessage("INFO","In Checkboxes filter...")

-- Should we use different colors?
useColors = false
if useColors then
    logMessage("INFO", "    Colors: Active")
else
    logMessage("INFO", "    Colors: Inactive")
end
    
logMessage("INFO", "")

local tcbegin = "[\\raisebox{-0.7ex}{\\small\\color{%s}%s}]\\begin{tcolorbox}[enhanced,nobeforeafter,tcbox raise base,box align=center,boxrule=0.4pt,top=0mm,bottom=0mm,right=0mm,left=0mm,arc=1pt,boxsep=2pt,before upper={\\vphantom{dlg}},colframe=%s!50!black,coltext=black,colback=%s!10!white]"
local tcend = "\\end{tcolorbox}"

local tcstring = "[\\small\\color{%s}{%s}]"

local type_tbl = {
	["[!]"] = {
		color = "red",
		icon = "\\faExclamationCircle"
	},
	["[?]"] = {
		color = "orange",
		icon = "\\faQuestionCircle"
	},
	["[*]"] = {
		color = "Dandelion",
		icon = "\\faStar"
	},
	["[@]"] = {
		color = "ForestGreen",
		icon = "\\faBook"
	},
	["[~]"] = {
		color = "cyan",
		icon = "\\faInfoCircle"
	},
	["[&]"] = {
		color = "NavyBlue",
		icon = "\\faPaperclip"
	},
	["[+]"] = {
		color = "ForestGreen",
		icon = "\\faThumbsUp"
	},
	["[-]"] = {
		color = "red",
		icon = "\\faThumbsDown"
	},
	["[=]"] = {
		color = "gray",
		icon = "\\faBan"
	},
	["[>]"] = {
		color = "purple",
		icon = "\\faPaperPlane"
	},
	["[/]"] = {
		color = "teal",
		icon = "\\faAdjust"
	},
	["[x]"] = {
		color = "ForestGreen",
		icon = "\\faCheckCircle[regular]"
	},
	["[ ]"] = {
		color = "black",
		icon = "\\faCircleO"
	},
}

function BulletList(li)
    for _, item in pairs(li.c) do
        local start = item[1].c[1]

        --print( item[1].c[1] )
        if start.t == "Str" then
            --print(next.t)
            --print(nextnext.t)
            
            local next = item[1].c[2]
            local nextnext = item[1].c[3]
            print( "START:" )
            print( start )
            print( next )
            print( nextnext )            
            print( "\n" )
            
            --if (next.t == "Space" ) and (nextnext.t == "Str") then
            --    print( item[1] )
            --    local color = "black"
            --    local icon = "\\faCircle[regular]"
            --    logMessage("INFO", "    Match: " .. "[ ]" .. " → " .. string.format(tcstring, color, icon))
            --end
            --print( item[1] )
            local tasktype = start.text:match("^%[.%]$")
            if tasktype and type_tbl[tasktype] then
                --logMessage("INFO", "    " .. tasktype )

                local color = type_tbl[tasktype].color
                local icon = type_tbl[tasktype].icon

                logMessage("INFO", "    Match: " .. tasktype .. " → " .. string.format(tcstring, color, icon))

                item[1].c[1] = pandoc.RawInline("latex", string.format(tcstring, color, icon))
                --item[1].c[1] = pandoc.RawInline("latex", string.format(tcbegin, color, icon, color, color, color))
                --item[1].c[#item[1].c + 1] = pandoc.RawInline("latex", tcend)
            end
        end
    end
    return li
end
