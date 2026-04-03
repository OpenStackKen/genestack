---
title: "Post-Install Steps"
weight: 50
---

Once you're done installing all of the observability pieces, you should update your Alertmanager configuration to make sure you have at least one notification integration activated.

## Example Alertmanager Configuration

> [!EXAMPLE]
> 
> In this example, we supply a Teams webhook URL to send all open alerts to a teams channel.
> 
> However, there are a plethora of other receivers available. For a full list, review prometheus documentation: [receiver-integration-settings](https://prometheus.io/docs/alerting/latest/configuration/#receiver-integration-settings).
>
> ``` shell
> read -p "webhook_url: " webhook_url;
> sed -i -e "s#https://webhook_url.example#$webhook_url#" \
> /etc/genestack/helm-configs/prometheus/alertmanager_config.yaml
> ```
> 
> You can ignore this step if you don't want to send alerts to Teams, the alertmanager will still deploy and provide information.
