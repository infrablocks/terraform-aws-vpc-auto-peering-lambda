require 'spec_helper'

describe 'Lambdas' do
  let(:region) { vars.region }
  let(:deployment_identifier) { vars.deployment_identifier }
  let(:search_regions) { vars.search_regions }
  let(:search_accounts) { vars.search_accounts }
  let(:peering_role_name) { vars.peering_role_name }
  
  let(:lambda_role_arn) { output_for(:harness, 'lambda_role_arn') }

  context 'vpc auto peering lambda' do
    subject {
      lambda("vpc-auto-peering-lambda-#{region}-#{deployment_identifier}")
    }

    its(:runtime) { should eq('python3.6') }
    its(:handler) { should eq('vpc_auto_peering_lambda.peer_vpcs_for')}
    its(:timeout) { should eq(300)}
    its(:role) { should eq(lambda_role_arn) }

    it { should have_env_var_value(
        'AWS_SEARCH_REGIONS', search_regions.join(',')) }
    it { should have_env_var_value(
        'AWS_SEARCH_ACCOUNTS', search_accounts.join(',')) }
    it { should have_env_var_value(
        'AWS_PEERING_ROLE_NAME', peering_role_name) }
  end
end
