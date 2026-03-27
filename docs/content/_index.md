---
title: "Genestack Documentation"
weight: 10
description: "Reference, design, deployment, and operations documentation for Genestack."
---
{{< home/hero
  eyebrow="Genestack Reference Documentation"
  heading="Build, Operate, and Extend Genestack"
  lead="Reference material for architecture, deployment, operations, and onboarding."
>}}


Browse the documentation and contribute on GitHub.

{{< home/button text="Get the code" param="github_repo" variant="secondary" icon="github" new_tab="true" >}}
{{< /home/hero >}}

Genestack combines Kubernetes, OpenStack, and supporting infrastructure into a
single cloud operations and deployment workflow.

<!-- prettier-ignore -->
<div class="td-cta-buttons my-5">
  <a {{% _param btn-lg primary %}} href="/overview/">
    Overview
  </a>
  <a {{% _param btn-lg secondary %}}
    href="/deployment-guide/">
    Deploy
  </a>
</div>

{{< home/section
  title="Core Guides"
  description="Primary documentation entry points."
>}}
{{< home/card
  title="Design Guide"
  url="/design-guide/"
  description="Cloud design decisions, regional structure, resiliency, and platform architecture guidance."
>}}
{{< home/card
  title="Deployment Guide"
  url="/deployment-guide/"
  description="Environment bring-up, platform prerequisites, and service deployment workflows."
>}}
{{< home/card
  title="Operations Guide"
  url="/operational-guide/"
  description="Day-two operations, troubleshooting, lifecycle tasks, and operational playbooks."
>}}
{{< /home/section >}}

{{< home/section
  title="Additional Guides"
  description="Audience-specific entry points and supporting reference material."
>}}
{{< home/card
  title="Overview"
  url="/overview/"
  description="Platform concepts, architecture, and component overviews."
>}}
{{< home/card
  title="Cloud Onboarding"
  url="/cloud-onboarding/"
  description="End-user onboarding for CLI setup, compute, networking, storage, and common OpenStack workflows."
>}}
{{< /home/section >}}

{{< home/actions title="External Resources" >}}
{{< home/button text="Discord" url="https://discord.gg/2mN5yZvV3a" >}}
{{< home/button text="Rackspace OpenStack" url="https://www.rackspace.com/solve/return-openstack" >}}
{{< /home/actions >}}
