#!/bin/bash
# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Ollama not ready, waiting..."
    sleep 2
done

echo "Ollama is ready. Pulling Phi-3.5 model..."
ollama pull phi3.5

echo "Phi-3.5 model pulled successfully!"
echo "Available models:"
ollama list
