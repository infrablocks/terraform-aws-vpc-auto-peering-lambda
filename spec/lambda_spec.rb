require 'spec_helper'

describe 'Lambdas' do
  include_context :terraform

  let(:region) {RSpec.configuration.region}
  let(:deployment_identifier) {RSpec.configuration.deployment_identifier}

  context 'auto peering lambda' do
    subject {
      lambda("auto-peering-#{region}-#{deployment_identifier}")
    }

    its(:runtime) { should eq('python3.6') }
    its(:handler) { should eq('auto_peering_lambda.peer_vpcs_for')}
    its(:timeout) { should eq(300)}
    its(:role) { should eq(iam_role("auto-peering-role-#{region}-#{deployment_identifier}").arn) }
  end
end
