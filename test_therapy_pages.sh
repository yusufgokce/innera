#!/bin/bash

echo "========================================"
echo "Testing Innera SEO Therapy Pages"
echo "========================================"
echo ""
echo "NOTE: All therapy pages are now in templates/seo/ directory"
echo ""

BASE_URL="http://127.0.0.1:8000"

# Check if server is running
echo "Checking if server is running..."
server_status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/")
if [ "$server_status" -ne 200 ]; then
  echo "❌ Server not responding at ${BASE_URL}"
  echo "Please start the server with: uvicorn main:app --reload"
  exit 1
fi
echo "✅ Server is running"
echo ""

# Array of all therapy endpoints
endpoints=(
  "/therapy|Hub Page"
  "/therapy/cbt|CBT"
  "/therapy/trauma-informed|Trauma"
  "/therapy/dbt|DBT"
  "/therapy/mindfulness|Mindfulness"
  "/therapy/act|ACT"
  "/therapy/attachment-therapy|Attachment"
  "/therapy/solution-focused|SFBT"
  "/therapy/internal-family-systems|IFS"
  "/therapy/narrative-therapy|Narrative"
  "/therapy/person-centred|Person-Centred"
  "/therapy/spiritual-care|Spiritual"
)

echo "Testing all therapy endpoints..."
echo "----------------------------------------"

passed=0
failed=0

# Test each endpoint
for item in "${endpoints[@]}"; do
  IFS='|' read -r endpoint name <<< "$item"
  http_status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${endpoint}")

  if [ "$http_status" -eq 200 ]; then
    echo "✅ ${name}: ${http_status}"
    ((passed++))
  else
    echo "❌ ${name}: ${http_status}"
    ((failed++))
  fi
done

echo "----------------------------------------"
echo "Results: ${passed} passed, ${failed} failed"
echo ""

# Content validation for hub page
echo "Validating hub page content..."
hub_content=$(curl -s "${BASE_URL}/therapy")

if echo "$hub_content" | grep -q "Evidence-Based Therapy Approaches"; then
  echo "✅ Hub page title found"
else
  echo "❌ Hub page title missing"
fi

if echo "$hub_content" | grep -q "Greater Toronto Area"; then
  echo "✅ GTA location keyword found"
else
  echo "❌ GTA location keyword missing"
fi

if echo "$hub_content" | grep -q '"@type"'; then
  echo "✅ Schema markup found"
else
  echo "❌ Schema markup missing"
fi

echo ""

# Content validation for CBT page (sample)
echo "Validating CBT page content..."
cbt_content=$(curl -s "${BASE_URL}/therapy/cbt")

if echo "$cbt_content" | grep -q "Cognitive Behavioural Therapy"; then
  echo "✅ CBT page title found"
else
  echo "❌ CBT page title missing"
fi

if echo "$cbt_content" | grep -q "University of Toronto"; then
  echo "✅ UofT source citation found"
else
  echo "❌ UofT source citation missing"
fi

if echo "$cbt_content" | grep -q '"@type": "MedicalTherapy"'; then
  echo "✅ Schema markup found"
else
  echo "❌ Schema markup missing"
fi

echo ""
echo "========================================"
echo "Testing complete!"
echo "All SEO pages located in: templates/seo/"
echo "========================================"
