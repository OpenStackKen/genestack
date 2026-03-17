---
title: "Deploy Keystone"
weight: 440
aliases:
  - /operational-guide/openstack-keystone-ldap/
  - /openstack-keystone-ldap/
---
The OpenStack Identity service supports integration with existing LDAP directories for authentication and authorization services. OpenStack Identity only supports read-only LDAP integration. Integrating Active Directory (AD) with OpenStack Keystone is usually done via LDAP backend. Keystone doesn’t talk to AD “natively” — it treats AD as an LDAP directory.

Keystone → LDAP driver → Active Directory

Auth happens against AD, but Keystone still manages projects, roles, tokens.

## Example LDAP configuration

> [!IMPORTANT]
> **LDAP/AD config `/etc/genestack/helm-configs/keystone/keystone-helm-overrides-ldap.yaml`**
>
>
> ```yaml
> ---
> conf:
>   keystone:
>     identity:
>       domain_specific_drivers_enabled: true
>       domain_config_dir: /etc/keystone/domains
>       driver: ldap
> ldap:
>   example.com:
>     url: ldaps://ldap.example.com
>     user: cn=readonly,dc=example,dc=com
>     password: example-password
>     suffix: dc=example,dc=com
>     user_tree_dn: ou=People,dc=example,dc=com
>     user_objectclass: inetOrgPerson
> ```
>

## Install/Reinstall Keystone Service

```bash
/opt/genestack/bin/install-keystone.sh
```

## Validate functionality

``` shell
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack user list --domain <AD domain name>
```

[UPSTREAM-DOCUMENTATION](https://docs.openstack.org/keystone/latest/admin/configuration.html#integrate-identity-with-ldap)
