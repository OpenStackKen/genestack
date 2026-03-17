---
title: "TopoLVM - In Cluster"
weight: 890
aliases:
  - /storage-topolvm/
---

# TopoLVM - In Cluster

[TopoLVM](https://github.com/topolvm/topolvm) is a capacity aware storage provisioner which can make use of physical volumes.

The following steps are one way to set it up, however, consult the [documentation](https://github.com/topolvm/topolvm/blob/main/docs/getting-started.md) for a full breakdown of everything possible with TopoLVM.

## Create the target volume group on your hosts

TopoLVM requires access to a volume group on the physical host to work, which means we need to set up a volume group on our hosts. By default, TopoLVM will use the controllers as storage hosts. The genestack Helm solution sets the general storage volume group to `vg-general`. This value can be changed within Helm overrides file found at `/opt/genestack/base-helm-configs/topolvm/helm-topolvm-overrides.yaml`.

> [!IMPORTANT]
> **Simple example showing how to create the needed volume group**
>
>
> ``` shell
> # NOTE sdX is a placeholder for a physical drive or partition.
> pvcreate /dev/sdX
> vgcreate vg-general /dev/sdX
> ```
>

Once the volume group is on your storage nodes, the node is ready for use.

### Deploy the TopoLVM Provisioner

> [!IMPORTANT]
> **Run the topolvm deployment Script bin/install-topolvm.sh**
>
>
> ``` shell
> ```shell
> #!/bin/bash
> 
> # Default parameter value
> TARGET=${1:-base}
> 
> # Directory to check for YAML files
> CONFIG_DIR="/etc/genestack/helm-configs/topolvm"
> 
> # Add the topolvm helm repository
> helm repo add topolvm https://topolvm.github.io/topolvm
> helm repo update
> 
> # Helm command setup
> HELM_CMD="helm upgrade --install topolvm topolvm/topolvm \
>     --create-namespace --namespace=topolvm-system \
>     --timeout 120m \
>     --post-renderer /etc/genestack/kustomize/kustomize.sh \
>     --post-renderer-args topolvm/${TARGET} \
>     -f /opt/genestack/base-helm-configs/topolvm/helm-topolvm-overrides.yaml"
> 
> # Check if YAML files exist in the specified directory
> if compgen -G "${CONFIG_DIR}/*.yaml" > /dev/null; then
>     # Add all YAML files from the directory to the helm command
>     for yaml_file in "${CONFIG_DIR}"/*.yaml; do
>         HELM_CMD+=" -f ${yaml_file}"
>     done
> fi
> 
> HELM_CMD+=" $@"
> 
> # Run the helm command
> echo "Executing Helm command:"
> echo "${HELM_CMD}"
> eval "${HELM_CMD}"
> ```
> ```

