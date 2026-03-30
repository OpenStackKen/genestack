---
title: "Release Notes"
weight: 50
---
## Release Notes

### 0.0.0

#### Prelude

Creating the foundation for the stable branch.

Initial release of a genestack installer for Rackspace OpenStack
environments

Blazar has been upgraded to OpenStack 2025.1 (Epoxy) release. This
upgrade brings important security fixes, policy enhancements with new
RBAC roles, and improved WSGI deployment capabilities. The Epoxy release
focuses on strengthening OpenStack's position as a VMware alternative
while enhancing security and operational capabilities.

Placement upgraded to OpenStack 2025.1 (Epoxy) release.

Glance Epoxy (2025.1) focuses on safer image handling, predictable
multi-store download behavior, and stability fixes for policy
initialization and RBD-backed deployments. The release introduces
stricter upload/import validation while retaining operator controls for
compatibility tuning.

#### New Features

-   Kubernetes deployment and management with Kubespray. This release
    uses Kubernetes 1.30.x and Kubespray 2.27.0.

    <https://docs.rackspacecloud.com/k8s-kubespray/>

&nbsp;

-   Kube-OVN CNI plugin is supported in this release. Kube-OVN can be
    deployed to provide networking services to the Kubernetes cluster.

    <https://docs.rackspacecloud.com/k8s-cni-kube-ovn/>

&nbsp;

-   Prometheus monitoring with the Prometheus Operator. This release
    uses Prometheus Operator to deploy and manage Prometheus, which is
    used for system monitoring and alerting.

    <https://docs.rackspacecloud.com/prometheus/>

&nbsp;

-   Kubernetes PVC Storage with Rook Ceph is supported in this release.
    Rook Ceph can be deployed internal to the Kubernetes cluster to
    provide persistent storage options.

    <https://docs.rackspacecloud.com/storage-ceph-rook-internal/>

&nbsp;

-   Kubernetes PVC Storage with Rook Ceph is supported in this release.
    Rook Ceph can be deployed external to the Kubernetes cluster to
    provide persistent storage options.

    <https://docs.rackspacecloud.com/storage-ceph-rook-external/>

&nbsp;

-   Kubernetes PVC Storage with NFS is supported in this release. NFS
    can be deployed external to the Kubernetes cluster to provide
    persistent storage options.

    <https://docs.rackspacecloud.com/storage-nfs-external/>

&nbsp;

-   Kubernetes PVC Storage with TopoLVM is supported in this release.
    TopoLVM can be deployed internal to the Kubernetes cluster to
    provide persistent storage options.

    <https://docs.rackspacecloud.com/storage-topolvm/>

&nbsp;

-   Kubernetes PVC Storage with Longhorn (recommended) is supported in
    this release. Longhorn can be deployed internal to the Kubernetes
    cluster to provide persistent storage options.

    <https://docs.rackspacecloud.com/storage-longhorn/>

&nbsp;

-   MetalLB LoadBalancer is supported in this release. MetalLB can be
    deployed to provide LoadBalancer services to the Kubernetes cluster.
    This is used by default for VIP address functionality within
    platform service loadbalancers.

    <https://docs.rackspacecloud.com/infrastructure-metallb/>

&nbsp;

-   MariaDB Operator is supported in this release. MariaDB Operator can
    be deployed to provide database services to the Kubernetes cluster.
    This is used by default for OpenStack Services

    <https://docs.rackspacecloud.com/databases-mariadb-operator/>

&nbsp;

-   Postgres Operator is supported in this release. The Zalando Postgres
    Operator can be deployed to provide database services for
    applications. This is used by default for OpenStack metering
    services.

    <https://docs.rackspacecloud.com/infrastructure-postgresql/>

&nbsp;

-   RabbitMQ Operator is supported in this release. RabbitMQ Operator
    can be deployed to provide message queue services to the Kubernetes
    cluster. This is used by default for OpenStack Services.

    <https://docs.rackspacecloud.com/infrastructure-rabbitmq/>

&nbsp;

-   Memcached is supported in this release. Memcached can be deployed to
    provide fast caching services to the Kubernetes cluster. This is
    used by default for OpenStack Services.

    <https://docs.rackspacecloud.com/infrastructure-memcached/>

&nbsp;

-   Libvirt is supported in this release for virtualization. Libvirt can
    be deployed to provide virtualization services to the Kubernetes
    cluster. This is used by default for OpenStack Services.

    <https://docs.rackspacecloud.com/infrastructure-libvirt/>

