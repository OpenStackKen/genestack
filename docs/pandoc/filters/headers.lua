--[[

     headers.lua
    A Pandoc Lua filter to insert page breaks before Level 1 headers (H1)

--]]

-- Logging
local function logMessage(level, message)
    -- Check if we're logging
    if logging then
        -- Basic logging to console
        print(string.format("[%s] %s: %s", os.date("%Y-%m-%d %H:%M:%S"), level, message))
    end
end

-- Should we use logging?
logging = false
logMessage("INFO", "In Headers filter...")

function Header(el)
    fmt = string.lower(pandoc.utils.stringify(FORMAT))
    if fmt == 'latex' then
        -- Add newline after H1
        if el.level == 1 then
            logMessage("INFO", "    H1 found: Inserting newpage...")
            return { pandoc.RawBlock("latex", "\\newpage"), el }
        -- Fix H4 formatting
        elseif el.level == 2 then
            logMessage("INFO", "    H2 found: NoOp...")
        elseif el.level == 3 then
            logMessage("INFO", "    H3 found: NoOp...")
        elseif el.level == 4 then
            logMessage("INFO", "    H4 found: Inserting newline...")
            return { el, pandoc.RawBlock("latex","\\hfill") }
        elseif el.level == 5 then
            logMessage("INFO", "    H5 found: Inserting newline...")
            return { el, pandoc.RawBlock("latex","\\hfill") }
        elseif el.level == 6 then
            logMessage("INFO", "    H6 found: Inserting newline...")
            return { el, pandoc.RawBlock("latex","\\hfill") }
        end
    end
end
