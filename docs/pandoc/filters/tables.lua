--[[

    tables.lua

    Table filter to change LaTeX to use tabularray instead of
    longtable

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
logMessage("INFO", "In Table filter...")

function get_rows_data(rows)
  local data = ''
  for j, row in ipairs(rows) do
    for k, cell in ipairs(row.cells) do
      local cell_text = pandoc.utils.stringify(cell.contents)

      -- This filter emits raw LaTeX table rows, so ordinary Markdown text no
      -- longer goes through Pandoc's normal LaTeX escaping. Escape the common
      -- LaTeX-special characters here so table content such as Prometheus
      -- templates, shell fragments, and config examples render literally.
      cell_text = cell_text:gsub('\\', '\\textbackslash{}')
      cell_text = cell_text:gsub('([{}$%%#&_])', '\\%1')
      cell_text = cell_text:gsub('~', '\\textasciitilde{}')
      cell_text = cell_text:gsub('%^', '\\textasciicircum{}')

      data = data .. cell_text
      if (k == #row.cells) then
        data = data .. ' \\\\ \n'
      else
        data = data .. ' & '
      end
    end
  end
  return data
end

function generate_tabularray(tbl)
  local table_class = 'longtblr'

  if (tbl.attributes['tablename'] ~= nil) then
    table_class = tbl.attributes['tablename']
  end

  local caption = pandoc.utils.stringify(tbl.caption.long)
  local caption_content = caption:match("{(.-)}")
  if caption_content then
    caption = caption:gsub("{.-}", "")
  end

  -- COLSPECS
  local col_specs = tbl.colspecs
  local col_specs_latex = ''
  for i, col_spec in ipairs(col_specs) do
    local align = col_spec[1]
    local width = col_spec[2]

     col_specs_latex = col_specs_latex .. 'X['
    --col_specs_latex = col_specs_latex .. '|'

    --if width ~= 0 and width ~= nil then
    --  col_specs_latex = col_specs_latex .. width..'\\linewidth,'
    --end
   
    if align == 'AlignCenter' then
      col_specs_latex = col_specs_latex .. 'c'
    elseif align == 'AlignRight' then
      col_specs_latex = col_specs_latex .. 'r'
    else -- elseif align == 'AlignLeft' then
      col_specs_latex = col_specs_latex .. 'l'
    end

    col_specs_latex = col_specs_latex .. ']'
  end

  -- If there's caption data, we override previous data
  if caption_content then
    local dict = {}
    for key, value in string.gmatch(caption_content, '(%w+)=([^%s]+)') do
        dict[key] = value
    end
    if dict["tablename"] then
      table_class = dict["tablename"]
    end
    if dict["colspec"] then
      col_specs_latex = dict["colspec"]
    end
  end

  -- TABLE DEFINITION
  local tabledef = ''

  tabledef = '\\SetTblrInner{rowsep=2pt,colsep=2pt}\n'

  tabledef = tabledef .. '\\begin{'..table_class..'}[theme=obsidian]{\n'
  tabledef = tabledef .. '  rowhead = 1,\n'
  --tabledef = tabledef .. '  hlines,\n  vlines,\n  cells = {font = \\fontsize{8pt}{10pt}\\tablefont},\n'
  --tabledef = tabledef .. '  row{1} = {bg=black, fg=white, font = \\bfseries\\fontsize{10pt}{12pt}\\tableheaderfont},\n'
  tabledef = tabledef .. '  hlines,\n  vlines,\n  cells = {font = \\fontsize{8pt}{10pt}\\interlight},\n'
  tabledef = tabledef .. '  row{1} = {bg=black, fg=white, font = \\fontsize{10pt}{12pt}\\intermedium},\n'
  -- Are captions broken?
  --tabledef = tabledef .. '  caption = {'..caption..'},\n'
  tabledef = tabledef .. '  colspec = {'..col_specs_latex..'}\n'
  tabledef = tabledef .. '}'
  local result = pandoc.List:new{pandoc.RawBlock("latex", tabledef )}

  -- HEADER
  local header_latex = get_rows_data(tbl.head.rows)
  result = result .. pandoc.List:new{pandoc.RawBlock("latex", header_latex)}

  -- ROWS
  local rows_latex = ''
  for j, tablebody in ipairs(tbl.bodies) do
    rows_latex = get_rows_data(tablebody.body)
  end
  result = result .. pandoc.List:new{pandoc.RawBlock("latex", rows_latex)}

  -- FOOTER
  local footer_latex = get_rows_data(tbl.foot.rows)
  result = result .. pandoc.List:new{pandoc.RawBlock("latex", footer_latex)}

  result = result .. pandoc.List:new{pandoc.RawBlock("latex", '\\end{'..table_class..'}')}
  return result
end



if FORMAT:match 'latex' then

  function Table (tbl)
    return generate_tabularray(tbl)
  end

  function RawBlock(raw)    
    if raw.format:match 'html' and raw.text:match '%<table' then
      blocks = pandoc.read(raw.text, raw.format).blocks
      for i, block in ipairs(blocks) do
        if block.t == 'Table' then
          return generate_tabularray(block)
        end
      end
    end
  end

end

-- when parsing to HTML
if FORMAT:match 'html' then

  function Table(tbl)
    local table_class = 'longtblr'
    local caption = pandoc.utils.stringify(tbl.caption.long)
    local caption_content = caption:match("{(.-)}")

    if caption_content then
      local dict = {}
      -- Extraer cada par clave=valor
      for key, value in string.gmatch(caption_content, '(%w+)=([^%s]+)') do
          dict[key] = value
          tbl.attributes[key] = value
      end
      tbl.caption.long = caption:gsub("{.-}", "")
    end    

    return tbl
  end

end
