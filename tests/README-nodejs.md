# Todo Application Tests

This directory contains comprehensive test suites for the FastAPI + HTMX Todo application using Node.js and Playwright.

## Test Files

### Node.js Tests (Playwright)

- **`todos.spec.js`** - Main test suite covering core functionality:
  - Creating todos
  - Editing todos
  - Toggling completion status
  - Deleting todos
  - Edge cases (special characters, long text, duplicates)
  - Order preservation

- **`advanced.spec.js`** - Advanced scenarios and workflows:
  - Empty input handling
  - Rapid operations
  - Complete user workflows
  - Unicode and emoji support
  - Network delay handling
  - HTMX behavior verification

### Python Tests (Existing)

- **`test_todos.py`** - Python-based Playwright tests for the same functionality

## Setup

### Prerequisites

- Node.js (v18 or later recommended)
- Python 3.x
- FastAPI application running

### Install Dependencies

#### For Node.js tests:

```bash
npm install
```

This will install:
- `@playwright/test` - Playwright testing framework
- `playwright` - Browser automation library

#### Install Playwright browsers:

```bash
npx playwright install
```

## Running Tests

### Node.js Tests

Run all tests:
```bash
npm test
```

Run tests in headed mode (see browser):
```bash
npm run test:headed
```

Run tests with UI mode (interactive):
```bash
npm run test:ui
```

Run tests in debug mode:
```bash
npm run test:debug
```

Run tests in specific browser:
```bash
npm run test:chromium
npm run test:firefox
npm run test:webkit
```

Run specific test file:
```bash
npx playwright test tests/todos.spec.js
```

Run specific test by name:
```bash
npx playwright test -g "should create a new todo"
```

### Python Tests

```bash
pytest tests/test_todos.py -v
```

## Test Configuration

The Playwright configuration is defined in `playwright.config.js`:

- **Base URL**: http://127.0.0.1:8000
- **Browsers**: Chromium, Firefox, WebKit
- **Reporters**: HTML report (generated in `playwright-report/`)
- **Screenshots**: Captured on failure
- **Traces**: Captured on first retry
- **Web Server**: Automatically starts FastAPI server before tests

## Test Coverage

The test suite covers:

### Core Functionality
✅ Page loading and initial state  
✅ Creating single and multiple todos  
✅ Editing todo text  
✅ Toggling todo completion status  
✅ Deleting todos  
✅ Empty list handling  

### Edge Cases
✅ Empty input validation  
✅ Special characters in todo text  
✅ Long text handling (200+ characters)  
✅ Duplicate todo texts  
✅ Unicode and emoji support  
✅ Whitespace-only input  
✅ Order preservation  

### User Workflows
✅ Complete workflow (create → edit → toggle → delete)  
✅ Rapid todo creation  
✅ Multiple delete operations  
✅ Editing completed todos  
✅ Deleting completed todos  

### Technical
✅ HTMX swap behavior  
✅ Network delay handling  
✅ Form reset after submission  

## Viewing Test Results

After running tests, you can view the HTML report:

```bash
npx playwright show-report
```

This opens an interactive report showing:
- Test results (passed/failed)
- Screenshots of failures
- Execution traces
- Test duration
- Browser compatibility

## CI/CD Integration

The tests are configured to work in CI environments:

- Retries: 2 retries on CI, 0 locally
- Workers: 1 worker on CI (parallel locally)
- Server: Automatically starts and stops
- Screenshots and traces: Captured on failure

Example GitHub Actions workflow:

```yaml
- name: Install dependencies
  run: npm ci

- name: Install Playwright browsers
  run: npx playwright install --with-deps

- name: Run tests
  run: npm test
```

## Debugging Tests

### Debug mode:
```bash
npm run test:debug
```

This opens Playwright Inspector where you can:
- Step through test execution
- Inspect element locators
- View console logs
- Take screenshots

### Headed mode:
```bash
npm run test:headed
```

See the browser while tests run.

### UI mode:
```bash
npm run test:ui
```

Interactive test runner with:
- Watch mode
- Time travel debugging
- Live trace viewer

## Best Practices

1. **Wait for HTMX**: Use `page.waitForTimeout(500)` after HTMX operations
2. **Locator specificity**: Use precise locators to avoid flaky tests
3. **Assertions**: Use Playwright's built-in `expect` for auto-retrying assertions
4. **Isolation**: Each test starts with a fresh page state
5. **Cleanup**: No manual cleanup needed - server restarts between test files

## Troubleshooting

### Server not starting
- Check if port 8000 is available
- Ensure `make run` command works manually
- Check FastAPI dependencies are installed

### Tests timing out
- Increase timeout in `playwright.config.js`
- Check network conditions
- Verify HTMX is loading correctly

### Flaky tests
- Increase wait times after HTMX operations
- Use more specific locators
- Check for race conditions in async operations

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add descriptive test names
3. Group related tests in `describe` blocks
4. Include assertions for both positive and negative cases
5. Document any special setup or teardown needs
