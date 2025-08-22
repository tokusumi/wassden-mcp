# Similar Cases Investigation

## Known Issues with pytest + AsyncMock + CI

### 1. pytest-xdist + AsyncMock Issues
- **GitHub Issue**: pytest-dev/pytest-xdist#721
- **Problem**: AsyncMock not properly serialized across worker processes
- **Solution**: Use `pytest-mock` plugin or disable xdist for async tests

### 2. Module Import Order Issues in CI
- **Problem**: Different import order in CI vs local
- **Cause**: Different PYTHONPATH or package installation order
- **Solution**: Ensure consistent import paths

### 3. Python 3.12 + unittest.mock Changes
- **GitHub Issue**: python/cpython#103960
- **Problem**: Changes in mock behavior in Python 3.12
- **Solution**: Update mock usage patterns

### 4. CI Environment Differences
- **Problem**: Different multiprocessing behavior on Linux vs macOS
- **Cause**: fork() vs spawn differences
- **Solution**: Set multiprocessing start method explicitly

## Investigation Commands

```bash
# Test in CI-like environment
docker run -it python:3.12.11-slim bash
pip install pytest pytest-xdist
# ... reproduce issue

# Check mock behavior differences
python -c "import unittest.mock; print(unittest.mock.__version__)"
python -c "import sys; print(sys.version_info)"

# Check multiprocessing behavior
python -c "import multiprocessing; print(multiprocessing.get_start_method())"
```

## Debugging Strategies

1. **Direct function replacement**: Instead of @patch, replace function directly
2. **Module-level mocking**: Mock at module level, not function level  
3. **Fixture-based mocking**: Use pytest fixtures instead of decorators
4. **Import timing**: Ensure imports happen after patches are applied

## Potential Solutions to Test

1. **Use pytest-mock plugin**:
```python
def test_with_pytest_mock(mocker):
    mock_func = mocker.patch("wassden.clis.experiment._run_experiment_async")
    # ... test code
```

2. **Manual module patching**:
```python
import wassden.clis.experiment
wassden.clis.experiment._run_experiment_async = AsyncMock()
```

3. **Monkeypatch fixture**:
```python
def test_with_monkeypatch(monkeypatch):
    mock_func = AsyncMock()
    monkeypatch.setattr("wassden.clis.experiment._run_experiment_async", mock_func)
```