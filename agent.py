import boto3
import json
import time
import zipfile
import logging
import pprint
from io import BytesIO

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')
session = boto3.session.Session()
region = session.region_name
account_id = sts_client.get_caller_identity()["Account"]

bedrock_agent_client = boto3.client('bedrock-agent')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def invoke_agent_helper(query, session_id, agent_id, alias_id, enable_trace=False, session_state=None):
    end_session: bool = False
    if not session_state:
        session_state = {}
  
    # invoke the agent API
    agent_response = bedrock_agent_runtime_client.invoke_agent(
        inputText=query,
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=session_id,
        enableTrace=enable_trace,
        endSession=end_session,
        sessionState=session_state
    )

    if enable_trace:
        logger.info(pprint.pprint(agent_response))

    event_stream = agent_response['completion']
    agent_answer = ""
    citations = []
    try:
        #ans = []
        #i=0
        for event in event_stream:
            if 'chunk' in event:
                chunk_data = event['chunk']
                if 'bytes' in chunk_data:
                    data = chunk_data['bytes']
                    if enable_trace:
                        logger.info(f"Final answer ->\n{data.decode('utf8')}")
                    agent_answer += data.decode('utf8')
                    #pprint.pprint("agent_answer "  + str(i) + " : "+ agent_answer)
                    # i+=1
                    #ans.extend(("", agent_answer))
                if 'attribution' in chunk_data and 'citations' in chunk_data['attribution']:
                    for citation in chunk_data['attribution']['citations']:
                        citation_data = {
                            'generatedResponsePart': citation.get('generatedResponsePart', {}),
                            'retrievedReferences': citation.get('retrievedReferences', [])
                        }
                        citations.append(citation_data)

        return agent_answer, citations
    except Exception as e:
        raise Exception("unexpected event.", e)
    #return "".join(ans)
