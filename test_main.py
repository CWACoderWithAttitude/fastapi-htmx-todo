"""
Tests for the FastAPI Todo application.

This module contains pytest tests for the create_todo and list_todos endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
from models import Todo


# Test database setup - use in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///./test_todos.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Override the get_db dependency to use test database.

    Yields:
        Session: Test database session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test.

    Yields:
        Session: Test database session.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a test client with dependency override.

    Args:
        test_db: Test database session fixture.

    Returns:
        TestClient: FastAPI test client.
    """
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestCreateTodo:
    """Tests for the create_todo endpoint."""

    def test_create_todo_success(self, client, test_db):
        """
        Test successful creation of a todo item.

        Verifies that:
        - Todo is created with correct text
        - Response status is 200
        - Todo is persisted in database
        """
        todo_text = "Buy groceries"

        response = client.post(
            "/todos",
            data={"todo": todo_text},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Verify todo was created in database
        todos = test_db.query(Todo).all()
        assert len(todos) == 1
        assert todos[0].todo == todo_text
        assert todos[0].done is False

    def test_create_todo_with_special_characters(self, client, test_db):
        """
        Test creating a todo with special characters.

        Verifies that special characters are properly handled.
        """
        todo_text = "Test <script>alert('xss')</script> & special chars!"

        response = client.post(
            "/todos",
            data={"todo": todo_text},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200

        # Verify todo was created with exact text
        todos = test_db.query(Todo).all()
        assert len(todos) == 1
        assert todos[0].todo == todo_text

    def test_create_multiple_todos(self, client, test_db):
        """
        Test creating multiple todo items.

        Verifies that multiple todos can be created sequentially.
        """
        todo_texts = ["First todo", "Second todo", "Third todo"]

        for todo_text in todo_texts:
            response = client.post(
                "/todos",
                data={"todo": todo_text},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200

        # Verify all todos were created
        todos = test_db.query(Todo).all()
        assert len(todos) == 3
        assert [t.todo for t in todos] == todo_texts

    def test_create_todo_empty_string(self, client, test_db):
        """
        Test creating a todo with empty string.

        Verifies that empty todos can be created (or rejected based on business rules).
        """
        response = client.post(
            "/todos",
            data={"todo": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        # Should accept empty string (adjust if validation is added)
        assert response.status_code == 200

        todos = test_db.query(Todo).all()
        assert len(todos) == 1
        assert todos[0].todo == ""


class TestListTodos:
    """Tests for the list_todos endpoint."""

    def test_list_todos_empty(self, client, test_db):
        """
        Test listing todos when database is empty.

        Verifies that an empty list is returned.
        """
        response = client.get("/todos")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_todos_json_response(self, client, test_db):
        """
        Test listing todos returns JSON when no HTMX header.

        Verifies that:
        - Response is JSON
        - All todos are returned
        - Todo structure is correct
        """
        # Create test todos
        todos_data = [
            {"todo": "First task", "done": False},
            {"todo": "Second task", "done": True},
            {"todo": "Third task", "done": False}
        ]

        for todo_data in todos_data:
            new_todo = Todo(**todo_data)
            test_db.add(new_todo)
        test_db.commit()

        response = client.get("/todos")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        json_response = response.json()
        assert len(json_response) == 3

        # Verify todo structure
        for i, todo in enumerate(json_response):
            assert "id" in todo
            assert todo["todo"] == todos_data[i]["todo"]
            assert todo["done"] == todos_data[i]["done"]

    def test_list_todos_htmx_response(self, client, test_db):
        """
        Test listing todos returns HTML when HTMX header is present.

        Verifies that:
        - Response is HTML
        - HTMX request is properly detected
        """
        # Create a test todo
        new_todo = Todo(todo="Test task", done=False)
        test_db.add(new_todo)
        test_db.commit()

        response = client.get("/todos", headers={"hx-request": "true"})

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"Test task" in response.content

    def test_list_todos_ordering(self, client, test_db):
        """
        Test that todos are returned in insertion order.

        Verifies that todos maintain their creation order.
        """
        todos_data = ["First", "Second", "Third"]

        for todo_text in todos_data:
            new_todo = Todo(todo=todo_text, done=False)
            test_db.add(new_todo)
        test_db.commit()

        response = client.get("/todos")
        json_response = response.json()

        assert len(json_response) == 3
        assert [t["todo"] for t in json_response] == todos_data

    def test_list_todos_mixed_done_status(self, client, test_db):
        """
        Test listing todos with mixed completion status.

        Verifies that both done and not-done todos are returned.
        """
        todos_data = [
            {"todo": "Done task", "done": True},
            {"todo": "Not done task", "done": False},
            {"todo": "Another done", "done": True}
        ]

        for todo_data in todos_data:
            new_todo = Todo(**todo_data)
            test_db.add(new_todo)
        test_db.commit()

        response = client.get("/todos")
        json_response = response.json()

        assert len(json_response) == 3
        assert json_response[0]["done"] is True
        assert json_response[1]["done"] is False
        assert json_response[2]["done"] is True


class TestIntegration:
    """Integration tests for create and list functionality."""

    def test_create_and_list_workflow(self, client, test_db):
        """
        Test the full workflow of creating and listing todos.

        Verifies that:
        - Created todos appear in the list
        - List reflects all created todos
        """
        # Initially empty
        response = client.get("/todos")
        assert response.json() == []

        # Create first todo
        client.post("/todos", data={"todo": "Task 1"})
        response = client.get("/todos")
        assert len(response.json()) == 1
        assert response.json()[0]["todo"] == "Task 1"

        # Create second todo
        client.post("/todos", data={"todo": "Task 2"})
        response = client.get("/todos")
        assert len(response.json()) == 2
        assert response.json()[1]["todo"] == "Task 2"

        # Create third todo
        client.post("/todos", data={"todo": "Task 3"})
        response = client.get("/todos")
        assert len(response.json()) == 3
        assert [t["todo"]
                for t in response.json()] == ["Task 1", "Task 2", "Task 3"]
