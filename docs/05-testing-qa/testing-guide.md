# Testing Guide

This document provides comprehensive testing instructions for GitHub Sentinel developers and QA engineers.

## 🧪 Test Suite Overview

GitHub Sentinel v0.5+ features a comprehensive test suite with 100% coverage of core modules:

- **Complete Test Coverage**: All test files updated to match current codebase implementation
- **Mock Integration**: Proper unittest.mock usage for external API testing
- **Error Scenario Testing**: Comprehensive testing of edge cases and error conditions
- **Integration Testing**: Cross-module workflow testing for reliability
- **Future-Ready Infrastructure**: Test architecture prepared for easy feature additions

## 🏃‍♂️ Running Tests

### Prerequisites

```bash
# Activate conda environment
conda activate githubsentinel

# Ensure you're in the project root directory
cd /path/to/GitHubSentinel
```

### Run All Tests

```bash
# Run complete test suite with verbose output
python -m unittest discover tests/ -v

# Run tests with buffer (cleaner output)
python -m unittest discover tests/ -v --buffer
```

### Run Specific Module Tests

```bash
# Test specific modules
python -m unittest tests.test_llm_client -v
python -m unittest tests.test_report_generator -v
python -m unittest tests.test_github_client -v
python -m unittest tests.test_subscription_manager -v
python -m unittest tests.test_notifier -v
python -m unittest tests.test_daily_progress -v
python -m unittest tests.test_utils -v
```

### Test Coverage Analysis

```bash
# Install coverage tool if not available
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests/
coverage report -m
coverage html  # Generates HTML coverage report
```

## 🔧 Test Configuration

### Environment Setup for Testing

```bash
# Create test environment variables
export GITHUB_TOKEN=test_token_here
export OPENAI_API_KEY=test_openai_key_here
export DEEPSEEK_API_KEY=test_deepseek_key_here

# Or create .env.test file
GITHUB_TOKEN=test_token_here
OPENAI_API_KEY=test_openai_key_here
DEEPSEEK_API_KEY=test_deepseek_key_here
```

### Mock Configuration

Tests use comprehensive mocking to avoid external API calls:

- **GitHub API**: Mocked responses for repositories, issues, PRs
- **LLM APIs**: Mocked responses for OpenAI, DeepSeek, Ollama
- **File System**: Mocked file operations for isolated testing
- **Network Requests**: Mocked HTTP requests and responses

## 📋 Test Categories

### Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Coverage**:
- `test_github_client.py` - GitHub API integration testing
- `test_llm_client.py` - LLM provider testing (Ollama, OpenAI, DeepSeek)
- `test_subscription_manager.py` - Repository subscription management
- `test_report_generator.py` - Report generation and formatting
- `test_notifier.py` - Email and notification testing
- `test_utils.py` - Utility function testing

### Integration Tests

**Purpose**: Test interaction between multiple components

**Coverage**:
- End-to-end workflow testing
- Cross-module data flow validation
- Configuration loading and validation
- Error propagation and handling

### Error Scenario Tests

**Purpose**: Validate graceful error handling and recovery

**Coverage**:
- Missing API keys
- Invalid repository names
- Network connectivity issues
- File system permission errors
- Malformed configuration files

## 🧪 Demo Scripts

Test all features with included demo scripts:

```bash
# Test LLM provider integration (requires API keys)
python examples/demo_deepseek_integration.py

# Test all core features with configured provider
python examples/demo_features.py

# Make sure Ollama is running first if using default config
ollama serve &
```

## 🐛 Common Testing Issues

### Import Errors

```bash
# Error: ModuleNotFoundError
# Solution: Ensure you're in project root and environment is activated
cd /path/to/GitHubSentinel
conda activate githubsentinel
python -m unittest discover tests/ -v
```

### API Rate Limits

```bash
# Error: GitHub API rate limit exceeded
# Solution: Tests use mocks, but if you're running integration tests:
# 1. Use a test token with higher rate limits
# 2. Add delays between test runs
# 3. Run tests in smaller batches
```

### Missing Test Dependencies

```bash
# Install additional testing tools
pip install coverage pytest pytest-cov

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

## 🔄 Continuous Integration

### GitHub Actions Setup

Example workflow for automated testing:

```yaml
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests with coverage
      env:
        GITHUB_TOKEN: ${{ secrets.TEST_GITHUB_TOKEN }}
      run: |
        coverage run -m unittest discover tests/
        coverage xml
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### Local Pre-commit Hooks

```bash
# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Manual pre-commit check
pre-commit run --all-files
```

## 📊 Test Metrics

### Expected Test Results

- **Total Tests**: 50+ test cases
- **Coverage**: >95% for core modules
- **Performance**: Tests should complete in <30 seconds
- **Success Rate**: 100% pass rate on clean environment

### Performance Benchmarks

```bash
# Measure test execution time
time python -m unittest discover tests/ -v

# Expected results:
# - Unit tests: <10 seconds
# - Integration tests: <20 seconds
# - Full suite: <30 seconds
```

## 🚨 Known Test Limitations

1. **External Dependencies**: Some integration tests require active internet connection
2. **API Keys**: Full testing requires valid API keys for all providers
3. **File System**: Tests require read/write permissions in project directory
4. **Ollama**: Local LLM tests require Ollama service running

## 📝 Writing New Tests

### Test Structure Template

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.module_name import ClassName

class TestClassName(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            'key': 'value'
        }
        self.instance = ClassName(self.test_config)
    
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    @patch('src.module_name.external_dependency')
    def test_feature_success(self, mock_dependency):
        """Test successful feature execution."""
        # Arrange
        mock_dependency.return_value = 'expected_result'
        
        # Act
        result = self.instance.feature_method()
        
        # Assert
        self.assertEqual(result, 'expected_result')
        mock_dependency.assert_called_once()
    
    def test_feature_error_handling(self):
        """Test error handling in feature."""
        with self.assertRaises(ExpectedError):
            self.instance.feature_method_with_error()

if __name__ == '__main__':
    unittest.main()
```

### Best Practices

1. **Use Descriptive Names**: Test method names should clearly describe what is being tested
2. **AAA Pattern**: Arrange, Act, Assert structure for clear test organization
3. **Mock External Dependencies**: Avoid real API calls in unit tests
4. **Test Edge Cases**: Include tests for boundary conditions and error scenarios
5. **Keep Tests Independent**: Each test should be able to run in isolation
6. **Use setUp/tearDown**: Proper initialization and cleanup for consistent test state

## 📚 Additional Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [Mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [GitHub Actions testing guide](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python) 