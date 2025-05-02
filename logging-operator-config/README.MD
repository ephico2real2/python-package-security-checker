### README.md

## Overview

This Helm chart deploys the Logging configuration for CloudWatch and Splunk logging.

## Prerequisites

** https://kube-logging.dev/docs/ **

- Kubernetes 1.26+
- Helm 3.0+

## Installation

To install the chart with the release name `my-release`:

```sh
helm lint ./helm-chart
```

```sh
helm install my-release ./helm-chart
```
## Values

The following table lists the configurable parameters of the Logging Config chart and their default values.

| Parameter                                      | Description                                           | Default                                       |
|------------------------------------------------|-------------------------------------------------------|-----------------------------------------------|
| `namespace`                                    | Kubernetes namespace                                  | `project-1`                                   |
| `nameOverride`                                 | Override the name of the chart                        | `""`                                          |
| `environmentName`                              | The environment name (e.g., production)               | `dev`                                         |
| `region`                                       | The AWS region                                        | `us-east-1`                                   |
| `targetClusterName`                            | The name of the target cluster                        | `dev-cluster`                                 |
| `flow.baseName`                                | Base name for the flow                                | `flow`                                        |
| `flow.labels.app.kubernetes.io/type`           | Labels to select for the Flow                         | `backend`                                     |
| `cloudwatch.enabled`                           | Enable CloudWatch logging                             | `true`                                        |
| `cloudwatch.output.name`                       | Suffix Name of the CloudWatch Output resource         | `cloudwatch-output`                           |
| `cloudwatch.output.log_group_name`             | CloudWatch log group name  (Please SKIP)              | `/aws/eks/test-cluster/project-1`             |
| `cloudwatch.output.log_stream_name`            | CloudWatch log stream name                            | `"${tag}"`                                    |
| `cloudwatch.output.auto_create_stream`         | Auto create CloudWatch log stream                     | `true`                                        |
| `cloudwatch.output.buffer.timekey`             | Time key for CloudWatch buffer                        | `30s`                                         |
| `cloudwatch.output.buffer.timekey_wait`        | Time key wait for CloudWatch buffer                   | `30s`                                         |
| `cloudwatch.output.buffer.timekey_use_utc`     | Use UTC time for CloudWatch buffer                    | `true`                                        |
| `splunk.enabled`                               | Enable Splunk logging                                 | `true`                                        |
| `splunk.hecTokenSecretName`                    | Suffix Name of the Splunk HEC token secret            | `splunk-hec-token`                            |
| `splunk.secretStore`                           | Suffix Secret store for Splunk HEC token              | `aws-secrets-manager`                         |
| `splunk.refreshInterval`                       | Refresh interval for the Splunk external secret       | `30m`                                         |
| `splunk.secretName`                            | Suffix Name of the secret in the secret store         | `splunk-hec-token`                            |
| `splunk.output.name`                           | Suffix Name of the Splunk Output resource             | `splunk-output`                               |
| `splunk.output.hec_host`                       | Splunk HEC host                                       | `splunk-single-standalone-headless`           |
| `splunk.output.insecure_ssl`                   | Allow insecure SSL                                    | `true`                                        |
| `splunk.output.hec_port`                       | Splunk HEC port                                       | `8088`                                        |
| `splunk.output.index`                          | Splunk index                                          | `main`                                        |
| `splunk.output.format_type`                    | Format type for Splunk logs                           | `json`                                        |

This table lists all configurable parameters for the Helm chart, providing descriptions and default values for each parameter.

# List the flow and output from the deployments

```bash
kubectl get flow,output,externalsecret,secretstore,secret
```

## OutPut

```bash
NAME                                                                      ACTIVE   PROBLEMS
flow.logging.banzaicloud.io/logging-config-logging-operator-config-flow   true

NAME                                                                                     ACTIVE   PROBLEMS
output.logging.banzaicloud.io/logging-config-logging-operator-config-cloudwatch-output   true
output.logging.banzaicloud.io/logging-config-logging-operator-config-splunk-output       true

NAME                                                                                         STORE                                                   REFRESH INTERVAL   STATUS         READY
externalsecret.external-secrets.io/logging-config-logging-operator-config-splunk-hec-token   logging-config-logging-operator-config-secret-manager   30m                SecretSynced   True
externalsecret.external-secrets.io/portal-db-secret                                          portal-secret-manager                                   5m                 SecretSynced   True
externalsecret.external-secrets.io/portal-insights-secrets                                   portal-secret-manager                                   5m                 SecretSynced   True
externalsecret.external-secrets.io/queue-db-secret                                           queue-secret-manager                                    5m                 SecretSynced   True
externalsecret.external-secrets.io/queue-insights-secrets                                    queue-secret-manager                                    5m                 SecretSynced   True

NAME                                                                                    AGE     STATUS   CAPABILITIES   READY
secretstore.external-secrets.io/logging-config-logging-operator-config-secret-manager   7m55s   Valid    ReadWrite      True
secretstore.external-secrets.io/portal-secret-manager                                   147d    Valid    ReadWrite      True
secretstore.external-secrets.io/queue-secret-manager                                    147d    Valid    ReadWrite      True

NAME                                                             TYPE                DATA   AGE
secret/logging-config-logging-operator-config-splunk-hec-token   Opaque              1      7m55s
secret/portal-db-secret                                          Opaque              2      169d
secret/portal-insights-secrets                                   Opaque              6      41d
secret/queue-db-secret                                           Opaque              2      169d
secret/queue-insights-secrets                                    Opaque              2      41d
secret/wildcard-jamf-chaos-io-tls                                kubernetes.io/tls   3      119d

```

## verify logging component from logging namespace

