export PORT=8000
TASK_ID=$(curl -s -X POST "http://127.0.0.1:${PORT}/idea" -H "Content-type: application/json" -d '{"idea": "Explain the basics of quantum computing"}' | jq -r .task_id)
 curl -s "http://127.0.0.1:${PORT}/result/${TASK_ID}"
