import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    """
    Point d'entrée : reçoit une requête client et déclenche Step Functions
    """
    # Variables d'environnement
    bucket_name = os.environ.get('BUCKET_NAME', 'PLACEHOLDER')
    state_machine_arn = os.environ.get('STATE_MACHINE_ARN', 'PLACEHOLDER')
    
    print(f"📥 Nouvelle requête reçue")
    
    # Extraire les données
    try:
        if isinstance(event, str):
            body = json.loads(event)
        elif 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
    except Exception as e:
        print(f"⚠️ Erreur parsing : {str(e)}")
        body = event
    
    # Données client
    customer_message = body.get('message', 'Message de test')
    customer_name = body.get('name', 'Client Test')
    customer_email = body.get('email', 'test@example.com')
    language = body.get('language', 'en')
    
    # ID unique
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:20]
    request_id = f"req-{timestamp}"
    
    print(f"🆔 Request ID : {request_id}")
    print(f"👤 Client : {customer_name}")
    print(f"🌍 Langue : {language}")
    print(f"💬 Message : {customer_message[:50]}...")
    
    # Préparer les données
    request_data = {
        'request_id': request_id,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'message': customer_message,
        'language': language,
        'timestamp': datetime.now().isoformat()
    }
    
    # Sauvegarder dans S3
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=f"incoming/{request_id}.json",
            Body=json.dumps(request_data, indent=2, ensure_ascii=False),
            ContentType='application/json'
        )
        print(f"✅ Sauvegardé dans S3 : incoming/{request_id}.json")
    except Exception as e:
        print(f"⚠️ Erreur S3 : {str(e)}")
    
    # Déclencher Step Functions
    try:
        response = stepfunctions.start_execution(
            stateMachineArn=state_machine_arn,
            name=request_id,
            input=json.dumps(request_data)
        )
        print(f"✅ Step Functions démarré : {response['executionArn']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'request_id': request_id,
                'status': 'processing',
                'execution_arn': response['executionArn'],
                'message': 'Votre demande est en cours de traitement'
            })
        }
    except Exception as e:
        print(f"⚠️ Erreur Step Functions : {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Erreur lors du démarrage du workflow'
            })
        }