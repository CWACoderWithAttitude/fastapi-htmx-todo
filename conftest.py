import pytest
import multiprocessing
import time
import uvicorn
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def fastapi_server():
    """Start FastAPI server in a separate process for testing."""
    def run_server():
        uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="error")

    # Start server in a separate process
    process = multiprocessing.Process(target=run_server, daemon=True)
    process.start()

    # Wait for server to start
    time.sleep(2)

    yield "http://127.0.0.1:8000"

    # Cleanup
    process.terminate()
    process.join()


@pytest.fixture(scope="function")
def page(page: Page, fastapi_server):
    """Navigate to the app before each test."""
    page.goto(fastapi_server)
    # Wait for the page to load and todos to be fetched
    page.wait_for_selector("#todos")
    yield page
