require 'spec_helper'

describe 'Lambdas' do
  let(:region) { vars.region }
  let(:deployment_identifier) { vars.deployment_identifier }

  context 'auto peering lambda' do
    subject {
      lambda("auto-peering-#{region}-#{deployment_identifier}")
    }

    its(:runtime) { should eq('python3.6') }
    its(:handler) { should eq('auto_peering_lambda.peer_vpcs_for')}
    its(:timeout) { should eq(300)}
    its(:role) do
      should eq(iam_role("auto-peering-role-#{region}-#{deployment_identifier}").arn)
    end
  end
end
