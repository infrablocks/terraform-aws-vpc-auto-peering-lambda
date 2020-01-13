require 'spec_helper'

describe 'IAM policies, profiles and roles' do
  let(:region) { vars.region }
  let(:deployment_identifier) { vars.deployment_identifier }
  let(:assumable_roles) { vars.assumable_roles }
  let(:role_arn) { output_for(:harness, 'lambda_role_arn') }

  context 'vpc auto peering lambda role' do
    subject {
      iam_role(role_arn)
    }

    it {should exist}

    it 'can be assumed by lambda' do
      actual = JSON.parse(
          URI.decode(subject.assume_role_policy_document),
          symbolize_names: true)
      expected = {
          Version: "2012-10-17",
          Statement: [
              {
                  Sid: "",
                  Effect: "Allow",
                  Action: "sts:AssumeRole",
                  Principal: {
                      Service: "lambda.amazonaws.com"
                  }
              }
          ]
      }

      expect(actual).to(eq(expected))
    end

    it 'allows log creation' do
      expect(subject).to(be_allowed_action('logs:CreateLogStream'))
      expect(subject).to(be_allowed_action('logs:CreateLogGroup'))
      expect(subject).to(be_allowed_action('logs:PutLogEvents'))
    end

    it 'allows only assumable roles to be assumed' do
      assumable_roles.each do |assumable_role|
        expect(subject)
            .to(be_allowed_action('sts:AssumeRole')
                .resource_arn(assumable_role))
      end
      expect(subject)
          .not_to(be_allowed_action('sts:AssumeRole')
                .resource_arn('arn:aws:iam::176145454894:role/other-role'))
    end

    it 'allows the caller identity to be fetched' do
      expect(subject).to(be_allowed_action('sts:GetCallerIdentity'))
    end
  end
end
