# frozen_string_literal: true

require 'confidante'
require 'git'
require 'rake_circle_ci'
require 'rake_github'
require 'rake_gpg'
require 'rake_ssh'
require 'rake_terraform'
require 'rspec/core/rake_task'
require 'rubocop/rake_task'
require 'securerandom'
require 'semantic'
require 'yaml'

require_relative 'lib/paths'
require_relative 'lib/version'

configuration = Confidante.configuration

def repo
  Git.open(Pathname.new('.'))
end

def latest_tag
  repo.tags.map do |tag|
    Semantic::Version.new(tag.name)
  end.max
end

task default: %i[
  test:code:fix
  test:unit
  test:integration
]

RakeTerraform.define_installation_tasks(
  path: File.join(Dir.pwd, 'vendor', 'terraform'),
  version: '1.3.1'
)

namespace :encryption do
  namespace :directory do
    desc 'Ensure CI secrets directory exists'
    task :ensure do
      FileUtils.mkdir_p('config/secrets/ci')
    end
  end

  namespace :passphrase do
    desc 'Generate encryption passphrase for CI GPG key'
    task generate: ['directory:ensure'] do
      File.write(
        'config/secrets/ci/encryption.passphrase',
        SecureRandom.base64(36)
      )
    end
  end
end

namespace :keys do
  namespace :deploy do
    RakeSSH.define_key_tasks(
      path: 'config/secrets/ci/',
      comment: 'maintainers@infrablocks.io'
    )
  end

  namespace :secrets do
    namespace :gpg do
      RakeGPG.define_generate_key_task(
        output_directory: 'config/secrets/ci',
        name_prefix: 'gpg',
        owner_name: 'InfraBlocks Maintainers',
        owner_email: 'maintainers@infrablocks.io',
        owner_comment: 'terraform-aws-vpc-auto-peering-lambda CI Key'
      )
    end

    task generate: ['gpg:generate']
  end
end

namespace :secrets do
  namespace :directory do
    desc 'Ensure secrets directory exists and is set up correctly'
    task :ensure do
      FileUtils.mkdir_p('config/secrets')
      unless File.exist?('config/secrets/.unlocked')
        File.write('config/secrets/.unlocked', 'true')
      end
    end
  end

  desc 'Regenerate all secrets'
  task regenerate: %w[
    directory:ensure
    encryption:passphrase:generate
    keys:deploy:generate
    keys:secrets:generate
  ]
end

RakeCircleCI.define_project_tasks(
  namespace: :circle_ci,
  project_slug: 'github/infrablocks/terraform-aws-vpc-auto-peering-lambda'
) do |t|
  circle_ci_config =
    YAML.load_file('config/secrets/circle_ci/config.yaml')

  t.api_token = circle_ci_config['circle_ci_api_token']
  t.environment_variables = {
    ENCRYPTION_PASSPHRASE:
      File.read('config/secrets/ci/encryption.passphrase')
          .chomp,
    CIRCLECI_API_KEY:
      YAML.load_file(
        'config/secrets/circle_ci/config.yaml'
      )['circle_ci_api_token']
  }
  t.checkout_keys = []
  t.ssh_keys = [
    {
      hostname: 'github.com',
      private_key: File.read('config/secrets/ci/ssh.private')
    }
  ]
end

RakeGithub.define_repository_tasks(
  namespace: :github,
  repository: 'infrablocks/terraform-aws-vpc-auto-peering-lambda'
) do |t, args|
  github_config =
    YAML.load_file('config/secrets/github/config.yaml')

  t.access_token = github_config['github_personal_access_token']
  t.deploy_keys = [
    {
      title: 'CircleCI',
      public_key: File.read('config/secrets/ci/ssh.public')
    }
  ]
  t.branch_name = args.branch_name
  t.commit_message = args.commit_message
end

namespace :pipeline do
  desc 'Prepare CircleCI Pipeline'
  task prepare: %i[
    circle_ci:env_vars:ensure
    circle_ci:checkout_keys:ensure
    circle_ci:ssh_keys:ensure
    github:deploy_keys:ensure
  ]
end