&nbsp;

-   OVN for OpenStack is supported in this release. OVN is deployed to
    provide networking services to OpenStack Consumers and is default
    for OpenStack.

    <https://docs.rackspacecloud.com/infrastructure-ovn-setup/>

&nbsp;

-   Log collection is supported in this release. Fluentbit can be
    deployed to provide log collection services to the Kubernetes
    cluster. This is used by default for all services.

    <https://docs.rackspacecloud.com/infrastructure-fluentbit/>

&nbsp;

-   Log aggregation is supported in this release. Loki can be deployed
    to provide log aggregation services to the Kubernetes cluster. This
    is used by default for all services.

    <https://docs.rackspacecloud.com/infrastructure-loki/>

&nbsp;

-   OpenStack Keystone is supported in this release. OpenStack Keystone
    can be deployed to provide identity services for OpenStack and is
    used by default.

    <https://docs.rackspacecloud.com/openstack-keystone/>

&nbsp;

-   OpenStack Glance is supported in this release. OpenStack Glance can
    be deployed to provide image services for OpenStack and is used by
    default.

    <https://docs.rackspacecloud.com/openstack-glance/>

&nbsp;

-   OpenStack Heat is supported in this release. OpenStack Heat can be
    deployed to provide orchestration services for OpenStack and is used
    by default.

    <https://docs.rackspacecloud.com/openstack-heat/>

&nbsp;

-   OpenStack Barbican is supported in this release. OpenStack Barbican
    can be deployed to provide key management services for OpenStack and
    is used by default.

    <https://docs.rackspacecloud.com/openstack-barbican/>

&nbsp;

-   OpenStack Cinder is supported in this release. OpenStack Cinder can
    be deployed to provide block storage services for OpenStack and is
    used by default.

    <https://docs.rackspacecloud.com/openstack-cinder/>

&nbsp;

-   OpenStack Placement is supported in this release. OpenStack
    Placement can be deployed to provide resource management services
    for OpenStack and is used by default.

    <https://docs.rackspacecloud.com/openstack-compute-kit-placement/>

&nbsp;

-   OpenStack Nova is supported in this release. OpenStack Nova can be
    deployed to provide compute services for OpenStack and is used by
    default.

    <https://docs.rackspacecloud.com/openstack-compute-kit-nova/>

&nbsp;

-   OpenStack Neutron is supported in this release. OpenStack Neutron
    can be deployed to provide networking services for OpenStack and is
    used by default.

    <https://docs.rackspacecloud.com/openstack-network-kit-neutron/>

&nbsp;

-   OpenStack Skyline is supported in this release. OpenStack Skyline
    can be deployed to provide dashboard services for OpenStack and is
    used by default.

    <https://docs.rackspacecloud.com/openstack-skyline/>

&nbsp;

-   OpenStack Octavia is supported in this release. OpenStack Octavia
    can be deployed to provide load balancing services for OpenStack and
    is used by default.

    <https://docs.rackspacecloud.com/openstack-octavia/>

&nbsp;

-   OpenStack Magnum is supported in this release. OpenStack Magnum can
    be deployed to provide container orchestration services for
    OpenStack and is used by default.

    <https://docs.rackspacecloud.com/openstack-magnum/>

&nbsp;

-   OpenStack Ceilometer is supported in this release. OpenStack
    Ceilometer can be deployed to provide telemetry services for
    OpenStack and is used by default.

    <https://docs.rackspacecloud.com/openstack-ceilometer/>

&nbsp;

-   Gnocchi is supported in this release. Gnocchi can be deployed to
    provide metric services for OpenStack and is used by default within
    the metering stack.

    <https://docs.rackspacecloud.com/openstack-gnocchi/>

&nbsp;

-   Grafana is supported in this release. Grafana can be deployed to
    provide metric visualization services for OpenStack and is used by
    default within the metering stack.

    <https://docs.rackspacecloud.com/grafana/>

&nbsp;

-   Service metric collection is supported in this release and is
    interconnected with prometheus and grafana to provide metric
    visualization services throughout the cluster.

    Supported Exporters:  
    -   Kube-OVN
    -   Envoy Gateway
    -   RabbitMQ
    -   Memcached
    -   MariaDB
    -   Postgres
    -   OpenStack
    -   Blackbox
    -   Pushgateway

    Dashboards are all pre-configured for all supported exporters and
    visualized via Grafana.

&nbsp;

-   Alert Manager is supported in this release. Alert Manager can be
    deployed to provide alerting services for the cluster and is used by
    default.

    <https://docs.rackspacecloud.com/alertmanager-slack/>

&nbsp;

-   Allow other kubernetes deployment models including Talos k8s stack
    to include a managed cert-manager helm chart. Decouple the
    cert-manager installation from the base kubespray ansible roles and
    allow the official upstream charts to provide chart and CRD updates
    including patched image rollouts. This includes envoy gateway-api
    support and custom DNS server forwarders.

&nbsp;

-   Added Designate is the DNS-as-a-Service (DNSaaS) component of
    Genestack. It provides API-driven management of DNS zones and
    records, so tenants and services can automatically create and update
    DNS entries as infrastructure changes.

&nbsp;

-   Envoy Gateway with a full featured configuration in support of
    OpenStack. Envoy implements the Gateway API with traffic policies,
    loadbalancers, and listeners which are configured to support the
    OpenStack APIs.

&nbsp;

-   HPA will now trigger off CPU utilization as well as RAM consumption.
    OpenStack services ram consumption is fairly static based on the
    number of workers, threads, and processes. With this change, CPU
    consumption will now also be considered for horizontal auto scaling.

    In order to ensure that HPA has been properly tuned for a 3-node
    hyper-converged lab deployment (our recommended lab/testing
    deployment) this change will also standardize, across all OpenStack
    services, the number of workers to 2, the number or processes to 2,
    and the number of threads per process to 1. Additionally, we will
    reduce the minReplicas from 3 to 2 to reduce overall resource usage
    while still maintaining a fault tolerant cluster.

    While this is NOT a breaking change, it will change the resource
    consumption of any deployment going forward.

&nbsp;

-   Add LDAP/AD Integration into Keystone config via genestack overrides
    file

&nbsp;

-   The OVN-Setup manifest will now set the MAC address of the neutron
    physical network interface to the MAC address of the OVN logical
    network interface using the hostname + interface name as the seed.

&nbsp;

-   **New WSGI Module**: A new module `blazar.wsgi` has been added to
    provide a consistent location for WSGI application objects. This
    simplifies deployment with modern WSGI servers like gunicorn and
    uWSGI by allowing module path references (e.g.,
    `blazar.wsgi.api:application`) instead of file paths.

&nbsp;

-   **Enhanced RBAC Policies**: Blazar now implements scope-based
    policies with new default roles (admin, member, and reader) provided
    by Keystone. All policies now support `scope_type` capabilities with
    project-level scoping, providing more granular access control while
    maintaining backward compatibility with legacy admin roles.

&nbsp;

-   **Instance Reservation Updates**: Fixed the ability to update the
    number of instances in an instance reservation while the lease is
    active, improving operational flexibility.

&nbsp;

-   Added `placement.wsgi` module for simplified WSGI server deployment.

&nbsp;

-   Added new configuration options:
    `[placement]max_allocation_candidates`,
    `[placement]allocation_candidates_generation_strategy`, and
    `[workarounds]optimize_for_wide_provider_trees` to improve
    allocation candidate generation performance, particularly in
    deployments with wide provider trees.

&nbsp;

-   Added image content inspection during upload/import to validate
    declared disk_format against uploaded data.

&nbsp;

-   Added configuration controls:
    \[image_format\]/require_image_format_match and
    \[image_format\]/gpt_safety_checks_nonfatal.

&nbsp;

-   Updated GET images behavior to sort image locations by configured
    store weight, affecting which backend location is preferred for
    download.

&nbsp;

-   Extended stores detail API output for RBD backends to include fsid.

&nbsp;

-   Added Openstack Trove support. Migrated Trove to use the official
    upstream OpenStack-Helm chart now that it has been merged and is
    available in the upstream repository.

#### Known Issues

-   The OVN loadbalancers options are by default available within
    Genestack but is currently "tech preview" and not recommended for
    production use.

&nbsp;

-   Skyline UI currently limits the loadbalancer types to Amphora. This
    is a known issue and will be resolved in a future release.

&nbsp;

-   The designate service cleaner is not functional at the moment as of
    Feb 2026, possibly fixed in 2026.2. Added custom image in base helm
    overrides file to fix.

