#!/bin/bash
# End-to-end flow test script
set -e

BASE="http://localhost:8000"
echo "========================================"
echo "  Bookstore E2E Flow Test"
echo "========================================"

# 1. Register customer
echo -e "\n[1] Registering customer..."
REGISTER=$(curl -s -X POST $BASE/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test_flow@example.com","username":"testflow","first_name":"Test","last_name":"Flow","password":"Test1234!","password_confirm":"Test1234!","role":"customer"}')
echo "$REGISTER" | python3 -m json.tool 2>/dev/null || echo "$REGISTER"
TOKEN=$(echo $REGISTER | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Login instead..."
  LOGIN=$(curl -s -X POST $BASE/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test_flow@example.com","password":"Test1234!"}')
  TOKEN=$(echo $LOGIN | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null)
fi
echo "TOKEN obtained: ${TOKEN:0:30}..."

# 2. Browse catalog
echo -e "\n[2] Browsing catalog..."
curl -s "$BASE/api/catalog/" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Total books: {d.get(\"total\",0)}')"

# 3. Get recommendations
echo -e "\n[3] Getting trending recommendations..."
curl -s "$BASE/api/recommendations/trending/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null | head -20

# 4. Health check
echo -e "\n[4] Gateway health check..."
curl -s $BASE/gateway/health/ | python3 -m json.tool

echo -e "\n========================================"
echo "  ✅ Flow test complete"
echo "========================================"
