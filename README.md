# AI-Client-Support-Project
# 🤖 Assistant Vocal Intelligent pour Support Client Multilingue

![AWS](https://img.shields.io/badge/AWS-Cloud-orange?style=for-the-badge&logo=amazon-aws)
![AI/ML](https://img.shields.io/badge/AI%2FML-Bedrock-blue?style=for-the-badge)
![Serverless](https://img.shields.io/badge/Serverless-Lambda-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

**Projet Cloud Engineering - AWS AI/ML**  
**Durée de réalisation :** 50 minutes  
**Coût par requête :** ~$0.002 (0.2 centimes)  
**Date :** Janvier 2025

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Technologies utilisées](#technologies-utilisées)
- [Déploiement](#déploiement)
- [Tests](#tests)
- [Métriques et performances](#métriques-et-performances)
- [Coûts](#coûts)
- [Captures d'écran](#captures-décran)
- [Résolution de problèmes](#résolution-de-problèmes)
- [Extensions possibles](#extensions-possibles)

---

## 🎯 Vue d'ensemble

### Problème résolu

Les entreprises reçoivent des milliers de demandes clients quotidiennes dans différentes langues. Le traitement manuel est :

- ⏱️ **Lent** : 24-48h de délai de réponse
- 💰 **Coûteux** : $50-100 par agent/heure  
- 🌍 **Limité** : Support multilingue complexe
- 😞 **Incohérent** : Qualité variable selon l'agent

### Solution apportée

Architecture serverless entièrement automatisée qui :

- ⚡ **Traite les demandes en < 10 secondes**
- 🤖 **Génère des réponses intelligentes avec IA générative (Claude 3 Haiku)**
- 🌎 **Support automatique de 75+ langues**
- 🎙️ **Réponses vocales pour accessibilité**
- 📊 **Analyse de sentiment en temps réel**
- 💵 **Coût : ~$0.002 par requête** (99.75% moins cher qu'un agent)

### Résultats clés

| Métrique | Valeur | Benchmark |
|----------|--------|-----------|
| **Temps de réponse** | 7-10 secondes | vs 24-48h (manuel) |
| **Langues supportées** | 75+ | Automatique |
| **Coût par requête** | $0.002 | vs $8 (manuel) |
| **Économie** | 99.75% | vs agents humains |
| **Précision sentiment** | > 90% | Amazon Comprehend |
| **Disponibilité** | 99.9%+ | Architecture serverless |

---

## 🏗️ Architecture

### Diagramme d'architecture

![Architecture d'Orchestration IA pour Support Client Multilingue](./Architecture%20d'Orchestration%20IA%20pour%20Support%20Client%20Multilingue.drawio.png)

### Architecture simplifiée
```
Client (Web/Mobile)
    ↓
Lambda 1: Process-Customer-Request
    ↓
AWS Step Functions (Orchestrateur)
    ├─→ Lambda 2: Translate & Analyze
    │   ├─→ Amazon Translate (75+ langues)
    │   └─→ Amazon Comprehend (Sentiment + Entités)
    ├─→ Lambda 3: Generate AI Response
    │   └─→ Amazon Bedrock (Claude 3 Haiku)
    ├─→ Lambda 4: Generate Voice Response
    │   └─→ Amazon Polly (Synthèse vocale)
    └─→ Lambda 5: Send Response
        ├─→ Amazon S3 (Stockage)
        └─→ Amazon SNS (Notification email)
```

### Flux de données
```
Message client (EN/ES/DE/etc.)
    ↓ Translate
Message traduit (FR)
    ↓ Comprehend
Sentiment + Entités + Priorité
    ↓ Bedrock (Claude)
Réponse IA personnalisée
    ↓ Polly
Réponse audio (MP3)
    ↓ S3 + SNS
Notification + Stockage
```

---

## ✨ Fonctionnalités

### 🌍 Support Multilingue Automatique

- **75+ langues supportées** (EN, ES, DE, IT, PT, ZH, JA, AR, etc.)
- Détection automatique de la langue source
- Traduction vers le français (langue pivot)
- Préservation du contexte et des nuances

### 🧠 Analyse Intelligente avec IA

**1. Analyse de sentiment (Amazon Comprehend)**
- Détection : POSITIVE, NEGATIVE, NEUTRAL, MIXED
- Scores de confiance détaillés (0-100%)
- Précision > 90%

**2. Extraction d'entités**
- Types : PERSON, ORGANIZATION, LOCATION, DATE, COMMERCIAL_ITEM, etc.
- Score de confiance par entité
- Filtrage intelligent (seuil > 80%)

**3. Détection automatique du problème**
- Catégories : livraison, produit, remboursement, compte, facturation
- Classification par mots-clés
- Routing intelligent

### 🤖 Génération de Réponses Contextuelles

**Claude 3 Haiku via Amazon Bedrock :**
- Réponses personnalisées selon le contexte
- Adaptation du ton selon le sentiment
- Propositions d'actions concrètes
- Gestes commerciaux pour cas négatifs
- Longueur optimisée (80-120 mots)

### 🎙️ Synthèse Vocale de Haute Qualité

**Amazon Polly Neural TTS :**
- Voix française naturelle (Lea)
- Qualité quasi-humaine
- Format MP3 optimisé
- URL présignée sécurisée (7 jours)

### 🚨 Priorisation Automatique
```
HIGH   : Sentiment très négatif (score > 70%) → SLA 1h
MEDIUM : Sentiment négatif modéré (30-70%)   → SLA 4h
NORMAL : Sentiment neutre ou positif         → SLA 24h
```

### 📊 Traçabilité Complète

- ID unique par requête
- Tous les fichiers sauvegardés dans S3
- Logs détaillés dans CloudWatch
- Workflow visuel dans Step Functions
- Audit trail complet

---

## 🛠️ Technologies utilisées

### Services AWS AI/ML

| Service | Usage | Justification |
|---------|-------|---------------|
| **Amazon Bedrock** | Claude 3 Haiku (LLM) | Génération réponses contextuelles, économique |
| **Amazon Comprehend** | NLP | Sentiment + entités, précision > 90% |
| **Amazon Translate** | Traduction | 75+ langues, traduction neurale |
| **Amazon Polly** | Text-to-Speech | Voix neurale haute qualité |

### Infrastructure AWS

| Service | Usage | Configuration |
|---------|-------|---------------|
| **AWS Step Functions** | Orchestration | 5 états, retry auto, error handling |
| **AWS Lambda** | Compute serverless | 5 fonctions, Python 3.11, 512 MB |
| **Amazon S3** | Storage | 4 dossiers, encryption AES-256 |
| **Amazon SNS** | Notifications | Email, format texte |
| **CloudWatch** | Monitoring | Logs 7 jours, métriques standard |

### Stack technique

- **Python 3.11** - Runtime Lambda
- **Boto3** - AWS SDK for Python
- **JSON** - Format de données
- **Markdown** - Documentation

---

## 🚀 Déploiement

### Prérequis

- ✅ Compte AWS actif
- ✅ Région **us-east-1** (N. Virginia) recommandée
- ✅ Amazon Bedrock activé (Claude 3 Haiku)
- ✅ Permissions IAM pour créer Lambda, Step Functions, S3, SNS, etc.

### Guide de déploiement rapide (50 minutes)

#### 1. Infrastructure de base (5 min)

**Créer le bucket S3 :**
```bash
aws s3 mb s3://support-ai-project-[vos-initiales] --region us-east-1
```

**Créer les dossiers :**
```bash
BUCKET="support-ai-project-[vos-initiales]"
aws s3api put-object --bucket $BUCKET --key incoming/
aws s3api put-object --bucket $BUCKET --key responses/
aws s3api put-object --bucket $BUCKET --key audio-responses/
aws s3api put-object --bucket $BUCKET --key transcripts/
```

**Créer le topic SNS :**
```bash
aws sns create-topic --name customer-support-alerts --region us-east-1

# S'abonner par email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:customer-support-alerts \
  --protocol email \
  --notification-endpoint votre@email.com
```

**⚠️ Confirmer l'email SNS dans votre boîte de réception**

#### 2. Activer Amazon Bedrock (2 min)

1. Console AWS → **Amazon Bedrock** → **Model access**
2. **"Manage model access"**
3. Cocher **Anthropic - Claude 3 Haiku**
4. **"Request model access"**
5. Attendre 30 sec → Vérifier status **"Access granted" ✅**

#### 3. Créer les 5 Lambda Functions (25 min)

**Configuration standard pour toutes les Lambda :**
- Runtime : Python 3.11
- Timeout : 60 seconds
- Memory : 512 MB

**Lambda 1 : Process-Customer-Request**
- Variables d'env : `BUCKET_NAME`, `STATE_MACHINE_ARN`
- Permissions : S3, Step Functions

**Lambda 2 : Translate-And-Analyze**
- Permissions : Translate, Comprehend

**Lambda 3 : Generate-AI-Response**
- Permissions : Bedrock InvokeModel

**Lambda 4 : Generate-Voice-Response**
- Variables d'env : `BUCKET_NAME`
- Permissions : Polly, S3

**Lambda 5 : Send-Response**
- Variables d'env : `SNS_TOPIC_ARN`, `BUCKET_NAME`
- Permissions : SNS, S3

> **Note :** Le code complet de chaque Lambda est disponible dans le repository GitHub.

#### 4. Créer Step Functions (10 min)

1. Console AWS → **Step Functions**
2. **"Create state machine"** → **"Write your workflow in code"**
3. Copier la définition JSON (voir fichier `step-functions-definition.json`)
4. Remplacer les ARN Lambda par vos ARN réels
5. Name : `Intelligent-Support-Workflow`
6. **"Create state machine"**
7. Copier l'ARN de la State Machine

#### 5. Configuration finale (3 min)

**Mettre à jour Lambda 1 avec l'ARN Step Functions :**
```bash
aws lambda update-function-configuration \
  --function-name Process-Customer-Request \
  --environment "Variables={
    BUCKET_NAME=support-ai-project-XX,
    STATE_MACHINE_ARN=arn:aws:states:us-east-1:XXX:stateMachine:Intelligent-Support-Workflow
  }" \
  --region us-east-1
```

### ✅ Checklist de déploiement
