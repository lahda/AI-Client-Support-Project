### Configuration :

5. **"Deploy"**

6. **Configuration → Environment variables** :
   - Key : `SNS_TOPIC_ARN`
   - Value : `arn:aws:sns:us-east-1:...` (celui noté au début)
   - Key : `BUCKET_NAME`
   - Value : `support-ai-project-[vos-initiales]`
   - **"Save"**

7. **Configuration → General configuration** :
   - Timeout : **60 seconds**
   - Memory : **512 MB**
   - **"Save"**

---

# 📋 PHASE 3 : CONFIGURATION IAM (5 minutes)

**Pour CHAQUE Lambda, ajouter les permissions nécessaires :**

### Lambda 1 : Process-Customer-Request

1. Ouvrir la Lambda → **Configuration** → **Permissions**
2. Cliquer sur le **nom du rôle** (lien bleu)
3. **Add permissions** → **Attach policies**
4. Chercher et cocher :
   - ✅ `AmazonS3FullAccess`
   - ✅ `AWSStepFunctionsFullAccess`
5. **Add permissions**

### Lambda 2 : Translate-And-Analyze

1. Configuration → Permissions → Cliquer sur le rôle
2. Add permissions → Attach policies :
   - ✅ `TranslateReadOnly`
   - ✅ `ComprehendReadOnly`

### Lambda 3 : Generate-AI-Response

