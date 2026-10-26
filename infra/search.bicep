// Azure AI Search for the NorthStar Knowledge Assistant.
//
//   az group create -n northstar-rg -l swedencentral
//   az deployment group create -g northstar-rg -f infra/search.bicep
//
// The Free tier (one per subscription) holds the knowledge base easily; set
// sku=basic for production limits and SLA.

param location string = resourceGroup().location

@allowed(['free', 'basic'])
param sku string = 'free'

param name string = 'northstar-search-${uniqueString(resourceGroup().id)}'

resource search 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: name
  location: location
  sku: { name: sku }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    // Key auth for the evals; Entra (RBAC) auth is enabled alongside it.
    authOptions: { aadOrApiKey: { aadAuthFailureMode: 'http401WithBearerChallenge' } }
  }
}

output endpoint string = 'https://${search.name}.search.windows.net'
output name string = search.name
