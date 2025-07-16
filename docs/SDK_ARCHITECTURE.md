# DTC API SDK Architecture

This document provides a technical overview of the DTC API SDK architecture, internal components, and data flow.

## SDK Architecture Overview

```mermaid
graph TB
    %% User Code
    subgraph UserCode ["User Application"]
        APP[Python Application]
        IMPORT[from dtc_api_sdk.client import DTCApiClient]
        CLIENT_INIT[client = DTCApiClient()]
    end
    
    %% SDK Core
    subgraph SDKCore ["DTC API SDK Core"]
        DTCCLIENT[DTCApiClient]
        MODELS[Data Models]
        EXCEPTIONS[Exception Classes]
        
        %% Client Methods
        subgraph ClientMethods ["Client Methods"]
            EXECUTE[execute_task]
            UPLOAD[upload_file_to_webhook]
            CREATE[create_pipeline]
            VALIDATE[validate_pipeline]
            DELETE[delete_pipeline]
            PROCESS[process_pipeline]
            VERSION[get_version]
            STATUS[get_status]
            SERVICES[get_services]
        end
        
        %% Internal Components
        subgraph Internal ["Internal Components"]
            MAKE_REQ[_make_request]
            HANDLE_RESP[_handle_response]
            SESSION[requests.Session]
            RETRY[Retry Strategy]
        end
    end
    
    %% API Layer
    subgraph APILayer ["DTC API Endpoints"]
        TASK_EP[/task]
        WEBHOOK_EP[/webhook]
        PIPE_EP[/pipe]
        VALIDATE_EP[/pipe/validate]
        PROCESS_EP[/pipe/process]
        VERSION_EP[/version]
        STATUS_EP[/status]
        SERVICES_EP[/services]
    end
    
    %% Connections
    APP --> IMPORT
    IMPORT --> CLIENT_INIT
    CLIENT_INIT --> DTCCLIENT
    
    DTCCLIENT --> ClientMethods
    ClientMethods --> Internal
    
    EXECUTE --> MAKE_REQ
    UPLOAD --> MAKE_REQ
    CREATE --> MAKE_REQ
    VALIDATE --> MAKE_REQ
    DELETE --> MAKE_REQ
    PROCESS --> MAKE_REQ
    VERSION --> MAKE_REQ
    STATUS --> MAKE_REQ
    SERVICES --> MAKE_REQ
    
    MAKE_REQ --> SESSION
    SESSION --> RETRY
    
    MAKE_REQ --> HANDLE_RESP
    HANDLE_RESP --> MODELS
    HANDLE_RESP --> EXCEPTIONS
    
    %% API Connections
    MAKE_REQ --> TASK_EP
    MAKE_REQ --> WEBHOOK_EP
    MAKE_REQ --> PIPE_EP
    MAKE_REQ --> VALIDATE_EP
    MAKE_REQ --> PROCESS_EP
    MAKE_REQ --> VERSION_EP
    MAKE_REQ --> STATUS_EP
    MAKE_REQ --> SERVICES_EP
```

## Document Processing Flow

```mermaid
sequenceDiagram
    participant User as User Code
    participant Client as DTCApiClient
    participant Internal as Internal Methods
    participant API as DTC API
    
    Note over User,API: Document Processing Workflow
    
    User->>Client: client = DTCApiClient()
    Client->>Internal: Initialize session & headers
    Internal-->>Client: Ready
    
    User->>Client: execute_task(pipeline_config)
    Client->>Internal: _make_request("PUT", "/task", data=config)
    Internal->>API: PUT /task
    API-->>Internal: {"status": "OK", "data": {"token": "abc123"}}
    Internal->>Client: _handle_response(response)
    Client-->>User: task_token = "abc123"
    
    User->>Client: upload_file_to_webhook(token, file_path)
    Client->>Internal: Read file & detect MIME type
    Internal->>Internal: Prepare headers & params
    Client->>Internal: _make_request("PUT", "/webhook", data=file_data)
    Internal->>API: PUT /webhook?type=cpu&apikey=key&token=abc123
    API-->>Internal: {"status": "OK", "data": {...}}
    Internal->>Client: _handle_response(response)
    Client-->>User: result = {...}
    
    Note over User,API: Task automatically cleans up
```

## Method-to-Endpoint Mapping

