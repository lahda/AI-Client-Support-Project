import json
import boto3

translate = boto3.client('translate')
comprehend = boto3.client('comprehend')

def lambda_handler(event, context):
    """
    Traduit le message avec Amazon Translate
    Analyse le sentiment et les entités avec Amazon Comprehend
    """
    print(f"📥 Traduction et analyse...")
    print(f"📦 Event reçu : {json.dumps(event)[:300]}...")
    
    # Extraire les données
    message = event.get('message', '')
    source_language = event.get('language', 'en')
    customer_name = event.get('customer_name', 'Client')
    
    print(f"🌍 Langue source : {source_language}")
    print(f"💬 Message original : {message[:100]}...")
    
    # TRADUCTION avec Amazon Translate
    if source_language != 'fr':
        try:
            print(f"🔄 Traduction {source_language} → fr...")
            translation_response = translate.translate_text(
                Text=message,
                SourceLanguageCode=source_language,
                TargetLanguageCode='fr'
            )
            translated_text = translation_response['TranslatedText']
            print(f"✅ Traduction réussie : {translated_text[:100]}...")
        except Exception as e:
            print(f"⚠️ Erreur Translate : {str(e)}")
            translated_text = message
    else:
        translated_text = message
        print(f"ℹ️ Langue déjà en français, pas de traduction nécessaire")
    
    # ANALYSE DE SENTIMENT avec Amazon Comprehend
    try:
        print(f"🔍 Analyse de sentiment...")
        sentiment_response = comprehend.detect_sentiment(
            Text=translated_text[:5000],  # Limite Comprehend
            LanguageCode='fr'
        )
        
        sentiment = sentiment_response['Sentiment']
        sentiment_scores = sentiment_response['SentimentScore']
        
        print(f"✅ Sentiment : {sentiment}")
        print(f"📊 Scores : Positive={sentiment_scores['Positive']:.2f}, "
              f"Negative={sentiment_scores['Negative']:.2f}, "
              f"Neutral={sentiment_scores['Neutral']:.2f}")
    except Exception as e:
        print(f"⚠️ Erreur Comprehend Sentiment : {str(e)}")
        sentiment = 'NEUTRAL'
        sentiment_scores = {
            'Positive': 0.33,
            'Negative': 0.33,
            'Neutral': 0.34,
            'Mixed': 0.0
        }
    
    # DÉTECTION D'ENTITÉS avec Amazon Comprehend
    try:
        print(f"🏷️ Détection d'entités...")
        entities_response = comprehend.detect_entities(
            Text=translated_text[:5000],
            LanguageCode='fr'
        )
        
        entities = []
        for entity in entities_response['Entities']:
            if entity['Score'] > 0.8:  # Seuil de confiance
                entities.append({
                    'text': entity['Text'],
                    'type': entity['Type'],
                    'score': round(entity['Score'], 3)
                })
        
        print(f"✅ Entités détectées : {len(entities)}")
        for ent in entities[:3]:  # Afficher les 3 premières
            print(f"   - {ent['text']} ({ent['type']}) : {ent['score']}")
    except Exception as e:
        print(f"⚠️ Erreur Comprehend Entities : {str(e)}")
        entities = []
    
    # Déterminer la PRIORITÉ
    if sentiment == 'NEGATIVE' and sentiment_scores['Negative'] > 0.7:
        priority = 'HIGH'
    elif sentiment == 'NEGATIVE':
        priority = 'MEDIUM'
    else:
        priority = 'NORMAL'
    
    print(f"🚨 Priorité assignée : {priority}")
    
    # Retourner les données enrichies
    result = {
        **event,
        'translated_message': translated_text,
        'original_message': message,
        'sentiment': sentiment,
        'sentiment_scores': {
            'Positive': round(sentiment_scores['Positive'], 3),
            'Negative': round(sentiment_scores['Negative'], 3),
            'Neutral': round(sentiment_scores['Neutral'], 3),
            'Mixed': round(sentiment_scores['Mixed'], 3)
        },
        'entities': entities,
        'priority': priority
    }
    
    print(f"✅ Traitement terminé")
    return result