from aws_cdk import core as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
import boto3
import base64
from botocore.exceptions import ClientError



# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from my_pipeline.my_pipeline_app_stage import MyPipelineAppStage


class MyPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        secret_name = "github-token3"
        region_name = "ap-southeast-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])


        source = CodePipelineSource.git_hub("SumanOjha/cdk-pipeline", "master", authentication=core.SecretValue.plain_text(secret))
        pipeline =  CodePipeline(self, "Pipeline", 
                        pipeline_name="MyPipeline",
                        synth=ShellStep("Synth", 
                            input=source,
                            commands=["npm ci", "npm run build", "npx cdk synth"]
                        )
                    )
        stage = pipeline.add_stage(
                        MyPipelineAppStage(self, "test",
                            env = cdk.Environment(account="357568851775", region="ap-southeast-2"))
                            # env = kwargs['env'])
                )
        '''
        stage.add_post(ShellStep('validate',
                            input=source,
                            commands=['curl -Ssf https://my.webservice.com/']))   
        '''
        # This is a change