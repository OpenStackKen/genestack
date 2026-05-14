---
title: "Releases"
description: "Genestack Major Releases"
---

## Genestack Versioning

Genestack uses a variation of the [CalVer](https://calver.org/) versioning scheme for its releases.

```mermaid
---
config:
  theme: neutral
  wrap: false
  flowchart:
      wrappingWidth: 200
---
flowchart TD
    subgraph REL[" "]
        RELEASE([2026.4.1-pre])
    end
    subgraph LABELS [" "]
        direction TD
        YR_LABEL["2026"]
        D1_LABEL["."]
        QTR_LABEL["4"]
        D2_LABEL["."]
        REL_LABEL["1"]
        D3_LABEL["-"]
        L_LABEL["pre"]
    end
%%    subgraph TAGS[" "]
%%        direction TD
        YR_TAG["Year"]
        QTR_TAG["Quarter"]
        REL_TAG["Release"]
        L_TAG["Release Tag</br>(Optional)"]
 %%   end

YR_LABEL & D1_LABEL & QTR_LABEL & D2_LABEL & REL_LABEL & D3_LABEL & L_LABEL

RELEASE ==> YR_LABEL
RELEASE ==> QTR_LABEL
RELEASE ==> REL_LABEL
RELEASE ==> L_LABEL

YR_LABEL --- YR_TAG
QTR_LABEL --- QTR_TAG
REL_LABEL --- REL_TAG
L_LABEL --- L_TAG

%% Class assignments
class REL,DESC,LABELS,TAGS layout
class D1,D2,D3 delimiter
class YR_TAG,QTR_TAG,REL_TAG,L_TAG tag
class D1_TAG,D2_TAG,D3_TAG tag
class YR_LABEL,QTR_LABEL,REL_LABEL,L_LABEL label
class D1_LABEL,D2_LABEL,D3_LABEL label
class RELEASE params

%% Styles
%%linkStyle 4,5,6,7 stroke:none,stroke-width:0,fill:none;
%%linkStyle 11,12,13,14 stroke-width:2px,fill:none,stroke:black;

classDef layout fill:none,stroke:none,color:none;
classDef delimiter fill:none,stroke:none,font-size:1.2em;
classDef tag fill:none,stroke:none,font-size:1em;
classDef label fill:none,stroke:none,font-size:1.2em;
classDef params font-size:1.1em,color:#0a6ffd;
classDef desc fill:none,stroke-width:0,color:none;

```

Genestack will have branches for quarter a release is made.  Releases will be tags in that branch.

```mermaid
---
config:
    theme: 'default'
    themeVariables:
        'git0': '#0a6ffd'
        'gitInv0': '#0a6ffd'
        'git1': '#eeeeee'
        'gitInv1': '#8b8f91'
        'git2': '#eeeeee'
        'gitInv2': '#8b8f91'
        tagLabelColor: '#0a6ffd'
        tagLabelBackground: '#eeeeee'
        tagLabelBorder: '#8b8f91'
        commitLabelColor: '#000000'
        commitLabelBackground: '#ffffff00'
---
gitGraph
   commit
   commit
   commit id: "2025.4.1 RELEASE" tag: "2025.4.1" type: HIGHLIGHT
   branch "2025.4"
   checkout "2025.4"
   commit
   commit
   commit id: "2025.4.2 RELEASE" tag: "2025.4.2" type: HIGHLIGHT
   commit
   checkout main
   commit
   commit
   commit
   commit id: "2026.1.1 RELEASE" tag: "2026.1.1" type: HIGHLIGHT
   branch "2026.1"
   checkout "2026.1"
   commit
   commit
   checkout main
   commit
   commit
```
