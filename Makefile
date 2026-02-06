.PHONY: init test lint clean run

# Python Interpreter (use venv or system python)
PYTHON := python3

init:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r dev-requirements.txt
	@echo "Setup complete."

test:
	@echo "Running tests..."
	pytest experiments src

lint:
	@echo "Running linters..."
	flake8 src
	black --check src
	mypy src

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@echo "Starting application..."
	# Placeholder for main entry point
	@echo "No main entry point configured yet."
