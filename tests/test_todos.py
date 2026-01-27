"""
Playwright end-to-end tests for the FastAPI+HTMX Todo application.
Tests cover creating, completing, and deleting tasks.
"""
import re
from playwright.sync_api import Page, expect


def test_create_task(page: Page):
    """Test creating a new todo task."""
    # Get initial todo count
    initial_todos = page.locator("#todos li").count()

    # Fill in the todo input and create a task
    todo_input = page.locator('input[name="todo"]')
    todo_input.fill("Buy groceries")

    # Click the Create button
    page.locator('button:has-text("Create")').click()

    # Wait for HTMX request to complete
    page.wait_for_timeout(500)

    # Verify the new todo appears in the list
    todos = page.locator("#todos li")
    expect(todos).to_have_count(initial_todos + 1)

    # Verify the todo text is present
    expect(page.locator('#todos li:has-text("Buy groceries")')).to_be_visible()

    # Verify input is cleared after submission
    expect(todo_input).to_have_value("")


def test_complete_task(page: Page):
    """Test marking a task as complete."""
    # First, create a task
    todo_input = page.locator('input[name="todo"]')
    todo_input.fill("Complete this task")
    page.locator('button:has-text("Create")').click()
    page.wait_for_timeout(500)

    # Find the checkbox for the newly created task
    task_li = page.locator('#todos li:has-text("Complete this task")')
    checkbox = task_li.locator('input[type="checkbox"]')

    # Verify checkbox is initially unchecked
    expect(checkbox).not_to_be_checked()

    # Click the checkbox to mark task as complete
    checkbox.click()
    page.wait_for_timeout(500)

    # Verify checkbox is now checked
    expect(checkbox).to_be_checked()

    # Verify the text input has line-through style (completed)
    text_input = task_li.locator('input[name="text"]')
    expect(text_input).to_have_attribute(
        "style", re.compile("text-decoration: line-through"))
    expect(text_input).to_be_disabled()


def test_delete_task(page: Page):
    """Test deleting a task."""
    # First, create a task
    todo_input = page.locator('input[name="todo"]')
    todo_input.fill("Task to delete")
    page.locator('button:has-text("Create")').click()
    page.wait_for_timeout(500)

    # Get the count before deletion
    todos_before = page.locator("#todos li").count()

    # Find and click the delete button for the task
    task_li = page.locator('#todos li:has-text("Task to delete")')
    delete_button = task_li.locator('input[type="button"][value="❌"]')
    delete_button.click()
    page.wait_for_timeout(500)

    # Verify the task has been removed
    todos_after = page.locator("#todos li").count()
    expect(todos_after).toBe(todos_before - 1)

    # Verify the specific task is no longer visible
    expect(page.locator('#todos li:has-text("Task to delete")')).not_to_be_visible()


def test_create_multiple_tasks(page: Page):
    """Test creating multiple tasks."""
    tasks = ["Task 1", "Task 2", "Task 3"]

    todo_input = page.locator('input[name="todo"]')

    for task_text in tasks:
        todo_input.fill(task_text)
        page.locator('button:has-text("Create")').click()
        page.wait_for_timeout(500)

    # Verify all tasks are visible
    for task_text in tasks:
        expect(page.locator(
            f'#todos li:has-text("{task_text}")')).to_be_visible()


def test_toggle_task_completion(page: Page):
    """Test toggling a task between complete and incomplete."""
    # Create a task
    todo_input = page.locator('input[name="todo"]')
    todo_input.fill("Toggle me")
    page.locator('button:has-text("Create")').click()
    page.wait_for_timeout(500)

    task_li = page.locator('#todos li:has-text("Toggle me")')
    checkbox = task_li.locator('input[type="checkbox"]')
    text_input = task_li.locator('input[name="text"]')

    # Mark as complete
    checkbox.click()
    page.wait_for_timeout(500)
    expect(checkbox).to_be_checked()
    expect(text_input).to_be_disabled()

    # Mark as incomplete
    checkbox.click()
    page.wait_for_timeout(500)
    expect(checkbox).not_to_be_checked()
    expect(text_input).not_to_be_disabled()
