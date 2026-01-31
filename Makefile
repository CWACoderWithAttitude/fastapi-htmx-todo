dev:
	@echo "This is for local development only"
	fastapi dev --host 0.0.0.0 main.py
tests:
	pytest test_main.py -v
test_update:
	pytest test_main.py::TestUpdateTodo -v
watch_update:
	watchfiles 'pytest test_main.py::TestUpdateTodo -v' main.py test_main.py
coverage:
	pytest test_main.py --cov=main --cov-report=html
