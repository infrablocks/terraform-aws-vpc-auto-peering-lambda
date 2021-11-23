Terraform AWS VPC Auto Peering
==============================

[![CircleCI](https://circleci.com/gh/infrablocks/terraform-aws-vpc-auto-peering-lambda.svg?style=svg)](https://circleci.com/gh/infrablocks/terraform-aws-vpc-auto-peering-lambda)

A Terraform module for automatically peering VPCs based on dependency 
information stored in tags.

Usage
-----

To use the module, include something like the following in your terraform 
configuration:

```hcl-terraform
module "vpc-auto-peering" {
  source = "infrablocks/vpc-auto-peering/aws"
  version = "0.1.12"
  
  region = "eu-west-2"
  deployment_identifier = "1bc5defe"

  infrastructure_events_topic_arn = "arn:aws:sns:eu-west-2:579878096224:infrastructure-events-topic-eu-west-2-335e1e54"
}
```

See the 
[Terraform registry entry](https://registry.terraform.io/modules/infrablocks/vpc-auto-peering-lambda/aws/latest) 
for more details.

### Inputs

| Name                            | Description                                                         | Default | Required |
|---------------------------------|---------------------------------------------------------------------|:-------:|:--------:|
| region                          | The region into which the VPC auto peering lambda is being deployed | -       | yes      |
| deployment_identifier           | An identifier for this instantiation                                | -       | yes      |
| infrastructure_events_topic_arn | The ARN of the SNS topic containing VPC events                      | -       | yes      |
| search_regions                  | AWS regions to search for dependency and dependent VPCs.            | -       | no       |


### Outputs

| Name                         | Description                                          |
|------------------------------|------------------------------------------------------|

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
https://github.com/infrablocks/terraform-aws-vpc-auto-peering-lambda. 
This project is intended to be a safe, welcoming space for collaboration, and 
contributors are expected to adhere to 
the [Contributor Covenant](http://contributor-covenant.org) code of conduct.


License
-------

The library is available as open source under the terms of the 
[MIT License](http://opensource.org/licenses/MIT).
