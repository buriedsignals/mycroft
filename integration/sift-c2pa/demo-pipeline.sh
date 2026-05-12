#!/bin/bash
#
# SIFT × C2PA Staged Pipeline Demo
#
# Demonstrates the multi-step signature flow:
#   1. Start pipeline (draft capture)
#   2. Add sources (incrementally)
#   3. Verify claims (SIFT verdicts)
#   4. Publish (final signature)
#
# Each stage creates a new claim that references the previous one,
# building a cryptographic provenance chain.
#

set -e

C2PA_SERVER="${C2PA_SERVER:-http://localhost:5002}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_stage() {
    echo ""
    echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│  STAGE $1: $2${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}▸${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_json() {
    if command -v jq &> /dev/null; then
        echo "$1" | jq .
    else
        echo "$1"
    fi
}

# Check server
echo ""
print_step "Checking C2PA server at $C2PA_SERVER..."
if ! curl -s "$C2PA_SERVER/api/sift/verdicts" > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Server not responding"
    echo "Start with: cd ~/Sites/noosphere/github/c2pa-artifact && python server/app.py"
    exit 1
fi
print_success "Server is running"

print_header "SIFT × C2PA Staged Pipeline Demo"

echo "This demo shows multi-step signatures as an artifact"
echo "progresses through the SIFT fact-checking pipeline."
echo ""
echo "Each stage creates a new claim referencing the previous,"
echo "building an auditable provenance chain."

# ============================================================================
# STAGE 1: DRAFT
# ============================================================================

print_stage "1" "DRAFT CAPTURE"

print_step "Starting new pipeline with draft..."

DRAFT_CONTENT="# Acme Corp Environmental Investigation

According to EPA records, Acme Corp paid \$2.3 million in environmental fines in 2025.
The company's Springfield facility exceeded emissions limits 47 times last year.
CEO John Smith stated the company has 'zero tolerance' for environmental violations."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/start" \
    -H "Content-Type: application/json" \
    -d "{
        \"draft_content\": \"$DRAFT_CONTENT\",
        \"title\": \"Acme Corp Environmental Investigation\",
        \"credential_id\": \"default\",
        \"investigator\": {
            \"name\": \"Jane Reporter\",
            \"organization\": \"Independent News Collective\",
            \"did\": \"did:web:mycroft.buriedsignals.com:users:jane\"
        }
    }")

print_json "$RESPONSE"

# Extract pipeline ID
PIPELINE_ID=$(echo "$RESPONSE" | grep -o '"pipeline_id":"[^"]*"' | cut -d'"' -f4)
CLAIM_1=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$PIPELINE_ID" ]; then
    echo -e "${RED}Failed to start pipeline${NC}"
    exit 1
fi

print_success "Pipeline started: $PIPELINE_ID"
print_success "Draft claim: $CLAIM_1"

sleep 1

# ============================================================================
# STAGE 2: SOURCES
# ============================================================================

print_stage "2" "SOURCE COLLECTION"

print_step "Adding source 1: EPA ECHO Database..."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/source" \
    -H "Content-Type: application/json" \
    -d '{
        "source": {
            "id": "prov-epa-001",
            "url": "https://echo.epa.gov/detailed-facility-report?fid=110012345678",
            "content_hash": "sha256:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "access_timestamp": "2026-05-09T14:15:00Z",
            "title": "EPA ECHO: Acme Corp Springfield Facility",
            "access_type": "full",
            "sift_step": "trace_to_original",
            "is_primary": true
        }
    }')

print_json "$RESPONSE"
CLAIM_2=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)
print_success "Source added, claim: $CLAIM_2"

sleep 0.5

print_step "Adding source 2: SEC Filing..."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/source" \
    -H "Content-Type: application/json" \
    -d '{
        "source": {
            "id": "prov-sec-002",
            "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001234567",
            "content_hash": "sha256:f6e5d4c3b2a1098765432109876543210fedcba9876543210fedcba98765432",
            "access_timestamp": "2026-05-09T14:22:00Z",
            "title": "SEC EDGAR: Acme Corp 10-K Filing 2025",
            "access_type": "full",
            "sift_step": "find_better_coverage",
            "is_primary": true
        }
    }')

print_json "$RESPONSE"
CLAIM_3=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)
print_success "Source added, claim: $CLAIM_3"

sleep 0.5

print_step "Adding source 3: State Environmental Records..."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/source" \
    -H "Content-Type: application/json" \
    -d '{
        "source": {
            "id": "prov-state-003",
            "url": "https://state.gov/environmental-enforcement/violations?facility=acme-springfield",
            "content_hash": "sha256:1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890",
            "access_timestamp": "2026-05-09T14:30:00Z",
            "title": "State Environmental Enforcement Database",
            "access_type": "full",
            "sift_step": "investigate_source",
            "is_primary": true
        }
    }')

