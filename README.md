# Anthropic API Combinations

Reference implementations demonstrating practical combinations of Anthropic's APIs and features.

## Implementations

### Batch Processing + Tool Use
Combines Claude's batch processing API with tool calling capabilities for parallel request handling.

Example: [Batch Calculator](examples/batch_processing/) processes multiple calculations simultaneously using a custom calculator tool.

# Set up
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

# Run batchprocessing for tool_use
```bash
python3 examples/batch_processing/run_batch_agent.py
```

