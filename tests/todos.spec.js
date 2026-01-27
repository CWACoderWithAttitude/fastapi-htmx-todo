// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Test suite for Todo application core functionality
 * Tests CRUD operations: Create, Read, Update, Delete, and Toggle
 */

test.describe('Todo Application', () => {

    test.beforeEach(async ({ page }) => {
        // Navigate to the application before each test
        await page.goto('/');

        // Wait for the page to load and HTMX to initialize
        await expect(page.locator('h1')).toContainText('FastAPI + HTMX');
    });

    test('should load the home page successfully', async ({ page }) => {
        // Verify page title
        await expect(page).toHaveTitle(/FastAPI \+ HTMX/);

        // Verify main heading is visible
        await expect(page.locator('h1')).toBeVisible();

        // Verify the form exists
        await expect(page.locator('input[name="todo"]')).toBeVisible();
        await expect(page.locator('button:has-text("Create")')).toBeVisible();

        // Verify the todos section exists
        await expect(page.locator('#todos')).toBeVisible();
    });

    test('should create a new todo', async ({ page }) => {
        const todoText = 'Buy groceries';

        // Fill in the todo input
        await page.locator('input[name="todo"]').fill(todoText);

        // Click the Create button
        await page.locator('button:has-text("Create")').click();

        // Wait for HTMX to update the DOM
        await page.waitForTimeout(500);

        // Verify the todo appears in the list
        await expect(page.locator(`#todos li:has-text("${todoText}")`)).toBeVisible();

        // Verify the input field is cleared
        await expect(page.locator('input[name="todo"]')).toHaveValue('');
    });

    test('should create multiple todos', async ({ page }) => {
        const todos = ['Task 1', 'Task 2', 'Task 3'];

        for (const todoText of todos) {
            await page.locator('input[name="todo"]').fill(todoText);
            await page.locator('button:has-text("Create")').click();
            await page.waitForTimeout(500);
        }

        // Verify all todos are present
        for (const todoText of todos) {
            await expect(page.locator(`#todos li:has-text("${todoText}")`)).toBeVisible();
        }

        // Verify the count
        const todoItems = page.locator('#todos li');
        await expect(todoItems).toHaveCount(todos.length);
    });

    test('should toggle todo completion status', async ({ page }) => {
        const todoText = 'Complete this task';

        // Create a todo
        await page.locator('input[name="todo"]').fill(todoText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Find the todo item and its checkbox
        const todoItem = page.locator(`#todos li:has-text("${todoText}")`);
        const checkbox = todoItem.locator('input[type="checkbox"]');
        const textInput = todoItem.locator('input[name="text"]');

        // Verify checkbox is initially unchecked
        await expect(checkbox).not.toBeChecked();

        // Click the checkbox to mark as complete
        await checkbox.click();
        await page.waitForTimeout(500);

        // Verify checkbox is now checked
        await expect(checkbox).toBeChecked();

        // Verify the text input has line-through style
        await expect(textInput).toHaveAttribute('style', /text-decoration: line-through/);
        await expect(textInput).toBeDisabled();

        // Toggle back to uncompleted
        await checkbox.click();
        await page.waitForTimeout(500);

        // Verify checkbox is unchecked again
        await expect(checkbox).not.toBeChecked();
    });

    test('should edit todo text', async ({ page }) => {
        const originalText = 'Original todo';
        const updatedText = 'Updated todo text';

        // Create a todo
        await page.locator('input[name="todo"]').fill(originalText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Find the todo item
        const todoItem = page.locator(`#todos li:has-text("${originalText}")`);
        const textInput = todoItem.locator('input[name="text"]');

        // Clear and update the text
        await textInput.clear();
        await textInput.fill(updatedText);

        // Wait for HTMX auto-update (250ms delay + network)
        await page.waitForTimeout(800);

        // Verify the updated text appears
        await expect(page.locator(`#todos li:has-text("${updatedText}")`)).toBeVisible();
    });

    test('should delete a todo', async ({ page }) => {
        const todoText = 'Task to delete';

        // Create a todo
        await page.locator('input[name="todo"]').fill(todoText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Get initial count
        const initialCount = await page.locator('#todos li').count();

        // Find and click the delete button
        const todoItem = page.locator(`#todos li:has-text("${todoText}")`);
        const deleteButton = todoItem.locator('input[type="button"][value="❌"]');
        await deleteButton.click();
        await page.waitForTimeout(500);

        // Verify the todo is removed
        await expect(page.locator(`#todos li:has-text("${todoText}")`)).not.toBeVisible();

        // Verify count decreased
        const finalCount = await page.locator('#todos li').count();
        expect(finalCount).toBe(initialCount - 1);
    });

    test('should handle empty todo list', async ({ page }) => {
        // Check if "No todos" message is displayed when list is empty
        const emptyMessage = page.locator('#todos li:has-text("No todos. Go create some!")');

        // The message should be visible if there are no todos
        const todoCount = await page.locator('#todos li').count();

        if (todoCount === 1) {
            await expect(emptyMessage).toBeVisible();
        }
    });

    test('should preserve todos order', async ({ page }) => {
        const todos = ['First todo', 'Second todo', 'Third todo'];

        // Create todos in order
        for (const todoText of todos) {
            await page.locator('input[name="todo"]').fill(todoText);
            await page.locator('button:has-text("Create")').click();
            await page.waitForTimeout(500);
        }

        // Verify todos appear in the correct order
        const todoItems = page.locator('#todos li');
        for (let i = 0; i < todos.length; i++) {
            const todoText = await todoItems.nth(i).locator('input[name="text"]').inputValue();
            expect(todoText).toBe(todos[i]);
        }
    });

    test('should allow multiple todos with same text', async ({ page }) => {
        const duplicateText = 'Duplicate task';

        // Create two todos with the same text
        await page.locator('input[name="todo"]').fill(duplicateText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        await page.locator('input[name="todo"]').fill(duplicateText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Verify both todos exist
        const duplicateTodos = page.locator(`#todos li:has-text("${duplicateText}")`);
        await expect(duplicateTodos).toHaveCount(2);
    });

    test('should handle special characters in todo text', async ({ page }) => {
        const specialText = 'Test with @#$%^&*() special chars';

        await page.locator('input[name="todo"]').fill(specialText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Verify the todo with special characters appears correctly
        const textInput = page.locator('#todos li').first().locator('input[name="text"]');
        await expect(textInput).toHaveValue(specialText);
    });

    test('should handle long todo text', async ({ page }) => {
        const longText = 'A'.repeat(200); // Create a long string

        await page.locator('input[name="todo"]').fill(longText);
        await page.locator('button:has-text("Create")').click();
        await page.waitForTimeout(500);

        // Verify the long text is saved correctly
        const textInput = page.locator('#todos li').first().locator('input[name="text"]');
        const value = await textInput.inputValue();
        expect(value).toBe(longText);
    });
});
