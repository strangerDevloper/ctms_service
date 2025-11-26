from typing import Any, Optional, Generic, TypeVar, List, Union
from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.inspection import inspect as sqlalchemy_inspect

T = TypeVar('T')


class PaginatedData(BaseModel, Generic[T]):
    """
    Paginated data model for list responses.
    
    Attributes:
        items: List of items
        total_count: Total number of items matching the query
        has_next_page: Whether there are more items available
        skip: Number of items skipped
        limit: Maximum number of items returned
    """
    items: List[T]
    total_count: int
    has_next_page: bool
    skip: int
    limit: int

    class Config:
        from_attributes = True


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard response model for all API responses.
    
    Attributes:
        data: The actual response data (can be any type)
        msg: Message describing the response
        status: Status code or status string (e.g., "success", "error")
    """
    data: Optional[T] = None
    msg: str = "Success"
    status: Any = status.HTTP_200_OK

    class Config:
        from_attributes = True
        json_encoders = {
            # Add custom encoders if needed
        }


class FormatResponse(Response):
    """
    Response formatter class that extends FastAPI's Response class.
    Formats all API responses in a standard format: {data, msg, status}
    """
    
    def __init__(
        self,
        data: Any = None,
        msg: str = "Success",
        status_code: int = status.HTTP_200_OK,
        **kwargs
    ):
        """
        Initialize formatted response.
        
        Args:
            data: The response data
            msg: Response message
            status_code: HTTP status code
            **kwargs: Additional arguments for Response
        """
        self.data = data
        self.msg = msg
        self.status_code = status_code
        super().__init__(**kwargs)
    
    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """
        Serialize data to JSON-serializable format.
        Handles SQLAlchemy models, Pydantic models, lists, and dicts.
        """
        if data is None:
            return None
        
        # If it's a list, serialize each item
        if isinstance(data, list):
            return [FormatResponse._serialize_data(item) for item in data]
        
        # Check if it's a SQLAlchemy model
        try:
            # Try to inspect if it's a SQLAlchemy model
            mapper = sqlalchemy_inspect(data, raiseerr=False)
            if mapper is not None and hasattr(mapper, 'columns'):
                # Convert SQLAlchemy model to dict
                result = {}
                for column in mapper.columns:
                    column_key = column.key
                    try:
                        value = getattr(data, column_key, None)
                        # Handle None values
                        if value is None:
                            result[column_key] = None
                        # Handle datetime and other special types
                        elif hasattr(value, 'isoformat'):  # datetime objects
                            result[column_key] = value.isoformat()
                        # Recursively serialize nested objects
                        elif isinstance(value, (list, tuple)):
                            result[column_key] = [FormatResponse._serialize_data(item) for item in value]
                        elif isinstance(value, dict):
                            result[column_key] = FormatResponse._serialize_data(value)
                        else:
                            result[column_key] = value
                    except Exception:
                        # Skip attributes that can't be accessed
                        continue
                return result
        except Exception:
            # Not a SQLAlchemy model, continue with jsonable_encoder
            pass
        
        # Use jsonable_encoder to handle Pydantic models, dicts, etc.
        try:
            return jsonable_encoder(data)
        except (TypeError, ValueError):
            # If jsonable_encoder fails, try to convert to string or dict
            if hasattr(data, '__dict__'):
                return FormatResponse._serialize_data(data.__dict__)
            return str(data)
    
    @staticmethod
    def success(
        data: Any = None,
        msg: str = "Operation completed successfully",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Create a success response.
        
        Args:
            data: The response data (can be SQLAlchemy models, Pydantic models, etc.)
            msg: Success message
            status_code: HTTP status code
            
        Returns:
            JSONResponse with formatted data
        """
        # Serialize data to JSON-serializable format
        serialized_data = FormatResponse._serialize_data(data)
        
        response_content = {
            "data": serialized_data,
            "msg": msg,
            "status": status_code
        }
        
        return JSONResponse(
            content=response_content,
            status_code=status_code
        )
    
    @staticmethod
    def created(
        data: Any = None,
        msg: str = "Resource created successfully",
        status_code: int = status.HTTP_201_CREATED
    ) -> JSONResponse:
        """
        Create a success response for resource creation.
        
        Args:
            data: The response data (can be SQLAlchemy models, Pydantic models, etc.)
            msg: Success message
            status_code: HTTP status code (default: 201)
            
        Returns:
            JSONResponse with formatted data
        """
        # Serialize data to JSON-serializable format
        serialized_data = FormatResponse._serialize_data(data)
        
        response_content = {
            "data": serialized_data,
            "msg": msg,
            "status": status_code
        }
        
        return JSONResponse(
            content=response_content,
            status_code=status_code
        )
    
    @staticmethod
    def error(
        msg: str = "An error occurred",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ) -> JSONResponse:
        """
        Create an error response.
        
        Args:
            msg: Error message
            status_code: HTTP status code
            data: Optional error details
            
        Returns:
            JSONResponse with formatted error data
        """
        # Serialize data to JSON-serializable format
        serialized_data = FormatResponse._serialize_data(data)
        
        response_content = {
            "data": serialized_data,
            "msg": msg,
            "status": status_code
        }
        
        return JSONResponse(
            content=response_content,
            status_code=status_code
        )
    
    @staticmethod
    def not_found(
        msg: str = "Resource not found",
        data: Any = None
    ) -> JSONResponse:
        """
        Create a not found response.
        
        Args:
            msg: Error message
            data: Optional error details
            
        Returns:
            JSONResponse with 404 status
        """
        return FormatResponse.error(
            msg=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )
    
    @staticmethod
    def bad_request(
        msg: str = "Bad request",
        data: Any = None
    ) -> JSONResponse:
        """
        Create a bad request response.
        
        Args:
            msg: Error message
            data: Optional error details
            
        Returns:
            JSONResponse with 400 status
        """
        return FormatResponse.error(
            msg=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )

