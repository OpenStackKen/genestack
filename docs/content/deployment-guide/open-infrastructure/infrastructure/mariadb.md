---
title: "MariaDB"
weight: 80
---

Deploying the MariaDB Operator and Mariadb Cluster


### Creating Secrets

> [!info]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation:

```bash
kubectl --namespace openstack \
        create secret generic mariadb \
        --type Opaque \
        --from-literal=root-password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Deploy the mariadb operator

```
CLUSTER_NAME=`kubectl config view --minify -o jsonpath='{.clusters[0].name}'`
echo $CLUSTER_NAME
```

If `cluster_name` was anything other than `cluster.local` you should pass that as a parameter to the installer

> [!example]
> 
> Run the mariadb-operator deployment Script `/opt/genestack/bin/install-mariadb-operator.sh` You can include cluster_name parameter from the output of $CLUSTER_NAME. If no parameters are provided, the system will deploy with `cluster.local` as the cluster name.

```bash {include="bin/install-mariadb-operator.sh"}
```

> [!NOTE]
> The operator may take a minute to get ready, before deploying the Galera cluster, wait until the webhook is online.

``` shell
kubectl --namespace mariadb-system get pods -w
```

## Deploying  the MariaDB Cluster

There are several deployment strategies that you can leverage for MariaDB deployment.  For production, either  **Galera** clustering or **Replication** is recommended.  

### Galera _(Recommended)_

> [!info] Galera Cluster setup
>
> The `galera` configuration is designed for high availability and production-ready deployments of MariaDB in OpenStack environments. By using the Galera Cluster, you can ensure that your database remains available and consistent even in the event of node failures, making it an ideal choice for critical cloud services.

MariaDB with Galera Cluster is a popular choice for ensuring high availability and scalability in OpenStack deployments. Galera is a synchronous multi-master replication plugin for MariaDB, allowing all nodes in the cluster to read and write simultaneously while ensuring data consistency across the entire cluster. This setup is particularly advantageous in OpenStack environments, where database operations must be highly reliable and available to support the various services that depend on them. By using Galera with MariaDB, OpenStack deployments can achieve near-instantaneous replication across multiple nodes, enhancing fault tolerance and providing a robust solution for handling the high-demand workloads typical in cloud environments.

To deploy MariaDB with Galera clustering, change the `/etc/genestack/kustomize/mariadb-cluster/overlay` file to replace `base` with the `galera` resource.

```yaml
resources:
- ../galera
```

Then deploy the cluster:

```bash
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```

### Replication _(Recommended)_

> [!info]
>
> MariaDB has a base configuration which is HA and production ready. If you're deploying on a small cluster the `aio` configuration may better suit the needs of the environment.

Replication in MariaDB involves synchronizing data between a primary database and one or more replicas, enabling continuous data availability even in the event of hardware failures or outages. By using MariaDB replication, OpenStack deployments can achieve improved fault tolerance and load balancing, ensuring that critical cloud services remain operational and performant at all times.

```bash
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```

### AIO

> [!INFO] All in one (AIO) setup
> 
> The `aio` configuration is designed for smaller OpenStack deployments or testing environments where simplicity and ease of management are prioritized over high availability. By using a single MariaDB server, the AIO setup provides a straightforward solution for managing the database needs of OpenStack without the complexity of clustering or replication.

In some OpenStack deployments, a single MariaDB server is used to manage the database needs of the cloud environment. While this setup is simpler and easier to manage than clustered solutions, it is typically suited for smaller environments or use cases where high availability and fault tolerance are not critical. A single MariaDB server provides a centralized database service for storing and managing the operational data of OpenStack components, ensuring consistent performance and straightforward management. However, it is important to recognize that this configuration presents a single point of failure, making it less resilient to outages or hardware failures compared to more robust, multi-node setups.

To deploy the AIO configuration, change the `/etc/genestack/kustomize/mariadb-cluster/overlay` file to replace `base` with the `aio` resource:

```yaml
resources:
- ../aio
```
Then deploy MariaDB:

``` shell
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```
