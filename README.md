Terraform AWS VPC Auto Peering Lambda
=====================================

[![CircleCI](https://circleci.com/gh/infrablocks/terraform-aws-vpc-auto-peering-lambda.svg?style=svg)](https://circleci.com/gh/infrablocks/terraform-aws-vpc-auto-peering-lambda)

A Terraform module for automatically peering VPCs based on dependency
information stored in tags.

The VPC auto peering lambda requires:

* An SNS topic which receives events whenever a VPC is created or destroyed
* A role to assume in order to create or destroy the peering connection and 
  routes

The VPC auto peering lambda consists of:

* A lambda function which responds to VPC lifecycle events on the SNS topic
* A subscription to the SNS topic
* IAM roles and policies allowing the lambda to function

Architecture
------------

The VPC auto-peering lambda automatically creates peering connections and
routes between VPCs based on relationships declared by each VPC via tags. In 
order to achieve this, the lambda needs to know when VPCs are provisioned and 
destroyed. 

Since AWS doesn't provide any built in events for VPC lifecycle, the
lambda relies on an alternative approach for such events, as provided by the
[`terraform-aws-vpc-lifecycle-event`](https://github.com/infrablocks/terraform-aws-vpc-lifecycle-event)
and
[`terraform-aws-infrastructure-events`](https://github.com/infrablocks/terraform-aws-infrastructure-events)
modules.

The `terraform-aws-infrastructure-events` module uses S3 objects to represent
provisions and destroys of pieces of infrastructure, converting the 
corresponding object creations and deletions into messages in an SNS topic. In
this way, Terraform configurations can signal changes to infrastructure by 
creating or deleting an S3 object whose key includes information about that 
infrastructure.

The `terraform-aws-vpc-lifecycle-event` module uses this mechanism to notify of
a VPC lifecycle change, such as when a VPC is provisioned or destroyed.

The diagram below shows how these modules work together:

![Diagram of architecture used by this module](https://raw.githubusercontent.com/infrablocks/terraform-aws-vpc-auto-peering-lambda/master/docs/architecture.png)

Note that for this to work, the `terraform-aws-infrastructure-events` and
`terraform-aws-vpc-auto-peering-lambda` modules should be created in one 
Terraform configuration while the `terraform-aws-vpc-lifecycle-event` module
should be used in the configuration that manages the VPC.

Usage
-----

To use the module, include something like the following in your terraform
configuration:

```hcl-terraform
module "vpc-auto-peering" {
  source  = "infrablocks/vpc-auto-peering/aws"
  version = "0.1.12"

  region                = "eu-west-2"
  deployment_identifier = "1bc5defe"

  infrastructure_events_topic_arn = "arn:aws:sns:eu-west-2:579878096224:infrastructure-events-topic-eu-west-2-335e1e54"
}
```

See the
[Terraform registry entry](https://registry.terraform.io/modules/infrablocks/vpc-auto-peering-lambda/aws/latest)
for more details.

### Inputs

| Name                            | Description                                                                | Default | Required |
|---------------------------------|----------------------------------------------------------------------------|:-------:|:--------:|
| region                          | The region into which the VPC auto peering lambda is being deployed.       | -       | Yes      |
| deployment_identifier           | An identifier for this instantiation.                                      | -       | Yes      |
| infrastructure_events_topic_arn | The ARN of the SNS topic containing VPC events.                            | -       | Yes      |
| search_regions                  | AWS regions to search for dependency and dependent VPCs.                   | `[]`    | No       |
| search_accounts                 | IDs of AWS accounts to search for dependency and dependent VPCs.           | `[]`    | No       |
| peering_role_name               | The name of the role to assume to create peering relationships and routes. | `""`    | No       |

### Outputs

| Name                         | Description                                          |
|------------------------------|------------------------------------------------------|
| lambda_role_arn              | The ARN of the created lambda.                       |

### Compatibility

This module is compatible with Terraform versions greater than or equal to
Terraform 0.14.

Development
-----------

### Machine Requirements

In order for the build to run correctly, a few tools will need to be installed
on your development machine:

* Ruby (2.3.1)
* Bundler
* git
* git-crypt
* gnupg
* direnv

#### Mac OS X Setup

Installing the required tools is best managed by [homebrew](http://brew.sh).

To install homebrew:

```
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Then, to install the required tools:

```
# ruby
brew install rbenv
brew install ruby-build
echo 'eval "$(rbenv init - bash)"' >> ~/.bash_profile
echo 'eval "$(rbenv init - zsh)"' >> ~/.zshrc
eval "$(rbenv init -)"
rbenv install 2.3.1
rbenv rehash
rbenv local 2.3.1
gem install bundler

# git, git-crypt, gnupg
brew install git
brew install git-crypt
brew install gnupg

# direnv
brew install direnv
echo "$(direnv hook bash)" >> ~/.bash_profile
echo "$(direnv hook zsh)" >> ~/.zshrc
eval "$(direnv hook $SHELL)"

direnv allow <repository-directory>
```

### Running the build

To provision module infrastructure, run tests and then destroy that
infrastructure, execute:

```bash
./go
```

To provision the module prerequisites:

```bash
./go deployment:prerequisites:provision[<deployment_identifier>]
```

To provision the module contents:

```bash
./go deployment:harness:provision[<deployment_identifier>]
```

To destroy the module contents:

```bash
./go deployment:harness:destroy[<deployment_identifier>]
```

To destroy the module prerequisites:

```bash
./go deployment:prerequisites:destroy[<deployment_identifier>]
```

### Common Tasks

#### Generate an SSH key pair

To generate an SSH key pair:

```
ssh-keygen -t rsa -b 4096 -C integration-test@example.com -N '' -f config/secrets/keys/bastion/ssh
```

#### Generate a self signed certificate

To generate a self signed certificate:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

To decrypt the resulting key:

```
openssl rsa -in key.pem -out ssl.key
```

#### Add a git-crypt user

To adding a user to git-crypt using their GPG key:

```
gpg --import ~/path/xxxx.pub
git-crypt add-gpg-user --trusted GPG-USER-ID

```

#### Managing CircleCI keys

To encrypt a GPG key for use by CircleCI:

```bash
openssl aes-256-cbc \
  -e \
  -md sha1 \
  -in ./config/secrets/ci/gpg.private \
  -out ./.circleci/gpg.private.enc \
  -k "<passphrase>"
```

To check decryption is working correctly:

```bash
openssl aes-256-cbc \
  -d \
  -md sha1 \
  -in ./.circleci/gpg.private.enc \
  -k "<passphrase>"
```

Contributing
------------

Bug reports and pull requests are welcome on GitHub at
https://github.com/infrablocks/terraform-aws-vpc-auto-peering-lambda. This
project is intended to be a safe, welcoming space for collaboration, and
contributors are expected to adhere to
the [Contributor Covenant](http://contributor-covenant.org) code of conduct.


License
-------

The library is available as open source under the terms of the
[MIT License](http://opensource.org/licenses/MIT).
