# Quiz didático

Aplicação de quiz com ranking de jogadores.

- **Frontend:** React + TypeScript (Vite)
- **Backend:** Django + Django REST Framework (Python, gerenciado com Poetry)
- **Banco de dados:** MySQL ou MariaDB (padrão) ou PostgreSQL

Autor: Daltro Oliveira Vinuto

Versões em produção:

- Frontend: https://quiz-4pzo2761m-daltro-oliveira-vinuto-s-projects.vercel.app/
- Backend: https://quiz-lz8r.onrender.com

---

## Estrutura

```
quiz/
├── backend/                 # API Django
│   ├── config/              # settings, urls, asgi/wsgi
│   ├── quiz/                # app principal (modelos, views, testes)
│   ├── api/
│   ├── .env.example         # modelo das variáveis do backend
│   └── pyproject.toml       # dependências (Poetry)
├── frontend/                # app React
│   ├── src/
│   ├── public/              # arquivos estáticos (inclui o .htaccess)
│   ├── .htaccess            # proteção caso a pasta frontend/ inteira fique exposta
│   ├── .env.example         # modelo das variáveis do frontend
│   └── package.json
└── .github/workflows/       # testes automáticos em MySQL, MariaDB e PostgreSQL
```

---

## Pré-requisitos

| Ferramenta | Versão | Para quê |
|---|---|---|
| Python | 3.12 ou mais novo | backend |
| Poetry | 2.x | instalar as dependências do backend |
| Node.js | 22 LTS ou mais novo (mínimo 20.19) | frontend |
| MySQL 8.0+ ou MariaDB 10.6+ | — | banco padrão |
| PostgreSQL 14+ | — | só se for usar `DB_ENGINE=postgres` |

Instalando o Poetry (recomendado via pipx):

```bash
pipx install poetry
```

O driver do MySQL (`mysqlclient`) é compilado na instalação e precisa das bibliotecas do cliente MySQL:

- **Ubuntu/Debian:** `sudo apt install pkg-config default-libmysqlclient-dev build-essential python3-dev`
- **macOS:** `brew install mysql-client pkg-config`
- **Windows:** normalmente o pip baixa o pacote já compilado, não precisa de nada extra.

---

## Rodando localmente

### 1. Banco de dados

Crie o banco e um usuário. No MySQL/MariaDB:

```sql
CREATE DATABASE quiz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'quiz'@'localhost' IDENTIFIED BY 'sua_senha';
GRANT ALL PRIVILEGES ON quiz_db.* TO 'quiz'@'localhost';
-- necessário para rodar os testes (o Django cria o banco test_quiz_db)
GRANT ALL PRIVILEGES ON test_quiz_db.* TO 'quiz'@'localhost';
FLUSH PRIVILEGES;
```

No PostgreSQL (opcional):

```sql
CREATE USER quiz WITH PASSWORD 'sua_senha' CREATEDB;
CREATE DATABASE quiz_db OWNER quiz;
```

### 2. Backend

```bash
cd backend
cp .env.example .env          # depois edite o .env (veja a tabela abaixo)
poetry install --no-root      # instala as dependências
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

A API fica em http://localhost:8000/api/ e o painel de administração em http://localhost:8000/admin/ (é por ele que se cadastram quizzes, questões e alternativas).

No `.env` local, o mínimo é preencher `SECRET_KEY`, `DB_USER` e `DB_PASSWORD`. Para gerar uma `SECRET_KEY`:

```bash
poetry run python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

### 3. Frontend

Em outro terminal:

```bash
cd frontend
cp .env.example .env          # os valores padrão já apontam para o backend local
npm install
npm run dev
```

O site abre em http://localhost:5173.

### 4. Testes

```bash
cd backend
poetry run python manage.py test quiz
```

Os testes rodam no banco configurado no `.env`. O usuário do banco precisa poder criar o banco de testes (`test_quiz_db`). A cada push ou pull request, o GitHub Actions roda os mesmos testes em MySQL 8.0, MySQL 8.4, MariaDB 10.11, MariaDB 11.4 e PostgreSQL 16 (`.github/workflows/db-compat.yml`).

---

## Variáveis de ambiente

### Backend (`backend/.env`)

| Variável | Local | Produção (Render) |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | qualquer chave gerada | chave longa e secreta, diferente da local |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | domínio do backend, ex.: `quiz-lz8r.onrender.com` |
| `FRONTEND_URL` | `http://localhost:5173` | URL do site na Vercel |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | URL do site na Vercel (com `https://`) |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5173` | URL do site na Vercel e a do backend |
| `DB_ENGINE` | `mysql` | `mysql` (ou `mariadb` / `postgres`) |
| `DATABASE_URL` | não precisa | URL do banco remoto, ex.: `mysql://usuario:senha@host:3306/quiz_db` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | dados do banco local | só se não usar `DATABASE_URL` |
| `CLOUDINARY_URL` | vazio (imagens ficam em `backend/media/`) | **obrigatório**: `cloudinary://api_key:api_secret@cloud_name` |
| `REDIS_URL` | `redis://127.0.0.1:6379` | URL do Redis do provedor |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | vazios, se não usar login Google | credenciais do Google Cloud |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/api/auth/google/callback/` | `https://<backend>/api/auth/google/callback/` |
| `DJANGO_SUPERUSER_USERNAME`, `_EMAIL`, `_PASSWORD` | não precisa | usados pelo `createsuperuser --noinput` no build |

