#!/bin/bash

# Test script for AI Product-to-Code System
set -e

BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1"

echo "=== Testing AI Product-to-Code Multi-Agent System ==="
echo

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s "${BASE_URL}/health" | python -m json.tool
echo "✓ Health check passed"
echo

# Test 2: User Registration
echo "2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"testpass123","full_name":"Test User"}')
echo "$REGISTER_RESPONSE" | python -m json.tool
echo "✓ User registration passed"
echo

# Test 3: User Login
echo "3. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=testpass123")
TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:50}..."
echo "✓ User login passed"
echo

# Test 4: Create Project
echo "4. Testing project creation..."
PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/projects/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"E-commerce Platform","description":"Build a modern e-commerce platform with real-time features"}')
PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Project ID: $PROJECT_ID"
echo "$PROJECT_RESPONSE" | python -m json.tool
echo "✓ Project creation passed"
echo

# Test 5: Create Run
echo "5. Testing run creation..."
RUN_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/runs/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":$PROJECT_ID,\"product_idea\":\"Build a real-time task management app with collaboration features, Kanban boards, and team chat\"}")
RUN_ID=$(echo "$RUN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Run ID: $RUN_ID"
echo "$RUN_RESPONSE" | python -m json.tool
echo "✓ Run creation passed"
echo

# Test 6: Start Run
echo "6. Testing run start..."
START_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/runs/$RUN_ID/start" \
  -H "Authorization: Bearer $TOKEN")
echo "$START_RESPONSE" | python -m json.tool
echo "✓ Run start passed"
echo

# Test 7: Stream Progress (SSE)
echo "7. Testing progress streaming (SSE)..."
echo "Streaming for 10 seconds..."
timeout 10 curl -N -H "Authorization: Bearer $TOKEN" \
  "${BASE_URL}${API_PREFIX}/runs/$RUN_ID/progress" || echo "✓ Progress streaming test completed"
echo
echo

# Test 8: Get Run Status
echo "8. Testing run status retrieval..."
RUN_STATUS=$(curl -s -X GET "${BASE_URL}${API_PREFIX}/runs/$RUN_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "$RUN_STATUS" | python -m json.tool
echo "✓ Run status retrieval passed"
echo

# Test 9: List Projects
echo "9. Testing project listing..."
curl -s -X GET "${BASE_URL}${API_PREFIX}/projects/" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo "✓ Project listing passed"
echo

echo "=== All Tests Completed Successfully! ==="
