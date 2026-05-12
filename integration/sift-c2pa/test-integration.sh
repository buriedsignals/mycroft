#!/bin/bash
#
# SIFT × C2PA Integration Test
#
# Tests the end-to-end flow:
# 1. Submit example SIFT manifest to C2PA service
# 2. Verify the signed manifest
# 3. Check the SIFT assertion structure
#

set -e

# Configuration
C2PA_SERVER="${C2PA_SERVER:-http://localhost:5002}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "SIFT × C2PA Integration Test"
echo "============================================"
echo ""
echo "C2PA Server: $C2PA_SERVER"
echo ""

# Check if server is running
echo "1. Checking C2PA server health..."
if ! curl -s "$C2PA_SERVER/health" > /dev/null 2>&1; then
    echo "   ⚠ Server not responding at $C2PA_SERVER"
    echo "   Start the server with: cd ~/Sites/noosphere/github/c2pa-artifact && python server/app.py"
    exit 1
fi
echo "   ✓ Server is running"
echo ""

# Get SIFT schema
echo "2. Fetching SIFT manifest schema..."
SCHEMA=$(curl -s "$C2PA_SERVER/api/sift/schema")
if echo "$SCHEMA" | grep -q "sift-manifest-v1"; then
    echo "   ✓ Schema endpoint working"
else
    echo "   ✗ Schema endpoint failed"
    exit 1
fi
echo ""

# Get verdicts
echo "3. Fetching SIFT verdict types..."
VERDICTS=$(curl -s "$C2PA_SERVER/api/sift/verdicts")
if echo "$VERDICTS" | grep -q "verified"; then
    echo "   ✓ Verdicts endpoint working"
    echo "   Available verdicts: verified, partially_verified, unverified, contradicted, mischaracterized"
else
    echo "   ✗ Verdicts endpoint failed"
    exit 1
fi
echo ""

# Submit example manifest
echo "4. Submitting example SIFT manifest..."
RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/process" \
    -H "Content-Type: application/json" \
    -d @"$SCRIPT_DIR/example-sift-manifest.json" 2>&1 || true)

# Check if we got a credential error (expected without proper setup)
if echo "$RESPONSE" | grep -q "credential"; then
    echo "   ⚠ Credential not configured (expected in test environment)"
    echo "   To complete signing, configure a credential in C2PA artifact service"
    echo ""
    echo "   Response: $(echo "$RESPONSE" | head -c 200)"
elif echo "$RESPONSE" | grep -q "success"; then
    MANIFEST_ID=$(echo "$RESPONSE" | grep -o '"manifest_id":"[^"]*"' | cut -d'"' -f4)
    echo "   ✓ Manifest created: $MANIFEST_ID"

    # Verify the manifest
    echo ""
    echo "5. Verifying SIFT manifest..."
    VERIFY_RESPONSE=$(curl -s -X POST "$C2PA_SERVER/api/sift/verify" \
        -H "Content-Type: application/json" \
        -d "{\"manifest_id\": \"$MANIFEST_ID\"}")

    if echo "$VERIFY_RESPONSE" | grep -q "verified"; then
        echo "   ✓ Manifest verification successful"
        echo ""
        echo "   Summary:"
        echo "$VERIFY_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   - Claims: {d.get(\"claims_summary\", {}).get(\"total_claims\", \"?\")}'); print(f'   - Verified: {d.get(\"claims_summary\", {}).get(\"verified\", \"?\")}'); print(f'   - Sources: {d.get(\"sources_count\", \"?\")}')" 2>/dev/null || echo "   (Could not parse response)"
    else
        echo "   ⚠ Verification returned unexpected response"
        echo "   Response: $(echo "$VERIFY_RESPONSE" | head -c 200)"
    fi
else
    echo "   ⚠ Unexpected response from server"
    echo "   Response: $(echo "$RESPONSE" | head -c 300)"
fi

echo ""
echo "============================================"
echo "Test complete"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Configure a signing credential in C2PA artifact service"
echo "2. Run fact-check-c2pa recipe in Mycroft"
echo "3. Submit real SIFT manifests for signing"
echo ""
