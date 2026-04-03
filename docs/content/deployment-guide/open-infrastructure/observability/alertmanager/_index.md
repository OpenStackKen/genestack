---
title: "Alertmanager"
weight: 20
type: docs
simple_list: true
cascade:
  - type: docs
---

Alerting with Prometheus is separated into two parts:

1. Alerting rules in Prometheus servers send alerts to an Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/).
2. The Alertmanager then manages those alerts.

Alertmanager provides a complete solution for handling alerts, including silencing, inhibition, aggregation and sending out notifications via methods such as email, on-call notification systems, and chat platforms. It takes care of deduplicating, grouping, and routing them to the correct receiver integration such as email, PagerDuty, or OpsGenie. It also takes care of silencing and inhibition of alerts.

## AlertManager Integrations

Configure AlertManager to send notifications when alerts are triggered. Available integrations include:

- [Slack Alerts](/deployment-guide/open-infrastructure/observability/alertmanager-slack/) - Send alerts to Slack channels
- Email notifications
- PagerDuty integration
- Webhook receivers

## Customize Alerting Rules

### Custom Alerting Rules

> [!GENESTACK]
>
> Genestack includes a set of default alerting rules that can be customized for your environment.

To view or modify the default Genestack rules:

```shell
less /etc/genestack/helm-configs/prometheus/alerting_rules.yaml
```

Edit this file to add, modify, or remove alerting rules based on your operational requirements.

### Operator-Provided Alerting Rules

Many Genestack operators come with built-in ServiceMonitor and PodMonitor resources that automatically:

- Expose scrape endpoints for metrics collection
- Provide pre-configured alerting rules tailored to the specific service

These operator-managed rules are curated for best practices and don't require manual configuration. For service-specific monitoring details, refer to the individual service documentation. For example: [RabbitMQ Operator Monitoring](/deployment-guide/open-infrastructure/infrastructure/rabbitmq/#rabbitmq-operator-monitoring).
