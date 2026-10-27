// A NorthStar project on the existing Azure AI Foundry resource (created by
// music_man/infra/foundry.bicep, with the gpt-4o deployment). Deploy into the
// Foundry resource's resource group:
//
//   az deployment group create -g musicman-rg -f infra/foundry-project.bicep \
//     -p foundryName=<Foundry resource name>

param foundryName string

param location string = resourceGroup().location

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryName
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: 'northstar-project'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'NorthStar Knowledge Agent'
    description: 'Knowledge agent over the NorthStar knowledge base (Azure AI Search) and the learner data lake (MCP).'
  }
}

output projectEndpoint string = 'https://${foundry.properties.customSubDomainName}.services.ai.azure.com/api/projects/${project.name}'
