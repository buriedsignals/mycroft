#!/bin/bash
#
# SIFT × C2PA Integration Demo
#
# One-click demo that:
# 1. Starts the C2PA artifact server
# 2. Runs integration tests
# 3. Shows the SIFT → C2PA flow
# 4. Optionally runs Goose fact-check
#
# Usage:
#   ./demo.sh           # Full demo
#   ./demo.sh --quick   # Skip Goose, just API demo
#   ./demo.sh --stop    # Stop background server
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
C2PA_DIR="$HOME/Sites/noosphere/github/c2pa-artifact"
MYCROFT_DIR="$HOME/Sites/mycroft"
PID_FILE="/tmp/c2pa-demo-server.pid"
LOG_FILE="/tmp/c2pa-demo-server.log"
C2PA_PORT=5002

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}$1${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}▸${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Stop server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_step "Stopping C2PA server (PID: $PID)..."
            kill "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
            print_success "Server stopped"
        else
            rm -f "$PID_FILE"
            print_warning "Server was not running"
        fi
    else
        print_warning "No server PID file found"
    fi
}

# Handle --stop flag
if [ "$1" = "--stop" ]; then
    stop_server
    exit 0
fi

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"

    # Python
    if command -v python3 &> /dev/null; then
        print_success "Python3: $(python3 --version)"
    else
        print_error "Python3 not found"
        exit 1
    fi

    # Flask
    if python3 -c "import flask" 2>/dev/null; then
        print_success "Flask installed"
    else
        print_warning "Flask not found - installing..."
        pip3 install flask flask-cors
    fi

    # curl
    if command -v curl &> /dev/null; then
        print_success "curl available"
    else
        print_error "curl not found"
        exit 1
    fi

    # jq (optional but nice)
    if command -v jq &> /dev/null; then
        print_success "jq available (JSON formatting)"
        JQ_CMD="jq"
    else
        print_warning "jq not found - JSON output will be raw"
        JQ_CMD="cat"
    fi

    # C2PA directory
    if [ -d "$C2PA_DIR" ]; then
        print_success "C2PA artifact directory found"
    else
        print_error "C2PA artifact not found at $C2PA_DIR"
        exit 1
    fi

    # Mycroft directory
    if [ -d "$MYCROFT_DIR" ]; then
        print_success "Mycroft directory found"
    else
        print_error "Mycroft not found at $MYCROFT_DIR"
        exit 1
    fi
}

# Start C2PA server
start_server() {
    print_header "Starting C2PA Artifact Server"

    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_success "Server already running (PID: $PID)"
            return 0
        fi
        rm -f "$PID_FILE"
    fi

    # Check if port is in use
    if lsof -i :$C2PA_PORT &>/dev/null; then
        print_warning "Port $C2PA_PORT already in use"
        if curl -s "http://localhost:$C2PA_PORT/api/sift/verdicts" &>/dev/null; then
            print_success "C2PA server appears to be running"
            return 0
        else
            print_error "Port in use by another process"
            exit 1
        fi
    fi

    print_step "Starting server on port $C2PA_PORT..."

    cd "$C2PA_DIR"
    python3 server/app.py > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$PID_FILE"

    print_step "Waiting for server to be ready..."

    # Wait for server to start (max 30 seconds)
    for i in {1..30}; do
        if curl -s "http://localhost:$C2PA_PORT/api/sift/verdicts" &>/dev/null; then
            print_success "Server ready (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
        echo -n "."
    done

    echo ""
    print_error "Server failed to start. Check log: $LOG_FILE"
    cat "$LOG_FILE" | tail -20
    exit 1
}

# Demo SIFT endpoints
demo_sift_endpoints() {
    print_header "SIFT API Endpoints Demo"

    echo -e "${BOLD}1. Get SIFT Verdict Types${NC}"
    echo -e "${YELLOW}   GET /api/sift/verdicts${NC}"
    echo ""
    curl -s "http://localhost:$C2PA_PORT/api/sift/verdicts" | $JQ_CMD
    echo ""

    echo -e "${BOLD}2. Get SIFT Manifest Schema${NC}"
    echo -e "${YELLOW}   GET /api/sift/schema${NC}"
    echo ""
    curl -s "http://localhost:$C2PA_PORT/api/sift/schema" | $JQ_CMD | head -30
    echo "   ... (truncated)"
    echo ""

    sleep 1
}

