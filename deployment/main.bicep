@description('Deploys the Healthcare Assistant infrastructure to Azure')
param location string = resourceGroup().location
param appName string = 'healthcare-assistant'
param environment string = 'dev'

// Azure OpenAI parameters
param openAiEndpoint string
param openAiApiKey string
param openAiDeploymentName string = 'gpt-4'
param openAiEmbeddingDeploymentName string = 'text-embedding-ada-002'

// Cosmos DB parameters
param cosmosDbAccountName string = '${appName}-cosmos-${environment}'
param databaseName string = 'HealthcareDB'
param knowledgeContainerName string = 'KnowledgeVectors'
param appointmentsContainerName string = 'Appointments'

// Storage account for Azure Functions
param storageAccountName string = '${appName}storage${environment}'

var functionAppName = '${appName}-functions-${environment}'
var webAppName = '${appName}-web-${environment}'
var orchestratorFunctionAppName = '${appName}-orchestrator-${environment}'

// Storage Account for Functions
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

// Cosmos DB Account
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-09-15' = {
  name: cosmosDbAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
  }
}

// Cosmos DB Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-09-15' = {
  parent: cosmosDbAccount
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

// Knowledge Vectors Container (with vector index)
resource knowledgeContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-09-15' = {
  parent: cosmosDatabase
  name: knowledgeContainerName
  properties: {
    resource: {
      id: knowledgeContainerName
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/embedding'
            type: 'quantizedFlat'
          }
        ]
      }
    }
  }
}

// Appointments Container
resource appointmentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-09-15' = {
  parent: cosmosDatabase
  name: appointmentsContainerName
  properties: {
    resource: {
      id: appointmentsContainerName
      partitionKey: {
        paths: ['/user_id']
        kind: 'Hash'
      }
    }
  }
}

// App Service Plan for Functions
resource functionAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan-${environment}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
}

// Specialized Tools Function App
resource specializedToolsFunctionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: functionAppServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_COSMOSDB_ENDPOINT'
          value: cosmosDbAccount.properties.documentEndpoint
        }
        {
          name: 'AZURE_COSMOSDB_KEY'
          value: cosmosDbAccount.listKeys().primaryMasterKey
        }
        {
          name: 'AZURE_COSMOSDB_DATABASE_NAME'
          value: databaseName
        }
        {
          name: 'AZURE_COSMOSDB_KNOWLEDGE_CONTAINER'
          value: knowledgeContainerName
        }
        {
          name: 'AZURE_COSMOSDB_APPOINTMENTS_CONTAINER'
          value: appointmentsContainerName
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAiEndpoint
        }
        {
          name: 'AZURE_OPENAI_API_KEY'
          value: openAiApiKey
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
          value: openAiDeploymentName
        }
        {
          name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
          value: openAiEmbeddingDeploymentName
        }
        {
          name: 'AZURE_OPENAI_API_VERSION'
          value: '2024-02-15-preview'
        }
      ]
      pythonVersion: '3.11'
    }
    httpsOnly: true
  }
}

// Orchestrator Function App
resource orchestratorFunctionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: orchestratorFunctionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: functionAppServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAiEndpoint
        }
        {
          name: 'AZURE_OPENAI_API_KEY'
          value: openAiApiKey
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
          value: openAiDeploymentName
        }
        {
          name: 'AZURE_OPENAI_API_VERSION'
          value: '2024-02-15-preview'
        }
        {
          name: 'SPECIALIZED_TOOLS_BASE_URL'
          value: 'https://${specializedToolsFunctionApp.properties.defaultHostName}/api'
        }
      ]
      pythonVersion: '3.11'
    }
    httpsOnly: true
  }
}

// App Service Plan for Web App
resource webAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-web-plan-${environment}'
  location: location
  sku: {
    name: 'F1'
    tier: 'Free'
  }
}

// Web App for Frontend
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: webAppServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'ORCHESTRATOR_URL'
          value: 'https://${orchestratorFunctionApp.properties.defaultHostName}/api/orchestrate'
        }
      ]
    }
    httpsOnly: true
  }
}

// Outputs
output orchestratorUrl string = 'https://${orchestratorFunctionApp.properties.defaultHostName}/api/orchestrate'
output specializedToolsUrl string = 'https://${specializedToolsFunctionApp.properties.defaultHostName}/api'
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint

