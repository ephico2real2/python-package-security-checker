{{/*
Expand the name of the chart.
*/}}
{{- define "logging-config.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "logging-config.fullname" -}}
{{- if .Values.nameOverride }}
{{- printf "%s-%s" (include "logging-config.name" .) .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" (include "logging-config.name" .) .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "logging-config.labels" -}}
app.kubernetes.io/name: {{ include "logging-config.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: "{{ .Chart.AppVersion }}"
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/type: {{ get .Values.flow.labels "app.kubernetes.io/type" }}
{{- end }}

