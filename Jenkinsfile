// Pipeline único: Preparar commit -> Frontend/Cypress (Mateus) -> Deploy (Fernando).
// O mesmo SHA é testado e publicado; qualquer falha antes do Deploy bloqueia a publicação.
properties([
    disableConcurrentBuilds(),
    parameters([
        string(name: 'COMMIT_SHA', defaultValue: '', description: 'SHA completo (40 caracteres) a testar e publicar. Vazio = ponta atual da main, resolvida uma única vez.'),
        string(name: 'RAILWAY_PROJECT_ID', defaultValue: '67641175-19f1-4597-a518-3ddea95e22fa', description: 'ID do projeto Railway.'),
        string(name: 'RAILWAY_SERVICE', defaultValue: 'EntreLinhas', description: 'Nome ou ID do serviço Railway.'),
        string(name: 'RAILWAY_ENVIRONMENT', defaultValue: 'production', description: 'Ambiente Railway.'),
        string(name: 'PUBLIC_URL', defaultValue: 'https://entrelinhas-production-7e6e.up.railway.app', description: 'Domínio HTTPS da aplicação, sem caminho.')
    ])
])

timeout(time: 30, unit: 'MINUTES') {
    node('built-in') {
        stage('Preparar commit') {
            deleteDir()
            git branch: 'main', url: 'https://github.com/C14-Inatel-2026-2/EntreLinhas.git'
            def requested = params.COMMIT_SHA.trim()
            if (!requested) {
                requested = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
            }
            if (!(requested ==~ /[0-9a-fA-F]{40}/)) {
                error('COMMIT_SHA precisa conter o SHA completo de 40 caracteres.')
            }
            withEnv(["REQUESTED_COMMIT=${requested}"]) {
                sh 'git checkout --detach "$REQUESTED_COMMIT"'
            }
            env.RELEASE_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
            for (value in [params.RAILWAY_PROJECT_ID, params.RAILWAY_SERVICE, params.RAILWAY_ENVIRONMENT, params.PUBLIC_URL]) {
                if (!value.trim()) { error('Preencha projeto, serviço, ambiente Railway e PUBLIC_URL.') }
            }
            if (!(params.PUBLIC_URL ==~ /https:\/\/[a-zA-Z0-9.-]+\/?/)) {
                error('PUBLIC_URL precisa ser um domínio HTTPS, sem caminho ou credenciais.')
            }
            sh 'command -v railway; command -v python3; railway --version'
        }
        stage('Frontend/Cypress - Mateus') {
            // Diretório temporário fora do workspace: banco, PID e log do Flask de teste.
            withEnv(["E2E_DIR=${pwd(tmp: true)}/e2e"]) {
                try {
                    timeout(time: 15, unit: 'MINUTES') {
                        sh '''#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    status=$?
    if [ -f "$E2E_DIR/flask.pid" ]; then
        kill "$(cat "$E2E_DIR/flask.pid")" 2>/dev/null || true
    fi
    if [ "$status" -ne 0 ] && [ -f "$E2E_DIR/flask.log" ]; then
        echo '--- log do Flask de teste ---'
        tail -n 50 "$E2E_DIR/flask.log" || true
    fi
    exit "$status"
}
trap cleanup EXIT

test "$(git rev-parse HEAD)" = "$RELEASE_COMMIT"
rm -rf "$E2E_DIR"
mkdir -p "$E2E_DIR" frontend/reports/frontend

# 1) Flask com banco isolado (arquivo novo a cada build, fora do workspace).
python3 -m venv .venv
.venv/bin/pip install --no-cache-dir -r backend/requirements.txt
PORT="$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
export DATABASE_PATH="$E2E_DIR/jogo-e2e.db"
( cd backend && exec ../.venv/bin/gunicorn --workers 1 --threads 4 --bind "127.0.0.1:$PORT" app:app > "$E2E_DIR/flask.log" 2>&1 ) &
echo $! > "$E2E_DIR/flask.pid"

# 2) Aguarda prontidão: /health (banco) e a interface estática.
python3 - "$PORT" <<'PY'
import json
import sys
import time
from urllib.request import urlopen

base = f'http://127.0.0.1:{sys.argv[1]}'
for attempt in range(30):
    try:
        with urlopen(base + '/health', timeout=3) as response:
            ok = response.status == 200 and json.load(response) == {'status': 'ok'}
        with urlopen(base + '/static/index.html', timeout=3) as response:
            ok = ok and response.status == 200 and b'id="form-iniciar"' in response.read()
        if ok:
            print('Flask pronto: banco e interface disponíveis.')
            raise SystemExit(0)
    except OSError:
        pass
    time.sleep(1)
raise SystemExit('Flask de teste não ficou pronto em 30 s.')
PY

# 3) Testes de frontend: unitários com cobertura + Cypress (mock e API real) contra o Flask.
cd frontend
npm ci
npx cypress install
npx cypress verify
npm run test:unit:ci
export CYPRESS_BASE_URL="http://127.0.0.1:$PORT"
npm run e2e:ci
'''
                    }
                    // Só chega aqui se tudo passou: libera o deploy para este SHA.
                    env.TESTS_APPROVED_COMMIT = env.RELEASE_COMMIT
                } finally {
                    sh '''#!/usr/bin/env bash
# Garantia extra de encerramento caso o stage tenha sido abortado antes do trap.
if [ -f "$E2E_DIR/flask.pid" ]; then kill "$(cat "$E2E_DIR/flask.pid")" 2>/dev/null || true; fi
rm -rf "$E2E_DIR"
exit 0
'''
                    archiveArtifacts artifacts: 'frontend/reports/**', allowEmptyArchive: true, fingerprint: true
                }
            }
        }
        stage('Deploy - Fernando') {
            if (currentBuild.currentResult != 'SUCCESS' || env.TESTS_APPROVED_COMMIT != env.RELEASE_COMMIT) {
                error("Deploy bloqueado: testes não aprovados para o SHA ${env.RELEASE_COMMIT}.")
            }
            echo "Deploy autorizado: SHA ${env.RELEASE_COMMIT} aprovado em Frontend/Cypress."
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
