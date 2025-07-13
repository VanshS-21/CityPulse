"""
Comprehensive tests for the enhanced error handling system.
Tests correlation IDs, structured logging, and error context management.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from uuid import UUID

# Import the enhanced error handling classes
import sys
sys.path.append('server')

from shared_exceptions import (
    ErrorCode,
    ErrorContext,
    error_context,
    CityPulseException,
    ValidationException,
    DatabaseException,
    ExternalServiceException,
    BusinessRuleException
)


class TestErrorContext:
    """Test the ErrorContext class."""
    
    def test_error_context_creation(self):
        """Test creating an error context."""
        ctx = ErrorContext()
        
        # Check that correlation_id is a valid UUID
        assert UUID(ctx.correlation_id)
        assert isinstance(ctx.timestamp, float)
        assert ctx.timestamp <= time.time()
        assert isinstance(ctx.context, dict)
        assert ctx.user_id is None
        assert ctx.request_id is None
        assert ctx.operation is None
    
    def test_error_context_with_values(self):
        """Test creating error context with specific values."""
        ctx = ErrorContext(
            correlation_id="test-correlation-id",
            user_id="user123",
            request_id="req456",
            operation="test_operation"
        )
        
        assert ctx.correlation_id == "test-correlation-id"
        assert ctx.user_id == "user123"
        assert ctx.request_id == "req456"
        assert ctx.operation == "test_operation"
    
    def test_add_context(self):
        """Test adding context information."""
        ctx = ErrorContext()
        ctx.add_context(key1="value1", key2="value2")
        
        assert ctx.context["key1"] == "value1"
        assert ctx.context["key2"] == "value2"
    
    def test_to_dict(self):
        """Test converting error context to dictionary."""
        ctx = ErrorContext(
            user_id="user123",
            request_id="req456",
            operation="test_operation"
        )
        ctx.add_context(test_key="test_value")
        
        result = ctx.to_dict()
        
        assert result["user_id"] == "user123"
        assert result["request_id"] == "req456"
        assert result["operation"] == "test_operation"
        assert result["context"]["test_key"] == "test_value"
        assert "correlation_id" in result
        assert "timestamp" in result


class TestErrorContextManager:
    """Test the error_context context manager."""
    
    def test_error_context_manager_success(self):
        """Test error context manager with successful operation."""
        with error_context(operation="test_op", user_id="user123") as ctx:
            assert ctx.operation == "test_op"
            assert ctx.user_id == "user123"
            assert UUID(ctx.correlation_id)
    
    @patch('shared_exceptions.logger')
    def test_error_context_manager_with_exception(self, mock_logger):
        """Test error context manager with exception."""
        test_exception = ValueError("Test error")
        
        with pytest.raises(ValueError):
            with error_context(operation="test_op", user_id="user123") as ctx:
                raise test_exception
        
        # Verify that the error was logged
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert call_args[0][0] == "Operation failed"
        assert call_args[1]["operation"] == "test_op"
        assert call_args[1]["user_id"] == "user123"
        assert call_args[1]["error_type"] == "ValueError"
        assert call_args[1]["error_message"] == "Test error"
    
    def test_error_context_manager_with_citypulse_exception(self):
        """Test error context manager with CityPulse exception."""
        with pytest.raises(CityPulseException) as exc_info:
            with error_context(operation="test_op") as ctx:
                raise CityPulseException("Test CityPulse error")
        
        # Check that correlation ID was added to the exception
        exception = exc_info.value
        assert hasattr(exception, 'correlation_id')
        assert UUID(exception.correlation_id)


class TestEnhancedCityPulseException:
    """Test the enhanced CityPulseException class."""
    
    def test_basic_exception_creation(self):
        """Test creating a basic CityPulse exception."""
        exc = CityPulseException("Test error")
        
        assert exc.message == "Test error"
        assert exc.error_code == ErrorCode.INTERNAL_ERROR
        assert isinstance(exc.details, dict)
        assert exc.cause is None
        assert UUID(exc.correlation_id)
        assert exc.user_id is None
        assert exc.request_id is None
        assert exc.operation is None
        assert isinstance(exc.timestamp, float)
    
    def test_exception_with_all_parameters(self):
        """Test creating exception with all parameters."""
        cause = ValueError("Original error")
        exc = CityPulseException(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": "test_field"},
            cause=cause,
            correlation_id="test-correlation",
            user_id="user123",
            request_id="req456",
            operation="test_operation"
        )
        
        assert exc.message == "Test error"
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.details == {"field": "test_field"}
        assert exc.cause == cause
        assert exc.correlation_id == "test-correlation"
        assert exc.user_id == "user123"
        assert exc.request_id == "req456"
        assert exc.operation == "test_operation"
    
    def test_exception_to_dict(self):
        """Test converting exception to dictionary."""
        exc = CityPulseException(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": "test_field"},
            user_id="user123",
            request_id="req456",
            operation="test_operation"
        )
        
        result = exc.to_dict()
        
        assert result["error_code"] == "VALIDATION_ERROR"
        assert result["message"] == "Test error"
        assert result["details"] == {"field": "test_field"}
        assert result["user_id"] == "user123"
        assert result["request_id"] == "req456"
        assert result["operation"] == "test_operation"
        assert "correlation_id" in result
        assert "timestamp" in result
    
    def test_exception_string_representation(self):
        """Test string representation of exception."""
        exc = CityPulseException(
            message="Test error",
            correlation_id="test-correlation"
        )
        
        str_repr = str(exc)
        assert "[test-correlation]" in str_repr
        assert "INTERNAL_ERROR" in str_repr
        assert "Test error" in str_repr
    
    @patch('shared_exceptions.logger')
    def test_exception_log_error(self, mock_logger):
        """Test logging exception with context."""
        exc = CityPulseException(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            user_id="user123",
            operation="test_operation"
        )
        
        exc.log_error()
        
        # Verify that the error was logged with correct context
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert call_args[0][0] == "CityPulse Exception"
        assert call_args[1]["error_code"] == "VALIDATION_ERROR"
        assert call_args[1]["message"] == "Test error"
        assert call_args[1]["user_id"] == "user123"
        assert call_args[1]["operation"] == "test_operation"


class TestSpecificExceptions:
    """Test specific exception classes."""
    
    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException(
            message="Invalid field",
            field="email",
            value="invalid-email"
        )
        
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.message == "Invalid field"
        assert "field" in exc.details
        assert "value" in exc.details
        assert exc.details["field"] == "email"
        assert exc.details["value"] == "invalid-email"
    
    def test_database_exception(self):
        """Test DatabaseException."""
        exc = DatabaseException(
            message="Database connection failed",
            operation="SELECT",
            table="users"
        )
        
        assert exc.error_code == ErrorCode.DATABASE_ERROR
        assert exc.message == "Database connection failed"
        assert "operation" in exc.details
        assert "table" in exc.details
    
    def test_external_service_exception(self):
        """Test ExternalServiceException."""
        exc = ExternalServiceException(
            message="Service unavailable",
            service="payment_gateway",
            status_code=503
        )
        
        assert exc.error_code == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert exc.message == "Service unavailable"
        assert "service" in exc.details
        assert "status_code" in exc.details
    
    def test_business_rule_exception(self):
        """Test BusinessRuleException."""
        exc = BusinessRuleException(
            message="Insufficient funds",
            rule="minimum_balance",
            context={"balance": 10, "required": 50}
        )
        
        assert exc.error_code == ErrorCode.BUSINESS_RULE_VIOLATION
        assert exc.message == "Insufficient funds"
        assert "rule" in exc.details
        assert "context" in exc.details


class TestErrorHandlingIntegration:
    """Integration tests for the error handling system."""
    
    @patch('shared_exceptions.logger')
    def test_full_error_flow(self, mock_logger):
        """Test complete error handling flow."""
        def failing_operation():
            raise ValueError("Something went wrong")
        
        with pytest.raises(ValueError):
            with error_context(
                operation="test_operation",
                user_id="user123",
                request_id="req456"
            ) as ctx:
                ctx.add_context(step="initialization", data={"key": "value"})
                failing_operation()
        
        # Verify comprehensive logging
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert call_args[0][0] == "Operation failed"
        assert call_args[1]["operation"] == "test_operation"
        assert call_args[1]["user_id"] == "user123"
        assert call_args[1]["request_id"] == "req456"
        assert call_args[1]["error_type"] == "ValueError"
        assert call_args[1]["context"]["step"] == "initialization"
        assert call_args[1]["context"]["data"]["key"] == "value"
    
    def test_nested_error_contexts(self):
        """Test nested error contexts."""
        with error_context(operation="outer_operation") as outer_ctx:
            outer_correlation_id = outer_ctx.correlation_id
            
            with error_context(operation="inner_operation") as inner_ctx:
                inner_correlation_id = inner_ctx.correlation_id
                
                # Each context should have its own correlation ID
                assert outer_correlation_id != inner_correlation_id
                assert UUID(outer_correlation_id)
                assert UUID(inner_correlation_id)
    
    def test_exception_correlation_propagation(self):
        """Test that correlation IDs propagate through exceptions."""
        with pytest.raises(CityPulseException) as exc_info:
            with error_context(operation="test_op") as ctx:
                original_correlation_id = ctx.correlation_id
                
                exc = CityPulseException("Test error")
                exc.correlation_id = original_correlation_id
                raise exc
        
        # Verify correlation ID is preserved
        exception = exc_info.value
        assert exception.correlation_id == original_correlation_id


class TestErrorCodeEnum:
    """Test the ErrorCode enumeration."""
    
    def test_error_code_values(self):
        """Test that error codes have correct values."""
        assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.DATABASE_ERROR == "DATABASE_ERROR"
        assert ErrorCode.EXTERNAL_SERVICE_ERROR == "EXTERNAL_SERVICE_ERROR"
        assert ErrorCode.BUSINESS_RULE_VIOLATION == "BUSINESS_RULE_VIOLATION"
    
    def test_error_code_completeness(self):
        """Test that all necessary error codes are defined."""
        required_codes = [
            "INTERNAL_ERROR", "INVALID_REQUEST", "UNAUTHORIZED", "FORBIDDEN",
            "NOT_FOUND", "CONFLICT", "RATE_LIMITED", "VALIDATION_ERROR",
            "DATABASE_ERROR", "EXTERNAL_SERVICE_ERROR", "BUSINESS_RULE_VIOLATION"
        ]
        
        available_codes = [code.value for code in ErrorCode]
        
        for required_code in required_codes:
            assert required_code in available_codes
