require 'bundler/setup'

require 'awspec'

require 'support/shared_contexts/terraform'

require 'securerandom'
require 'netaddr'
require 'open-uri'

require_relative '../lib/terraform'

RSpec.configure do |config|
  deployment_identifier = ENV['DEPLOYMENT_IDENTIFIER']

  def current_public_ip_cidr
    "#{open('http://whatismyip.akamai.com').read}/32"
  end

  config.example_status_persistence_file_path = '.rspec_status'

  config.add_setting :region, default: 'eu-west-2'
  config.add_setting :deployment_identifier,
      default: deployment_identifier || SecureRandom.hex[0, 8]

  config.before(:suite) do
    variables = RSpec.configuration
    configuration_directory =
        Paths.from_project_root_directory('spec', 'infra')

    puts
    puts "Provisioning with deployment identifier: #{variables.deployment_identifier}"
    puts

    Terraform.clean
    Terraform.get(directory: configuration_directory)
    Terraform.apply(
        directory: configuration_directory,
        vars: {
            region: variables.region,
            deployment_identifier: variables.deployment_identifier
        })

    puts
  end

  config.after(:suite) do
    unless deployment_identifier
      variables = RSpec.configuration
      configuration_directory =
          Paths.from_project_root_directory('spec', 'infra')

      puts
      puts "Destroying with deployment identifier: #{variables.deployment_identifier}"
      puts

      Terraform.clean
      Terraform.get(directory: configuration_directory)
      Terraform.destroy(
          directory: configuration_directory,
          force: true,
          vars: {
              region: variables.region,
              deployment_identifier: variables.deployment_identifier
          })

      puts
    end
  end
end