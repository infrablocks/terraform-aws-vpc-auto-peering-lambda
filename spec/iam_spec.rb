require 'spec_helper'

describe 'IAM policies, profiles and roles' do
  include_context :terraform

  let(:region) {RSpec.configuration.region}
  let(:deployment_identifier) {RSpec.configuration.deployment_identifier}

  context 'auto peering role' do
    subject {
      iam_role("auto-peering-role-#{region}-#{deployment_identifier}")
    }

    it {should exist}

    it 'allows assuming a role of lambda' do
      policy_document = JSON.parse(
          URI.decode(subject.assume_role_policy_document))
      expect(policy_document["Statement"].count).to(eq(1))

      policy_document_statement = policy_document["Statement"].first

      expect(policy_document_statement['Effect']).to(eq('Allow'))
      expect(policy_document_statement['Action']).to(eq('sts:AssumeRole'))
      expect(policy_document_statement['Principal']['Service'])
          .to(eq('lambda.amazonaws.com'))
    end

    it {
      should have_iam_policy(
                 "auto-peering-policy-#{region}-#{deployment_identifier}")
    }
  end

  context 'auto peering policy' do
    subject {
      iam_policy("auto-peering-policy-#{region}-#{deployment_identifier}")
    }

    let(:policy_document) do
      policy_version_response = iam_client.get_policy_version({
          policy_arn: subject.arn,
          version_id: subject.default_version_id,
      })

      JSON.parse(URI.decode(
          policy_version_response.policy_version.document))
    end

    it {should exist}

    it 'allows EC2 actions' do
      expect(policy_document["Statement"].count).to(eq(1))

      policy_document_statement = policy_document["Statement"].first
      expect(policy_document_statement['Effect']).to(eq('Allow'))
      expect(policy_document_statement['Resource']).to(eq('*'))
      expect(policy_document_statement['Action']).to(include('ec2:AcceptVpcPeeringConnection'))
      expect(policy_document_statement['Action']).to(include('ec2:CreateVpcPeeringConnection'))
      expect(policy_document_statement['Action']).to(include('ec2:DeleteVpcPeeringConnection'))
      expect(policy_document_statement['Action']).to(include('ec2:DescribeVpcPeeringConnections'))
      expect(policy_document_statement['Action']).to(include('ec2:CreateRoute'))
      expect(policy_document_statement['Action']).to(include('ec2:DeleteRoute'))
      expect(policy_document_statement['Action']).to(include('ec2:DescribeRouteTables'))
      expect(policy_document_statement['Action']).to(include('ec2:DescribeTags'))
      expect(policy_document_statement['Action']).to(include('ec2:DescribeVpcs'))
    end

    it 'allows log creation' do
      expect(policy_document["Statement"].count).to(eq(1))

      policy_document_statement = policy_document["Statement"].first
      expect(policy_document_statement['Effect']).to(eq('Allow'))
      expect(policy_document_statement['Resource']).to(eq('*'))
      expect(policy_document_statement['Action']).to(include('logs:CreateLogStream'))
      expect(policy_document_statement['Action']).to(include('logs:CreateLogGroup'))
      expect(policy_document_statement['Action']).to(include('logs:PutLogEvents'))
    end
  end
end
