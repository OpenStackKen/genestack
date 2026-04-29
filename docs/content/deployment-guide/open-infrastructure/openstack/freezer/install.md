---
title: "Installation"
weight: 20
---

You will need to install both the Freezer API as well as the Freezer Client (including Freezer-Agent and Freezer-Scheduler)

## Installing Freezer-API

> [!tip]
>
> Login to your flex openstack cluster

### Create secrets

> [!note]
>
> Manual secret generation is only required if you haven't run the
> `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation

``` shell
kubectl --namespace openstack \
        create secret generic freezer-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"

kubectl --namespace openstack \
        create secret generic freezer-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"

kubectl --namespace openstack \
        create secret generic freezer-keystone-test-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"

kubectl --namespace openstack \
        create secret generic freezer-keystone-service-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

### Run the package deployment

> [!example]
>
> Run the Freezer deployment Script `/opt/genestack/bin/install-freezer.sh`

```bash {include="bin/install-freezer.sh"}

```

#### Validate Install Success

> [!command]
>
> ```bash
> kubectl get pods -n openstack | grep -i freezer
> kubectl get configmaps -n openstack | grep -i freezer
> kubectl get secrets -n openstack | grep freezer
> kubectl get service -n openstack | grep freezer
> ```

> [!output]
>
> ```bash
> kubectl get pods -n openstack | grep -i freezer
> freezer-api-5b8fcbcf8b-g6z6h               1/1     Running     0              3m54s
> freezer-api-5b8fcbcf8b-rbx4r               1/1     Running     0              4m9s
> freezer-api-5b8fcbcf8b-zc9c7               1/1     Running     0              3m54s
> freezer-db-sync-l7mnh                      0/1     Completed   0              4m9s
> freezer-ks-endpoints-bz6t5                 0/3     Completed   0              3m32s
> freezer-ks-service-jxgp7                   0/1     Completed   0              3m52s
> freezer-ks-user-tqqqt                      0/1     Completed   0              2m54s
>
> kubectl get configmaps -n openstack | grep -i freezer
> freezer-bin                      7      4m35s
>
> kubectl get secrets -n openstack | grep freezer
> freezer-admin                                                    Opaque               1      6d9h
> freezer-db-admin                                                 Opaque               1      4m45s
> freezer-db-password                                              Opaque               1      6d9h
> freezer-db-user                                                  Opaque               1      4m45s
> freezer-etc                                                      Opaque               4      4m45s
> freezer-keystone-admin                                           Opaque               9      4m45s
> freezer-keystone-service-password                                Opaque               1      6d9h
> freezer-keystone-test-password                                   Opaque               1      6d9h
> freezer-keystone-user                                            Opaque               9      4m45s
> sh.helm.release.v1.freezer.v1                                    helm.sh/release.v1   1      4m45s
>
> kubectl get service -n openstack | grep -i freezer
> freezer-api                 ClusterIP      10.x.x.x   <none>        9090/TCP
> ```


> [!tip]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single region or lab deployment you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`.

## Installing Freezer-Agent and Freezer-Scheduler on Freezer-Client

In this case its assumed that your Freezer-Client is actually a VM which can talk to
the openstack api endpoints of your flex cluster.

> [!note]
>
> In this case its assumed Ubuntu OS is the OS of choice on the freezer-client VM. However, it can really be any OS as long as its able to run python, since all freezer-agent code runs inside the virtual environment.

```bash
sudo apt-get install python3-dev
sudo apt install python3.12-venv
sudo python3 -m venv freezer-venv
source freezer-venv/bin/activate

pip install pymysql
pip install freezer
```

Now freezer binaries are available inside the virtual environment.

Create RC file with flex openstack cluster credentials like this example:

```bash
# ==================== BASIC AUTHENTICATION ====================
export OS_AUTH_URL="https://keystone.cloud.dev/v3"
export OS_USERNAME=admin
export OS_PASSWORD=password
export OS_PROJECT_NAME=admin
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default

# ==================== API VERSIONS ====================
export OS_IDENTITY_API_VERSION=3

# ==================== ENDPOINT CONFIGURATION ====================
export OS_ENDPOINT_TYPE=publicURL
export OS_REGION_NAME=RegionOne

# ==================== SSL CONFIGURATION ====================
export OS_INSECURE=true
export PYTHONHTTPSVERIFY=0
```

> [!warning]
>
> Make sure your DNS resolution is able to resolve the public endpoints for freezer service running on your openstack flex cluster.

Create `freezer-scheduler.conf` file

```ini title="freezer-scheduler.conf"
[DEFAULT]

freezer_endpoint_interface=public

# Logging Configuration (Recommended)
log_file = /var/log/freezer/scheduler.log
log_dir = /var/log/freezer
use_syslog = False

# Client Identification (CRITICAL)
# This ID is used by the API to assign jobs to this specific scheduler instance.
# It's usually set to the VM's hostname.
client_id = freezer-client

# Jobs Directory (Where the scheduler looks for local job definitions - optional)
jobs_dir = /home/ubuntu/freezer-bkp-dir

# API Polling Interval (in seconds)
interval = 60

[keystone_authtoken]
auth_url = https://keystone.cloud.dev/v3
auth_type = password
project_domain_name = Default
user_domain_name = Default
project_name = service
username = freezer
password = freezer-service-password
```

Start freezer-scheduler

```bash
freezer-scheduler start \
            --insecure \
            --config-file /etc/freezer/freezer-scheduler.conf
```
### Register Freezer agent

> [!example]
>
> Create client description using json file `client_register_config.json`

```json title="client_register_config.json"
{
  "client_id": "backup-client-vm",
  "client_name": "backup-client-vm",
  "client_os": "Linux",
  "architecture": "x86_64",
  "os_version": "Ubuntu 24.04 LTS"
}
```

> [!command]
>
> ```bash
> freezer client-register --file client_register_config.json
> ```

> [!output]
>
> ```bash
> Client backup-client-vm registered
> ```

While running above command, have a watch on kubectl logs of freezer-api pods in your openstack cluster:

```bash
sudo kubectl logs -n openstack freezer-api-6849445b5c-7s4cn -f
sudo kubectl logs -n openstack freezer-api-6849445b5c-dqm8n -f
...
2025-10-06 15:43:25.809 1 INFO freezer_api.db.sqlalchemy.api [req-d7f36415-4b7f-4f8f-a36c-1917f117f6f4 - - - - - -]  Client registered, client_id: backup-client-vm
```
