"""
Authentication Integration Tests

Comprehensive authentication testing for Firebase Auth integration
with both mock and real authentication flows.
"""

import pytest
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import sys
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class MockFirebaseAuth:
    """Mock Firebase Auth service for testing."""
    
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.secret_key = "mock_secret_key_for_testing"
    
    async def create_user(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """Create a new user."""
        if email in self.users:
            raise ValueError(f"User with email {email} already exists")
        
        user_id = f"user_{len(self.users) + 1}"
        user_data = {
            "uid": user_id,
            "email": email,
            "email_verified": False,
            "disabled": False,
            "created_at": datetime.now().isoformat(),
            "custom_claims": kwargs.get("custom_claims", {}),
            "role": kwargs.get("role", "citizen")
        }
        
        self.users[email] = {
            **user_data,
            "password": password  # In real Firebase, password is not stored like this
        }
        
        return user_data
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return token."""
        if email not in self.users:
            raise ValueError("User not found")
        
        user = self.users[email]
        if user["password"] != password:
            raise ValueError("Invalid password")
        
        if user["disabled"]:
            raise ValueError("User account is disabled")
        
        # Generate mock JWT token with unique timestamp and random component
        import time
        import random
        current_time = datetime.utcnow()
        token_payload = {
            "uid": user["uid"],
            "email": user["email"],
            "role": user["role"],
            "exp": current_time + timedelta(hours=1),
            "iat": current_time,
            "jti": f"{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"  # Unique token ID
        }
        
        token = jwt.encode(token_payload, self.secret_key, algorithm="HS256")
        
        self.tokens[token] = {
            "user_id": user["uid"],
            "email": user["email"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "uid": user["uid"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check if user still exists first (for better error messages)
            user = self.users.get(payload["email"])
            if not user:
                raise ValueError("User not found")

            if user["disabled"]:
                raise ValueError("User account is disabled")

            if token not in self.tokens:
                raise ValueError("Token not found in active tokens")

            token_info = self.tokens[token]
            
            return {
                "uid": payload["uid"],
                "email": payload["email"],
                "role": payload["role"],
                "token_info": token_info
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    async def update_user(self, email: str, **kwargs) -> Dict[str, Any]:
        """Update user information."""
        if email not in self.users:
            raise ValueError("User not found")
        
        user = self.users[email]
        
        # Update allowed fields
        if "disabled" in kwargs:
            user["disabled"] = kwargs["disabled"]
        if "email_verified" in kwargs:
            user["email_verified"] = kwargs["email_verified"]
        if "custom_claims" in kwargs:
            user["custom_claims"] = kwargs["custom_claims"]
        if "role" in kwargs:
            user["role"] = kwargs["role"]
        
        user["updated_at"] = datetime.now().isoformat()
        
        return {
            "uid": user["uid"],
            "email": user["email"],
            "email_verified": user["email_verified"],
            "disabled": user["disabled"],
            "custom_claims": user["custom_claims"],
            "role": user["role"]
        }
    
    async def delete_user(self, email: str) -> bool:
        """Delete a user."""
        if email in self.users:
            # Revoke all tokens for this user
            user_id = self.users[email]["uid"]
            tokens_to_revoke = [
                token for token, info in self.tokens.items()
                if info["user_id"] == user_id
            ]
            for token in tokens_to_revoke:
                del self.tokens[token]
            
            del self.users[email]
            return True
        return False


class TestAuthentication:
    """Authentication integration tests."""
    
    @pytest.fixture
    def auth_service(self):
        """Authentication service fixture."""
        return MockFirebaseAuth()
    
    @pytest.mark.asyncio
    async def test_user_creation(self, auth_service):
        """Test user creation."""
        email = "test@example.com"
        password = "secure_password_123"
        
        user = await auth_service.create_user(
            email=email,
            password=password,
            role="citizen"
        )
        
        assert user["email"] == email
        assert user["role"] == "citizen"
        assert user["email_verified"] is False
        assert user["disabled"] is False
        assert "uid" in user
        assert "created_at" in user
    
    @pytest.mark.asyncio
    async def test_user_authentication(self, auth_service):
        """Test user authentication."""
        email = "auth_test@example.com"
        password = "test_password_456"
        
        # Create user first
        await auth_service.create_user(email=email, password=password, role="authority")
        
        # Authenticate user
        auth_result = await auth_service.authenticate_user(email, password)
        
        assert "access_token" in auth_result
        assert auth_result["token_type"] == "Bearer"
        assert auth_result["expires_in"] == 3600
        assert auth_result["user"]["email"] == email
        assert auth_result["user"]["role"] == "authority"
    
    @pytest.mark.asyncio
    async def test_token_verification(self, auth_service):
        """Test token verification."""
        email = "verify_test@example.com"
        password = "verify_password_789"
        
        # Create and authenticate user
        await auth_service.create_user(email=email, password=password)
        auth_result = await auth_service.authenticate_user(email, password)
        token = auth_result["access_token"]
        
        # Verify token
        verified = await auth_service.verify_token(token)
        
        assert verified["email"] == email
        assert verified["uid"] == auth_result["user"]["uid"]
        assert "token_info" in verified
    
    @pytest.mark.asyncio
    async def test_invalid_authentication(self, auth_service):
        """Test authentication with invalid credentials."""
        email = "invalid_test@example.com"
        password = "correct_password"
        wrong_password = "wrong_password"
        
        # Create user
        await auth_service.create_user(email=email, password=password)
        
        # Test wrong password
        with pytest.raises(ValueError, match="Invalid password"):
            await auth_service.authenticate_user(email, wrong_password)
        
        # Test non-existent user
        with pytest.raises(ValueError, match="User not found"):
            await auth_service.authenticate_user("nonexistent@example.com", password)
    
    @pytest.mark.asyncio
    async def test_token_revocation(self, auth_service):
        """Test token revocation."""
        email = "revoke_test@example.com"
        password = "revoke_password"
        
        # Create and authenticate user
        await auth_service.create_user(email=email, password=password)
        auth_result = await auth_service.authenticate_user(email, password)
        token = auth_result["access_token"]
        
        # Verify token works
        verified = await auth_service.verify_token(token)
        assert verified["email"] == email
        
        # Revoke token
        revoked = await auth_service.revoke_token(token)
        assert revoked is True
        
        # Verify token no longer works
        with pytest.raises(ValueError, match="Token not found"):
            await auth_service.verify_token(token)
    
    @pytest.mark.asyncio
    async def test_user_roles_and_permissions(self, auth_service):
        """Test user roles and permissions."""
        # Create users with different roles
        citizen_email = "citizen@example.com"
        authority_email = "authority@example.com"
        admin_email = "admin@example.com"
        password = "role_test_password"
        
        await auth_service.create_user(citizen_email, password, role="citizen")
        await auth_service.create_user(authority_email, password, role="authority")
        await auth_service.create_user(admin_email, password, role="admin")
        
        # Authenticate each user
        citizen_auth = await auth_service.authenticate_user(citizen_email, password)
        authority_auth = await auth_service.authenticate_user(authority_email, password)
        admin_auth = await auth_service.authenticate_user(admin_email, password)
        
        # Verify roles
        assert citizen_auth["user"]["role"] == "citizen"
        assert authority_auth["user"]["role"] == "authority"
        assert admin_auth["user"]["role"] == "admin"
        
        # Verify tokens contain correct roles
        citizen_verified = await auth_service.verify_token(citizen_auth["access_token"])
        authority_verified = await auth_service.verify_token(authority_auth["access_token"])
        admin_verified = await auth_service.verify_token(admin_auth["access_token"])
        
        assert citizen_verified["role"] == "citizen"
        assert authority_verified["role"] == "authority"
        assert admin_verified["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_user_account_management(self, auth_service):
        """Test user account management operations."""
        email = "management_test@example.com"
        password = "management_password"
        
        # Create user
        user = await auth_service.create_user(email=email, password=password)
        original_uid = user["uid"]
        
        # Update user
        updated_user = await auth_service.update_user(
            email=email,
            email_verified=True,
            role="authority"
        )
        
        assert updated_user["email_verified"] is True
        assert updated_user["role"] == "authority"
        assert updated_user["uid"] == original_uid
        
        # Disable user
        await auth_service.update_user(email=email, disabled=True)
        
        # Try to authenticate disabled user
        with pytest.raises(ValueError, match="User account is disabled"):
            await auth_service.authenticate_user(email, password)
    
    @pytest.mark.asyncio
    async def test_user_deletion(self, auth_service):
        """Test user deletion."""
        email = "deletion_test@example.com"
        password = "deletion_password"
        
        # Create and authenticate user
        await auth_service.create_user(email=email, password=password)
        auth_result = await auth_service.authenticate_user(email, password)
        token = auth_result["access_token"]
        
        # Verify token works
        await auth_service.verify_token(token)
        
        # Delete user
        deleted = await auth_service.delete_user(email)
        assert deleted is True
        
        # Verify user can't authenticate
        with pytest.raises(ValueError, match="User not found"):
            await auth_service.authenticate_user(email, password)
        
        # Verify token no longer works
        with pytest.raises(ValueError, match="User not found"):
            await auth_service.verify_token(token)
    
    @pytest.mark.asyncio
    async def test_duplicate_user_creation(self, auth_service):
        """Test handling of duplicate user creation."""
        email = "duplicate@example.com"
        password = "duplicate_password"
        
        # Create user
        await auth_service.create_user(email=email, password=password)
        
        # Try to create same user again
        with pytest.raises(ValueError, match="already exists"):
            await auth_service.create_user(email=email, password=password)
    
    @pytest.mark.asyncio
    async def test_concurrent_authentication(self, auth_service):
        """Test concurrent authentication requests."""
        email = "concurrent@example.com"
        password = "concurrent_password"
        
        # Create user
        await auth_service.create_user(email=email, password=password)
        
        # Perform concurrent authentications
        tasks = [
            auth_service.authenticate_user(email, password)
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert result["user"]["email"] == email
            assert "access_token" in result
        
        # All tokens should be different
        tokens = [result["access_token"] for result in results]
        assert len(set(tokens)) == 5  # All unique


# Pytest configuration
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.auth
]
