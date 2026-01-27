# Test Instructions

## Setup

1. Install test dependencies:
```bash
pip install -r requirements.txt
playwright install
```

2. Run the tests:
```bash
pytest tests/test_todos.py -v
```

## Test Coverage

The test suite includes:
- **test_create_task**: Verifies that new tasks can be created
- **test_complete_task**: Tests marking a task as complete
- **test_delete_task**: Tests deleting a task
- **test_create_multiple_tasks**: Tests creating multiple tasks in sequence
- **test_toggle_task_completion**: Tests toggling task completion status

## Running Specific Tests

```bash
# Run a specific test
pytest tests/test_todos.py::test_create_task -v

# Run with browser visible (headed mode)
pytest tests/test_todos.py --headed

# Run tests in a specific browser
pytest tests/test_todos.py --browser chromium
pytest tests/test_todos.py --browser firefox
pytest tests/test_todos.py --browser webkit
```
