## 0.1.13 (January 17th, 2017)

BACKWARDS INCOMPATIBILITIES / NOTES:

* Dependencies are now expected to be in the format 
  '<component>-<deployment_identifier>,...' to allow multiple deployments of
  the same component within a region with specific peering relationships. All
  existing dependency relationships will need to be updated to include the
  deployment identifier.
  
IMPROVEMENTS:

* The lambda can be configured with an AWS_SEARCH_REGIONS environment variable
  that allows for cross-region peering. Only the regions listed, as a comma
  separated string, will be searched during auto peering.
* The lambda now has a reserved concurrent execution of 1 to prevent parallel
  invocations.
