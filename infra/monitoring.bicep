// Azure Monitor for the NorthStar knowledge agent: Log Analytics plus a
// workspace-based Application Insights resource. The agent exports its
// OpenTelemetry traces (Agent Framework spans for agent runs, model calls,
// and tool calls) here via APPLICATIONINSIGHTS_CONNECTION_STRING.
//
//   az deployment group create -g northstar-rg -f infra/monitoring.bicep

param location string = resourceGroup().location

param prefix string = 'northstar'

var suffix = uniqueString(resourceGroup().id)

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs-${suffix}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-agent-insights-${suffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
    IngestionMode: 'LogAnalytics'
  }
}

output connectionString string = insights.properties.ConnectionString
output appInsightsName string = insights.name
