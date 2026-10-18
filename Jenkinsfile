// CI/CD Jenkins: main é consultada a cada 2 minutos; alterações aprovadas passam por todos os testes antes do deploy.
def automatic = !currentBuild.getBuildCauses('hudson.triggers.SCMTrigger$SCMTriggerCause').isEmpty()
// O mesmo SHA é testado e publicado; qualquer falha antes do Deploy bloqueia a publicação.
properties([
    disableConcurrentBuilds(),
    pipelineTriggers([pollSCM('H/2 * * * *')]),
    parameters([
        string(name: 'COMMIT_SHA', defaultValue: '', description: 'SHA completo (40 caracteres) a testar e publicar. Vazio = ponta atual da main, resolvida uma única vez.'),
        booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Execução manual: publicar após os testes. Execuções automáticas da main publicam quando tudo passa.'),
        string(name: 'RAILWAY_PROJECT_ID', defaultValue: '67641175-19f1-4597-a518-3ddea95e22fa', description: 'ID do projeto Railway.'),
        string(name: 'RAILWAY_SERVICE', defaultValue: 'EntreLinhas', description: 'Nome ou ID do serviço Railway.'),
        string(name: 'RAILWAY_ENVIRONMENT', defaultValue: 'production', description: 'Ambiente Railway.'),
        string(name: 'PUBLIC_URL', defaultValue: 'https://entrelinhas-production-7e6e.up.railway.app', description: 'Domínio HTTPS da aplicação, sem caminho.')
    ])
])

def publish = automatic || params.DEPLOY

timeout(time: 30, unit: 'MINUTES') {
    node('built-in') {
        stage('Preparar commit') {
            deleteDir()
            git branch: 'main', url: 'https://github.com/C14-Inatel-2026-2/EntreLinhas.git'
            env.DOMAIN_APPROVED_COMMIT = ''
            env.BACKEND_APPROVED_COMMIT = ''
            env.TESTS_APPROVED_COMMIT = ''
            // Polling sempre usa a main atual, ignorando parâmetros de builds manuais anteriores.
            def requested = automatic ? '' : (params.COMMIT_SHA ?: '').trim()
            echo(automatic ? 'Acionamento automático: nova revisão da main.' : 'Acionamento manual.')
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
            if (publish) {
                for (value in [params.RAILWAY_PROJECT_ID, params.RAILWAY_SERVICE, params.RAILWAY_ENVIRONMENT, params.PUBLIC_URL]) {
                    if (!value.trim()) { error('Preencha projeto, serviço, ambiente Railway e PUBLIC_URL.') }
                }
                if (!(params.PUBLIC_URL ==~ /https:\/\/[a-zA-Z0-9.-]+\/?/)) {
                    error('PUBLIC_URL precisa ser um domínio HTTPS, sem caminho ou credenciais.')
                }
            }
            sh 'command -v python3; node --version; npm --version'
            if (publish) { sh 'railway --version' }
        }
        stage('Build') {
            sh '''
                set -eu
                python3 -m venv .venv
                .venv/bin/python -m pip install -r backend/requirements.txt
                mkdir -p reports/backend frontend/reports/frontend
                cd frontend
                npm ci
                npx cypress install
                npx cypress verify
            '''
        }
        stage('Testes de jogo e baralho - Caio') {
            try {
                dir('backend') {
                    sh '''
                        ../.venv/bin/python -m pytest tests/test_jogo.py tests/test_baralho.py \
                            --junitxml=../reports/domain/junit.xml --cov=src.jogo --cov=src.Baralho \
                            --cov-report=term-missing --cov-report=xml:../reports/domain/coverage.xml \
                            --cov-report=html:../reports/domain/htmlcov
                    '''
                }
                env.DOMAIN_APPROVED_COMMIT = env.RELEASE_COMMIT
            } finally {
                junit testResults: 'reports/domain/junit.xml', allowEmptyResults: true
                archiveArtifacts artifacts: 'reports/domain/**', allowEmptyArchive: true
            }
        }
        stage('Backend e cobertura - Henrique') {
            withEnv(["DATABASE_PATH=${pwd(tmp: true)}/backend-tests.db"]) {
                try {
                    sh '.venv/bin/python -m unittest discover -s scripts/ci/tests -v > reports/backend/ci-guards.txt 2>&1'
                    dir('backend') {
                        sh '''
                            ../.venv/bin/python -m pytest tests/ --ignore=tests/test_jogo.py --ignore=tests/test_baralho.py --cov-append --junitxml=../reports/backend/junit.xml \
                                --cov=app --cov=db --cov=jogo --cov=src --cov-report=term-missing \
                                --cov-report=xml:../reports/backend/coverage.xml \
                                --cov-report=html:../reports/backend/htmlcov
                        '''
                    }
                    env.BACKEND_APPROVED_COMMIT = env.RELEASE_COMMIT
                } finally {
                    sh 'rm -f "$DATABASE_PATH" "$DATABASE_PATH-journal" "$DATABASE_PATH-wal" "$DATABASE_PATH-shm"'
                    junit testResults: 'reports/backend/junit.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'reports/backend/**', allowEmptyArchive: true
                }
            }
        }
        stage('Frontend/Cypress - Mateus') {
            try {
                timeout(time: 15, unit: 'MINUTES') {
                    withEnv(['CYPRESS_BROWSER=chromium']) {
                        sh '.venv/bin/python scripts/ci/frontend.py'
                    }
                }
                env.TESTS_APPROVED_COMMIT = env.RELEASE_COMMIT
            } finally {
                archiveArtifacts artifacts: 'frontend/reports/**', allowEmptyArchive: true
            }
        }
        stage('Deploy - Fernando') {
            if (currentBuild.currentResult != 'SUCCESS' || env.DOMAIN_APPROVED_COMMIT != env.RELEASE_COMMIT || env.BACKEND_APPROVED_COMMIT != env.RELEASE_COMMIT || env.TESTS_APPROVED_COMMIT != env.RELEASE_COMMIT) {
                error("Deploy bloqueado: testes não aprovados para o SHA ${env.RELEASE_COMMIT}.")
            }
            if (!publish) {
                echo "CI aprovada para ${env.RELEASE_COMMIT}. DEPLOY desmarcado: nenhuma publicação."
                return
            }
            echo "Deploy autorizado: SHA ${env.RELEASE_COMMIT} aprovado em domínio, backend e frontend/Cypress."
            withCredentials([string(credentialsId: 'railway-project-token', variable: 'RAILWAY_TOKEN')]) {
                withEnv([
                    "RAILWAY_PROJECT_ID=${params.RAILWAY_PROJECT_ID}",
                    "RAILWAY_SERVICE=${params.RAILWAY_SERVICE}",
                    "RAILWAY_ENVIRONMENT=${params.RAILWAY_ENVIRONMENT}",
                    "PUBLIC_URL=${params.PUBLIC_URL}"
                ]) {
                    sh '.venv/bin/python scripts/ci/deploy.py'
                }
            }
        }
    }
}
