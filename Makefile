format:
	uv run mypy .
	uv run black .
	uv run ruff check . --fix
