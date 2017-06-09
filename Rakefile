require 'rspec/core/rake_task'
require 'rake_terraform'
require 'securerandom'
require 'git'
require 'semantic'
require 'lino'

require_relative 'lib/public_ip'

DEPLOYMENT_IDENTIFIER = SecureRandom.hex[0, 8]

RakeTerraform.define_installation_tasks(version: '0.9.8')

task :default => 'test:integration'

namespace :test do
  task :unit do
    Dir.chdir('src/lambda-definitions/auto_peering') do
      Lino::CommandLineBuilder.for_command('python')
          .with_environment_variable('PYTHONPATH', '.')
          .with_option('-m', 'unittest')
          .with_argument('discover')
          .build
          .execute
    end
  end

  RSpec::Core::RakeTask.new(:integration => ['terraform:ensure']) do
    ENV['AWS_REGION'] = 'eu-west-2'
  end
end

RakeTerraform.define_command_tasks do |t|
  t.argument_names = [:deployment_identifier]

  t.configuration_name = 'VPC auto peering module'
  t.configuration_directory = 'spec/infra'

  t.vars = lambda do |args|
    terraform_vars_for(
        deployment_identifier: args.deployment_identifier ||
            DEPLOYMENT_IDENTIFIER)
  end
end

namespace :release do
  desc 'Increment and push tag'
  task :tag do
    repo = Git.open('.')
    tags = repo.tags
    latest_tag = tags.map {|tag| Semantic::Version.new(tag.name)}.max
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