Observações:

- Quando `DATABASE_URL` existe, ela tem prioridade sobre as variáveis `DB_*`, e o tipo da URL precisa combinar com o `DB_ENGINE` (`mysql://` para MySQL/MariaDB, `postgresql://` para PostgreSQL).
- Com `DEBUG=False` o Django força HTTPS, usa cookies seguros e guarda as imagens no Cloudinary.
- No `.env`, comentários vão sempre na linha de cima da variável. Um `#` no fim da linha vira parte do valor.

### Frontend (`frontend/.env`)

| Variável | Local | Produção (Vercel) |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api` | `https://quiz-lz8r.onrender.com/api` |
| `VITE_BACKEND_URL` | `http://localhost:8000` | `https://quiz-lz8r.onrender.com` |
| `VITE_BACKEND_DOMAIN` | `localhost:8000` | `quiz-lz8r.onrender.com` |
| `VITE_LOGO_URL` | `/logo_da_feb.png` | `/logo_da_feb.png` ou URL de uma imagem (ex.: Cloudinary) |

As variáveis `VITE_` são gravadas no código no momento do build e ficam visíveis no navegador: nunca coloque senhas nelas. Depois de mudar alguma na Vercel, é preciso fazer um novo deploy.

---

## Deploy

### Backend no Render

Crie um **Web Service** apontando para o repositório, com:

- **Root Directory:** `backend`
- **Build Command:**
  ```bash
  pip install poetry && poetry install --no-interaction --no-root && poetry run python manage.py migrate && (poetry run python manage.py createsuperuser --noinput || true) && poetry run python manage.py collectstatic --noinput
  ```
- **Start Command:**
  ```bash
  poetry run daphne -b 0.0.0.0 -p $PORT config.asgi:application
  ```
- **Environment:** as variáveis da coluna "Produção" da tabela do backend, mais `PYTHON_VERSION=3.12.8` (ou outra 3.12+).

O banco MySQL/MariaDB pode ficar em qualquer provedor externo; basta colocar a URL dele em `DATABASE_URL`. Crie o banco com `utf8mb4`.

### Frontend na Vercel

Importe o repositório e configure:

- **Root Directory:** `frontend`
- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment Variables:** as da coluna "Produção" da tabela do frontend.

Depois de publicar o frontend, confira se a URL dele está em `FRONTEND_URL`, `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` do backend.

### Frontend em servidor Apache

Rode `npm run build` e envie o **conteúdo** de `frontend/dist/` para a pasta pública do site. O `dist/.htaccess` (gerado a partir de `frontend/public/.htaccess`):

- desliga a listagem de diretórios (`Options -Indexes`), então pastas como `/assets/` não mostram seus arquivos;
- bloqueia arquivos ocultos (`.env`, `.git`), source maps, configurações e código-fonte;
- manda as demais rotas para o `index.html`.

Se a pasta `frontend/` inteira for enviada ao servidor, o `frontend/.htaccess` faz o site ser servido só a partir de `dist/` e mantém `src/`, `node_modules/` e `.env` inacessíveis. Nos dois casos o Apache precisa de `AllowOverride All` (e dos módulos `rewrite` e `headers`). A Vercel ignora `.htaccess`, e lá não existe listagem de diretórios.

---

## Banco de dados

O schema e as consultas usam apenas o ORM do Django, sem SQL específico de um banco, então as mesmas migrations funcionam em MySQL, MariaDB e PostgreSQL. No MySQL/MariaDB a conexão usa `utf8mb4` (acentos e emojis), `sql_mode` estrito (erro em vez de truncar dados) e isolamento `READ COMMITTED`, o mesmo do PostgreSQL. O ranking é agrupado em Python para não depender da collation do banco.

Para trocar de banco, mude o `DB_ENGINE` (e a URL ou as variáveis `DB_*`) e rode `poetry run python manage.py migrate`.

### Copiando os dados do PostgreSQL para o MySQL

```bash
# 1) com DB_ENGINE=postgres e os dados do Postgres no .env
poetry run python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e admin.logentry -e sessions --indent 2 > dados.json

# 2) com DB_ENGINE=mysql e os dados do MySQL no .env
poetry run python manage.py migrate
poetry run python manage.py loaddata dados.json
```