&nbsp;

-   No explicit unresolved known issues were identified in the reviewed
    Epoxy Glance note fragments; operators should still validate
    upload/import behavior with real image sets due to stricter format
    checks.

#### Upgrade Notes

-   When upgrading from a previous release of Genestack, if SAML
    Federation was enabled, you must update the HTTP Routes for both
    Keystone and Skyline. During the development of the SAML Federation
    feature, Keystone and Skyline HTTRoutes were updated to have cookie
    driven session persistence to ensure compatibility with Shibboleth.

        Full example files for the HTTP Routes can be found in the
        ``etc/gateway-api/routes`` directory.

    The following stanza should be added to the HTTP Routes for
    Keystone; file typically located at
    `/etc/genestack/gateway-api/routes/custom-keystone-gateway-route.yaml`.

    ``` yaml
    sessionPersistence:
      sessionName: KeystoneSession
      type: Cookie
      absoluteTimeout: 300s
      cookieConfig:
        lifetimeType: Permanent
    ```

    The following stanza should be added to the HTTP Routes for Skyline;
    file typically located at
    `/etc/genestack/gateway-api/routes/custom-skyline-gateway-route.yaml`.

    ``` yaml
    sessionPersistence:
      sessionName: SkylineSession
      type: Cookie
      absoluteTimeout: 300s
      cookieConfig:
        lifetimeType: Permanent
    ```

    Once the configuration is updated, Run the deployment update with
    the following apply commands.

    ``` shell
    kubectl -n openstack apply -f /etc/genestack/gateway-api/routes/custom-keystone-gateway-route.yaml
    kubectl -n openstack apply -f /etc/genestack/gateway-api/routes/custom-skyline-gateway-route.yaml
    ```

    Once the HTTP Routes are updated, verify that the changes have been
    applied by checking the status of the HTTP Routes.

    ``` shell
    kubectl -n openstack get httproutes.gateway.networking.k8s.io custom-keystone-gateway-route -o yaml
    kubectl -n openstack get httproutes.gateway.networking.k8s.io custom-skyline-gateway-route -o yaml
    ```

&nbsp;

-   When upgrading from a pre-release to stable, the following changes
    will need to be made to the ansible inventory or group_vars to
    support stable cert-manager

    ``` yaml
    cert_manager_controller_extra_args:
      - "--enable-gateway-api"
    ```

    In previous builds the `--enable-gateway-api` was unset, but it is
    now a required option.

&nbsp;

-   When upgrading from a pre-release to stable, the following changes
    will need to be made to the ansible inventory or group_vars to
    support stable metallb

    ``` yaml
    metallb_enabled: false
    ```

    In previous builds the `metallb_enabled` was set to true, but it is
    now managed by the MetalLB helm chart.

&nbsp;

-   When upgrading from a pre-release to stable, the following changes
    will need to be made to the ansible inventory or group_vars to
    eliminate the CNI plugin from the Kubespray Management.

    ``` yaml
    kube_network_plugin: none
    ```

    In previous builds the `kube_network_plugin` was set to kube-ovn,
    but it is now managed by the Kube-OVN helm chart.

&nbsp;

-   When upgrading from a pre-release to stable, the following changes
    will need to be made to the ansible inventory or group_vars to
    eliminate the previous assumption of the kubeadm patch files.

    ``` yaml
    kubeadm_patches: []
    ```

    In previous builds the `kubeadm_patches` was set to a dictionary of
    patches that would deploy files into the environment. This interface
    was changed upstream and now must be a list of string type patches.
    Review the upstream documentation\[0\] for more information.

    \[0\]
    <https://github.com/kubernetes-sigs/kubespray/blob/v2.27.0/roles/kubernetes/kubeadm_common/defaults/main.yml>

&nbsp;

-   When upgrading from a pre-release to stable, the following file no
    longer has any effect on the environment and can be removed from the
    ansible group_vars.

    /etc/genestack/inventory/group_vars/k8s_cluster/k8s-net-kube-ovn.yml

    This file can be eliminated.

&nbsp;

-   When upgrading from a pre-release to stable, review the Kube-OVN to
    Helm migration documentation at
    <https://docs.rackspacecloud.com/k8s-cni-kube-ovn-helm-conversion>
    as this step will be required before running Kubespray again.

&nbsp;