1. Configuration → Permissions → Cliquer sur le rôle
2. Add permissions → **Create inline policy**
3. Cliquer sur **JSON** et coller :
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-haiku-*"
            ]
        }
    ]
}
```

4. **Next** → Policy name : `BedrockInvokePolicy` → **Create policy**

### Lambda 4 : Generate-Voice-Response

1. Configuration → Permissions → Cliquer sur le rôle
2. Add permissions → Attach policies :
   - ✅ `AmazonPollyFullAccess`
   - ✅ `AmazonS3FullAccess`

### Lambda 5 : Send-Response

1. Configuration → Permissions → Cliquer sur le rôle
2. Add permissions → Attach policies :
   - ✅ `AmazonSNSFullAccess`
   - ✅ `AmazonS3FullAccess`

---

# 📋 PHASE 4 : CRÉATION STEP FUNCTIONS (10 minutes)

## Étape 4.1 : Récupérer les ARN des Lambda ⏱️ 3 min

**📝 Ouvrir un fichier texte et noter les ARN de vos Lambda :**

Pour chaque Lambda (2, 3, 4, 5) :
1. Ouvrir la Lambda
2. En haut à droite, **copier l'ARN complet**
3. Format : `arn:aws:lambda:us-east-1:123456789012:function:NomDeLaLambda`

**Noter :**
- Lambda 2 : `arn:aws:lambda:us-east-1:XXXXX:function:Translate-And-Analyze`
- Lambda 3 : `arn:aws:lambda:us-east-1:XXXXX:function:Generate-AI-Response`
- Lambda 4 : `arn:aws:lambda:us-east-1:XXXXX:function:Generate-Voice-Response`
- Lambda 5 : `arn:aws:lambda:us-east-1:XXXXX:function:Send-Response`

---

## Étape 4.2 : Créer la State Machine ⏱️ 7 min

1. **AWS Console** → **"Step Functions"**
2. **"Create state machine"**
3. **Choisir "Write your workflow in code"**
4. **Type** : Standard
5. Dans **Definition**, **COLLER CE JSON** :
```json
{
  "Comment": "Intelligent Multilingual Customer Support with AI Services",
  "StartAt": "TranslateAndAnalyze",
  "States": {
    "TranslateAndAnalyze": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:REMPLACER:function:Translate-And-Analyze",
        "Payload.$": "$"
      },
      "ResultPath": "$",
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "OutputPath": "$.result",
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "ErrorHandler",
          "ResultPath": "$.error"
        }
      ],
      "Next": "CheckPriority"
    },
    "CheckPriority": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.priority",
          "StringEquals": "HIGH",
          "Next": "HighPriorityNotification"
        }
      ],
      "Default": "GenerateAIResponse"
    },
    "HighPriorityNotification": {
      "Type": "Pass",
      "Comment": "Cas haute priorité détecté - traitement immédiat",
      "Result": {
        "priority_alert": "HIGH_PRIORITY_DETECTED"
      },
      "ResultPath": "$.priority_notification",
      "Next": "GenerateAIResponse"
    },
    "GenerateAIResponse": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:REMPLACER:function:Generate-AI-Response",
        "Payload.$": "$"
      },
      "ResultPath": "$",
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "OutputPath": "$.result",
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "ErrorHandler",
          "ResultPath": "$.error"
        }
      ],
      "Next": "GenerateVoiceResponse"
    },
    "GenerateVoiceResponse": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:REMPLACER:function:Generate-Voice-Response",
        "Payload.$": "$"
      },
      "ResultPath": "$",
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "OutputPath": "$.result",
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "SendResponse",
          "ResultPath": "$.error",
          "Comment": "Continue même si Polly échoue"
        }
      ],
      "Next": "SendResponse"
    },
    "SendResponse": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:REMPLACER:function:Send-Response",
        "Payload.$": "$"
      },
      "ResultPath": "$",
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "ErrorHandler",
          "ResultPath": "$.error"
        }
      ],
      "End": true
    },
    "ErrorHandler": {
      "Type": "Pass",
      "Comment": "Gestion des erreurs - log et notification",
      "Result": {
        "status": "error",
        "message": "Une erreur s'est produite dans le workflow"
      },
      "End": true
    }
  }
}
```

6. **⚠️ REMPLACER les ARN :**
   - Chercher (Ctrl+F) : `REMPLACER`
   - Remplacer par votre **numéro de compte AWS** (12 chiffres)
   - OU remplacer manuellement chaque ARN complet avec ceux notés

7. **Cliquer "Next"**

8. **Settings** :
   - State machine name : `Intelligent-Support-Workflow`
   - Permissions : **"Create new role"**
   - Logging : **OFF** (par défaut)

9. **Cliquer "Create state machine"**

10. **📝 COPIER L'ARN de la State Machine** (en haut de la page)
    - Format : `arn:aws:states:us-east-1:123456789012:stateMachine:Intelligent-Support-Workflow`

---

## Étape 4.3 : Mettre à jour Lambda 1 ⏱️ 1 min

1. **Retourner dans Lambda 1** (Process-Customer-Request)
2. **Configuration** → **Environment variables** → **Edit**
3. **Modifier** `STATE_MACHINE_ARN` :
   - Remplacer `PLACEHOLDER` par l'ARN Step Functions copié
4. **"Save"**

---

# 📋 PHASE 5 : TESTS (5-10 minutes)

## Test 1 : Client mécontent (Anglais → Français) ⏱️ 3 min

1. **Aller dans Lambda 1** (Process-Customer-Request)
2. Cliquer **"Test"** (en haut)
3. **Configure test event** :
   - Event name : `test-negative-en`
   - **Coller ce JSON** :
```json
{
  "body": "{\"name\": \"Sarah Johnson\", \"email\": \"sarah.johnson@example.com\", \"message\": \"I am extremely disappointed with my recent purchase! The laptop arrived damaged with a cracked screen. I've sent 3 emails to support over the past week and received NO response. This is completely unacceptable. I want an immediate refund or replacement!\", \"language\": \"en\"}"
}
```

4. **"Save"** → **"Test"**

### ✅ Vérifications :

**A. Résultat Lambda 1 :**
- Status : `200`
- Body contient : `"status": "processing"` et un `request_id`

**B. Step Functions :**
1. Aller dans **Step Functions** → **State machines** → `Intelligent-Support-Workflow`
2. Cliquer sur **Executions**
3. Voir l'exécution en cours (Status : **Running** puis **Succeeded**)
4. Cliquer sur l'exécution → **Graph view** → Voir toutes les étapes en vert ✅
5. Cliquer sur chaque étape pour voir les logs

**C. Email SNS :**
- Vous devriez recevoir un email avec :
  - Titre : `🚨 Support Client - Sarah Johnson [HIGH] - NEGATIVE`
  - Contenu détaillé avec traduction, sentiment, réponse IA, URL audio

**D. S3 :**
1. Aller dans **S3** → Bucket `support-ai-project-[vos-initiales]`
2. Vérifier :
   - `incoming/req-XXX.json` ✅
   - `responses/req-XXX_complete.json` ✅
   - `audio-responses/req-XXX.mp3` ✅
3. **Télécharger le MP3 et l'écouter** 🎧

**E. CloudWatch Logs :**
- Pour chaque Lambda, voir les logs détaillés

---

## Test 2 : Client satisfait (Espagnol → Français) ⏱️ 2 min

Créer un nouveau test dans Lambda 1 :
```json
{
  "body": "{\"name\": \"Carlos Rodriguez\", \"email\": \"carlos@example.com\", \"message\": \"¡Excelente servicio! Recibí mi pedido antes de lo esperado. La calidad del producto es excepcional y el empaque muy cuidado. Estoy muy satisfecho con esta compra y definitivamente volveré a comprar aquí. Muchas gracias al equipo!\", \"language\": \"es\"}"
}
```

**Attendu :**
- Priorité : **NORMAL**
- Sentiment : **POSITIVE**
- Email avec emoji 😊

---

## Test 3 : Question livraison (Allemand → Français) ⏱️ 2 min
```json
{
  "body": "{\"name\": \"Hans Mueller\", \"email\": \"hans@example.com\", \"message\": \"Guten Tag, ich habe vor 5 Tagen bestellt aber mein Paket ist noch nicht angekommen. Die Tracking-Nummer zeigt keine Updates. Können Sie mir bitte den aktuellen Status mitteilen? Wann kann ich mit der Lieferung rechnen?\", \"language\": \"de\"}"
}
```

**Attendu :**
- Priorité : **MEDIUM**
- Sentiment : **NEGATIVE** ou **NEUTRAL**
- Entités détectées : numéros, dates

---

## Test 4 : Message en français direct ⏱️ 2 min
```json
{
  "body": "{\"name\": \"Marie Dubois\", \"email\": \"marie@example.com\", \"message\": \"Bonjour, j'ai une question concernant les modalités de retour pour un article acheté il y a 2 semaines. Le produit ne correspond pas à mes attentes. Quelle est la procédure à suivre ? Merci d'avance.\", \"language\": \"fr\"}"
}
```

**Attendu :**
- Pas de traduction (déjà en français)
- Sentiment : **NEUTRAL**
- Réponse professionnelle sur les retours

---

# ✅ CHECKLIST FINALE

### Infrastructure :
- [ ] Bucket S3 créé avec 4 dossiers
- [ ] Topic SNS créé et email confirmé
- [ ] Bedrock activé (Claude 3 Haiku accessible)

### Lambda Functions :
- [ ] Lambda 1 : Process-Customer-Request (avec variables d'env)
- [ ] Lambda 2 : Translate-And-Analyze
- [ ] Lambda 3 : Generate-AI-Response
- [ ] Lambda 4 : Generate-Voice-Response (avec BUCKET_NAME)
- [ ] Lambda 5 : Send-Response (avec SNS_TOPIC_ARN et BUCKET_NAME)

### Permissions IAM :
- [ ] Lambda 1 : S3 + Step Functions
- [ ] Lambda 2 : Translate + Comprehend
- [ ] Lambda 3 : Bedrock (policy custom)
- [ ] Lambda 4 : Polly + S3
- [ ] Lambda 5 : SNS + S3

### Step Functions :
- [ ] State Machine créée avec les bons ARN
- [ ] Lambda 1 mise à jour avec STATE_MACHINE_ARN

### Tests :
- [ ] Test 1 (négatif anglais) : ✅ Succeeded
- [ ] Email SNS reçu avec tous les détails
- [ ] 3 fichiers générés dans S3
- [ ] MP3 téléchargé et écouté
- [ ] Logs CloudWatch vérifiés

---

# 🎯 LIVRABLES PORTFOLIO

## 1. Architecture Diagram

Créer sur **draw.io** ou **Lucidchart** :

📂 Explication des dossiers
✅ Dossiers UTILISÉS (doivent contenir des fichiers après test) :

incoming/ ← Requêtes initiales (Lambda 1)

Fichiers : req-XXXXXX.json
Contenu : Message original du client


responses/ ← Interactions complètes (Lambda 5)

Fichiers : req-XXXXXX_complete.json
Contenu : Tout le workflow (traduction, sentiment, réponse IA, etc.)


audio-responses/ ← Fichiers audio Polly (Lambda 4)

Fichiers : req-XXXXXX.mp3
Contenu : Réponse vocale générée