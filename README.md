# Barbell

An *open* dataset allowing <abbr title="FIRST Robotics Competition">FRC</abbr> teams to upload match images, and download object detection datasets.

> [!WARNING]
> This project is in ***pre-alpha*** as of June 24, 2025. Everything is still at the "it works on my machine" point, except it doesn't even work for me! :sweat_smile:

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/FastAPI-%23009485?style=for-the-badge&logo=fastapi&logoColor=%23ffffff)

## Todo:

See [issues](https://github.com/crummyh/Barbell/issues)

## Developing

If you are interested in helping, read this then take a look at [issues](https://github.com/crummyh/Barbell/issues) to see what I am working on.

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
│   ├── db/              # Database managers
│   ├── models/          # Data models
│   ├── services/        # Various services and abstractions
│   ├── tasks/           # Asynchronous background tasks
│   ├── tests/           # Tests
│   ├── web/             # Files for the website
│   │   ├── static/      # Static files
│   │   └── templates/   # HTML Jinja templates
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
Linux:
```bash
# Pre-requirements
# * Have git installed
# * Have Docker Compose installed

# Setup
git clone "https://github.com/crummyh/Barbell.git" # (Or use ssh)
cd Barbell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x setup.sh
./setup.sh

Rename .env.db.example to .env.db!!!

# Now start working!

# To run tests use:
./run-tests.sh

# To run the app use:
docker compose up --build

# To connect to the database use:
psql -h localhost -p 5432 -U myuser -d myappdb

# To close the app run:
docker compose down

# When you are done run:
deactivate
```

Windows:
Good luck, have fun!

Mac:
Probably similar to the Linux instructions, good luck!