-   The memcached helm chart now places memcached on the openstack
    control plane using the label openstack-control-plane=enabled. Min
    replicas set to 1 as default setting and can be change according the
    control plane installation.

&nbsp;

-   The metallb configuration is now consolidated and cleaned up by
    providing the metallb IP address pools:
    -   gateway-api-external for Envoy
    -   primary for all internal services including MariaDB, RabbitMQ
        and others
    -   The pool pool1 is replaced by primary

&nbsp;

-   Neutron OVN setting localnet_learn_fdb is now enabled to avoid
    flodding on provider networks once port security is disabled. See
    <https://launchpad.net/bugs/2012069>

&nbsp;

-   Operators upgrading from an early build will need to ensure that the
    OVN-Setup manifest is re-applied so that the MAC address of the
    neutron physical network interface is set. Operators who chose to
    not run this manifest will need will need to set their MAC addresses
    manually.

    See
    <https://docs.openstack.org/neutron/latest/install/ovn/manual_install.html>
    for more information on the manual OVN Setup process.

&nbsp;

-   **WSGI Script Removal**: The `blazar-api-wsgi` script has been
    removed. Deployment configurations must be updated to reference the
    Python module path `blazar.wsgi.api:application` for WSGI servers
    that support module paths (gunicorn, uWSGI), or implement a custom
    `.wsgi` script for servers like mod_wsgi.

    Example uWSGI configuration change:

    ``` ini
    # Old configuration
    [uwsgi]
    wsgi-file = /bin/blazar-api-wsgi

    # New configuration
    [uwsgi]
    module = blazar.wsgi.api:application
    ```

&nbsp;

-   **Policy Migration**: While old policy rules remain supported for
    backward compatibility, operators should plan to migrate to the new
    scope-aware policies. The legacy `admin_or_owner` rule is deprecated
    in favor of new role-based rules like `project_member_api`,
    `project_reader_api`, `project_member_or_admin`, and
    `project_reader_or_admin`.

&nbsp;

-   **Image Updates**: Blazar container images have been updated to
    version `2025.1-latest`. Ensure your helm overrides reference the
    correct image tags as shown in
    `base-helm-configs/blazar/blazar-helm-overrides.yaml`.

&nbsp;

-   Helm chart updated to `2025.1.2+0cd784591`.

&nbsp;

-   Consider configuring `max_allocation_candidates` and
    `allocation_candidates_generation_strategy` for wide provider trees.

&nbsp;

-   Support for running Glance services on Windows operating systems has
    been removed.

&nbsp;

-   Upload/import now checks content against disk_format by default;
    operators should review current image pipelines and user workflows
    for format mismatch failures and tune related image_format options
    as needed.

#### Deprecation Notes

-   The barbican chart will now use the online OSH helm repository. This
    change will allow the barbican chart to be updated more frequently
    and will allow the barbican chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall barbican
    kubectl -n openstack delete -f /etc/genestack/kustomize/barbican/base/barbican-rabbitmq-queue.yaml
    /opt/genestack/bin/install-barbican.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   In early builds of Genestack Kube-OVN was deployed and managed by
    Kubespray; however, this is no longer the case. The Kube-OVN helm
    chart is now used to deploy and manage the Kube-OVN CNI plugin.

&nbsp;

-   In early builds of Genestack MetalLB was deployed and managed by
    Kubespray; however, this is no longer the case. The MetalLB helm
    chart is now used to deploy and manage the MetalLB LoadBalancer.

&nbsp;

-   In early builds of Genestack the cert-manager option
    `ExperimentalGatewayAPISupport` was set to true, within the ansible
    group_vars. This option should be removed as it no longer has any
    effect.

&nbsp;