```mermaid
graph LR
    %% SDK Methods
    subgraph SDKMethods ["SDK Methods"]
        EXEC[execute_task]
        UPLOAD[upload_file_to_webhook]
        CREATE[create_pipeline]
        VALIDATE[validate_pipeline]
        DELETE[delete_pipeline]
        PROCESS[process_pipeline]
        VERSION[get_version]
        STATUS[get_status]
        SERVICES[get_services]
        SEND[send_webhook]
        TASK_STATUS[get_task_status]
        CANCEL[cancel_task]
    end
    
    %% API Endpoints
    subgraph APIEndpoints ["API Endpoints"]
        TASK_PUT[PUT /task]
        WEBHOOK_PUT[PUT /webhook]
        PIPE_POST[POST /pipe]
        PIPE_VALIDATE[POST /pipe/validate]
        PIPE_DELETE[DELETE /pipe]
        PIPE_PROCESS[PUT /pipe/process]
        VERSION_GET[GET /version]
        STATUS_GET[GET /status]
        SERVICES_GET[GET /services]
        TASK_GET[GET /task]
        TASK_DELETE[DELETE /task]
    end
    
    %% Mappings
    EXEC --> TASK_PUT
    UPLOAD --> WEBHOOK_PUT
    CREATE --> PIPE_POST
    VALIDATE --> PIPE_VALIDATE
    DELETE --> PIPE_DELETE
    PROCESS --> PIPE_PROCESS
    VERSION --> VERSION_GET
    STATUS --> STATUS_GET
    SERVICES --> SERVICES_GET
    SEND --> WEBHOOK_PUT
    TASK_STATUS --> TASK_GET
    CANCEL --> TASK_DELETE
```

## Error Handling Flow

```mermaid
graph TB
    %% Request Flow
    REQUEST[API Request]
    RESPONSE[API Response]
    
    %% Response Handling
    subgraph ResponseHandling ["Response Handling"]
        PARSE[Parse JSON]
        STATUS_CHECK[Check Status Code]
        RESPONSE_STATUS[Check Response Status]
    end
    
    %% Success Path
    subgraph SuccessPath ["Success Path"]
        API_RESPONSE[APIResponse Object]
        RETURN_DATA[Return Data to User]
    end
    
    %% Error Path
    subgraph ErrorPath ["Error Handling"]
        HTTP_ERROR[HTTP Error]
        AUTH_ERROR[Authentication Error]
        VALIDATION_ERROR[Validation Error]
        NETWORK_ERROR[Network Error]
        DTC_ERROR[DTC API Error]
    end
    
    %% Flow
    REQUEST --> RESPONSE
    RESPONSE --> ResponseHandling
    
    PARSE --> STATUS_CHECK
    STATUS_CHECK --> RESPONSE_STATUS
    
    %% Success
    RESPONSE_STATUS -->|status: "OK"| API_RESPONSE
    API_RESPONSE --> RETURN_DATA
    
    %% Errors
    STATUS_CHECK -->|401| AUTH_ERROR
    STATUS_CHECK -->|422| VALIDATION_ERROR
    STATUS_CHECK -->|4xx/5xx| HTTP_ERROR
    PARSE -->|Connection Error| NETWORK_ERROR
    RESPONSE_STATUS -->|status: "Error"| DTC_ERROR
```

## Data Models Structure

```mermaid
graph TB
    %% Base Models
    subgraph BaseModels ["Base Data Models"]
        RESPONSE_STATUS[ResponseStatus]
        API_RESPONSE[APIResponse]
    end
    
    %% Specific Models
    subgraph SpecificModels ["Specific Models"]
        PIPELINE_CONFIG[PipelineConfig]
        PIPELINE_INFO[PipelineInfo]
        TASK_INFO[TaskInfo]
        SERVICE_INFO[ServiceInfo]
        TASK_STATUS[TaskStatus]
    end
    
    %% Response Structure
    subgraph ResponseStructure ["Response Structure"]
        STATUS[status: "OK" | "Error"]
        DATA[data: Any]
        ERROR[error: Dict]
        METRICS[metrics: Dict]
    end
    
    %% Relationships
    API_RESPONSE --> ResponseStructure
    RESPONSE_STATUS --> STATUS
    
    PIPELINE_CONFIG --> DATA
    PIPELINE_INFO --> DATA
    TASK_INFO --> DATA
    SERVICE_INFO --> DATA
    TASK_STATUS --> DATA
```

## Authentication & Session Management

