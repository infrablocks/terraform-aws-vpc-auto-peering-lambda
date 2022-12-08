# frozen_string_literal: true

require 'spec_helper'

describe 'IAM' do
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

    it 'creates an IAM role' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_role')
              .once)
    end

    it 'includes the region and deployment identifier in the IAM role name' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_role')
              .with_attribute_value(
                :name, including(region).and(including(deployment_identifier))
              ))
    end

    it 'allows the lambda service to assume the IAM role' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_role')
              .with_attribute_value(
                :assume_role_policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Action: 'sts:AssumeRole',
                  Principal: {
                    Service: 'lambda.amazonaws.com'
                  }
                )
              ))
    end

    it 'creates an IAM policy' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .once)
    end

    it 'includes the region and deployment identifier in the IAM policy name' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :name, including(region).and(including(deployment_identifier))
              ))
    end

    it 'allows the execution role to manage logs and get tokens' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Resource: '*',
                  Action: %w[
                    sts:GetCallerIdentity
                    logs:CreateLogGroup
                    logs:CreateLogStream
                    logs:PutLogEvents
                  ]
                )
              ))
    end

    it 'does not allow the execution role to assume roles in any ' \
       'search accounts' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Action: 'sts:AssumeRole'
                )
              ))
    end

    it 'creates an IAM policy attachment' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy_attachment')
              .once)
    end

    it 'includes the region and deployment identifier in the IAM policy ' \
       'attachment name' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy_attachment')
              .with_attribute_value(
                :name, including(region).and(including(deployment_identifier))
              ))
    end
  end

  describe 'when no search accounts provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = []
        vars.peering_role_name = 'peering-role'
      end
    end

    it 'does not allow the execution role to assume roles in any ' \
       'search accounts' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Action: 'sts:AssumeRole'
                )
              ))
    end
  end

  describe 'when one search account provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = ['123456789012']
        vars.peering_role_name = 'peering-role'
      end
    end

    it 'allows the execution role to assume a role with the provided ' \
       'peering role name in the provided search account' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Resource: 'arn:aws:iam::123456789012:role/peering-role',
                  Action: 'sts:AssumeRole'
                )
              ))
    end
  end

  describe 'when many search accounts provided' do
    before(:context) do
      @plan = plan(role: :root) do |vars|
        vars.search_accounts = %w[
          123456789012
          234567890123
        ]
        vars.peering_role_name = 'peering-role'
      end
    end

    it 'allows the execution role to assume a role with the provided ' \
       'peering role name in the provided search account' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_iam_policy')
              .with_attribute_value(
                :policy,
                a_policy_with_statement(
                  Effect: 'Allow',
                  Resource: %w[
                    arn:aws:iam::123456789012:role/peering-role
                    arn:aws:iam::234567890123:role/peering-role
                  ],
                  Action: 'sts:AssumeRole'
                )
              ))
    end
  end
end
