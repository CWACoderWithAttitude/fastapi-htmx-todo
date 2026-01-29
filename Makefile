dev:
	@echo "This is for local development only"
	fastapi dev --host 0.0.0.0 main.py
tests:
	pytest test_main.py -v
coverage:
	pytest test_main.py --cov=main --cov-report=html
	