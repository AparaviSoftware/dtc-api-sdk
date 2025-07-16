# Pipeline vs Task Workflows - User Flow Guide

This guide explains when and how to use the two main processing approaches in the DTC API: **Pipeline Endpoints** and **Task Endpoints**.

## Quick Decision Guide

| Use Case | Recommended Approach | Why |
|----------|---------------------|-----|
| One-time document processing | **Task Endpoint** | Simpler, direct execution |
| Batch processing same format | **Pipeline Endpoint** | Reusable, more efficient |
| Production webhook processing | **Task Endpoint** | Self-contained, easier cleanup |
| Interactive web interfaces | **Pipeline Endpoint** | Persistent, UI-friendly |

## Pipeline Endpoints Workflow

### When to Use Pipelines
- **Reusable Processing**: Same configuration used multiple times
- **Interactive Applications**: Web interfaces that need persistent pipelines
- **Batch Processing**: Multiple files with identical processing requirements
- **Long-running Services**: Applications that process files continuously

### Pipeline Flow

```
1. Validate → 2. Create → 3. Process → 4. Cleanup
```

#### Step 1: Validate Pipeline Configuration
```python
# Validate your pipeline configuration before creating
is_valid = client.validate_pipeline({
    "pipeline": {
        "source": "webhook_1",
        "components": [
            {"id": "webhook_1", "provider": "webhook", "config": {"mode": "Source"}},
            {"id": "parse_1", "provider": "parse", "input": [{"lane": "tags", "from": "webhook_1"}]},
            {"id": "response_1", "provider": "response", "input": [{"lane": "text", "from": "parse_1"}]}
        ]
    }
})
```

#### Step 2: Create Pipeline
```python
# Create a reusable pipeline
pipeline_token = client.create_pipeline({
    "pipeline": {
        "source": "webhook_1",
        "components": [...],  # Same configuration as validation
        "id": "my-reusable-pipeline"
    }
}, name="Document Processing Pipeline")
```

#### Step 3: Process Files (Multiple Times)
```python
# Process multiple files using the same pipeline
for file_path in file_list:
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Upload and process
    client.upload_files(pipeline_token, [file_path])
    result = client.process_pipeline(pipeline_token, {
        "filename": file_path,
        "data": base64.b64encode(file_content).decode()
    })
```

#### Step 4: Cleanup Pipeline
```python
# Clean up when done
client.delete_pipeline(pipeline_token)
```

### Pipeline Advantages
- ✅ **Reusable**: Create once, use many times
- ✅ **Efficient**: No repeated setup overhead
- ✅ **Persistent**: Survives between processing calls
- ✅ **Web UI Compatible**: Works with `/chat` and `/dropper` endpoints

### Pipeline Disadvantages
- ❌ **Manual Cleanup**: Must remember to delete pipelines
- ❌ **More Complex**: Multi-step process
- ❌ **Resource Usage**: Pipelines consume resources until deleted
- ❌ **Token Management**: Need to track pipeline tokens

## Task Endpoints Workflow

### When to Use Tasks
- **One-off Processing**: Single file or unique processing requirements
- **Webhook Processing**: Direct API integration without UI
- **Production Services**: Self-contained processing with automatic cleanup
- **Prototyping**: Quick testing of configurations

### Task Flow

```
1. Execute → 2. Process → 3. Auto-cleanup
```

#### Step 1: Execute Task (Direct Processing)
```python
# Execute task with immediate processing
task_token = client.execute_task({
    "pipeline": {
        "source": "webhook_1",
        "components": [
            {"id": "webhook_1", "provider": "webhook", "config": {"mode": "Source"}},
            {"id": "parse_1", "provider": "parse", "input": [{"lane": "tags", "from": "webhook_1"}]},
            {"id": "response_1", "provider": "response", "input": [{"lane": "text", "from": "parse_1"}]}
        ]
    }
}, name="One-time Document Processing", threads=4)
```

#### Step 2: Process Data (Webhook Approach)
```python
# Send data directly to the task
with open(file_path, 'rb') as f:
    file_content = f.read()

result = client.send_webhook(task_token, {
    "filename": os.path.basename(file_path),
    "content_type": "application/pdf",
    "size": len(file_content),
    "data": base64.b64encode(file_content).decode()
})

# Task automatically cleans up after processing
```

### Task Advantages
- ✅ **Simple**: Single API call to start processing
- ✅ **Self-contained**: No manual cleanup required
- ✅ **Automatic Cleanup**: Resources freed after completion
- ✅ **Thread Control**: Specify processing threads (1-16)

### Task Disadvantages
- ❌ **Single Use**: Cannot reuse for multiple files
- ❌ **Setup Overhead**: Configuration repeated for each task
- ❌ **No Persistence**: Cannot be used with web interfaces

## Real-World Examples

### Example 1: Production Webhook Service (Task Approach)

