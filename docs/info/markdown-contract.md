---
title: "Markdown Contract"
weight: 20
---

# Markdown Contract

The source Markdown in `/docs` should stay close to GitHub Flavored Markdown.
The goal is to keep the content broadly portable while still rendering cleanly
in Hugo-based sites.

## Preferred Syntax

- Use standard fenced code blocks with an explicit language when possible.
- Use GFM alert blocks for notices:

```md
> [!NOTE]
> This is a note.
```

- Use root-relative links for shared internal links:

```md
[Deployment guide](/deployment-guide/)
```

- Use root-relative asset links for shared images:

```md
![Architecture diagram](/assets/images/diagram-genestack.png)
```

## Nonstandard Handling

- Mermaid diagrams are allowed in fenced `mermaid` code blocks.
- If local Hugo or `genestack-site` needs additional rendering support, document
  the exact behavior here before it becomes part of the shared content contract.
