// Job de Fernando: publica o commit recebido do pipeline após Build e Testes.
pipeline {
    agent { label 'linux' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }
    parameters {
        string(name: 'COMMIT_SHA', defaultValue: '', description: 'SHA completo aprovado nas etapas anteriores de Build e Testes.')
        string(name: 'RAILWAY_PROJECT_ID', defaultValue: '', description: 'ID do projeto Railway.')
        string(name: 'RAILWAY_SERVICE', defaultValue: 'EntreLinhas', description: 'Nome ou ID do serviço Railway.')
        string(name: 'RAILWAY_ENVIRONMENT', defaultValue: 'production', description: 'Ambiente Railway.')
        string(name: 'PUBLIC_URL', defaultValue: '', description: 'Domínio HTTPS da aplicação, sem caminho.')
    }
    stages {
        stage('Preparar commit') {
            steps {
                deleteDir()
                checkout scm
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
                        sh 'bash scripts/deploy-railway.sh'
                    }
                }
            }
        }
    }
}