namespace :virtualenv do
  desc 'Create a virtualenv for the lambda'
  task :create do
    mkdir_p 'vendor'
    sh 'python -m venv vendor/virtualenv'
  end

  desc 'Upgrade dependencies within the virtualenv for the lambda'
  task :upgrade do
    sh_with_virtualenv 'pip install --upgrade pip'
  end

  desc 'Destroy the virtualenv for the lambda'
  task :destroy do
    rm_rf 'vendor/virtualenv'
  end

  desc 'Ensure a virtualenv exists for the lambda with dependencies available'
  task :ensure do
    unless File.exist?('vendor/virtualenv')
      Rake::Task['virtualenv:create'].invoke
    end
    Rake::Task['virtualenv:upgrade'].invoke
  end
end

namespace :dependencies do
  namespace :install do
    desc 'Install dependencies for auto peering lambda.'
    task auto_peering_lambda: ['virtualenv:ensure'] do
      puts 'Running unit tests for auto_peering lambda'
      puts

      sh_with_virtualenv(
        'pip install -r lambdas/auto_peering/requirements.txt'
      )
    end

    desc 'Install dependencies for all lambdas.'
    task all: ['dependencies:install:auto_peering_lambda']
  end
end

RuboCop::RakeTask.new

namespace :test do
  namespace :code do
    desc 'Run all checks on the test code'
    task check: [:rubocop]

    desc 'Attempt to automatically fix issues with the test code'
    task fix: [:'rubocop:autocorrect_all']
  end

  namespace :unit do
    desc 'Run unit tests of auto peering lambda.'
    task auto_peering_lambda: ['dependencies:install:all'] do
      puts 'Running integration tests'
      puts

      sh_with_virtualenv(
        'python -m unittest discover -s ./lambdas/auto_peering'
      )
    end

    desc 'Run unit test of Terraform configuration'
    RSpec::Core::RakeTask.new(
      terraform_configuration: ['terraform:ensure']
    ) do |t|
      t.pattern = 'spec/unit/**{,/*/**}/*_spec.rb'
      t.rspec_opts = '-I spec/unit'

      ENV['AWS_REGION'] = configuration.region
    end

    desc 'Run unit tests of all lambdas.'
    task all: %w[
      test:unit:auto_peering_lambda
      test:unit:terraform_configuration
    ]
  end

  namespace :integration do
    desc 'Run module integration tests'
    RSpec::Core::RakeTask.new(all: ['terraform:ensure']) do |t|
      t.pattern = 'spec/integration/**{,/*/**}/*_spec.rb'
      t.rspec_opts = '-I spec/integration'

      ENV['AWS_REGION'] = configuration.region
    end
  end

  task all: %w[test:unit:all test:integration:all]
end

namespace :deployment do
  namespace :prerequisites do
    RakeTerraform.define_command_tasks(
      configuration_name: 'prerequisites',
      argument_names: [:seed]
    ) do |t, args|
      deployment_configuration =
        configuration
        .for_scope(role: :prerequisites)
        .for_overrides(args.to_h)

      t.source_directory = 'spec/unit/infra/prerequisites'
      t.work_directory = 'build/infra'

      t.state_file = deployment_configuration.state_file
      t.vars = deployment_configuration.vars
    end
  end

  namespace :root do
    RakeTerraform.define_command_tasks(
      configuration_name: 'root',
      argument_names: [:seed]
    ) do |t, args|
      deployment_configuration =
        configuration
        .for_scope(role: :root)
        .for_overrides(args.to_h)

      t.source_directory = 'spec/unit/infra/root'
      t.work_directory = 'build/infra'

      t.state_file = deployment_configuration.state_file
      t.vars = deployment_configuration.vars
    end
  end
end

namespace :version do
  desc 'Bump version for specified type (pre, major, minor, patch)'
  task :bump, [:type] do |_, args|
    next_tag = latest_tag.send("#{args.type}!")
    repo.add_tag(next_tag.to_s)
    repo.push('origin', 'main', tags: true)
    puts "Bumped version to #{next_tag}."
  end

  desc 'Release module'
  task :release do
    next_tag = latest_tag.release!
    repo.add_tag(next_tag.to_s)
    repo.push('origin', 'main', tags: true)
    puts "Released version #{next_tag}."
  end
end

def sh_with_virtualenv(command)
  virtualenv_path = File.expand_path('vendor/virtualenv/bin')
  existing_path = ENV.fetch('PATH', nil)
  path = "#{virtualenv_path}:#{existing_path}"

  system({ 'PATH' => path }, command) or raise
end