```mermaid
graph TB
    %% Initialization
    subgraph Init ["Client Initialization"]
        ENV_VAR[Environment Variable: DTC_API_KEY]
        PARAM[Parameter: api_key]
        AUTH_ERROR[AuthenticationError]
    end
    
    %% Session Setup
    subgraph Session ["Session Configuration"]
        REQUESTS_SESSION[requests.Session]
        RETRY_STRATEGY[Retry Strategy]
        DEFAULT_HEADERS[Default Headers]
        TIMEOUT[Timeout Configuration]
    end
    
    %% Authentication Flow
    subgraph AuthFlow ["Authentication Flow"]
        BEARER_TOKEN[Bearer Token Header]
        API_KEY_HEADER[API Key Header]
        WEBHOOK_AUTH[Webhook Authentication]
    end
    
    %% Flow
    ENV_VAR -->|Found| Session
    PARAM -->|Provided| Session
    ENV_VAR -->|Not Found| AUTH_ERROR
    PARAM -->|Not Provided| AUTH_ERROR
    
    Session --> REQUESTS_SESSION
    REQUESTS_SESSION --> RETRY_STRATEGY
    REQUESTS_SESSION --> DEFAULT_HEADERS
    REQUESTS_SESSION --> TIMEOUT
    
    %% Authentication Types
    DEFAULT_HEADERS --> BEARER_TOKEN
    WEBHOOK_AUTH --> API_KEY_HEADER
    
    %% Notes
    BEARER_TOKEN -.->|Most endpoints| API_KEY_HEADER
    API_KEY_HEADER -.->|Webhook only| WEBHOOK_AUTH
```

## File Upload Process

```mermaid
graph TB
    %% Input
    subgraph Input ["Input"]
        FILE_PATH[File Path]
        TASK_TOKEN[Task Token]
        CONTENT_TYPE[Content Type]
        TIMEOUT[Timeout]
    end
    
    %% Processing
    subgraph Processing ["File Processing"]
        FILE_EXISTS[Check File Exists]
        DETECT_MIME[Auto-detect MIME Type]
        READ_FILE[Read File as Binary]
        PREPARE_HEADERS[Prepare Headers]
        PREPARE_PARAMS[Prepare URL Parameters]
    end
    
    %% Request
    subgraph Request ["HTTP Request"]
        WEBHOOK_URL[Webhook URL]
        PUT_REQUEST[PUT Request]
        BINARY_DATA[Binary File Data]
    end
    
    %% Response
    subgraph Response ["Response Handling"]
        HTTP_RESPONSE[HTTP Response]
        JSON_PARSE[Parse JSON]
        ERROR_HANDLE[Error Handling]
        RETURN_RESULT[Return Result]
    end
    
    %% Flow
    FILE_PATH --> FILE_EXISTS
    FILE_EXISTS -->|Exists| DETECT_MIME
    FILE_EXISTS -->|Not Found| ERROR_HANDLE
    
    CONTENT_TYPE -->|Provided| PREPARE_HEADERS
    DETECT_MIME -->|Auto-detected| PREPARE_HEADERS
    
    FILE_PATH --> READ_FILE
    TASK_TOKEN --> PREPARE_PARAMS
    
    PREPARE_HEADERS --> PUT_REQUEST
    PREPARE_PARAMS --> WEBHOOK_URL
    READ_FILE --> BINARY_DATA
    
    WEBHOOK_URL --> PUT_REQUEST
    BINARY_DATA --> PUT_REQUEST
    
    PUT_REQUEST --> HTTP_RESPONSE
    HTTP_RESPONSE --> JSON_PARSE
    JSON_PARSE --> RETURN_RESULT
    HTTP_RESPONSE --> ERROR_HANDLE
```

## Key Components

### DTCApiClient
- **Purpose**: Main entry point for all API operations
- **Configuration**: API key, base URL, timeout, retry strategy
- **Methods**: High-level methods for document processing

### Internal Request Handler
- **`_make_request()`**: Handles all HTTP requests with retry logic
- **`_handle_response()`**: Processes responses and handles errors
- **Session Management**: Persistent connection pooling

### Data Models
- **APIResponse**: Standardized response format
- **Configuration Models**: Pipeline, task, and service configurations
- **Exception Classes**: Specific error types for different failure modes

### Error Handling
- **Network Errors**: Connection timeouts, SSL errors
- **Authentication Errors**: Invalid API keys
- **Validation Errors**: Invalid pipeline configurations
- **API Errors**: Server-side processing errors

## Usage Patterns

### Task-based Processing (Recommended)
```python
# Create task → Upload file → Automatic cleanup
task_token = client.execute_task(pipeline_config)
result = client.upload_file_to_webhook(task_token, file_path)
```

### Pipeline-based Processing
```python
# Create pipeline → Process multiple files → Manual cleanup
pipeline_token = client.create_pipeline(pipeline_config)
result = client.process_pipeline(pipeline_token, file_path)
client.delete_pipeline(pipeline_token)
```

### System Information
```python
# Get system health and service information
version = client.get_version()
status = client.get_status()
services = client.get_services()
```

---

This architecture provides a clean, Pythonic interface to the DTC API while handling the complexity of HTTP requests, authentication, error handling, and data processing internally. 