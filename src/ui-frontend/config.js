/**
 * Configuration file for the Healthcare Assistant Frontend
 * This file can be updated during deployment to point to the correct endpoints
 */

// Get configuration from environment or use defaults
const getConfig = () => {
  // In Azure Web App, these can be set as environment variables
  // For static hosting, update these values directly or use a build process
  
  // Try to get from window object (set by server-side rendering or build process)
  if (window.APP_CONFIG) {
    return window.APP_CONFIG;
  }
  
  // Default configuration (update these for your deployment)
  return {
    // Orchestrator API endpoint
    // Format: https://[FunctionAppName].azurewebsites.net/api/orchestrate
    ORCHESTRATOR_URL: window.location.hostname.includes('localhost') 
      ? 'http://localhost:7071/api/orchestrate'
      : 'https://healthbotorchestrator.azurewebsites.net/api/orchestrate',
    
    // Optional: Function key for authentication
    // Get this from Azure Portal > Function App > Functions > orchestrate > Function Keys
    FUNCTION_KEY: '',
    
    // API timeout in milliseconds
    TIMEOUT: 30000
  };
};

// Export configuration
window.CONFIG = getConfig();

