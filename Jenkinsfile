// Job de Fernando: publica o commit recebido do pipeline após Build e Testes.
pipeline {
    agent { label 'built-in' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }
    parameters {
        string(name: 'COMMIT_SHA', defaultValue: '', description: 'SHA completo aprovado nas etapas anteriores de Build e Testes.')
        string(name: 'RAILWAY_PROJECT_ID', defaultValue: '67641175-19f1-4597-a518-3ddea95e22fa', description: 'ID do projeto Railway.')
        string(name: 'RAILWAY_SERVICE', defaultValue: 'EntreLinhas', description: 'Nome ou ID do serviço Railway.')
        string(name: 'RAILWAY_ENVIRONMENT', defaultValue: 'production', description: 'Ambiente Railway.')
        string(name: 'PUBLIC_URL', defaultValue: 'https://entrelinhas-production-7e6e.up.railway.app', description: 'Domínio HTTPS da aplicação, sem caminho.')
    }
    stages {
        stage('Preparar commit') {
            steps {
                deleteDir()
                git branch: 'main', url: 'https://github.com/C14-Inatel-2026-2/EntreLinhas.git'
                script {
                    def requested = params.COMMIT_SHA.trim()
                    if (!(requested ==~ /[0-9a-fA-F]{40}/)) {
                        error('COMMIT_SHA precisa conter o SHA completo de 40 caracteres.')
                    }
                    if (requested) {
                        withEnv(["REQUESTED_COMMIT=${requested}"]) {
                            sh 'git checkout --detach "$REQUESTED_COMMIT"'
                        }
                    }
                    env.RELEASE_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    for (value in [params.RAILWAY_PROJECT_ID, params.RAILWAY_SERVICE, params.RAILWAY_ENVIRONMENT, params.PUBLIC_URL]) {
                        if (!value.trim()) { error('Preencha projeto, serviço, ambiente Railway e PUBLIC_URL.') }
                    }
                    if (!(params.PUBLIC_URL ==~ /https:\/\/[a-zA-Z0-9.-]+\/?/)) {
                        error('PUBLIC_URL precisa ser um domínio HTTPS, sem caminho ou credenciais.')
                    }
                }
                sh 'command -v railway; command -v python3; railway --version'
            }
        }
        stage('Deploy - Fernando') {
            steps {
                withCredentials([string(credentialsId: 'railway-project-token', variable: 'RAILWAY_TOKEN')]) {
                    withEnv([
                        "RAILWAY_PROJECT_ID=${params.RAILWAY_PROJECT_ID}",
                        "RAILWAY_SERVICE=${params.RAILWAY_SERVICE}",
                        "RAILWAY_ENVIRONMENT=${params.RAILWAY_ENVIRONMENT}",
                        "PUBLIC_URL=${params.PUBLIC_URL}"
                    ]) {
                        sh '''#!/usr/bin/env bash
set -euo pipefail
test "$(git rev-parse HEAD)" = "$RELEASE_COMMIT"
test -z "$(git status --porcelain --untracked-files=no)"
railway up --project "$RAILWAY_PROJECT_ID" \
    --service "$RAILWAY_SERVICE" --environment "$RAILWAY_ENVIRONMENT" \
    --message "Jenkins ${BUILD_NUMBER} commit ${RELEASE_COMMIT}"

python3 - <<'PY'
import json
import os
import time
from urllib.request import urlopen

base = os.environ['PUBLIC_URL'].rstrip('/')
for attempt in range(12):
    try:
        with urlopen(base + '/health', timeout=10) as response:
            if response.status != 200 or json.load(response) != {'status': 'ok'}:
                raise ValueError('Banco indisponível')
        with urlopen(base + '/static/index.html', timeout=10) as response:
            if response.status != 200 or b'id="form-iniciar"' not in response.read():
                raise ValueError('Interface indisponível')
        print('Deploy verificado: interface e banco disponíveis.')
        break
    except (OSError, ValueError) as error:
        print(f'Verificação {attempt + 1}/12: {error}')
        if attempt == 11:
            raise SystemExit('Deploy não passou na verificação pública.')
        time.sleep(5)
PY
'''
                    }
                }
            }
        }
    }
}
