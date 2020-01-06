require 'rspec/core/rake_task'
require 'securerandom'
require 'git'
require 'semantic'
require 'rake_terraform'

require_relative 'lib/configuration'
require_relative 'lib/version'

configuration = Configuration.new

def repo
  Git.open('.')
end

def latest_tag
  repo.tags.map do |tag|
    Semantic::Version.new(tag.name)
  end.max
end

RakeTerraform.define_installation_tasks(
    path: File.join(Dir.pwd, 'vendor', 'terraform'),
    version: '0.12.16')

task :default => 'test:all'

namespace :virtualenv do
  task :create do
    mkdir_p 'vendor'
    sh 'python -m venv vendor/virtualenv'
  end

  task :upgrade do
    sh_with_virtualenv 'pip install --upgrade pip'
  end

  task :destroy do
    rm_rf 'vendor/virtualenv'
  end

  task :ensure do
    unless File.exists?('vendor/virtualenv')
      Rake::Task['virtualenv:create'].invoke
    end
    Rake::Task['virtualenv:upgrade'].invoke
  end
end

namespace :dependencies do
  namespace :install do
    desc "Install dependencies for auto peering lambda."
    task :auto_peering_lambda => ['virtualenv:ensure'] do
      puts 'Running unit tests for auto_peering lambda'
      puts

      sh_with_virtualenv(
          'pip install -r lambdas/auto_peering/requirements.txt')
    end

    desc "Install dependencies for all lambdas."
    task :all => ['dependencies:install:auto_peering_lambda']
  end
end

namespace :test do
  namespace :unit do
    desc "Run unit tests of auto peering lambda."
    task :auto_peering_lambda => ['dependencies:install:all'] do
      puts 'Running integration tests'
      puts

      sh_with_virtualenv(
          'python -m unittest discover -s ./lambdas/auto_peering')
    end

    desc "Run unit tests of all lambdas."
    task :all => ['test:unit:auto_peering_lambda']
  end

  namespace :integration do
    RSpec::Core::RakeTask.new(:all => ['terraform:ensure']) do
      ENV['AWS_REGION'] = 'eu-west-2'
      ENV['TF_PLUGIN_CACHE_DIR'] =
          "#{Paths.project_root_directory}/vendor/terraform/plugins"
    end
  end

  task :all => %w(test:unit:all test:integration:all)
end

namespace :deployment do
  namespace :prerequisites do
    RakeTerraform.define_command_tasks do |t|
      t.argument_names = [:deployment_identifier]

      t.configuration_name = 'prerequisites'
      t.source_directory =
          configuration.for(:prerequisites).source_directory
      t.work_directory =
          configuration.for(:prerequisites).work_directory

      t.state_file =
          configuration.for(:prerequisites).state_file

      t.vars = lambda do |args|
        configuration.for(:prerequisites, args)
            .vars
            .to_h
      end
    end
  end

  namespace :harness do
    RakeTerraform.define_command_tasks do |t|
      t.argument_names = [:deployment_identifier]

      t.configuration_name = 'VPC auto peering module'
      t.source_directory = configuration.for(:harness).source_directory
      t.work_directory = configuration.for(:harness).work_directory

      t.state_file = configuration.for(:harness).state_file

      t.vars = lambda do |args|
        configuration.for(:harness, args)
            .vars
            .to_h
      end
    end
  end
end

namespace :version do
  task :bump, [:type] do |_, args|
    next_tag = latest_tag.send("#{args.type}!")
    repo.add_tag(next_tag.to_s)
    repo.push('origin', 'master', tags: true)
    puts "Bumped version to #{next_tag}."
  end

  task :release do
    next_tag = latest_tag.release!
    repo.add_tag(next_tag.to_s)
    repo.push('origin', 'master', tags: true)
    puts "Released version #{next_tag}."
  end
end

def sh_with_virtualenv command
  virtualenv_path = File.expand_path('vendor/virtualenv/bin')
  existing_path = ENV['PATH']
  path = "#{virtualenv_path}:#{existing_path}"

  system({'PATH' => path}, command) or fail
end