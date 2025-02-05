# List available recipes
default:
    @just --list

# Run pre-commit hooks on all files
pre-commit:
    uv run pre-commit run --all-files

# Run pyright type checking
pyright:
    uv run pyright

# Run Django development server
django-runserver:
    cd src && uv run python manage.py runserver

# Run Django migrations
django-migrate:
    cd src && uv run python manage.py migrate

# Make Django migrations
django-makemigrations:
    cd src && uv run python manage.py makemigrations

# Create a Django superuser
django-createsuperuser:
    cd src && uv run python manage.py createsuperuser

# Run Django shell
django-shell:
    cd src && uv run python manage.py shell

# Clean Python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "htmlcov" -exec rm -r {} +
    find . -type d -name ".pytest_cache" -exec rm -r {} +
