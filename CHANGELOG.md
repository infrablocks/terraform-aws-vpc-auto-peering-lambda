## 2.0.0 (May 28th, 2021)

BACKWARDS INCOMPATIBILITIES / NOTES:

* This module is now compatible with Terraform 0.14 and higher.

## 0.1.20 (January 17th, 2018)

BUGFIXES:

* Accept peering connection from acceptor end.

## 0.1.19 (January 17th, 2018)

BUGFIXES:

* Accept peering connection from acceptor end.

## 0.1.18 (January 17th, 2018)

BUGFIXES:

* Correctly request peering connection in multi region case.

## 0.1.17 (January 17th, 2018)

IMPROVEMENTS:

* Log errors in lambda.

## 0.1.16 (January 17th, 2018)

BUGFIXES:

* Correctly enhance VPC with region.

## 0.1.15 (January 17th, 2018)

BUGFIXES:

* Fix construction of EC2 resource by region map.

## 0.1.14 (January 17th, 2018)

IMPROVEMENTS:

* Add `search_regions` optional var to allow VPC search regions to be specified.

## 0.1.13 (January 17th, 2018)

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
