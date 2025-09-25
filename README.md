# Barbell

An *open* dataset allowing <abbr title="FIRST Robotics Competition">FRC</abbr> teams to upload match images, and download object detection datasets.

> [!WARNING]
> This project is in ***pre-alpha*** as of June 24, 2025. Everything is still at the "it works on my machine" point, except it doesn't even work for me! :sweat_smile:

> [!NOTE]
> I don't quite have time in my schedule to work on this right now. The project is ***not*** abandoned, and I will come back to it in 2026

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/FastAPI-%23009485?style=for-the-badge&logo=fastapi&logoColor=%23ffffff)

## Todo:

See [issues](https://github.com/crummyh/Barbell/issues)

## Developing

If you are interested in helping, read this, then take a look at [issues](https://github.com/crummyh/Barbell/issues) to see what I am working on.

### Libraries Used

* Python 3.10
* FastAPI
* SQLModel
* Jinja
* Bootstrap 5
* Quercus.js
* MJML
* AWS
  * S3
  * PostgreSQL

### Project Structure

```bash
Barbell/
├── app/                 # The backend python project
│   ├── api/             # The API endpoints
│   ├── core/            # App-level core logic/config
│   ├── crud/            # CRUD interface layer
│   ├── models/          # Data models
│   ├── services/        # Various services and abstractions
│   ├── tasks/           # Asynchronous background tasks
│   ├── tests/           # Tests
│   ├── web/             # Files for the website
│   │   ├── static/      # Static files
│   │   └── templates/   # HTML Jinja templates
│   ├── database.py      # Database managers
│   └── main.py          # Main entrypoint
├── frontend/            # The frontend Node project
│   ├── email_templates/ # MJML email templates
│   ├── js/              # JS
│   │   ├── components/  # General components
│   │   ├── pages/       # Specific pages
│   │   ├── utils/       # Utilities
│   │   ├── index.js     # Dynamically load js depending on page
│   │   └── main.js      # Import libraries
│   └── scss/            # SCSS
│       ├── base/        # Global variables, mixins and more
│       ├── components/  # Styles for common components
│       ├── pages/       # Styles for specific pages
│       └── main.scss    # Main style entrypoint
└── README.md <----------- You are here!
```

### Running Locally
#### Pre-requirements

* Have git installed
* Have Docker Compose installed
* Have Python 3.10+ installed

#### Initial Setup
```bash
# Clone the repository
git clone "https://github.com/crummyh/Barbell.git" # (Or use ssh)
cd Barbell

# Install uv (if not already installed)
pip install uv

# Create project environment and install dependencies
uv sync

# Set up pre-commit hooks
uv run pre-commit install

# Run setup script
chmod +x ./scripts/setup.sh
./scripts/setup.sh

# Rename environment file
# ⚠️  IMPORTANT: Rename .env.db.example to .env.db !!!
```

### Daily Development Workflow
#### Starting Development
```bash
cd Barbell
# No need to activate virtual environment - uv handles it automatically!
```
#### Running the Application
```bash
docker compose up --build
```
#### Running Tests
```bash
./scripts/run-tests.sh
```
#### Code Quality Checks
```bash
# Format and lint your code (runs automatically on commit)
uv run pre-commit run --all-files

# Run individual tools if needed:
uv run black .                    # Format code
uv run ruff check --fix .         # Lint and auto-fix
uv run mypy .                     # Type checking
```
#### Making Commits
```bash
# Stage your changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "Your commit message"

# If pre-commit makes changes, re-add and commit:
git add .
git commit -m "Your commit message"
```
#### Database Connection
```bash
psql -h localhost -p 5432 -U myuser -d myappdb
```
Shutting Down
```bash
docker compose down
```

### Adding New Dependencies
#### Production Dependencies
```bash
uv add package-name
```
#### Development Dependencies
```bash
uv add --dev package-name
```

### Useful Commands
#### Package Management
```bash
uv sync                           # Install/update all dependencies
uv add package-name              # Add production dependency
uv add --dev package-name        # Add development dependency
uv remove package-name           # Remove dependency
uv tree                          # Show dependency tree
```
#### Code Quality
```bash
uv run pre-commit run            # Run hooks on staged files
uv run pre-commit run --all-files # Run hooks on all files
uv run pre-commit autoupdate     # Update hook versions
```
#### Running Scripts
```bash
uv run python script.py          # Run Python scripts
uv run uvicorn main:app --reload # Run FastAPI with auto-reload
uv run pytest tests/             # Run specific test directory
```
### Troubleshooting
#### Pre-commit Issues
```bash
# Clean and reinstall hooks
uv run pre-commit clean
uv run pre-commit install

# Skip hooks in emergency (use sparingly!)
git commit --no-verify -m "Emergency fix"
```
#### Dependency Issues
```bash
# Recreate environment
rm -rf .venv
uv sync
```
#### Docker Issues
```bash
# Rebuild containers
docker compose down
docker compose up --build --force-recreate
```
