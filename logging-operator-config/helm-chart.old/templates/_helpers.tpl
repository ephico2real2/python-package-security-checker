{{/*
Generate basic labels.
*/}}
{{- define "logging-operator-config.labels" -}}
app.kubernetes.io/name: {{ include "logging-operator-config.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Define the name for the logging-operator-config.
*/}}
{{- define "logging-operator-config.name" -}}
{{ default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end -}}