```bash
kubectl get pods -n logging

## OutPut

NAME                                            READY   STATUS      RESTARTS   AGE
logging-operator-7c896d44b6-mf6zg               1/1     Running     0          44d
logging-operator-fluentbit-8qnrx                1/1     Running     0          8d
logging-operator-fluentbit-j4vdm                1/1     Running     0          7d2h
logging-operator-fluentbit-kkkv8                1/1     Running     0          8d
logging-operator-fluentbit-kn8gb                1/1     Running     0          6d11h
logging-operator-fluentbit-ks6ff                1/1     Running     0          8d
logging-operator-fluentd-0                      3/3     Running     0          6d11h   ==> Central Fluentd router Pod
logging-operator-fluentd-configcheck-3990572c   0/1     Completed   0          10m     ==> configuration validator Job

```

## verify 

```bash
kubectl -n logging logs -f logging-operator-fluentd-0
```


```bash
### Truncated
  <label @d9b07ec8f519991aa37a959e4ed32939>
    <match kubernetes.**>
      @type tag_normaliser
      @id flow:datajar-django-dev:logging-config-logging-operator-config-flow:0
      format "${namespace_name}.${pod_name}.${container_name}"
    </match>
    <match **>
      @type copy
      <store>
        @type "cloudwatch_logs"
        @id flow:datajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operator-config-cloudwatch-output
        auto_create_stream true
        log_group_name "/aws/eks/euw2-datajar-dev231206/datajar-django-dev"
        log_stream_name "${tag}"
        region "eu-west-2"
        <buffer tag,time>
          @type "file"
          chunk_limit_size 8MB
          path "/buffers/flow:datajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operator-config-cloudwatch-output.*.buffer"
          retry_forever true
          timekey 30s
          timekey_use_utc true
          timekey_wait 30s
        </buffer>
      </store>
      <store>
        @type "splunk_hec"
        @id flow:datajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operator-config-splunk-output
        hec_host "https://http-inputs-jamf.splunkcloud.com"
        hec_port 443
        hec_token xxxxxx
        index "cloud_dev_datajar_application"
        insecure_ssl true
        <buffer tag,time>
          @type "file"
          chunk_limit_size 8MB
          path "/buffers/flow:datajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operator-config-splunk-output.*.buffer"
          retry_forever true
          timekey 10m
          timekey_wait 1m
        </buffer>
        <format>
          @type "json"
        </format>
      </store>
    </match>
  </label>
  <label @1224b1f3b4d162538ecdddf2cf171964>
    <match kubernetes.**>
      @type tag_normaliser
      @id clusterflow:logging:cloudwatch:0
      format "${namespace_name}.${pod_name}.${container_name}"
    </match>
    <match **>
      @type cloudwatch_logs
      @id clusterflow:logging:cloudwatch:clusteroutput:logging:cloudwatch
      auto_create_stream true
      log_group_name "/aws/eks/euw2-datajar-dev231206/addons"
      log_stream_name "${tag}"
      region "eu-west-2"
      <buffer tag,time>
        @type "file"
        chunk_limit_size 8MB
        flush_thread_count 8
        path "/buffers/clusterflow:logging:cloudwatch:clusteroutput:logging:cloudwatch.*.buffer"
        retry_forever true
        timekey 15m
        timekey_use_utc true
        timekey_wait 60s
      </buffer>
    </match>
  </label>
  <label @ERROR>
    <match **>
      @type null
      @id main-fluentd-error
    </match>
  </label>
  <match **>
    @type null
    @id main-no-output
  </match>
</ROOT>
2024-06-05 22:25:55 +0000 [info]: finished dry run mode

```

```bash
2024-06-06 13:50:09 +0000 [info]: adding match in @d9b07ec8f519991aa37a959e4ed32939 pattern="kubernetes.**" type="tag_normaliser"
2024-06-06 13:50:09 +0000 [info]: adding match in @d9b07ec8f519991aa37a959e4ed32939 pattern="**" type="copy"
2024-06-06 13:50:09 +0000 [info]: adding match in @66824a0009aded45c315e47475225383 pattern="kubernetes.**" type="tag_normaliser"
2024-06-06 13:50:09 +0000 [info]: adding match in @66824a0009aded45c315e47475225383 pattern="**" type="splunk_hec"
2024-06-06 13:50:09 +0000 [info]: adding match in @1224b1f3b4d162538ecdddf2cf171964 pattern="kubernetes.**" type="tag_normaliser"
2024-06-06 13:50:09 +0000 [info]: adding match in @1224b1f3b4d162538ecdddf2cf171964 pattern="**" type="cloudwatch_logs
```

## Possible connections errors

```bash

2024-06-05 23:37:11 +0000 [warn]: #0 [flow:tor-config-splunk-oudatajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operatput] failed to flush the buffer. retry_times=10 next_retry_time=2024-06-05 23:55:40 +0000 chunk="61a2cab6de70f6255dddffde9fa3b178" error_class=SocketError error="Failed to open TCP connection to https:443 (getaddrinfo: Name does not resolve)"
  2024-06-05 23:37:11 +0000 [warn]: #0 suppressed same stacktrace
2024-06-05 23:55:39 +0000 [warn]: #0 [flow:datajar-django-dev:logging-config-logging-operator-config-flow:output:datajar-django-dev:logging-config-logging-operator-config-splunk-output] failed to flush the buffer. retry_times=11 next_retry_time=2024-06-06 00:30:01 +0000 chunk="61a2cab6de70f6255dddffde9fa3b178" error_class=SocketError error="Failed to open TCP connection to https:443 (getaddrinfo: Name does not resolve)"
  2024-06-05 23:55:39 +0000 [warn]: #0 suppressed same stacktrace

```


