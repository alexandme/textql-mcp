# TextQL Code Quality Commands in Conda Environment

The following commands should be run within the textql conda environment:

## Code Quality Commands

```bash
# Format code (before commits)
conda run -n textql python -m black . tests/

# Lint code (before commits)
conda run -n textql python -m ruff check . tests/

# Run all tests
conda run -n textql python -m pytest tests/

# Run specific test
conda run -n textql python -m pytest tests/path_to_test.py::TestClass::test_function
```

Alternatively, activate the conda environment first, then run:
```bash
# Activate environment
conda activate textql

# Then run commands
python -m black . tests/
python -m ruff check . tests/
python -m pytest tests/
```

## Note on Environment Setup

When setting up the environment, make sure all dependencies are installed, including any required for testing:

```bash
# Create and activate environment
conda create -n textql python=3.10 -y
conda activate textql

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install the package in development mode
```

If you encounter import errors when running tests, you may need to install additional dependencies or ensure the package is installed in development mode.
