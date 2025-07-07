"""
Basic test to verify pytest configuration is working
"""

import pytest
import sys
import os

def test_python_version():
    """Test that we're running Python 3.11+"""
    assert sys.version_info >= (3, 11)

def test_basic_math():
    """Test basic mathematical operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5

def test_string_operations():
    """Test string operations"""
    test_string = "CityPulse"
    assert test_string.lower() == "citypulse"
    assert len(test_string) == 9
    assert "City" in test_string

def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert test_list[0] == 1
    assert test_list[-1] == 5
    assert sum(test_list) == 15

def test_dict_operations():
    """Test dictionary operations"""
    test_dict = {"name": "CityPulse", "version": "1.0", "type": "testing"}
    assert test_dict["name"] == "CityPulse"
    assert "version" in test_dict
    assert len(test_dict) == 3

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_parametrized(input, expected):
    """Test parametrized test cases"""
    assert input * 2 == expected

def test_environment_variables():
    """Test environment variable access"""
    # This should work in any environment
    path = os.environ.get('PATH')
    assert path is not None
    assert len(path) > 0

class TestBasicClass:
    """Test class-based testing"""
    
    def test_class_method(self):
        """Test method in a test class"""
        assert True
    
    def test_setup_method(self):
        """Test that setup works"""
        self.test_value = "test"
        assert self.test_value == "test"
