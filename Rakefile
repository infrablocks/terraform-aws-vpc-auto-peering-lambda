require 'rspec/core/rake_task'
require 'securerandom'
require 'git'
require 'semantic'

require_relative 'lib/public_ip'
require_relative 'lib/terraform'

DEPLOYMENT_IDENTIFIER = SecureRandom.hex[0, 8]

Terraform::Tasks.install('0.8.6')

task :default => 'test:integration'

namespace :test do
  RSpec::Core::RakeTask.new(:integration => ['terraform:ensure']) do
    ENV['AWS_REGION'] = 'eu-west-2'
  end
end

namespace :provision do
  desc 'Provisions module in AWS'
  task :aws, [:deployment_identifier] => ['terraform:ensure'] do |_, args|
    deployment_identifier = args.deployment_identifier || DEPLOYMENT_IDENTIFIER
    configuration_directory = Paths.from_project_root_directory('src')

    puts "Provisioning with deployment identifier: #{deployment_identifier}"

    Terraform.clean
    Terraform.apply(
        directory: configuration_directory,
        vars: terraform_vars_for(
            deployment_identifier: deployment_identifier))
  end
end

namespace :destroy do
  desc 'Destroys module in AWS'
  task :aws, [:deployment_identifier] => ['terraform:ensure'] do |_, args|
    deployment_identifier = args.deployment_identifier || DEPLOYMENT_IDENTIFIER
    configuration_directory = Paths.from_project_root_directory('src')

    puts "Destroying with deployment identifier: #{deployment_identifier}"

    Terraform.clean
    Terraform.destroy(
        directory: configuration_directory,
        force: true,
        vars: terraform_vars_for(
            deployment_identifier: deployment_identifier))
  end
end

namespace :release do
  desc 'Increment and push tag'
  task :tag do
    repo = Git.open('.')
    tags = repo.tags
    latest_tag = tags.map { |tag| Semantic::Version.new(tag.name) }.max
    next_tag = latest_tag.increment!(:patch)
    repo.add_tag(next_tag.to_s)
    repo.push('origin', 'master', tags: true)
  end
end

def terraform_vars_for(opts)
  {
      region: 'eu-west-2',
      deployment_identifier: opts[:deployment_identifier]
  }
end
