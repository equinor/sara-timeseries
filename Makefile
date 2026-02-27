format:
	mypy .
	black .
	ruff check . --fix
