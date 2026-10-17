# Backend

API Flask, persistência SQLite e regras do jogo. As dependências Python ficam em
`requirements.txt`; os testes e a configuração pytest ficam nesta pasta.

Execute a partir de `backend/`:

```sh
python -m pip install -r requirements.txt
python -m flask --app app run --host 127.0.0.1 --port 5000
python -m pytest
python -m src.main
```

O Flask também serve `../frontend/static/` em `/static`, mantendo interface e API
na mesma origem. Abra `http://127.0.0.1:5000/`.
O banco padrão é `jogo.db` no diretório de execução; `DATABASE_PATH` permite
selecionar outro arquivo, inclusive o banco existente na raiz do repositório.

`app.py` contém as rotas, `db.py` a persistência, `jogo.py` o estado da API e
`src/` as classes de domínio. A suíte completa fica em `tests/`.
