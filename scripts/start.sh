#!/usr/bin/env bash
# ============================================================
# start.sh — Inicializa e executa o projeto Entre Linhas
# ============================================================
# Uso:  ./start.sh [--install]
#
# Sem argumentos : ativa o venv e inicia o servidor web.
# --install      : cria o venv (se necessário), instala todas
#                  as dependências e inicializa o banco de dados
#                  antes de iniciar o servidor.
# ============================================================

set -euo pipefail

# ── Cores para o terminal ────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

# ── Diretório raiz do projeto ────────────────────────────────
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR=".venv"
PORT=8000

# ── Funções utilitárias ──────────────────────────────────────
info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $*"; }
fail()    { echo -e "${RED}[ERRO]${NC}  $*"; exit 1; }

# ── Verificar pré-requisitos ─────────────────────────────────
check_prerequisites() {
    command -v python3 >/dev/null 2>&1 || fail "python3 não encontrado. Instale Python 3.9+."
    command -v node    >/dev/null 2>&1 || fail "node não encontrado. Instale Node.js 22/24/26+."
    command -v npm     >/dev/null 2>&1 || fail "npm não encontrado. Instale Node.js 22/24/26+."
}

# ── Criar / ativar virtualenv ────────────────────────────────
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        info "Criando virtualenv em $VENV_DIR ..."
        python3 -m venv "$VENV_DIR"
        success "Virtualenv criado."
    fi
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    success "Virtualenv ativado ($(python3 --version))."
}

# ── Instalar dependências ────────────────────────────────────
install_deps() {
    info "Instalando dependências Python ..."
    python3 -m pip install --quiet --upgrade pip
    python3 -m pip install --quiet -r requirements.txt
    success "Dependências Python instaladas."

    info "Instalando dependências Node.js ..."
    npm ci --silent
    success "Dependências Node.js instaladas."
}

# ── Inicializar banco de dados ───────────────────────────────
init_db() {
    info "Inicializando banco de dados SQLite ..."
    python3 -c "
from db import conectar_bd, criar_tabelas
conn = conectar_bd()
criar_tabelas(conn)
conn.close()
print('Banco de dados pronto.')
"
    success "Banco de dados inicializado."
}

# ── Iniciar o servidor web ───────────────────────────────────
start_server() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   🎴  Entre Linhas — Servidor iniciado!     ║${NC}"
    echo -e "${GREEN}║   Acesse: http://127.0.0.1:${PORT}              ║${NC}"
    echo -e "${GREEN}║   Pressione Ctrl+C para encerrar.            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    python3 -m http.server "$PORT" --bind 127.0.0.1 --directory static
}

# ── Fluxo principal ──────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}🎴 Entre Linhas — Setup & Run${NC}"
    echo ""

    check_prerequisites

    if [[ "${1:-}" == "--install" ]]; then
        setup_venv
        install_deps
        init_db
    else
        if [ ! -d "$VENV_DIR" ]; then
            warn "Virtualenv não encontrado. Executando instalação completa..."
            setup_venv
            install_deps
            init_db
        else
            setup_venv
        fi
    fi

    start_server
}

main "$@"
