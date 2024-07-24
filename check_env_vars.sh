  #!/bin/sh
  set -e

  required_vars=(
    "AZURE_OPENAI_API_KEY"
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_SEARCH_API_KEY"
    "AZURE_SEARCH_ENDPOINT"
    "AZURE_SP_ID"
    "AZURE_SP_SECRET"
    "AZURE_TENANT"
  )

  for var in "${required_vars[@]}"
  do
    if [ -z "${!var}" ]; then
      echo "Error: $var is not set."
      exit 1
    fi
  done