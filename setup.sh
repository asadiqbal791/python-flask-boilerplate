#!/usr/bin/env bash
# setup.sh — one-command project setup
# Usage: bash setup.sh

set -e

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERR]${NC}  $1"; exit 1; }

echo ""
echo "  Python Flask Boilerplate — Setup"
echo "  ================================="
echo ""

# ── Python version check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python || error "Python not found. Install Python 3.10+")
PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Found Python $PY_VERSION at $PYTHON"

REQUIRED_MAJOR=3; REQUIRED_MINOR=10
ACTUAL_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
ACTUAL_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
if [[ $ACTUAL_MAJOR -lt $REQUIRED_MAJOR ]] || [[ $ACTUAL_MAJOR -eq $REQUIRED_MAJOR && $ACTUAL_MINOR -lt $REQUIRED_MINOR ]]; then
  error "Python 3.10+ required. Found $PY_VERSION"
fi

# ── Virtual environment ───────────────────────────────────────────────────────
if [[ ! -d ".venv" ]]; then
  info "Creating virtual environment (.venv)..."
  $PYTHON -m venv .venv
  success "Virtual environment created"
else
  warn ".venv already exists — skipping creation"
fi

VENV_PYTHON=".venv/bin/python"
VENV_PIP=".venv/bin/pip"
[[ ! -f "$VENV_PYTHON" ]] && VENV_PYTHON=".venv/Scripts/python"  # Windows
[[ ! -f "$VENV_PIP" ]]    && VENV_PIP=".venv/Scripts/pip"

# ── Install dependencies ──────────────────────────────────────────────────────
info "Installing dependencies..."
$VENV_PIP install --quiet --upgrade pip
$VENV_PIP install --quiet -r requirements.txt
success "Dependencies installed"

# ── .env file ─────────────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
  info "Creating .env from .env.example..."
  cp .env.example .env

  # Generate random secrets
  SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || $VENV_PYTHON -c "import secrets; print(secrets.token_hex(32))")
  JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || $VENV_PYTHON -c "import secrets; print(secrets.token_hex(32))")

  # Portable sed for macOS and Linux
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
    sed -i '' "s/your-jwt-secret-change-in-production/$JWT_SECRET/" .env
  else
    sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-change-in-production/$JWT_SECRET/" .env
  fi
  success ".env created with auto-generated secrets"
else
  warn ".env already exists — skipping"
fi

# ── Ask: SQL or MongoDB? ──────────────────────────────────────────────────────
echo ""
echo "  Which database do you want to use?"
echo "  [1] PostgreSQL (default, recommended)"
echo "  [2] MySQL"
echo "  [3] SQLite  (no setup needed, great for local dev)"
echo "  [4] MongoDB"
echo ""
read -rp "  Choice [1-4, default=1]: " DB_CHOICE
DB_CHOICE=${DB_CHOICE:-1}

case $DB_CHOICE in
  2)
    DB_ENGINE="mysql"
    read -rp "  MySQL URL [mysql+pymysql://root:password@localhost:3306/flask_db]: " DB_URL
    DB_URL=${DB_URL:-"mysql+pymysql://root:password@localhost:3306/flask_db"}
    ;;
  3)
    DB_ENGINE="sqlite"
    DB_URL="sqlite:///flask_dev.db"
    warn "SQLite selected — great for local dev, not recommended for production"
    ;;
  4)
    DB_ENGINE="mongodb"
    read -rp "  MongoDB URI [mongodb://localhost:27017/flask_db]: " MONGO_URI
    MONGO_URI=${MONGO_URI:-"mongodb://localhost:27017/flask_db"}
    ;;
  *)
    DB_ENGINE="postgresql"
    read -rp "  Postgres URL [postgresql://postgres:postgres@localhost:5432/flask_db]: " DB_URL
    DB_URL=${DB_URL:-"postgresql://postgres:postgres@localhost:5432/flask_db"}
    ;;
esac

# Write DB config to .env
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_I="sed -i ''"
else
  SED_I="sed -i"
fi

if [[ "$DB_ENGINE" == "mongodb" ]]; then
  $SED_I "s|MONGO_ENABLED=false|MONGO_ENABLED=true|" .env
  $SED_I "s|MONGODB_URI=.*|MONGODB_URI=$MONGO_URI|" .env
  success "MongoDB configured"
else
  $SED_I "s|DATABASE_URL=.*|DATABASE_URL=$DB_URL|" .env 2>/dev/null || \
    echo "DATABASE_URL=$DB_URL" >> .env
  success "$DB_ENGINE configured"
fi

# ── Run migrations (SQL only) ─────────────────────────────────────────────────
if [[ "$DB_ENGINE" != "mongodb" ]]; then
  info "Running database migrations..."
  FLASK_ENV=development .venv/bin/flask db upgrade 2>/dev/null && \
    success "Migrations applied" || \
    warn "Migration failed — is your database running? Run 'flask db upgrade' manually after starting DB"
fi

# ── Seed (optional) ───────────────────────────────────────────────────────────
echo ""
read -rp "  Seed database with sample users? [y/N]: " DO_SEED
if [[ "$DO_SEED" =~ ^[Yy]$ ]]; then
  FLASK_ENV=development .venv/bin/flask seed && success "Database seeded"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}  Setup complete!${NC}"
echo ""
echo "  Start the server:"
echo "    source .venv/bin/activate"
echo "    flask run         # development"
echo "    python run.py     # development (alternative)"
echo ""
echo "  Useful commands:"
echo "    flask db-status       show active database"
echo "    flask seed            seed sample data"
echo "    flask seed --fresh    drop + reseed"
echo "    flask create-admin    create admin user"
echo "    flask routes          list all routes"
echo "    flask shell           Python REPL with models pre-loaded"
echo ""
echo "  Swagger docs:  http://localhost:5000/docs/"
echo "  Health check:  http://localhost:5000/health"
echo ""