-   The blazar chart will now use the online OSH helm repository. This
    change will allow the blazar chart to be updated more frequently and
    will allow the blazar chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall blazar
    kubectl -n openstack delete -f /etc/genestack/kustomize/blazar/base/blazar-rabbitmq-queue.yaml
    /opt/genestack/bin/install-blazar.sh
    ```

    This operation should have no operational impact on running
    workloads but should be performed during a maintenance window.

&nbsp;

-   The ceilometer chart will now use the online OSH helm repository.
    This change will allow the ceilometer chart to be updated more
    frequently and will allow the ceilometer chart to be used with the
    OpenStack-Helm project. Upgrading to this chart may require changes
    to the deployment configuration. Simple updates can be made by
    running the following command:

    ``` shell
    helm -n openstack uninstall ceilometer
    kubectl -n openstack delete -f /etc/genestack/kustomize/ceilometer/base/ceilometer-rabbitmq-queue.yaml
    /opt/genestack/bin/install-ceilometer.sh
    ```

    This operation should have no operational impact but should be
    performed during a maintenance window.

&nbsp;

-   The cinder chart will now use the online OSH helm repository. This
    change will allow the cinder chart to be updated more frequently and
    will allow the cinder chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall cinder
    kubectl -n openstack delete -f /etc/genestack/kustomize/cinder/base/cinder-rabbitmq-queue.yaml
    /opt/genestack/bin/install-cinder.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The cloudkitty chart will now use the online OSH helm repository.
    This change will allow the cloudkitty chart to be updated more
    frequently and will allow the cloudkitty chart to be used with the
    OpenStack-Helm project. Upgrading to this chart may require changes
    to the deployment configuration. Simple updates can be made by
    running the following command:

    ``` shell
    helm -n openstack uninstall cloudkitty
    kubectl -n openstack delete -f /etc/genestack/kustomize/cloudkitty/base/cloudkitty-rabbitmq-queue.yaml
    /opt/genestack/bin/install-cloudkitty.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The glance chart will now use the online OSH helm repository. This
    change will allow the glance chart to be updated more frequently and
    will allow the glance chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall glance
    kubectl -n openstack delete -f /etc/genestack/kustomize/glance/base/glance-rabbitmq-queue.yaml
    /opt/genestack/bin/install-glance.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The gnocchi chart will now use the online OSH helm repository. This
    change will allow the gnocchi chart to be updated more frequently
    and will allow the gnocchi chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall gnocchi
    kubectl -n openstack delete -f /etc/genestack/kustomize/gnocchi/base/gnocchi-rabbitmq-queue.yaml
    /opt/genestack/bin/install-gnocchi.sh
    ```

&nbsp;

-   The heat chart will now use the online OSH helm repository. This
    change will allow the heat chart to be updated more frequently and
    will allow the heat chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall heat
    kubectl -n openstack delete -f /etc/genestack/kustomize/heat/base/heat-rabbitmq-queue.yaml
    /opt/genestack/bin/install-heat.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The horizon chart will now use the online OSH helm repository. This
    change will allow the horizon chart to be updated more frequently
    and will allow the horizon chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall horizon
    /opt/genestack/bin/install-horizon.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The keystone chart will now use the online OSH helm repository. This
    change will allow the keystone chart to be updated more frequently
    and will allow the keystone chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall keystone
    kubectl -n openstack delete -f /etc/genestack/kustomize/keystone/base/keystone-rabbitmq-queue.yaml
    /opt/genestack/bin/install-keystone.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The libvirt chart will now use the online OSH helm repository. This
    change will allow the libvirt chart to be updated more frequently
    and will allow the libvirt chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall libvirt
    /opt/genestack/bin/install-libvirt.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The magnum chart will now use the online OSH helm repository. This
    change will allow the magnum chart to be updated more frequently and
    will allow the magnum chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall magnum
    kubectl -n openstack delete -f /etc/genestack/kustomize/magnum/base/magnum-rabbitmq-queue.yaml
    /opt/genestack/bin/install-magnum.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The masakari chart will now use the online OSH helm repository. This
    change will allow the masakari chart to be updated more frequently
    and will allow the masakari chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall masakari
    kubectl -n openstack delete -f /etc/genestack/kustomize/masakari/base/masakari-rabbitmq-queue.yaml
    /opt/genestack/bin/install-masakari.sh
    ```

    This operation should have no operational impact on running
    workloads but should be performed during a maintenance window.

&nbsp;

