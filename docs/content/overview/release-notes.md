---
title: "Release Notes"
weight: 60
---
All release notes are generated using [reno](https://docs.openstack.org/reno/latest/).

To manually generate your release notes and refresh this page's Markdown
source, run the following commands:

``` shell
pip install -r dev-requirements.txt
apt update && apt install -y pandoc
reno report -o /tmp/reno.rst
pandoc /tmp/reno.rst -f rst -t markdown -o docs/content/overview/release-notes.md
```
