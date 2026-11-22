#!/bin/bash
# start.sh — Start the AML Transaction Monitoring application
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# === Helper Functions ===

# Portable path conversion for Windows programs under Git Bash
native_path() {
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$1"
    else
        printf '%s' "$1"
    fi
}

# Port detection (lsof on macOS/Linux, netstat under Git Bash on Windows)
port_in_use() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -iTCP:"$1" -sTCP:LISTEN -t >/dev/null 2>&1
    else
        netstat -an 2>/dev/null | grep -Eq "[:.]$1[[:space:]].*LISTEN"
    fi
}

find_available_port() {
    local port=$1
    while port_in_use "$port"; do
        echo "Port $port in use, trying $((port+1))..." >&2
        port=$((port+1))
    done
    echo $port
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    # Python 3.11+ — probe by running it (python3 may be the Windows Store stub)
    PYTHON=""
    for c in python3 python; do
        if "$c" -c 'import sys' >/dev/null 2>&1; then
            PYTHON=$c
            break
        fi
    done

    if [ -n "$PYTHON" ]; then
        PYTHON_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
            echo "❌ Python 3.11+ required (found $PYTHON_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Python $PYTHON_VERSION"
        fi
    else
        echo "❌ Python 3 not found. Install from https://python.org"
        errors=$((errors+1))
    fi

    # Node.js 20.19+/22.12+
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
        NODE_MINOR=$(echo "$NODE_VERSION" | cut -d. -f2)
        
        if [ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]; then
            echo "❌ Node.js 20.19+ or 22.12+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        elif [ "$NODE_MAJOR" -eq 21 ]; then
            echo "❌ Node.js 20.19+ or 22.12+ required (found $NODE_VERSION; Node 21 is not supported)"
            errors=$((errors+1))
        elif [ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -lt 12 ]; then
            echo "❌ Node.js 22.12+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        elif [ "$NODE_MAJOR" -lt 20 ]; then
            echo "❌ Node.js 20.19+ or 22.12+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Node.js $NODE_VERSION"
        fi
    else
        echo "❌ Node.js not found. Install from https://nodejs.org"
        errors=$((errors+1))
    fi

    # npm
    if ! command -v npm &>/dev/null; then
        echo "❌ npm not found"
        errors=$((errors+1))
    else
        echo "✓ npm $(npm --version)"
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

# === Stop previous run ===
echo "=== Stopping any previous run ==="
if [ -f .pids ]; then
    while IFS= read -r pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && echo "  Stopped PID $pid" || true
        fi
    done < .pids
    rm -f .pids
    echo "  Previous services stopped"
else
    echo "  No previous run detected"
fi
echo ""

check_prerequisites

# === Backend Setup ===
echo "=== Setting up backend ==="
cd backend

# Create .venv if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi

# Activate venv (Windows venvs have Scripts/, macOS/Linux venvs have bin/)
if [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Copy dev.env to .env if .env doesn't exist
if [ ! -f .env ]; then
    if [ -f dev.env ]; then
        cp dev.env .env
        echo "  Created .env from dev.env"
    fi
fi

# Install dependencies
echo "Installing backend dependencies..."
pip install . -q

# Database setup
DB_PATH="$SCRIPT_DIR/backend/app.db"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$(native_path "$DB_PATH")}"
echo "  Database: $DATABASE_URL"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Run seed data
echo "Seeding database..."
python -m app.seed

cd "$SCRIPT_DIR"

# === Find available ports ===
BACKEND_PORT=$(find_available_port 9000)
FRONTEND_PORT=$(find_available_port 5173)

# === Update CORS origins in backend .env ===
if [ -f backend/.env ]; then
    # Portable sed wrapper
    portable_sed() {
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "$@"
        else
            sed -i "$@"
        fi
    }
    
    # Update CORS_ORIGINS to include the chosen frontend port
    portable_sed "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:$FRONTEND_PORT|" backend/.env
fi

# === Start backend ===
echo ""
echo "=== Starting backend on http://localhost:$BACKEND_PORT ==="
cd backend
uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# === Frontend Setup ===
echo ""
echo "=== Setting up frontend ==="
cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# === Start frontend ===
echo ""
echo "=== Starting frontend on http://localhost:$FRONTEND_PORT ==="
# The Vite proxy reads BACKEND_PORT from the environment
BACKEND_PORT="$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# === Save PIDs ===
echo "$BACKEND_PID" > .pids
echo "$FRONTEND_PID" >> .pids

# === Print URLs and credentials ===
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ AML Transaction Monitoring is running"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend:  http://localhost:$FRONTEND_PORT"
echo "  Backend:   http://localhost:$BACKEND_PORT"
echo "  API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Default Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Investigator:"
echo "    Username:  riya"
echo "    Password:  password123"
echo ""
echo "  Compliance Officer:"
echo "    Username:  morgan"
echo "    Password:  password123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

wait
