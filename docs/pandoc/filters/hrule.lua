--[[

     hrule.lua
    Fixes LaTeX horizontal rules to be full-width

--]]

local function logMessage(level, message)
    -- Check if we're logging
    if logging then
        -- Basic logging to console
        print(string.format("[%s] %s: %s", os.date("%Y-%m-%d %H:%M:%S"), level, message))
    end
end

logging = false
logMessage("INFO","In HRule filter...")

if FORMAT:match "latex" then
    function HorizontalRule ()
        return {
            pandoc.RawBlock("latex","\\vspace{1em}\\hrule\\vspace{1em}")
        }
    end
end
