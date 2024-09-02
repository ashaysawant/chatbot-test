import json
import boto3
import secrets
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    # Print the incoming event for reference
    print("Incoming event:", json.dumps(event))
    
    # Extract the request body from the incoming event
    if isinstance(event['body'], str):
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            # If the request body is not valid JSON
            error_response = {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in request body"})
            }
            return error_response
    elif isinstance(event['body'], dict):
        body = event['body']
    else:
        # If the body is neither string nor dict, handle the error
        error_response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid request body format"})
        }
        return error_response
    
    # save profile info to Dynamo DB
    return(save_profile_info(body['user_profile']))
    

def save_profile_info(user_profile):
    print("inside sp", user_profile)
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ai-wazard-profile')
    print("table ",table)
    # Prepare the item to be inserted
    item = {
        'session_id': user_profile['session_id'],
        'name': user_profile['name'],
        'income': user_profile['income'],
        'total_networth': user_profile['total_networth'],
        'age': user_profile['age'],
        'investment_horizon': user_profile['investment_horizon'],
        'investment_objective': user_profile['investment_objective'],
        'investment_risk': user_profile['investment_risk'],
        'preferred_asset_class': user_profile['preferred_asset_class'],
        'existing_investments': user_profile['existing_investments'],
        'history': user_profile['history']
    }

    try:
        # Insert the item into the DynamoDB table
        resp=table.put_item(Item=item)
        print("resp ",resp)
        return {
            'statusCode': 200,
            'body': json.dumps('Item inserted successfully')
        }
    except ClientError as e:
        print("exception ",e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inserting item: {e.response['Error']['Message']}")
        }
        
def generate_session():
    return secrets.token_hex(16)
    #return base64.b64encode(os.urandom(16)).decode('ascii')
