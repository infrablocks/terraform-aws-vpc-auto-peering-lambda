## 0.1.13 (January 17th, 2017)

BACKWARDS INCOMPATIBILITIES / NOTES:

* Dependencies are now expected to be in the format 
  '<component>-<deployment_identifier>,...' to allow multiple deployments of
  the same component within a region with specific peering relationships. All
  existing dependency relationships will need to be updated to include the
  deployment identifier.  
