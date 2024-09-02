import json
import os
import sys
import boto3
import botocore
from botocore.client import Config
from agent import  invoke_agent_helper
import pprint
import uuid
import logging

def lambda_handler(event, context):
    logtrace = os.environ['logtrace']
    if logtrace:
            logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=2)
    query_params = event.get('queryStringParameters', {})
    kbId = os.environ['kbid']
    useAgent = os.environ['useAgent']

    query = event['message'] 
    sessionId = event['sessionId']   
    if logtrace:
        logger.info(pp.pprint('This is the internal prompt'))
        pp.pprint((query))
        logger.info(pp.pprint(sessionId))
    if not sessionId and useAgent =='yes':
        sessionId = str(uuid.uuid4())
    agent_id = os.environ['AgentID'] 
    alias_id = os.environ['AliasID'] 
    guardrail_id = os.environ['guardrailId'] 
    guardrail_version = os.environ['guardrailVersion'] 
    bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
    bedrock_client = boto3.client('bedrock-runtime')
    bedrock_agent_client = boto3.client("bedrock-agent-runtime",
                                  config=bedrock_config)
    boto3_session = boto3.session.Session()
    region_name = boto3_session.region_name



    #prompt_data = """
    #            Command: Give me an brief overv on wealth management
    #            """
    #body = json.dumps({"inputText": prompt_data, "textGenerationConfig": {"topP": 0.95, "temperature": 0.1}})
    # modelId = 'amazon.titan-text-premier-v1:0' # Make sure Titan text premier is available in the account you are doing this workshop in before uncommenting!
    #model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    model_id = os.environ['modelId']
    accept = 'application/json'
    contentType = 'application/json'

    # Set the response headers
    headers = {
        'Content-Type': 'text/html'
    }
    


    
    def retrieveAndGenerate(input, kbId, guardrail_id, guardrail_version, sessionId=None, model_id = model_id, region_id = region_name):
        model_arn = f'arn:aws:bedrock:{region_id}::foundation-model/{model_id}'
        print("input :",input)
        if sessionId:
            return bedrock_agent_client.retrieve_and_generate(
                input={
                    'text': input
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'generationConfiguration': {
                            'guardrailConfiguration': {
                                'guardrailId': guardrail_id,
                                'guardrailVersion':  guardrail_version
                            }
                        },   
                        'knowledgeBaseId': kbId,
                        'modelArn': model_arn
                    }
                },
                sessionId=sessionId
            )
        else:
            return bedrock_agent_client.retrieve_and_generate(
                input={
                    'text': input
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'generationConfiguration': {
                            'guardrailConfiguration': {
                                'guardrailId': guardrail_id,
                                'guardrailVersion':  guardrail_version
                            }
                        },                        
                        'knowledgeBaseId': kbId,
                        'modelArn': model_arn
                    }
                }
            )
    
    #If Environment variable for Agent is true, invoke Agent helper, Else use RetrieveAndGenerate API
    if useAgent == 'yes':
        agent_text, citations = invoke_agent_helper(query, sessionId, agent_id, alias_id, enable_trace=True)
        if logtrace:
            logger.info(pp.pprint('This is a generated output from Agent'))
            pp.pprint(agent_text)
            logger.info(pp.pprint('This is a citations from Agent'))
            pp.pprint(citations)
        response_body = {
            "output":agent_text,
            "sessionId":sessionId,
            "citations":citations
        }
        
    else:
        response = retrieveAndGenerate(query, kbId, guardrail_id, guardrail_version,sessionId=sessionId, model_id=model_id,region_id=region_name)
        print("response ",response)
        sessionId = response['sessionId']
        generated_text = response['output']['text']
        if logtrace:
            logger.info(pp.pprint('This is a generated output from RetrieveAndGenerate API'))
            pp.pprint(generated_text)
    
        citations = response["citations"]
        contexts = []
        for citation in citations:
            retrievedReferences = citation["retrievedReferences"]
            citation_data = {
                'retrievedReferences': retrievedReferences
            }
            contexts.append(citation_data)
        if logtrace:
            logger.info(pp.pprint("contexts:"))
            pp.pprint(contexts)
        response_body = {
            "output":generated_text,
            "sessionId":sessionId,
            "citations": contexts
        }
        #outputText = response_body.get('results')[0].get('outputText')
        #html_content = generated_text.replace('\n', '')   
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': response_body
    }
