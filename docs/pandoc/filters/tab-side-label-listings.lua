local function latex_escape(text)
  return text
    :gsub("\\", "\\textbackslash{}")
    :gsub("([{}$%%#&_])", "\\%1")
    :gsub("~", "\\textasciitilde{}")
    :gsub("%^", "\\textasciicircum{}")
end

local function append_header_include(meta, latex_block)
  local header_includes = meta["header-includes"]
  local raw_block = pandoc.MetaBlocks({ pandoc.RawBlock("latex", latex_block) })

  if not header_includes then
    meta["header-includes"] = pandoc.MetaList({ raw_block })
    return meta
  end

  if header_includes.t == "MetaList" then
    header_includes[#header_includes + 1] = raw_block
    meta["header-includes"] = header_includes
    return meta
  end

  meta["header-includes"] = pandoc.MetaList({ header_includes, raw_block })
  return meta
end

local function build_latex_preamble()
  return [[
\newlength{\GenestackSideLabelExtent}
\newlength{\GenestackSideLabelGutter}
\newlength{\GenestackSideLabelMinHeight}
\newlength{\GenestackSideLabelRightInset}
\newcommand{\GenestackSideLabelSetup}[1]{%
  \settowidth{\GenestackSideLabelExtent}{\sffamily\bfseries\scriptsize #1}%
  \setlength{\GenestackSideLabelGutter}{54pt}%
  \setlength{\GenestackSideLabelMinHeight}{\dimexpr\GenestackSideLabelExtent + 6mm\relax}%
  \setlength{\GenestackSideLabelRightInset}{18pt}%
}
\newtcolorbox{GenestackSideLabelBox}[2][]{
  enhanced,
  breakable,
  parbox=false,
  colback=white,
  opacityback=1,
  colframe=black,
  coltext=black,
  boxrule=0.2pt,
  arc=3pt,
  outer arc=3pt,
  width=.95\linewidth,
  left skip=.05\linewidth,
  right skip=0pt,
  left=2mm,
  right=2mm,
  top=3mm,
  bottom=3mm,
  boxsep=0mm,
  before={\GenestackSideLabelSetup{#2}},
  minipage=\GenestackSideLabelMinHeight,
  before skip=6pt,
  after skip=6pt,
  halign=flush left,
  valign=center,
  overlay unbroken and first={
    \node[
      text=black,
      font=\sffamily\bfseries\scriptsize,
      rotate=90,
      align=center,
      inner sep=0pt,
      anchor=center
    ] at ([xshift=-10pt]frame.west) {#2};
  },
  overlay middle and last={
    \node[
      text=black,
      font=\sffamily\bfseries\scriptsize,
      rotate=90,
      align=center,
      inner sep=0pt,
      anchor=center
    ] at ([xshift=-10pt]frame.west) {#2};
  },
  #1
}
]]
end

function Meta(meta)
  if not FORMAT:match("latex") then
    return meta
  end

  return append_header_include(meta, build_latex_preamble())
end

function CodeBlock(el)
  if not FORMAT:match("latex") then
    return nil
  end

  if not el.classes:includes("tab-side-label") then
    return nil
  end

  local label = el.attributes["tab-label"] or el.attributes["label"] or "Tab"
  local label_tex = latex_escape(label)
  local box_options = ""

  if label == "Expected Output" then
    box_options = "[minipage=\\dimexpr\\GenestackSideLabelMinHeight + 1mm\\relax]"
  end

  local parts = {
    "\\begin{GenestackSideLabelBox}" .. box_options .. "{" .. label_tex .. "}",
    "\\begin{Verbatim}[fontsize=\\small,breaklines,breakanywhere]",
    el.text,
    "\\end{Verbatim}",
    "\\end{GenestackSideLabelBox}",
  }

  return pandoc.RawBlock("latex", table.concat(parts, "\n"))
end
