--[[

    images.lua

    inspired by image-width.lua

    A Pandoc Lua filter to adjust image widths based on caption format
    Format: ![Caption text|width](image.png)
    Function to create a new caption from text

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
logMessage("INFO", "In Images filter...")


function isNumber(str)
    return not (str == "" or str:find("%D"))  -- str:match("%D") also works
end

function round(n)
    return math.floor(n + 0.5)
end

function numPercent( num )
    local num = (100 * (num / 1000))

    if num > 100 then
        num = 100
    elseif num < 0 then
        num = 0
    end

    return round(num)
end

function create_caption(text)
    -- For simple captions, we can just use a Str element
    if text:find("^%s*$") then
        -- Empty caption
        return {}
    else
        -- Non-empty caption
        return pandoc.Inlines(pandoc.Str(text))
    end
end

-- Function to process the image and extract width from caption
function process_image(img)

    -- Center the image
    img.attributes.position ="center"
    logMessage("INFO", "Image: Centered...")
    
    -- Convert the caption to a single string
    local caption_text = pandoc.utils.stringify(img.caption)
    if string.len(caption_text) > 35 then
        elipses = "..."
    else
        elipses = ""
    end
    logMessage("INFO", "       Caption = " .. string.sub(caption_text,1,35) .. elipses)

    -- Check to see if the caption is only a number, and treat it as a size
    if isNumber(caption_text) then
        logMessage("INFO", "       Caption is a number...")
        
        local width = caption_text:match("(%d+)")
        width = numPercent(width)
        logMessage("INFO", "       Image width is " .. width .. "%")
        
        img.caption = create_caption("")
        logMessage("INFO", "       Caption removed...")
            
        -- Set the width attribute for the image (in pixels)
        img.attributes.width = width .. "%"        
        
    end        


    -- Check if the caption contains a pipe followed by a number
    -- Using a more flexible pattern that looks for a pipe character followed by digits
    local pipe_pos = caption_text:find("|")

    if pipe_pos then
        
        logMessage("INFO", "       Pipe found...")

        -- Extract the parts before and after the pipe
        local new_caption = caption_text:sub(1, pipe_pos - 1)
        local width_part = caption_text:sub(pipe_pos + 1)

        -- Extract the width number from the width part
        local width = width_part:match("(%d+)")
        width = numPercent(width)
        logMessage("INFO", "       Image width is " .. width .. "%")
        
        if width then
            
            -- Update the image caption without the width part
            img.caption = create_caption(new_caption)

            logMessage("INFO", "       Width removed from caption...")
            local caption_text = new_caption
            if string.len(caption_text) > 35 then
                elipses = "..."
            else
                elipses = ""
            end
            logMessage("INFO", "       New caption = " .. string.sub(caption_text,1,30) .. elipses)            

            -- Set the width attribute for the image (in pixels)
            img.attributes.width = width .. "%"

            -- Log the attributes
            for k, v in pairs(img.attributes) do end

            -- Return the modified image
            return img
        else
        end
    else
    end

    -- If no width specification was found, return the image unchanged
    return img
end

-- Handler for standalone images
function Image(img)   
    --print (img )
    return process_image(img) 
end

-- Handler for Figure blocks (which may contain images)
function Figure(fig)
    
    -- Check if the figure has an image
    for i, block in ipairs(fig.content) do
        if block.t == "Plain" then
            for j, inline in ipairs(block.content) do
                if inline.t == "Image" then
                    -- Process the image
                    local processed_image = process_image(inline)
                    -- Update the image in the figure
                    block.content[j] = processed_image

                    -- Also update the figure caption if needed
                    if processed_image.caption then
                        -- Extract the caption text
                        local caption_text =
                            pandoc.utils.stringify(processed_image.caption)
                        -- Update the figure caption
                        fig.caption = create_caption(caption_text)
                    end
                end
            end
        end
    end

    return fig
end

-- Log when the filter is loaded

-- Return the filter
return {{Image = Image}, {Figure = Figure}}
