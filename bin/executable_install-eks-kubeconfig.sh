#!/usr/bin/env bash
# install-eks-kubeconfig — Update local kubeconfig from EKS
# Usage: install-eks-kubeconfig [dev|prod|both]
set -euo pipefail

AWS_REGION="us-west-2"
EKS_CLUSTER="general"
AWS_PROFILE_DEV="development"
AWS_PROFILE_PROD="production"
TARGET="${1:-both}"

log() { printf "\n\033[1;34m==> %s\033[0m\n" "$*"; }

mkdir -p "$HOME/.kube"

if [[ "$TARGET" == "dev" || "$TARGET" == "both" ]]; then
  log "Updating kubeconfig: dev ($AWS_PROFILE_DEV)"
  aws eks update-kubeconfig \
    --profile "$AWS_PROFILE_DEV" \
    --region  "$AWS_REGION" \
    --name    "$EKS_CLUSTER" \
    --alias   "dev" \
    --kubeconfig "$HOME/.kube/config"
fi

if [[ "$TARGET" == "prod" || "$TARGET" == "both" ]]; then
  log "Updating kubeconfig: prod ($AWS_PROFILE_PROD)"
  aws eks update-kubeconfig \
    --profile "$AWS_PROFILE_PROD" \
    --region  "$AWS_REGION" \
    --name    "$EKS_CLUSTER" \
    --alias   "prd" \
    --kubeconfig "$HOME/.kube/config"
fi

echo "✅ kubeconfig updated. Contexts available:"
kubectl config get-contexts
