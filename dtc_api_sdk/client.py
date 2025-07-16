"""
Main API client for the Aparavi Data Toolchain API.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import (
    APIResponse, 
    PipelineConfig, 
    PipelineInfo, 
    TaskInfo, 
    ServiceInfo,
    ResponseStatus,
    TaskStatus
)
from .exceptions import (
    DTCApiError, 
    AuthenticationError, 
    ValidationError,
    PipelineError,
    TaskError,
    NetworkError
)


class DTCApiClient:
    """
    Aparavi Data Toolchain API client.
    
    This client provides a Python interface to interact with the Aparavi DTC API,
    handling authentication, request/response processing, and error handling.
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        base_url: str = "https://eaas-dev.aparavi.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the DTC API client.
        
        Args:
            api_key: API key for authentication. If not provided, will look for 
                    DTC_API_KEY environment variable.
            base_url: Base URL for the API. Defaults to dev environment.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        self.api_key = api_key or os.getenv("DTC_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key is required. Set DTC_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "dtc-api-sdk-python/0.1.0"
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict[str, Any] = None,
        data: Any = None,
        files: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> APIResponse:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            files: Files to upload
            headers: Additional headers
            
        Returns:
            APIResponse object with parsed response data
            
        Raises:
            DTCApiError: For various API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Prepare request arguments
            kwargs = {
                "params": params,
                "timeout": self.timeout,
                "headers": headers or {}
            }
            
            # Handle different content types
            if files:
                # For multipart form data, don't set Content-Type (requests will set it)
                if "Content-Type" in self.session.headers:
                    kwargs["headers"]["Content-Type"] = None
                kwargs["files"] = files
            elif data is not None:
                if isinstance(data, (dict, list)):
                    kwargs["json"] = data
                else:
                    kwargs["data"] = data
            
            # Make the request
            response = self.session.request(method, url, **kwargs)
            
            # Handle response
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise DTCApiError(f"Request failed: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> APIResponse:
        """
        Handle and parse API response.
        
        Args:
            response: Raw HTTP response
            
        Returns:
            Parsed APIResponse object
            
        Raises:
            DTCApiError: For various API errors
        """
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # If response is not JSON, create a basic response structure
            if response.status_code >= 400:
                raise DTCApiError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            response_data = {"status": "OK", "data": response.text}
        
        # Create APIResponse object
        api_response = APIResponse(
            status=ResponseStatus(response_data.get("status", "Error")),
            data=response_data.get("data"),
            error=response_data.get("error"),
            metrics=response_data.get("metrics")
        )
        
        # Handle error responses
        if not api_response.is_success or response.status_code >= 400:
            error_msg = api_response.error_message or f"HTTP {response.status_code}"
            
            if response.status_code == 401:
                raise AuthenticationError(error_msg, response.status_code, response_data)
            elif response.status_code == 422:
                raise ValidationError(error_msg, response.status_code, response_data)
            else:
                raise DTCApiError(error_msg, response.status_code, response_data)
        
        return api_response
    
    # Health Check Methods
    
    def get_version(self) -> str:
        """
        Get the API version.
        
        Returns:
            Version string
        """
        response = self._make_request("GET", "/version")
        return response.data
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get server status.
        
        Returns:
            Server status information
        """
        response = self._make_request("GET", "/status")
        return response.data
    
    # Pipeline Management Methods
    
    def create_pipeline(
        self, 
        config: Union[PipelineConfig, Dict[str, Any]], 
        name: str = None
    ) -> str:
        """
        Create a new processing pipeline.
        
        Args:
            config: Pipeline configuration
            name: Optional pipeline name
            
        Returns:
            Pipeline token for subsequent operations
        """
        if isinstance(config, PipelineConfig):
            config_dict = config.to_dict()
        else:
            config_dict = config
            
        params = {"name": name} if name else {}
        
        response = self._make_request("POST", "/pipe", params=params, data=config_dict)
        
        # Handle both dict and string responses
        if isinstance(response.data, dict):
            if not response.data or "token" not in response.data:
                raise PipelineError("Pipeline creation failed: no token returned")
            return response.data["token"]
        elif isinstance(response.data, str):
            # If response is a string, try to parse it as a token
            if response.data and len(response.data.strip()) > 0:
                return response.data.strip()
            else:
                raise PipelineError("Pipeline creation failed: empty response")
        else:
            raise PipelineError(f"Pipeline creation failed: unexpected response type {type(response.data)}")
    
    def delete_pipeline(self, token: str) -> bool:
        """
        Delete an existing pipeline.
        
        Args:
            token: Pipeline token
            
        Returns:
            True if deletion was successful
        """
        params = {"token": token}
        response = self._make_request("DELETE", "/pipe", params=params)
        return response.is_success
    
    def validate_pipeline(self, config: Union[PipelineConfig, Dict[str, Any]]) -> bool:
        """
        Validate a pipeline configuration without creating it.
        
        Args:
            config: Pipeline configuration to validate
            
        Returns:
            True if configuration is valid
        """
        if isinstance(config, PipelineConfig):
            config_dict = config.to_dict()
        else:
            config_dict = config
            
        response = self._make_request("POST", "/pipe/validate", data=config_dict)
        return response.is_success
    
    def upload_files(self, token: str, files: List[Union[str, Path]]) -> bool:
        """
        Upload files to a pipeline for processing.
        
        Args:
            token: Pipeline token
            files: List of file paths to upload
            
        Returns:
            True if upload was successful
        """
        params = {"token": token}
        
        # Prepare files for upload
        file_data = {}
        for i, file_path in enumerate(files):
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_data[f"file_{i}"] = (file_path.name, open(file_path, 'rb'))
        
        try:
            response = self._make_request("PUT", "/pipe/process", params=params, files=file_data)
            return response.is_success
        finally:
            # Close all file handles
            for file_handle in file_data.values():
                file_handle[1].close()
    
    # Task Management Methods
    
    def execute_task(
        self, 
        config: Union[PipelineConfig, Dict[str, Any]], 
        name: str = None,
        threads: int = None
    ) -> str:
        """
        Execute a one-off task.
        
        Args:
            config: Task configuration
            name: Optional task name
            threads: Number of threads to use (1-16)
            
        Returns:
            Task token
        """
        if isinstance(config, PipelineConfig):
            config_dict = config.to_dict()
        else:
            config_dict = config
            
        params = {}
        if name:
            params["name"] = name
        if threads:
            if not 1 <= threads <= 16:
                raise ValueError("Threads must be between 1 and 16")
            params["threads"] = threads
            
        response = self._make_request("PUT", "/task", params=params, data=config_dict)
        
        # Handle both dict and string responses
        if isinstance(response.data, dict):
            if not response.data or "token" not in response.data:
                raise TaskError("Task execution failed: no token returned")
            return response.data["token"]
        elif isinstance(response.data, str):
            # If response is a string, try to parse it as a token
            if response.data and len(response.data.strip()) > 0:
                return response.data.strip()
            else:
                raise TaskError("Task execution failed: empty response")
        else:
            raise TaskError(f"Task execution failed: unexpected response type {type(response.data)}")
    
    def get_task_status(self, token: str) -> TaskInfo:
        """
        Get the status of a task.
        
        Args:
            token: Task token
            
        Returns:
            TaskInfo object with current status
        """
        params = {"token": token}
        response = self._make_request("GET", "/task", params=params)
        
        # Handle both dict and string responses
        if isinstance(response.data, dict):
            data = response.data
        else:
            # If response is not a dict, create a basic structure
            data = {"status": "unknown", "error_message": f"Unexpected response: {response.data}"}
            
        return TaskInfo(
            token=token,
            status=TaskStatus(data.get("status", "pending")),
            name=data.get("name"),
            progress=data.get("progress"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            result=data.get("result")
        )
    
    def cancel_task(self, token: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            token: Task token
            
        Returns:
            True if cancellation was successful
        """
        params = {"token": token}
        response = self._make_request("DELETE", "/task", params=params)
        return response.is_success
    
    def wait_for_task(self, token: str, poll_interval: int = 5, timeout: int = 300) -> TaskInfo:
        """
        Wait for a task to complete.
        
        Args:
            token: Task token
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            
        Returns:
            Final TaskInfo when task completes
            
        Raises:
            TimeoutError: If task doesn't complete within timeout
            TaskError: If task fails
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task_info = self.get_task_status(token)
            
            if task_info.status == TaskStatus.COMPLETED:
                return task_info
            elif task_info.status == TaskStatus.FAILED:
                raise TaskError(f"Task failed: {task_info.error_message}")
            elif task_info.status == TaskStatus.CANCELLED:
                raise TaskError("Task was cancelled")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Task did not complete within {timeout} seconds")
    
    # Webhook and UI Methods
    
    def send_webhook(self, token: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send webhook data to a task.
        
        Args:
            token: Task token
            webhook_data: Data to send via webhook
            
        Returns:
            Webhook response data
        """
        params = {"token": token}
        response = self._make_request("PUT", "/webhook", params=params, data=webhook_data)
        
        # Handle both dict and string responses
        if isinstance(response.data, dict):
            return response.data
        else:
            # If response is not a dict, wrap it in a dict
            return {"response": response.data, "status": "received"}
    
    def get_chat_url(self, token: str, pipeline_type: str, api_key: str = None) -> str:
        """
        Get chat interface URL with session parameters.
        
        Args:
            token: Task token
            pipeline_type: Type of pipeline
            api_key: API key (uses client's key if not provided)
            
        Returns:
            Chat URL with session parameters
        """
        api_key = api_key or self.api_key
        params = {
            "type": pipeline_type,
            "token": token,
            "apikey": api_key
        }
        return f"{self.base_url}/chat?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    def get_dropper_url(self, token: str, pipeline_type: str, api_key: str = None) -> str:
        """
        Get dropper interface URL with session parameters.
        
        Args:
            token: Task token
            pipeline_type: Type of pipeline
            api_key: API key (uses client's key if not provided)
            
        Returns:
            Dropper URL with session parameters
        """
        api_key = api_key or self.api_key
        params = {
            "type": pipeline_type,
            "token": token,
            "apikey": api_key
        }
        return f"{self.base_url}/dropper?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    # Service Management Methods
    
    def get_services(self, service_name: str = None) -> List[ServiceInfo]:
        """
        Get available services.
        
        Args:
            service_name: Optional specific service name to filter
            
        Returns:
            List of ServiceInfo objects
        """
        params = {"service": service_name} if service_name else {}
        response = self._make_request("GET", "/services", params=params)
        
        services_data = response.data or []
        if not isinstance(services_data, list):
            services_data = [services_data]
        
        return [
            ServiceInfo(
                name=service.get("name", ""),
                status=service.get("status", "unknown"),
                version=service.get("version"),
                description=service.get("description"),
                endpoints=service.get("endpoints")
            )
            for service in services_data
        ] 