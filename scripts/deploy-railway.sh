#!/usr/bin/env bash
set -euo pipefail
# Nunca habilitar set -x aqui: RAILWAY_TOKEN vem das Credentials do Jenkins.
: "${RAILWAY_TOKEN:?Configure a credencial railway-project-token no Jenkins.}"
: "${RAILWAY_PROJECT_ID:?Informe o projeto Railway.}"
: "${RAILWAY_SERVICE:?Informe o serviço Railway.}"
: "${RAILWAY_ENVIRONMENT:?Informe o ambiente Railway.}"
: "${PUBLIC_URL:?Informe o domínio público HTTPS.}"
: "${RELEASE_COMMIT:?Informe o commit validado pelos jobs.}"
command -v railway >/dev/null
command -v python3 >/dev/null

if [[ "$(git rev-parse HEAD)" != "$RELEASE_COMMIT" ]]; then
    echo "O checkout não corresponde ao commit aprovado." >&2
    exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo "Existem alterações em arquivos versionados. Deploy bloqueado." >&2
    exit 1
fi

# Sem --detach: aguarda o resultado do deploy, não apenas o upload.
railway up --project "$RAILWAY_PROJECT_ID" \
    --service "$RAILWAY_SERVICE" --environment "$RAILWAY_ENVIRONMENT" \
    --message "Jenkins ${BUILD_NUMBER:-local} commit ${RELEASE_COMMIT}"
python3 scripts/verify-deploy.py "$PUBLIC_URL"
