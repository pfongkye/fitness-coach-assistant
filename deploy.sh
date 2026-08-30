#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Run Deployment Script for AI Expert Fitness Coach Assistant (ADK)
# ==============================================================================
set -e

PROJECT_ID=${GCP_PROJECT:-"fitness-coach-dev"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="fitness-coach-assistant"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "================================================================="
echo "🚀 Deploying AI Fitness Coach Assistant to Google Cloud Run"
echo "Project: $PROJECT_ID | Region: $REGION | Service: $SERVICE_NAME"
echo "================================================================="

# 1. Ensure GCP project is set
gcloud config set project "$PROJECT_ID"

# 2. Build and submit container to Google Cloud Artifact Registry / Container Registry
echo "📦 Building container image..."
gcloud builds submit --tag "$IMAGE_NAME" .

# 3. Deploy to Cloud Run with Web UI enabled and public unauthenticated access
echo "🌐 Deploying to Cloud Run with Web UI (--with_ui equivalent)..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --set-env-vars GEMINI_MODEL="gemini-3.6-flash",GCP_PROJECT="$PROJECT_ID",GCP_REGION="$REGION",GEMINI_API_KEY="$GEMINI_API_KEY"

echo "================================================================="
echo "✅ Deployment Complete! Visit your Cloud Run Service URL above to access the Web UI."
echo "================================================================="
