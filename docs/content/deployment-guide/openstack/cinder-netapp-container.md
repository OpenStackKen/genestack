---
title: "NetApp **Container** Volume Worker – Backend Options Guide"
weight: 410
aliases:
  - /deployment-guide/openstack-cinder-netapp-container/
  - /openstack-cinder-netapp-container/
---
**Audience:** Cloud operators who will deploy the *containerised* NetApp Cinder volume worker (NFS‑only).

**Why a separate guide?** The container image does **not** support iSCSI; if you need iSCSI, follow the
[NetApp Volume Worker – Operator Guide](/deployment-guide/openstack-cinder-netapp-worker/) instead.

## 1  Understand the BACKENDS Variable

The container expects a single environment variable – `BACKENDS` – that embeds one or more backend definitions. Each backend is a comma‑separated
list of **10** fields; multiple backends are separated by semicolons.

``` bash
BACKENDS="<field0>,<field1>,…,<field10>; <field0>,<field1>,…,<field10>; …"
```

### 1.1  Field Reference

| Index | Field Name                     | Purpose / Example                                           | Type    |
| ----- | ------------------------------ | ----------------------------------------------------------- | ------- |
| **0** | `backend_name`                 | Logical name → becomes `volume_backend_name` (`nfs-prod-a`) | String  |
| **1** | `netapp_login`                 | API username                                                | String  |
| **2** | `netapp_password`              | API password (store secret!)                                | String  |
| **3** | `netapp_server_hostname`       | FQDN or IP of ONTAP cluster                                 | String  |
| **4** | `netapp_server_port`           | 80 / 443                                                    | Integer |
| **5** | `netapp_vserver`               | SVM that exports the NFS volumes                            | String  |
| **6** | `netapp_dedup`                 | `True` or `False`                                           | Boolean |
| **7** | `netapp_compression`           | `True` or `False`                                           | Boolean |
| **8** | `netapp_thick_provisioned`     | `True` (guaranteed) or `False` (thin)                       | Boolean |
| **9** | `netapp_lun_space_reservation` | `enabled` / `disabled`                                      | String  |

> [!TIP]
> **Dedup + compression combo**
>
>
> ONTAP generally requires both `dedup=True` and `compression=True` for best space savings on hybrid‐disk aggregates.
>

## 2  Operator Workflow

1. ✅ Draft backend string
2. 🔐 Create Kubernetes secret
3. 🚀 Deploy Kustomize manifest
4. 🔍 Validate Cinder services & exports

### 2.1  Draft the BACKENDS String

Fill in real values; keep the order **exactly** as in § 1.1.

``` bash
export BACKENDS="nfs-prod-a,netappuser,supersecret,ontap‑01.example.com,443,SVM01,none,True,True,False,disabled"
```

For multiple backends:

``` bash
export BACKENDS="nfs-prod-a,netappuser,supersecret,ontap‑01.example.com,443,SVM01,none,True,True,False,disabled; \
                nfs-dr-b,netappuser,supersecret,ontap‑02.example.com,443,SVM02,none,True,True,False,disabled"
```

### 2.2  Create the Secret

``` bash
kubectl -n openstack create secret generic cinder-netapp \
        --type Opaque \
        --from-literal=BACKENDS="${BACKENDS}"
```

> [!CAUTION]
> **Store passwords securely**
>
>
> Prefer `--from-file` with an encrypted `backends.env` manifest in GitOps pipelines instead of inline literals.
>

### 2.3  Deploy the Worker

``` bash
kubectl -n openstack apply -k /etc/genestack/kustomize/cinder/netapp
```

The Kustomize overlay mounts the secret as an env‑file and launches the container.

## 3  Post‑Deployment Checks

### 3.1  Volume Type Mapping

Create a volume type per backend and attach `extra_specs`:

``` bash
openstack --os-cloud default volume type create nfs-prod-a
```

> [!IMPORTANT]
> **Expected Output**
>
>
> ``` shell
> +-------------+---------------------------------------+
> | Field       | Value                                 |
> +-------------+---------------------------------------+
> | description | None                                  |
> | id          | 6af6ade2-53ca-4260-8b79-1ba2f208c91d  |
> | is_public   | True                                  |
> | name        | nfs-prod-a                            |
> +-------------+---------------------------------------+
> ```
>

Refer to:

- [Volume QoS](/operational-guide/openstack-cinder-volume-qos-policies/)
- [Provisioning Specs](/operational-guide/openstack-cinder-volume-provisioning-specs/)
- [Extra Specs](/operational-guide/openstack-cinder-volume-type-specs/)

> [!WARNING]
> **Backend without policies = sad tenants**
>
>
> Skipping this step may leave tenants with a backend they cannot consume or that violates performance guarantees.
>

### 3.2  Service Health

``` bash
kubectl -n openstack exec -it openstack-admin-client -- openstack volume service list
```

You should see entries like:

> [!IMPORTANT]
> **Expected Output**
>
>
> ``` shell
> +------------------+--------------------------------------------------------------------+------+---------+-------+----------------------------+
> | Binary           | Host                                                               | Zone | Status  | State | Updated At                 |
> +------------------+--------------------------------------------------------------------+------+---------+-------+----------------------------+
> | cinder-scheduler | cinder-volume-worker                                               | az1  | enabled | up    | 2023-12-26T17:43:07.000000 |
> | cinder-volume    | cinder-volume-netapp-worker@nfs-prod-a                             | az1  | enabled | up    | 2023-12-26T17:43:04.000000 |
> +------------------+--------------------------------------------------------------------+------+---------+-------+----------------------------+
> ```
>

## Appendix

### Example Secret Manifest (GitOps‑friendly)

> [!IMPORTANT]
>
>
> Inject secrets manager values (e.g., `sealed-secrets`, `external-secrets`) in place of `${…}` placeholders.
>
> ``` yaml
> apiVersion: v1
> kind: Secret
> metadata:
>     name: cinder-netapp
>     namespace: openstack
> stringData:
>     BACKENDS: >
>     nfs-prod-a,${ONTAP_USER},${ONTAP_PASS},ontap-01.example.com,443,SVM01,none,True,True,False,disabled;
>     nfs-dr-b,${ONTAP_USER},${ONTAP_PASS},ontap-02.example.com,443,SVM02,none,True,True,False,disabled
> ```
>

### Common Issues

| Symptom                               | Likely Cause                     | Resolution                                        |
| ------------------------------------- | -------------------------------- | ------------------------------------------------- |
| `No valid host was found`             | Type not mapped to backend       | Check `volume_backend_name` extra‑spec            |
| `HTTP 403` from ONTAP API in logs     | Wrong creds or insufficient role | Verify `netapp_login` permissions                 |
| Pod crash‑loop with `BACKENDS` parse  | Missing or extra field           | Ensure **11** fields per backend, no trailing `;` |
| NFS export accessible but perms issue | SVM export‑policy mismatch       | Update ONTAP export policy to allow compute CIDRs |
