import json
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Génère une réponse intelligente avec Amazon Bedrock (Claude 3 Haiku)
    """
    print(f"📥 Génération de réponse avec Bedrock...")
    print(f"📦 Event reçu : {json.dumps(event)[:300]}...")
    
    # Extraire les données
    customer_name = event.get('customer_name', 'Client')
    translated_message = event.get('translated_message', '')
    sentiment = event.get('sentiment', 'NEUTRAL')
    priority = event.get('priority', 'NORMAL')
    entities = event.get('entities', [])
    sentiment_scores = event.get('sentiment_scores', {})
    
    print(f"👤 Client : {customer_name}")
    print(f"😊 Sentiment : {sentiment} (Negative: {sentiment_scores.get('Negative', 0):.2f})")
    print(f"🚨 Priorité : {priority}")
    print(f"🏷️ Entités : {len(entities)}")
    
    # Préparer le contexte pour Claude
    entities_text = ", ".join([f"{e['text']} ({e['type']})" for e in entities[:5]]) if entities else "aucune"
    
    # Construire le prompt
    prompt = f"""Tu es un assistant de support client professionnel et empathique pour une entreprise e-commerce.

Contexte de la demande :
- Client : {customer_name}
- Sentiment détecté : {sentiment}
- Niveau de priorité : {priority}
- Score de négativité : {sentiment_scores.get('Negative', 0):.0%}
- Entités mentionnées : {entities_text}

Message du client (traduit en français) :
"{translated_message}"

Instructions :
1. Analyse le message et identifie la problématique principale
2. Réponds de manière professionnelle, empathique et chaleureuse
3. Adapte ton ton au sentiment détecté :
   - Si NEGATIVE : montre beaucoup d'empathie, présente des excuses, propose une solution concrète immédiate
   - Si NEUTRAL : sois professionnel et aidant
   - Si POSITIVE : sois reconnaissant et maintiens cette satisfaction
4. Propose une action concrète ou les prochaines étapes
5. Sois concis mais complet (80-120 mots maximum)
6. Utilise un français professionnel et naturel
7. Si approprié pour un cas très négatif, mentionne un geste commercial

Génère maintenant la réponse parfaite pour ce client :"""

    print(f"📝 Prompt préparé ({len(prompt)} caractères)")
    
    # Appel à Amazon Bedrock avec Claude 3 Haiku
    try:
        print(f"🤖 Appel à Bedrock (Claude 3 Haiku)...")
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 400,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # Nettoyer la réponse
        ai_response = ai_response.strip()
        
        print(f"✅ Réponse Bedrock générée ({len(ai_response)} caractères)")
        print(f"📄 Réponse : {ai_response[:150]}...")
        
        return {
            **event,
            'ai_response': ai_response,
            'model_used': 'Claude 3 Haiku (Bedrock)',
            'bedrock_success': True
        }
        
    except Exception as e:
        print(f"⚠️ ERREUR Bedrock : {str(e)}")
        
        # Réponse de secours (fallback)
        if sentiment == 'NEGATIVE':
            fallback = f"Bonjour {customer_name}, nous sommes sincèrement désolés de cette situation. Votre satisfaction est notre priorité absolue. Notre équipe va traiter votre demande en urgence et vous contacter sous 2 heures pour résoudre ce problème. En attendant, nous vous offrons un geste commercial de 15% sur votre prochaine commande. Merci de votre patience."
        else:
            fallback = f"Bonjour {customer_name}, nous avons bien reçu votre message et nous vous remercions de nous avoir contactés. Notre équipe examine votre demande attentivement et vous répondra dans les plus brefs délais avec toutes les informations nécessaires. Nous restons à votre disposition."
        
        print(f"🔄 Utilisation de la réponse de secours")
        
        return {
            **event,
            'ai_response': fallback,
            'model_used': 'Fallback Template',
            'bedrock_success': False,
            'bedrock_error': str(e)
        }