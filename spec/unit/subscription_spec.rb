# frozen_string_literal: true

require 'spec_helper'

describe 'topic subscription' do
  let(:region) do
    var(role: :root, name: 'region')
  end
  let(:deployment_identifier) do
    var(role: :root, name: 'deployment_identifier')
  end
  let(:infrastructure_events_topic_arn) do
    output(role: :prerequisites, name: 'infrastructure_events_topic_arn')
  end

  describe 'by default' do
    before(:context) do
      @plan = plan(role: :root)
    end

    it 'creates an SNS topic subscription' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_sns_topic_subscription')
              .once)
    end

    it 'uses the provided topic ARN' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_sns_topic_subscription')
              .with_attribute_value(
                :topic_arn, infrastructure_events_topic_arn
              ))
    end

    it 'uses a protocol of "lambda"' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_sns_topic_subscription')
              .with_attribute_value(
                :protocol, 'lambda'
              ))
    end

    it 'creates a lambda permission' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_permission')
              .once)
    end

    it 'allows the function to be invoked' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_permission')
              .with_attribute_value(:action, 'lambda:InvokeFunction'))
    end

    it 'allows a principal of "sns.amazonaws.com"' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_permission')
              .with_attribute_value(:principal, 'sns.amazonaws.com'))
    end

    it 'allows the provided topic to invoke' do
      expect(@plan)
        .to(include_resource_creation(type: 'aws_lambda_permission')
              .with_attribute_value(
                :source_arn, infrastructure_events_topic_arn
              ))
    end
  end
end