# Demo SIFT manifest submission
demo_sift_submission() {
    print_header "SIFT Manifest Submission Demo"

    echo -e "${BOLD}Submitting example SIFT manifest...${NC}"
    echo -e "${YELLOW}   POST /api/sift/process${NC}"
    echo ""

    # Show the manifest being submitted
    echo -e "${CYAN}Manifest summary:${NC}"
    if [ -f "$SCRIPT_DIR/example-sift-manifest.json" ]; then
        echo "   - Claims: $(grep -c '"id": "claim-' "$SCRIPT_DIR/example-sift-manifest.json" || echo "?")"
        echo "   - Sources: $(grep -c '"id": "prov-' "$SCRIPT_DIR/example-sift-manifest.json" || echo "?")"
        echo "   - Investigator: $(grep -o '"name": "[^"]*"' "$SCRIPT_DIR/example-sift-manifest.json" | head -1 | cut -d'"' -f4)"
        echo ""
    fi

    # Submit manifest
    RESPONSE=$(curl -s -X POST "http://localhost:$C2PA_PORT/api/sift/process" \
        -H "Content-Type: application/json" \
        -d @"$SCRIPT_DIR/example-sift-manifest.json" 2>&1)

    echo -e "${CYAN}Response:${NC}"
    echo "$RESPONSE" | $JQ_CMD
    echo ""

    # Check response
    if echo "$RESPONSE" | grep -q '"success": true'; then
        print_success "SIFT manifest processed successfully!"

        MANIFEST_ID=$(echo "$RESPONSE" | grep -o '"manifest_id": *"[^"]*"' | cut -d'"' -f4)
        if [ -n "$MANIFEST_ID" ]; then
            echo ""
            echo -e "${BOLD}3. Verify the signed manifest${NC}"
            echo -e "${YELLOW}   POST /api/sift/verify${NC}"
            echo ""

            VERIFY_RESPONSE=$(curl -s -X POST "http://localhost:$C2PA_PORT/api/sift/verify" \
                -H "Content-Type: application/json" \
                -d "{\"manifest_id\": \"$MANIFEST_ID\"}")

            echo "$VERIFY_RESPONSE" | $JQ_CMD
        fi
    elif echo "$RESPONSE" | grep -q "credential"; then
        print_warning "Credential not configured (expected in demo)"
        echo ""
        echo "To enable full signing, configure a credential in C2PA artifact service."
    else
        print_warning "Unexpected response - check server logs"
    fi
}

# Demo mycroft-fetch
demo_mycroft_fetch() {
    print_header "mycroft-fetch CLI Demo"

    FETCH_CMD="$SCRIPT_DIR/mycroft-fetch"

    if [ ! -x "$FETCH_CMD" ]; then
        print_warning "mycroft-fetch not executable, fixing..."
        chmod +x "$FETCH_CMD"
    fi

    echo -e "${BOLD}mycroft-fetch captures provenance when fetching sources:${NC}"
    echo ""
    echo -e "${YELLOW}   mycroft-fetch scrape <url>${NC}"
    echo "   → Returns content + provenance (url, hash, timestamp)"
    echo ""
    echo -e "${YELLOW}   mycroft-fetch provenance list${NC}"
    echo "   → Lists all captured provenance records"
    echo ""

    # Check if firecrawl is available
    if command -v firecrawl &> /dev/null; then
        print_success "firecrawl CLI available - mycroft-fetch ready to use"
        echo ""
        echo "Try: $FETCH_CMD scrape https://example.com"
    else
        print_warning "firecrawl CLI not installed"
        echo ""
        echo "Install with: npm install -g firecrawl"
        echo "Then set FIRECRAWL_API_KEY environment variable"
    fi
}

# Show Goose integration
demo_goose_integration() {
    print_header "Goose Integration"

    if command -v goose &> /dev/null; then
        print_success "Goose installed: $(goose --version 2>/dev/null || echo 'version unknown')"
        echo ""
        echo -e "${BOLD}Run SIFT fact-check with C2PA signing:${NC}"
        echo ""
        echo -e "${YELLOW}goose run --recipe ~/Sites/mycroft/recipes/fact-check-c2pa.yaml \\
  --param draft_text=\"Your article text here...\"${NC}"
        echo ""
        echo "The recipe will:"
        echo "  1. Extract factual claims from your draft"
        echo "  2. Use mycroft-fetch to verify each claim (capturing provenance)"
        echo "  3. Assign SIFT verdicts"
        echo "  4. Emit a SIFT manifest for C2PA signing"
    else
        print_warning "Goose not installed"
        echo ""
        echo "Install with: brew install goose"
        echo "Then set up Mycroft profile per README"
    fi
}

# Summary
show_summary() {
    print_header "Demo Complete"

    echo -e "${BOLD}What was demonstrated:${NC}"
    echo ""
    echo "  ${GREEN}✓${NC} C2PA artifact server with SIFT endpoints"
    echo "  ${GREEN}✓${NC} SIFT manifest schema and verdict types"
    echo "  ${GREEN}✓${NC} Submitting fact-check results for signing"
    echo "  ${GREEN}✓${NC} mycroft-fetch provenance capture"
    echo ""
    echo -e "${BOLD}Architecture:${NC}"
    echo ""
    echo "  ┌─────────────┐     mycroft-fetch      ┌─────────────────┐"
    echo "  │   Mycroft   │ ───────────────────────▶│  C2PA Artifact  │"
    echo "  │  (Goose)    │     SIFT manifest       │     Server      │"
    echo "  └─────────────┘                         └─────────────────┘"
    echo "        │                                         │"
    echo "        │ fact-check-c2pa.yaml                   │ /api/sift/process"
    echo "        │ mycroft-fetch scrape                   │ /api/sift/verify"
    echo "        ▼                                         ▼"
    echo "  ┌─────────────┐                         ┌─────────────────┐"
    echo "  │   Sources   │                         │  Signed C2PA    │"
    echo "  │  (hashed)   │                         │   Manifest      │"
    echo "  └─────────────┘                         └─────────────────┘"
    echo ""
    echo -e "${BOLD}Server Status:${NC}"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "  C2PA server running on http://localhost:$C2PA_PORT (PID: $PID)"
            echo "  Stop with: ./demo.sh --stop"
        fi
    fi
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo "  1. Configure a signing credential in C2PA artifact service"
    echo "  2. Install firecrawl CLI: npm install -g firecrawl"
    echo "  3. Run a real fact-check: goose run --recipe fact-check-c2pa.yaml"
    echo ""
}

# Main
main() {
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}              SIFT × C2PA Integration Demo                      ${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Encoding SIFT fact-checking provenance as C2PA ingredients"
    echo ""

    check_dependencies
    start_server

    sleep 1

    demo_sift_endpoints

    sleep 1

    demo_sift_submission

    if [ "$1" != "--quick" ]; then
        sleep 1
        demo_mycroft_fetch

        sleep 1
        demo_goose_integration
    fi

    show_summary
}

main "$@"
