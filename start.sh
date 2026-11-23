#!/bin/bash
# start.sh — Start the AML Transaction Monitoring & Compliance Workbench
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Portable sed (macOS + Linux)
portable_sed() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
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

# Utility for native Windows paths under Git Bash
native_path() { 
    if command -v cygpath >/dev/null 2>&1; then 
        cygpath -m "$1"
    else 
        printf '%s' "$1"
    fi
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    # Probe by running it: under Git Bash `python3` may be the Windows Store stub.
    PYTHON=""
    for c in python3 python; do
        if "$c" -c 'import sys' >/dev/null 2>&1; then PYTHON=$c; break; fi
    done
    if [ -n "$PYTHON" ]; then
        PYTHON_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
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

    # Node.js 20.19+ (required by Vite)
    if [ -f "frontend/package.json" ]; then
        if command -v node &>/dev/null; then
            NODE_VERSION=$(node --version | sed 's/v//')
            NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
            NODE_MINOR=$(echo $NODE_VERSION | cut -d. -f2)
            if [ "$NODE_MAJOR" -lt 20 ] || ([ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]); then
                echo "❌ Node.js 20.19+ required (found $NODE_VERSION)"
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
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

check_prerequisites

# === Backend Setup ===
BACKEND_DIR="backend"
echo "=== Setting up backend ==="
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi

# Windows venvs (Git Bash) have Scripts/, macOS/Linux venvs have bin/.
if [ -f .venv/Scripts/activate ]; then 
    source .venv/Scripts/activate
else 
    source .venv/bin/activate
fi

echo "Installing backend dependencies..."
pip install --quiet . || { echo "❌ Backend dependency installation failed"; exit 1; }

# Load environment from dev.env if .env doesn't exist
if [ ! -f ".env" ]; then
    if [ -f "dev.env" ]; then
        echo "Copying dev.env to .env..."
        cp dev.env .env
    fi
fi

# Database — default to SQLite with absolute path
DB_PATH="$SCRIPT_DIR/backend/app.db"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$(native_path "$DB_PATH")}"
echo "  Database: $DATABASE_URL"

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head || { echo "❌ Database migration failed"; exit 1; }

# Run seed script
if [ -f "app/seed.py" ]; then
    echo "Seeding database..."
    python app/seed.py 2>/dev/null || true
fi

# Find available backend port
BACKEND_PORT=$(find_available_port 9000)
echo "Starting backend on http://localhost:$BACKEND_PORT"

# Start backend in background
python -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# === Frontend Setup ===
FE_DIR="frontend"
FRONTEND_PORT=""

if [ -d "$FE_DIR" ] && [ -f "$FE_DIR/package.json" ]; then
    echo ""
    echo "=== Setting up frontend ==="
    cd "$FE_DIR"
    
    echo "Installing frontend dependencies..."
    npm install --quiet || { echo "❌ Frontend dependency installation failed"; kill "$BACKEND_PID" 2>/dev/null; exit 1; }

    FRONTEND_PORT=$(find_available_port 5173)

    # The browser calls a relative /api; vite.config.ts proxies it to BACKEND_PORT.
    echo "Starting frontend on http://localhost:$FRONTEND_PORT"
    BACKEND_PORT="$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
    FE_PID=$!
    cd "$SCRIPT_DIR"
fi

# Save PIDs
echo "$BACKEND_PID" > .pids
[ -n "$FE_PID" ] && echo "$FE_PID" >> .pids

echo ""
echo "========================================="
echo " AML Workbench - Services Running"
echo "========================================="
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  API Docs: http://localhost:$BACKEND_PORT/api/v1/docs"
echo "  Health:   http://localhost:$BACKEND_PORT/health"
[ -n "$FRONTEND_PORT" ] && echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "=== Default Credentials ==="
echo "  Investigator: investigator@example.com / investigator123"
echo "  Officer:      officer@example.com / officer123"
echo "  Auditor:      auditor@example.com / auditor123"
echo "  Supervisor:   supervisor@example.com / supervisor123"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================="
echo ""

wait
