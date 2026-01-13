import json
import boto3
import os

sns = boto3.client("sns")
s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    Envoie la notification finale via Amazon SNS
    Sauvegarde l'interaction complète dans S3
    """
    print("📥 Envoi de la réponse finale...")
    print(f"📦 Event reçu : {json.dumps(event)[:300]}...")

    # Variables d'environnement
    sns_topic_arn = os.environ.get("SNS_TOPIC_ARN", "PLACEHOLDER")
    bucket_name = os.environ.get("BUCKET_NAME", "PLACEHOLDER")

    # Extraction des données
    request_id = event.get("request_id", "unknown")
    customer_name = event.get("customer_name", "Client")
    customer_email = event.get("customer_email", "")
    original_message = event.get("original_message", "")
    translated_message = event.get("translated_message", "")
    language = event.get("language", "unknown")
    sentiment = event.get("sentiment", "NEUTRAL")
    priority = event.get("priority", "NORMAL")
    entities = event.get("entities", [])
    sentiment_scores = event.get("sentiment_scores", {})
    ai_response = event.get("ai_response", "")
    audio_url = event.get("audio_url", "")
    model_used = event.get("model_used", "Unknown")
    bedrock_success = event.get("bedrock_success", False)
    polly_success = event.get("polly_success", False)

    print(f"👤 Client : {customer_name}")
    print(f"😊 Sentiment : {sentiment}")
    print(f"🚨 Priorité : {priority}")
    print(f"🤖 Modèle : {model_used}")
    print(f"✅ Bedrock : {bedrock_success}, Polly : {polly_success}")

    # Sauvegarde S3
    complete_interaction = {
        "request_id": request_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "language": language,
        "original_message": original_message,
        "translated_message": translated_message,
        "sentiment": sentiment,
        "sentiment_scores": sentiment_scores,
        "priority": priority,
        "entities": entities,
        "ai_response": ai_response,
        "audio_url": audio_url,
        "model_used": model_used,
        "services_used": {
            "translate": language != "fr",
            "comprehend": True,
            "bedrock": bedrock_success,
            "polly": polly_success,
            "s3": True,
            "sns": True,
        },
        "timestamp": event.get("timestamp", ""),
    }

    try:
        response_key = f"responses/{request_id}_complete.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=response_key,
            Body=json.dumps(complete_interaction, indent=2, ensure_ascii=False),
            ContentType="application/json",
        )
        print(f"✅ Interaction sauvegardée : {response_key}")
    except Exception as e:
        print(f"⚠️ Erreur S3 : {str(e)}")

    # Emojis
    emoji = {"HIGH": "🚨", "MEDIUM": "⚠️", "NORMAL": "😊"}.get(priority, "📧")
    sentiment_emoji = {
        "POSITIVE": "😊",
        "NEUTRAL": "😐",
        "NEGATIVE": "😞",
        "MIXED": "🤔",
    }.get(sentiment, "📄")

    # Message SNS
    message = f"""{emoji} NOUVELLE INTERACTION CLIENT TRAITÉE

═══════════════════════════════════════════════════
📋 INFORMATIONS CLIENT
═══════════════════════════════════════════════════
👤 Nom : {customer_name}
📧 Email : {customer_email}
🌍 Langue : {language.upper()}
🆔 ID Requête : {request_id}

═══════════════════════════════════════════════════
📊 ANALYSE AUTOMATIQUE
═══════════════════════════════════════════════════
{sentiment_emoji} Sentiment : {sentiment}
📈 Scores :
   • Positif : {sentiment_scores.get("Positive", 0):.1%}
   • Négatif : {sentiment_scores.get("Negative", 0):.1%}
   • Neutre : {sentiment_scores.get("Neutral", 0):.1%}
🚨 Priorité : {priority}
🏷️ Entités détectées : {len(entities)}
"""

    if entities:
        message += "\n   Entités principales :\n"
        for ent in entities[:3]:
            message += (
                f"   • {ent.get('text', 'N/A')} "
                f"({ent.get('type', 'N/A')}) - "
                f"{ent.get('score', 0):.1%}\n"
            )

    message += f"""
═══════════════════════════════════════════════════
💬 MESSAGE ORIGINAL
═══════════════════════════════════════════════════
{original_message}
"""

    if language != "fr":
        message += f"""
═══════════════════════════════════════════════════
🔄 TRADUCTION
═══════════════════════════════════════════════════
{translated_message}
"""

    message += f"""
═══════════════════════════════════════════════════
🤖 RÉPONSE GÉNÉRÉE ({model_used})
═══════════════════════════════════════════════════
{ai_response}

═══════════════════════════════════════════════════
🎧 RÉPONSE AUDIO
═══════════════════════════════════════════════════
"""

    message += (
        f"✅ Audio disponible (7 jours) :\n{audio_url}\n"
        if polly_success
        else "⚠️ Erreur génération audio\n"
    )

    message += """
═══════════════════════════════════════════════════
☁️ SERVICES AWS UTILISÉS
═══════════════════════════════════════════════════
✅ Lambda
✅ Step Functions
"""
    if language != "fr":
        message += "✅ Amazon Translate\n"

    message += f"""✅ Amazon Comprehend
{'✅' if bedrock_success else '⚠️'} Amazon Bedrock
{'✅' if polly_success else '⚠️'} Amazon Polly
✅ Amazon S3
✅ Amazon SNS
═══════════════════════════════════════════════════
"""

    # Envoi SNS
    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject=f"{emoji} Support Client - {customer_name} [{priority}] - {sentiment}",
            Message=message,
        )
        sns_success = True
    except Exception as e:
        print(f"⚠️ Erreur SNS : {str(e)}")
        sns_success = False

    return {
        "statusCode": 200,
        "request_id": request_id,
        "status": "completed",
        "services_status": {
            "translate": language != "fr",
            "comprehend": True,
            "bedrock": bedrock_success,
            "polly": polly_success,
            "s3": True,
            "sns": sns_success,
        },
    }
