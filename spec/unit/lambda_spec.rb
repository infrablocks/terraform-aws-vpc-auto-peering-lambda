# frozen_string_literal: true

require 'spec_helper'

describe 'lambda' do
  let(:region) do
    var(role: :root, name: 'region')
  end
  let(:deployment_identifier) do
    var(role: :root, name: 'deployment_identifier')
  end

  describe 'by default' do
    before(:context) do
      @plan = plan(role: :root)
    end

    it 'creates a lambda function' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .once)
    end

    it 'includes the region and deployment identifier in the lambda ' \
       'function name' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                :function_name,
                including(region).and(including(deployment_identifier))
              ))
    end

    it 'uses a handler of "vpc_auto_peering_lambda.peer_vpcs_for"' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                :handler,
                'vpc_auto_peering_lambda.peer_vpcs_for'
              ))
    end

    it 'uses a runtime of "python3.9"' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(:runtime, 'python3.9'))
    end

    it 'uses a timeout of 300 seconds' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(:timeout, 300))
    end

    it 'has one reserved concurrent execution' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(:reserved_concurrent_executions, 1))
    end

    it 'includes an AWS_SEARCH_REGIONS environment variable with an ' \
       'empty string as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_REGIONS: '')
              ))
    end

    it 'includes an AWS_SEARCH_ACCOUNTS environment variable with an ' \
       'empty string as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_ACCOUNTS: '')
              ))
    end

    it 'includes an AWS_PEERING_ROLE_NAME environment variable with an ' \
       'empty string as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_PEERING_ROLE_NAME: '')
              ))
    end
  end

  describe 'when no search regions provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_regions = []
      end
    end

    it 'includes an AWS_SEARCH_REGIONS environment variable with an ' \
       'empty string as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_REGIONS: '')
              ))
    end
  end

  describe 'when one search region provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_regions = %w[
          eu-west-1
        ]
      end
    end

    it 'includes an AWS_SEARCH_REGIONS environment variable with a ' \
       'string containing the search region as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_REGIONS: 'eu-west-1')
              ))
    end
  end

  describe 'when two search regions provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_regions = %w[
          eu-west-1
          eu-west-2
        ]
      end
    end

    it 'includes an AWS_SEARCH_REGIONS environment variable with a ' \
       'string containing comma separated search regions as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_REGIONS: 'eu-west-1,eu-west-2')
              ))
    end
  end

  describe 'when no search accounts provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = []
      end
    end

    it 'includes an AWS_SEARCH_ACCOUNTS environment variable with an ' \
       'empty string as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_ACCOUNTS: '')
              ))
    end
  end

  describe 'when one search account provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = %w[
          123456789012
        ]
      end
    end

    it 'includes an AWS_SEARCH_ACCOUNTS environment variable with a ' \
       'string containing the search account as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(AWS_SEARCH_ACCOUNTS: '123456789012')
              ))
    end
  end

  describe 'when two search accounts provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = %w[
          123456789012
          234567890123
        ]
      end
    end

    it 'includes an AWS_SEARCH_ACCOUNTS environment variable with a ' \
       'string containing comma separated search accounts as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(
                  AWS_SEARCH_ACCOUNTS: '123456789012,234567890123'
                )
              ))
    end
  end

  describe 'when peering role name provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.peering_role_name = 'peering-role'
      end
    end

    it 'includes an AWS_SEARCH_ACCOUNTS environment variable with a ' \
       'string containing comma separated search accounts as value' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_function')
              .with_attribute_value(
                [:environment, 0, :variables],
                a_hash_including(
                  AWS_PEERING_ROLE_NAME: 'peering-role'
                )
              ))
    end
  end
end
