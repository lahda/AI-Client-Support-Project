import json
import boto3
import os

polly = boto3.client('polly')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Convertit la réponse texte en audio avec Amazon Polly
    """
    print(f"📥 Génération de la réponse vocale...")
    print(f"📦 Event reçu : {json.dumps(event)[:300]}...")
    
    # Variables d'environnement
    bucket_name = os.environ.get('BUCKET_NAME', 'PLACEHOLDER')
    
    # Extraire les données
    ai_response = event.get('ai_response', 'Réponse de test')
    request_id = event.get('request_id', 'test-id')
    customer_name = event.get('customer_name', 'Client')
    
    print(f"🔊 Texte à synthétiser : {ai_response[:100]}...")
    print(f"🆔 Request ID : {request_id}")
    
    # Générer l'audio avec Amazon Polly
    try:
        print(f"🎙️ Appel à Amazon Polly (voix Lea, Neural)...")
        
        response = polly.synthesize_speech(
            Text=ai_response,
            OutputFormat='mp3',
            VoiceId='Lea',  # Voix française féminine
            Engine='neural',  # Meilleure qualité
            LanguageCode='fr-FR'
        )
        
        print(f"✅ Audio généré avec succès")
        
        # Lire le stream audio
        audio_data = response['AudioStream'].read()
        audio_size = len(audio_data)
        print(f"📦 Taille audio : {audio_size} bytes ({audio_size/1024:.2f} KB)")
        
        # Sauvegarder dans S3
        audio_key = f"audio-responses/{request_id}.mp3"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=audio_key,
            Body=audio_data,
            ContentType='audio/mpeg',
            Metadata={
                'customer_name': customer_name,
                'request_id': request_id,
                'voice': 'Lea',
                'engine': 'neural'
            }
        )
        
        print(f"✅ Audio sauvegardé dans S3 : {audio_key}")
        
        # Générer une URL présignée (valide 7 jours)
        audio_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': audio_key
            },
            ExpiresIn=604800  # 7 jours
        )
        
        print(f"✅ URL présignée générée (valide 7 jours)")
        print(f"🔗 URL : {audio_url[:100]}...")
        
        return {
            **event,
            'audio_url': audio_url,
            'audio_s3_key': audio_key,
            'audio_size_kb': round(audio_size/1024, 2),
            'polly_success': True
        }
        
    except Exception as e:
        print(f"⚠️ ERREUR Polly/S3 : {str(e)}")
        
        return {
            **event,
            'audio_url': 'ERROR_GENERATING_AUDIO',
            'audio_s3_key': 'error',
            'audio_size_kb': 0,
            'polly_success': False,
            'polly_error': str(e)
        }