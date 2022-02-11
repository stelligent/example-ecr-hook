# Stelligent::ECRExample::Hook

This is an example CloudFormation Hook that checks compliance against [AWS::ECR::Repository](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html) resources.

## What does it enforce?

1) Repo Encryption is using KMS
2) Images are scanned on push
3) Image tags are immutable

## When does it run?

This hook will run against all `AWS::ECR::Repository` resources at create or update.

## Publishing and testing the hook

To package and publish the hook into your account run
`cfn submit --set-default`.

Note the ARN of the generated hook, or gather it using `aws cloudformation list-types`

Finally, enable the hook to execute against stacks in the account by pushing up a type configuration. In this example, the hook executes against `ALL` stacks, but on errors will `WARN`. Set your hook ARN as appropriate.
```bash
export HOOK_TYPE_ARN=<your arn>
export HOOK_CONFIG=$(cat test/hook_configuration.json)
aws cloudformation set-type-configuration --configuration $HOOK_CONFIG --type-arn $HOOK_TYPE_ARN

# Execute a test with the example cfn template
aws cloudformation deploy --template-file test/ecr_test.yml --stack-name ecr-hook-test
# Review the stack events to see hook results
aws cloudformation describe-stack-events --stack-name ecr-hook-test
# Cleanup the test stack
aws cloudformation delete-stack --stack-name ecr-hook-test
```

### Implementation
The hook schema is defined in [stelligent-ecrexample-hook.json](stelligent-ecrexample-hook.json).

The hook implementation is contained in [src/stelligent_ecrexample_hook/handlers.py](src/stelligent_ecrexample_hook/handlers.py)

