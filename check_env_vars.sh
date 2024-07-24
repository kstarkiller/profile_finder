#!/bin/bash
set -e

# Vérifier que les variables d'environnement sont définies
if [ -z "$AZURE_OPENAI_API_KEY" ] || \
   [ -z "$AZURE_OPENAI_ENDPOINT" ] || \
   [ -z "$AZURE_SEARCH_API_KEY" ] || \
   [ -z "$AZURE_SEARCH_ENDPOINT" ] || \
   [ -z "$AZURE_SP_ID"] || \
   [ -z "$AZURE_SP_SECRET" ] || \
   [ -z "$AZURE_TENANT" ] || \
   [ -z "$IMAGE_TAG" ]; then
    echo "Une ou plusieurs variables d'environnement ne sont pas définies"
    exit 1
fi