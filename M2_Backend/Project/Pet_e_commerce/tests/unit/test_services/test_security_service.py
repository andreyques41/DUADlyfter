"""
Unit tests for SecurityService.

Tests cover:
- Password hashing with bcrypt and pepper
- Password verification
- Security configuration (bcrypt rounds)
- Both class methods and convenience functions
- Edge cases and error handling
"""

import pytest
from unittest.mock import patch, MagicMock
from app.auth.services.security_service import (
    SecurityService,
    hash_password,
    verify_password,
    APP_PEPPER,
    SECURITY_CONFIG
)


@pytest.mark.unit
@pytest.mark.auth
class TestSecurityService:
    """Test SecurityService class methods."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = SecurityService.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_applies_pepper(self, mocker):
        """Test that hash_password adds application pepper."""
        password = "test_password"
        
        # Mock bcrypt functions
        mock_salt = b'$2b$14$mockSaltValue1234567890'
        mock_hashed = b'$2b$14$mockedHashedPasswordValue'
        
        mocker.patch('bcrypt.gensalt', return_value=mock_salt)
        mock_hashpw = mocker.patch('bcrypt.hashpw', return_value=mock_hashed)
        
        SecurityService.hash_password(password)
        
        # Verify bcrypt.hashpw was called with peppered password
        expected_peppered = (password + APP_PEPPER).encode('utf-8')
        mock_hashpw.assert_called_once_with(expected_peppered, mock_salt)
    
    def test_hash_password_uses_configured_rounds(self, mocker):
        """Test that hash_password uses configured bcrypt rounds."""
        password = "test_password"
        
        mock_gensalt = mocker.patch('bcrypt.gensalt', return_value=b'salt')
        mocker.patch('bcrypt.hashpw', return_value=b'hashed')
        
        SecurityService.hash_password(password)
        
        # Verify gensalt called with configured rounds
        mock_gensalt.assert_called_once_with(rounds=SECURITY_CONFIG['bcrypt_rounds'])
    
    def test_hash_password_produces_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "same_password"
        
        hash1 = SecurityService.hash_password(password)
        hash2 = SecurityService.hash_password(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
    
    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "correct_password_123"
        hashed = SecurityService.hash_password(password)
        
        result = SecurityService.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_failure(self):
        """Test failed password verification with wrong password."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        hashed = SecurityService.hash_password(correct_password)
        
        result = SecurityService.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_applies_pepper(self, mocker):
        """Test that verify_password adds application pepper."""
        password = "test_password"
        hashed = "hashed_password"
        
        # Mock bcrypt.checkpw
        mock_checkpw = mocker.patch('bcrypt.checkpw', return_value=True)
        
        SecurityService.verify_password(password, hashed)
        
        # Verify checkpw was called with peppered password
        expected_peppered = (password + APP_PEPPER).encode('utf-8')
        mock_checkpw.assert_called_once_with(
            expected_peppered,
            hashed.encode('utf-8')
        )
    
    def test_verify_password_with_empty_password(self):
        """Test verification with empty password."""
        empty_password = ""
        hashed = SecurityService.hash_password("actual_password")
        
        result = SecurityService.verify_password(empty_password, hashed)
        
        assert result is False
    
    def test_hash_password_with_special_characters(self):
        """Test hashing password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        
        hashed = SecurityService.hash_password(password)
        
        assert isinstance(hashed, str)
        # Verify it can be verified
        assert SecurityService.verify_password(password, hashed) is True
    
    def test_hash_password_with_unicode(self):
        """Test hashing password with unicode characters."""
        password = "pässwörd_日本語_🔒"
        
        hashed = SecurityService.hash_password(password)
        
        assert isinstance(hashed, str)
        assert SecurityService.verify_password(password, hashed) is True
    
    def test_verify_password_timing_safe(self, mocker):
        """Test that password verification uses timing-safe comparison."""
        password = "test_password"
        hashed = "hashed_password"
        
        # Mock bcrypt.checkpw to verify it's being used
        mock_checkpw = mocker.patch('bcrypt.checkpw', return_value=False)
        
        result = SecurityService.verify_password(password, hashed)
        
        # bcrypt.checkpw is timing-safe by design
        assert mock_checkpw.called
        assert result is False


@pytest.mark.unit
@pytest.mark.auth
class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_hash_password_convenience_function(self):
        """Test hash_password convenience function."""
        password = "test_password"
        
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password_convenience_function(self):
        """Test verify_password convenience function."""
        password = "test_password"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_convenience_functions_match_class_methods(self):
        """Test that convenience functions produce same results as class methods."""
        password = "test_password_123"
        
        # Hash using both methods
        class_hashed = SecurityService.hash_password(password)
        func_hashed = hash_password(password)
        
        # Both hashes should verify the password
        assert SecurityService.verify_password(password, class_hashed) is True
        assert verify_password(password, func_hashed) is True
        
        # Cross-verification should also work
        assert SecurityService.verify_password(password, func_hashed) is True
        assert verify_password(password, class_hashed) is True


@pytest.mark.unit
@pytest.mark.auth
class TestSecurityConfiguration:
    """Test security configuration settings."""
    
    def test_app_pepper_exists(self):
        """Test that APP_PEPPER is configured."""
        assert APP_PEPPER is not None
        assert isinstance(APP_PEPPER, str)
        assert len(APP_PEPPER) > 0
    
    def test_bcrypt_rounds_configured(self):
        """Test that bcrypt rounds are configured."""
        assert 'bcrypt_rounds' in SECURITY_CONFIG
        assert isinstance(SECURITY_CONFIG['bcrypt_rounds'], int)
        assert SECURITY_CONFIG['bcrypt_rounds'] >= 10  # Minimum recommended
    
    def test_bcrypt_rounds_value_reasonable(self):
        """Test that bcrypt rounds are in reasonable range."""
        rounds = SECURITY_CONFIG['bcrypt_rounds']
        
        # Too low is insecure, too high is impractical
        assert 10 <= rounds <= 20


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashingEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_very_long_password(self):
        """Test hashing very long password."""
        password = "a" * 1000  # 1000 character password
        
        hashed = SecurityService.hash_password(password)
        
        assert isinstance(hashed, str)
        assert SecurityService.verify_password(password, hashed) is True
    
    def test_password_with_null_bytes(self):
        """Test password containing null bytes."""
        password = "password\x00with\x00nulls"
        
        hashed = SecurityService.hash_password(password)
        
        # Should handle null bytes properly
        assert isinstance(hashed, str)
    
    def test_verify_with_malformed_hash(self, mocker):
        """Test verification with malformed hash."""
        password = "test_password"
        malformed_hash = "not_a_valid_bcrypt_hash"
        
        # bcrypt.checkpw will raise ValueError for invalid hash
        mocker.patch('bcrypt.checkpw', side_effect=ValueError("Invalid salt"))
        
        with pytest.raises(ValueError):
            SecurityService.verify_password(password, malformed_hash)
    
    def test_hash_empty_password(self):
        """Test hashing empty password (should still work)."""
        password = ""
        
        hashed = SecurityService.hash_password(password)
        
        assert isinstance(hashed, str)
        # Empty password with pepper should still hash
        assert SecurityService.verify_password(password, hashed) is True
    
    def test_case_sensitivity(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123"
        hashed = SecurityService.hash_password(password)
        
        # Different case should fail
        assert SecurityService.verify_password("testpassword123", hashed) is False
        assert SecurityService.verify_password("TESTPASSWORD123", hashed) is False
        
        # Exact match should succeed
        assert SecurityService.verify_password("TestPassword123", hashed) is True
