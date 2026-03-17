---
title: "Quick Start Guide"
weight: 50
aliases:
  - /deployment-guide/build-test-envs/
  - /build-test-envs/
---
This guide will walk you through the process of deploying a test environment for Genestack. This is a great way to get started
with the platform and to familiarize yourself with the deployment process. The following steps will guide you through the process
of deploying a test environment on an OpenStack cloud in a simple three node configuration that is hyper-converged.

## Build Script

The following script will deploy a hyperconverged lab environment on an OpenStack cloud. The script can be found at
[`scripts/hyperconverged-lab.sh`](https://raw.githubusercontent.com/rackerlabs/genestack/refs/heads/main/scripts/hyperconverged-lab.sh).

> [!NOTE]
> **View the  Hyper-converged Lab Script**
>
>
> ``` shell
> #!/usr/bin/env bash
> # shellcheck disable=SC2124,SC2145,SC2294,SC2086,SC2087,SC2155
> #
> # Hyperconverged Lab Deployment Selector
> #
> # This script provides a simple interface to deploy Genestack (OpenStack on Kubernetes)
> # in a hyperconverged configuration using either:
> #
> #   1. Kubespray   - Traditional approach using Ubuntu VMs and Kubespray/Ansible
> #   2. Talos Linux - Modern approach using Talos Linux immutable OS
> #
> # Usage:
> #   ./hyperconverged-lab.sh                    # Interactive mode - prompts for platform
> #   ./hyperconverged-lab.sh kubespray [args]   # Deploy using Kubespray
> #   ./hyperconverged-lab.sh talos [args]       # Deploy using Talos Linux
> #
> # For uninstall, use the corresponding uninstall scripts:
> #   ./hyperconverged-lab-kubespray-uninstall.sh
> #   ./hyperconverged-lab-talos-uninstall.sh
> #
> 
> set -o pipefail
> set -e
> 
> SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
> 
> function show_usage() {
>     cat <<EOF
> Hyperconverged Lab Deployment Script
> 
> This script deploys Genestack (OpenStack on Kubernetes) in a hyperconverged
> configuration on OpenStack infrastructure.
> 
> USAGE:
>     $(basename "$0") [PLATFORM] [OPTIONS]
> 
> PLATFORMS:
>     kubespray    Deploy using Kubespray on Ubuntu (traditional approach)
>                  - Uses Ubuntu VMs with SSH access
>                  - Kubernetes deployed via Kubespray/Ansible
>                  - Requires SSH keypair for node access
> 
>     talos        Deploy using Talos Linux (modern approach)
>                  - Uses Talos Linux immutable OS
>                  - Kubernetes deployed via talosctl
>                  - No SSH - managed via Talos API
>                  - Includes Talos-specific configs for Longhorn, Kube-OVN, Ceph
> 
>     help         Show this help message
> 
> OPTIONS:
>     -i <list>    Comma-separated list of OpenStack services to include
>     -e <list>    Comma-separated list of OpenStack services to exclude
>     -x           Run extra operations (k9s install, Octavia preconf, etc.)
> 
> ENVIRONMENT VARIABLES:
>     ACME_EMAIL          Email for ACME/Let's Encrypt certificates
>     GATEWAY_DOMAIN      Domain name for the gateway (default: cluster.local)
>     OS_CLOUD            OpenStack cloud configuration name (default: default)
>     OS_FLAVOR           Flavor to use for instances
>     OS_IMAGE            Image to use (platform-specific defaults apply)
>     LAB_NAME_PREFIX     Prefix for all created resources
>     LAB_NETWORK_MTU     MTU for lab networks (default: 1500)
>     HYPERCONVERGED_DEV  If set to "true", enables development mode which transports
>                         the local environment checkout into the hyperconverged lab
>                         for easier testing and debugging.
>     HYPERCONVERGED_CINDER_VOLUME
>                         If set to "true", enables iSCSI cinder volume support.
>     DISABLE_OPENSTACK
>                         if set to "true", no openstack services will be deployed.
> 
> EXAMPLES:
>     # Interactive mode - will prompt for platform choice
>     $(basename "$0")
> 
>     # Deploy using Kubespray
>     $(basename "$0") kubespray
> 
>     # Deploy using Talos Linux
>     $(basename "$0") talos
> 
>     # Deploy Kubespray with extra services and extras enabled
>     $(basename "$0") kubespray -i heat,octavia -x
> 
>     # Deploy Talos with specific services excluded
>     $(basename "$0") talos -e skyline
> 
> UNINSTALL:
>     Use the platform-specific uninstall scripts:
> 
>     # Uninstall Kubespray deployment
>     ./hyperconverged-lab-kubespray-uninstall.sh
> 
>     # Uninstall Talos deployment
>     ./hyperconverged-lab-talos-uninstall.sh
> 
> For more information, see the Genestack documentation.
> EOF
> }
> 
> function prompt_for_platform() {
>     echo ""
>     echo "Hyperconverged Lab Deployment"
>     echo "============================="
>     echo ""
>     echo "Select your deployment platform:"
>     echo ""
>     echo "  1) Kubespray"
>     echo "     - Traditional approach using Ubuntu VMs"
>     echo "     - Kubernetes deployed via Kubespray/Ansible"
>     echo "     - SSH-based node management"
>     echo ""
>     echo "  2) Talos Linux"
>     echo "     - Modern immutable Linux OS designed for Kubernetes"
>     echo "     - API-based management (no SSH)"
>     echo "     - Includes Talos-specific configurations for Longhorn, Kube-OVN, Ceph"
>     echo ""
> 
>     read -rp "Enter your choice [1/2]: " choice
> 
>     case "$choice" in
>         1|kubespray|Kubespray|KUBESPRAY)
>             echo ""
>             echo "Selected: Kubespray"
>             PLATFORM="kubespray"
>             ;;
>         2|talos|Talos|TALOS)
>             echo ""
>             echo "Selected: Talos Linux"
>             PLATFORM="talos"
>             ;;
>         *)
>             echo "Invalid choice. Please enter 1 or 2."
>             exit 1
>             ;;
>     esac
> }
> 
> # Check for help flag first
> if [[ "$1" == "help" || "$1" == "--help" || "$1" == "-h" ]]; then
>     show_usage
>     exit 0
> fi
> 
> # Determine platform from first argument or prompt
> if [[ -n "$1" && "$1" != -* ]]; then
>     case "$1" in
>         kubespray|Kubespray|KUBESPRAY)
>             PLATFORM="kubespray"
>             shift
>             ;;
>         talos|Talos|TALOS)
>             PLATFORM="talos"
>             shift
>             ;;
>         *)
>             echo "Unknown platform: $1"
>             echo ""
>             show_usage
>             exit 1
>             ;;
>     esac
> else
>     prompt_for_platform
> fi
> 
> # Execute the appropriate platform-specific script
> case "$PLATFORM" in
>     kubespray)
>         echo ""
>         echo "Launching Kubespray deployment..."
>         echo ""
>         exec "${SCRIPT_DIR}/hyperconverged-lab-kubespray.sh" "$@"
>         ;;
>     talos)
>         echo ""
>         echo "Launching Talos Linux deployment..."
>         echo ""
>         exec "${SCRIPT_DIR}/hyperconverged-lab-talos.sh" "$@"
>         ;;
> esac
> ```
>

The build script is interactive and will prompt you for the following information

| <div style="width:156px">Variable</div> | Description | <div style="width:156px">Default</div> |
|----------|-------------|---------|
| `ACME_EMAIL` | Email address for Let's Encrypt. If an email address is defined and a real domain is used, the deployment will attempt to pull production certificates. | "" |
| `GATEWAY_DOMAIN` | Domain name used for routes within the gateway API. If a valid domain is used, it will be associated with the gateway routes. | "cluster.local" |
| `OS_CLOUD` | OpenStack cloud name. | "default" |
| `OS_FLAVOR` | OpenStack instance flavor, this will automatically select a flavor with < 24GiB of RAM. | "gp.X.8.16" |
| `OS_IMAGE` | OpenStack image name. | "Ubuntu 24.04" |
| `HYPERCONVERGED_DEV` | enable hyperconverged development mode. This will attempt to sync a local copy of Genestack to the development environment. | `false` |
| `LAB_NAME_PREFIX` | Prefix for the lab environment. Useful when building multiple labs in a single project | "hyperconverged" |

All of the variables can be defined on the command line using environment variables.

> [!IMPORTANT]
> **Deploying a Hyper-converged Lab Environment with Environment Variables**
>
>
> ``` shell
> export ACME_EMAIL="user@domain.com"
> export GATEWAY_DOMAIN="cluster.local"
> export OS_CLOUD="default"
> export OS_FLAVOR="gp.0.8.16"
> export OS_IMAGE="Ubuntu 24.04"
> export HYPERCONVERGED_DEV="false"
> /opt/genestack/scripts/hyperconverged-lab.sh
> ```
>

## Overview

A simple reference architecture for a hyper-converged lab environment is shown below. This environment consists of three nodes
that are connected to a two networks. The networks are connected via a router that provides external connectivity.

``` mermaid
%%{ init: { "theme": "default",
            "flowchart": { "curve": "basis", "nodeSpacing": 80, "rankSpacing": 60 } } }%%
            
flowchart TB
    %% Define clusters/subgraphs for clarity
    subgraph Public_Network ["<div style="width:15em; height:8.5em; display:flex; justify-content: flex-start; align-items:flex-end;">Public Network</div>"]
        PF("Floating IP<br>(203.0.113.x)")
    end

    subgraph Router ["<div style="width:29em; height:8.5em; display:flex; justify-content: flex-start; align-items:flex-end;">Router</div>"]
        TR("hyperconverged-router<br>(with external gateway)")
    end

    subgraph Hyperconverged_Net ["<div style="width:55em; height:8.5em; display:flex; justify-content: flex-start; align-items:flex-end;">HyperConverged Net</div>"]
        TN("hyperconverged-net<br>(192.168.100.x)")
    end

    subgraph Hyperconverged_Compute_Net ["<div style="width:43em; height:10em; display:flex; justify-content: flex-start; align-items:flex-end;">HyperConverged Compute Net</div>"]
        TCN("hyperconverged-compute-net<br>(192.168.102.x)")
    end

    %% Hyperconverged Nodes
    subgraph NODE_0 ["<div style="width:15em; height:7em; display:flex; justify-content: flex-start; align-items:flex-end;">Node 0</div>"]
        HPC0("hyperconverged-0")
    end

    subgraph Node_1 ["<div style="width:15em; height:7em; display:flex; justify-content: flex-start; align-items:flex-end;">Node 1</div>"]
        HPC1("hyperconverged-1")
    end

    subgraph Node_2 ["<div style="width:15em; height:7em; display:flex; justify-content: flex-start; align-items:flex-end;">Node 2</div>"]
        HPC2("hyperconverged-2")
    end

    %% Connections
    PF --> TR
    TR --> TN

    TN -- mgmt port --> HPC0
    TN -- mgmt port --> HPC1
    TN -- mgmt port --> HPC2

    HPC0 -- compute port --> TCN
    HPC1 -- compute port --> TCN
    HPC2 -- compute port --> TCN
```

## Build Phases

The deployment script will perform the following steps:

- Create a new OpenStack router
- Create a new OpenStack networks
- Create a new OpenStack security groups
- Create a new OpenStack ports
- Create a new OpenStack keypair
- Create a new OpenStack instance
- Create a new OpenStack floating IP
- Execute the basic Genestack installation

## Post Deployment

After the deployment is complete, the script will output the internal and external floating IP address information.

With this information, operators can login to the Genestack instance and begin to explore the platform.

> [!IMPORTANT]
>
> Genestack uses DNS to route services in Kubernetes, which may be a bit different from what you might be used to in other lab environments, where
> IP addresses are used heavily.  To be able to access OpenStack externally from the jumpbox, set `GATEWAY_DOMAIN` to a DNS domain that you control.
>

### Setting up DNS for a Hyper-Converged Lab

At the end of the hyper-converged lab script run, you will see output that looks like this:

```
The lab is now ready for use and took 1298 seconds to complete.
This is the jump host address WW.XX.YY.ZZ, write this down.
This is the VIP address internally 192.168.100.NN with public address AA.BB.CC.DD within MetalLB, write this down.
```

To make DNS correctly resolve the OpenStack services in the lab, you will need to set some DNS entries for the `GATEWAY_DOMAIN` you specified when building the lab.  Using the "cluster.local" default example domain, you should configure something like this:

```
jumpbox.cluster.local       A       WW.XX.YY.ZZ
cluster.local               A       AA.BB.CC.DD
*.cluster.local             CNAME   cluster.local
```

> [!WARNING]
>
> Do **NOT** use `cluster.local` as your domain.  You will need to use a domain that you control and you will need to set the `GATEWAY_DOMAIN` variable to this prior to building your hyper-converged lab.
>

### Accessing your Hyper-Converged Lab

When generating your hyper-converged lab, the script creates an SSH key pair and puts it into your `$HOME/.ssh` directory.  The name of the key is derived from the `LAB_NAME_PREFIX` variable, and the default is `hyperconverged`.

To access the lab, you can SSH into the jumpbox using this key as the default user of the OpenStack Glance image you specified.  The default image is Ubuntu 24.04 LTS which has a default user of `ubuntu`.  In this case, the SSH command would be as follows:

```bash
bash$ ssh -i $HOME/.ssh/hyperconverged-key.pem ubuntu@jumpbox.cluster.local
```

The jumpbox user has passwordless sudo if configured in the Glance image. (The Ubuntu 24.04 LTS image has this.)

If you sudo to the `root` user, and look at the `clouds.yaml` file for that user, you will be able to see the OpenStack `admin` user password:

```
bash$ sudo su - root
bash# cat $HOME/.config/openstack/clouds.yaml
cache:
  auth: true
  expiration_time: 3600
clouds:
  default:
    auth:
      auth_url: http://keystone-api.openstack.svc.cluster.local:5000/v3
      project_name: admin
      tenant_name: default
      project_domain_name: default
      username: admin
      password: <PASSWORD>
      user_domain_name: default
    region_name: RegionOne
    interface: internal
    identity_api_version: "3"
```

This can be used to login to the Skyline web console.  To access the Skyline web console, you can just enter `https://skyline.cluster.local` (again, using `cluster.local` as an example) and access it from your web browser.

> [!NOTE]
>
> If you get SSL errors, wait a bit. Cert Manager takes time to generate all the SSL certs it using with Let's Encrypt.
>

## Demo

[![asciicast](https://asciinema.org/a/706976.svg)](https://asciinema.org/a/706976)