```python
class DocumentProcessor:
    def __init__(self):
        self.client = DTCApiClient()
        self.webhook_config = {
            "pipeline": {
                "source": "webhook_1",
                "components": [
                    {"id": "webhook_1", "provider": "webhook", "config": {"hideForm": True, "mode": "Source"}},
                    {"id": "parse_1", "provider": "parse", "input": [{"lane": "tags", "from": "webhook_1"}]},
                    {"id": "response_1", "provider": "response", "input": [{"lane": "text", "from": "parse_1"}]}
                ]
            }
        }
    
    def process_document(self, file_path):
        """Process single document using task endpoint."""
        # Create task for this specific document
        task_token = self.client.execute_task(
            self.webhook_config, 
            name=f"process_{os.path.basename(file_path)}"
        )
        
        # Process the document
        with open(file_path, 'rb') as f:
            result = self.client.send_webhook(task_token, {
                "filename": os.path.basename(file_path),
                "content_type": "application/pdf",
                "data": base64.b64encode(f.read()).decode()
            })
        
        # Task automatically cleans up
        return result
```

### Example 2: Batch Processing Service (Pipeline Approach)

```python
class BatchProcessor:
    def __init__(self):
        self.client = DTCApiClient()
        self.pipeline_token = None
    
    def setup_pipeline(self):
        """Create reusable pipeline for batch processing."""
        config = {
            "pipeline": {
                "source": "webhook_1",
                "components": [
                    {"id": "webhook_1", "provider": "webhook", "config": {"mode": "Source"}},
                    {"id": "parse_1", "provider": "parse", "input": [{"lane": "tags", "from": "webhook_1"}]},
                    {"id": "response_1", "provider": "response", "input": [{"lane": "text", "from": "parse_1"}]}
                ]
            }
        }
        
        self.pipeline_token = self.client.create_pipeline(config, name="Batch Processor")
    
    def process_batch(self, file_paths):
        """Process multiple files using the same pipeline."""
        if not self.pipeline_token:
            self.setup_pipeline()
        
        results = []
        for file_path in file_paths:
            # Use the same pipeline for all files
            result = self.client.process_pipeline(self.pipeline_token, file_path)
            results.append(result)
        
        return results
    
    def cleanup(self):
        """Clean up the pipeline when done."""
        if self.pipeline_token:
            self.client.delete_pipeline(self.pipeline_token)
```

## Performance Comparison

### Processing 100 Documents

| Approach | Setup Time | Processing Time | Cleanup Time | Total Time |
|----------|------------|----------------|--------------|------------|
| **100 Tasks** | 100 × 2s = 200s | 100 × 10s = 1000s | 0s (automatic) | **1200s** |
| **1 Pipeline** | 1 × 2s = 2s | 100 × 10s = 1000s | 1 × 1s = 1s | **1003s** |

**Pipeline approach is ~16% faster for batch processing**

## Error Handling Patterns

### Task Endpoint Error Handling
```python
try:
    task_token = client.execute_task(config)
    result = client.send_webhook(task_token, data)
    # No cleanup needed - automatic
except Exception as e:
    # Task automatically cleaned up even on failure
    print(f"Processing failed: {e}")
```

### Pipeline Endpoint Error Handling
```python
pipeline_token = None
try:
    pipeline_token = client.create_pipeline(config)
    result = client.process_pipeline(pipeline_token, data)
finally:
    # Always clean up pipeline
    if pipeline_token:
        client.delete_pipeline(pipeline_token)
```

## Best Practices

### Use Tasks When:
- Processing individual documents in a service
- Building webhook endpoints
- Prototyping and testing
- You want automatic resource cleanup
- Processing requirements change per request

### Use Pipelines When:
- Processing multiple files with same configuration
- Building web applications with UI
- Long-running services that process files continuously
- You need to optimize performance for repeated processing
- Working with `/chat` or `/dropper` endpoints

## Migration Guide

### From Pipeline to Task
```python
# Old pipeline approach
pipeline_token = client.create_pipeline(config)
result = client.process_pipeline(pipeline_token, data)
client.delete_pipeline(pipeline_token)

# New task approach
task_token = client.execute_task(config)
result = client.send_webhook(task_token, data)
# No cleanup needed
```

### From Task to Pipeline
```python
# Old task approach (repeated for each file)
for file_path in files:
    task_token = client.execute_task(config)
    result = client.send_webhook(task_token, data)

# New pipeline approach (reuse for all files)
pipeline_token = client.create_pipeline(config)
try:
    for file_path in files:
        result = client.process_pipeline(pipeline_token, data)
finally:
    client.delete_pipeline(pipeline_token)
```

## Summary

- **Tasks**: Simple, self-contained, automatic cleanup - ideal for webhooks and one-off processing
- **Pipelines**: Reusable, efficient for batch processing, requires manual cleanup - ideal for applications and repeated processing

Choose based on your use case: **Tasks for webhooks and services**, **Pipelines for batch processing and applications**. 