-   The neutron chart will now use the online OSH helm repository. This
    change will allow the neutron chart to be updated more frequently
    and will allow the neutron chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall neutron
    kubectl -n openstack delete -f /etc/genestack/kustomize/neutron/base/neutron-rabbitmq-queue.yaml
    /opt/genestack/bin/install-neutron.sh
    ```

&nbsp;

-   The nova chart will now use the online OSH helm repository. This
    change will allow the nova chart to be updated more frequently and
    will allow the nova chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall nova
    kubectl -n openstack delete -f /etc/genestack/kustomize/nova/base/nova-rabbitmq-queue.yaml
    /opt/genestack/bin/install-nova.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   The octavia chart will now use the online OSH helm repository. This
    change will allow the octavia chart to be updated more frequently
    and will allow the octavia chart to be used with the OpenStack-Helm
    project. Upgrading to this chart may require changes to the
    deployment configuration. Simple updates can be made by running the
    following command:

    ``` shell
    helm -n openstack uninstall octavia
    kubectl -n openstack delete -f /etc/genestack/kustomize/octavia/base/octavia-rabbitmq-queue.yaml
    /opt/genestack/bin/install-octavia.sh
    ```

    Depending on the state of the Octavia deployment, it may be
    nessessary to rerun the ansible-playbook for the octavia deployment.
    Note that this playbook will drop a marker file
    `/tmp/octavia_hm_controller_ip_port_list` which may need to be
    cleaned up before rerunning the playbook.

    <https://docs.rackspacecloud.com/openstack-octavia/#run-the-playbook>

    That said, if the deployment was healthy before, the cleanup steps
    should not be needed. This operation should have no operational
    impact on running VMs but should be performed during a maintenance
    window.

&nbsp;

-   The placement chart will now use the online OSH helm repository.
    This change will allow the placement chart to be updated more
    frequently and will allow the placement chart to be used with the
    OpenStack-Helm project. Upgrading to this chart may require changes
    to the deployment configuration. Simple updates can be made by
    running the following command:

    ``` shell
    helm -n openstack uninstall placement
    /opt/genestack/bin/install-placement.sh
    ```

    This operation should have no operational impact on running VMs but
    should be performed during a maintenance window.

&nbsp;

-   **WSGI Script Deprecated and Removed**: The `blazar-api-wsgi` script
    has been removed in Epoxy (15.0.0). Use the module path
    `blazar.wsgi.api:application` instead.

&nbsp;

-   **Legacy Policy Rules**: The following policy rules are deprecated
    and will be silently ignored in future releases:

    -   `admin_or_owner` - Use `project_member_api` or
        `project_reader_api`
    -   Legacy `rule:admin_or_owner` references - Use new role-based
        rules

    JSON-formatted policy files have been deprecated since Blazar 7.0.0
    (Wallaby). Use the `oslopolicy-convert-json-to-yaml` tool to migrate
    to YAML format.

&nbsp;

-   No new deprecations were explicitly called out in the reviewed Epoxy
    Glance fragments.

#### Security Issues

-   **Critical Lease Security Fix**: Resolved a security vulnerability
    (LP#2120655) where any user could update or delete a lease from any
    project if they had the lease ID. With default policy configuration,
    regular users cannot see lease IDs from other projects. However,
    operators running the Resource Availability Calendar with overridden
    policies may have been vulnerable without this fix.

#### Bug Fixes

-   Fixed host randomization feature functionality (LP#2099927).

&nbsp;

-   Fixed an issue preventing updates to the instance count in active
    instance reservations (LP#2138386).

&nbsp;

-   Resolved security vulnerability allowing unauthorized lease
    modifications across projects (LP#2120655).

&nbsp;

-   Fixed excessive memory consumption when generating allocation
    candidates in deployments with wide provider trees.

&nbsp;

-   LP \#2081009: Fixed oslo_config.cfg.NotInitializedError when
    switching the default policy_file in oslo.policy.

&nbsp;

-   LP \#2086675: Fixed suspected performance regression for RBD
    backends linked to image location sorting behavior.

#### Other Notes

-   Current HPA values included in this change were determined using
    the, workers=2, processes=2, and threads=1 model. A hyper-converged
    lab was created and workers, processes,threads reduced to provide a
    baseline of resource usage. From pod requests and limits were
    adjusted to take into account the baseline resource consumption.

    In base-helm-configs, por resources needed to be enabled and the
    requests/limits configured. If limits is set to {} it is pulling the
    defaults from the Helm chart. \[example\] resources: enabled: true
    api: requests: memory: "384Mi" cpu: "200m" limits: {}

&nbsp;

-   **Genestack Configuration**: The current Genestack configuration
    already uses the `2025.1-latest` image tags and includes proper
    RabbitMQ quorum queue configuration with notification routing to
    Ceilometer for billing integration.

&nbsp;

-   **Python Version**: OpenStack Epoxy requires Python 3.9 as the
    minimum supported version. Python 3.8 support has been removed
    across OpenStack projects.
