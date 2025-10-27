#!/bin/bash

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="client-app"

echo "Setting up ECR repository..."

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

echo "ECR repository '$ECR_REPOSITORY' is ready in region '$AWS_REGION'"
echo "Repository URI: $(aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)"