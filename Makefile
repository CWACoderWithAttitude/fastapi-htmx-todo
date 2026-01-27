dev:
	@echo "This is for local development only"
	fastapi dev --host 0.0.0.0 main.py
svc1="fastapi-htmx-todo_devcontainer-fastapi-htmx-todo"
cmd1="fastapi dev --host 0.0.0.0 main.py"
cmd2="pip install -r requirements.txt"
run_dev:
	#docker-compose -f .devcontainer/docker-compose.yml exec $(svc1) $(cmd1)
	docker-compose -f .devcontainer/docker-compose.yml start $(svc1) 
# https://playwright.dev/python/docs/browsers	
playwright-install:
	@echo "Installing Playwright browsers..."
	playwright install --with-deps --only-shell
test: #playwright-install
	@echo "Running tests..."
	#pytest tests/test_tools.py
	docker-compose -f .devcontainer/docker-compose.yml exec playwright bash