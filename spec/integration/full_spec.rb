# frozen_string_literal: true

require 'spec_helper'

describe 'full' do
  let(:region) do
    var(role: :full, name: 'region')
  end
  let(:deployment_identifier) do
    var(role: :full, name: 'deployment_identifier')
  end
  let(:search_regions) do
    var(role: :full, name: 'search_regions')
  end
  let(:search_accounts) do
    var(role: :full, name: 'search_accounts')
  end
  let(:peering_role_name) do
    var(role: :full, name: 'peering_role_name')
  end

  let(:lambda_role_arn) do
    output(role: :full, name: 'lambda_role_arn')
  end

  before(:context) do
    apply(role: :full)
  end

  after(:context) do
    destroy(
      role: :full,
      only_if: -> { !ENV['FORCE_DESTROY'].nil? || ENV['SEED'].nil? }
    )
  end

  describe 'vpc auto peering lambda' do
    subject(:peering_lambda) do
      lambda("vpc-auto-peering-lambda-#{region}-#{deployment_identifier}")
    end

    its(:runtime) do
      is_expected.to(eq('python3.9'))
    end

    its(:handler) do
      is_expected.to(eq('vpc_auto_peering_lambda.peer_vpcs_for'))
    end

    its(:timeout) do
      is_expected.to(eq(300))
    end

    its(:role) do
      is_expected.to(eq(lambda_role_arn))
    end

    it {
      expect(peering_lambda)
        .to(have_env_var_value(
              'AWS_SEARCH_REGIONS', search_regions.join(',')
            ))
    }

    it {
      expect(peering_lambda)
        .to(have_env_var_value(
              'AWS_SEARCH_ACCOUNTS', search_accounts.join(',')
            ))
    }

    it {
      expect(peering_lambda)
        .to(have_env_var_value(
              'AWS_PEERING_ROLE_NAME', peering_role_name
            ))
    }
  end

  describe 'vpc auto peering lambda execution role' do
    subject(:execution_role) do
      iam_role(lambda_role_arn)
    end

    it { is_expected.to exist }

    it 'can be assumed by lambda' do
      actual = JSON.parse(
        CGI.unescape(execution_role.assume_role_policy_document),
        symbolize_names: true
      )
      expected = {
        Version: '2012-10-17',
        Statement: [
          {
            Sid: '',
            Effect: 'Allow',
            Action: 'sts:AssumeRole',
            Principal: {
              Service: 'lambda.amazonaws.com'
            }
          }
        ]
      }

      expect(actual).to(eq(expected))
    end

    it 'allows log creation' do
      expect(execution_role)
        .to(be_allowed_action('logs:CreateLogStream')
              .and(be_allowed_action('logs:CreateLogGroup'))
              .and(be_allowed_action('logs:PutLogEvents')))
    end

    it 'allows assumable roles to be assumed' do
      search_accounts.each do |search_account|
        expect(execution_role)
          .to(be_allowed_action('sts:AssumeRole')
                .resource_arn(
                  "arn:aws:iam::#{search_account}:role/#{peering_role_name}"
                ))
      end
    end

    it 'does not allow other roles to be assumed' do
      expect(execution_role)
        .not_to(be_allowed_action('sts:AssumeRole')
                  .resource_arn('arn:aws:iam::176145454894:role/other-role'))
    end

    it 'allows the caller identity to be fetched' do
      expect(execution_role)
        .to(be_allowed_action('sts:GetCallerIdentity'))
    end
  end
end