print_json "$RESPONSE"
CLAIM_4=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)
print_success "Source added, claim: $CLAIM_4"

sleep 1

# ============================================================================
# STAGE 3: VERIFY
# ============================================================================

print_stage "3" "SIFT VERIFICATION"

print_step "Submitting claim verdicts..."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/verify" \
    -H "Content-Type: application/json" \
    -d '{
        "claims": [
            {
                "id": "claim-001",
                "text": "Acme Corp paid $2.3 million in EPA fines in 2025",
                "verdict": "verified",
                "sources": ["prov-epa-001", "prov-sec-002"],
                "notes": "Confirmed by EPA enforcement database and company SEC filing"
            },
            {
                "id": "claim-002",
                "text": "Springfield facility exceeded emissions limits 47 times",
                "verdict": "partially_verified",
                "sources": ["prov-state-003"],
                "notes": "State records show 42 violations, not 47"
            },
            {
                "id": "claim-003",
                "text": "CEO stated zero tolerance for violations",
                "verdict": "verified",
                "sources": ["prov-sec-002"],
                "notes": "Direct quote from 2025 shareholder letter"
            }
        ],
        "summary": {
            "verified": 2,
            "partially_verified": 1,
            "unverified": 0,
            "contradicted": 0,
            "mischaracterized": 0,
            "total_claims": 3,
            "total_sources": 3
        }
    }')

print_json "$RESPONSE"
CLAIM_5=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)
print_success "Verification complete, claim: $CLAIM_5"

sleep 1

# ============================================================================
# STAGE 4: PUBLISH
# ============================================================================

print_stage "4" "PUBLICATION"

print_step "Publishing final signed artifact..."

RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/publish" \
    -H "Content-Type: application/json" \
    -d '{
        "publish_metadata": {
            "publisher": "Independent News Collective",
            "published_url": "https://news.example.com/acme-investigation"
        }
    }')

print_json "$RESPONSE"
FINAL_MANIFEST=$(echo "$RESPONSE" | grep -o '"final_manifest_id":"[^"]*"' | cut -d'"' -f4)
CLAIM_6=$(echo "$RESPONSE" | grep -o '"claim_id":"[^"]*"' | cut -d'"' -f4)
print_success "Published! Final manifest: $FINAL_MANIFEST"

sleep 1

# ============================================================================
# SHOW CHAIN
# ============================================================================

print_header "Claim Chain"

print_step "Fetching complete provenance chain..."

RESPONSE=$(curl -s "$C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/chain")
print_json "$RESPONSE"

echo ""
echo -e "${BOLD}Chain Visualization:${NC}"
echo ""
echo "  ┌─────────────────────────────────────────────────────────────┐"
echo "  │  DRAFT         → claim: ${CLAIM_1:0:8}...                    │"
echo "  │       ↓                                                     │"
echo "  │  SOURCE 1 (EPA) → claim: ${CLAIM_2:0:8}... (parent: draft)   │"
echo "  │       ↓                                                     │"
echo "  │  SOURCE 2 (SEC) → claim: ${CLAIM_3:0:8}... (parent: src1)    │"
echo "  │       ↓                                                     │"
echo "  │  SOURCE 3 (State) → claim: ${CLAIM_4:0:8}... (parent: src2)  │"
echo "  │       ↓                                                     │"
echo "  │  VERIFY         → claim: ${CLAIM_5:0:8}... (parent: src3)    │"
echo "  │       ↓                                                     │"
echo "  │  PUBLISH        → claim: ${CLAIM_6:0:8}... (parent: verify)  │"
echo "  └─────────────────────────────────────────────────────────────┘"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

print_header "Demo Complete"

echo -e "${BOLD}What was demonstrated:${NC}"
echo ""
echo "  ${GREEN}✓${NC} Stage 1: Draft captured and signed"
echo "  ${GREEN}✓${NC} Stage 2: Three sources added with individual claims"
echo "  ${GREEN}✓${NC} Stage 3: SIFT verification with verdicts"
echo "  ${GREEN}✓${NC} Stage 4: Final publication signature"
echo ""
echo "  ${GREEN}✓${NC} Each stage created a new claim referencing the previous"
echo "  ${GREEN}✓${NC} Total claims in chain: 6"
echo "  ${GREEN}✓${NC} Full provenance from draft → sources → verdicts → publication"
echo ""
echo -e "${BOLD}Pipeline ID:${NC} $PIPELINE_ID"
echo -e "${BOLD}Final Manifest:${NC} $FINAL_MANIFEST"
echo ""
echo "View pipeline status:"
echo "  curl $C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID"
echo ""
echo "View claim chain:"
echo "  curl $C2PA_SERVER/api/sift/pipeline/$PIPELINE_ID/chain"
echo ""
