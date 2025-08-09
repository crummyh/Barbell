# frcVisionDataset

An *open* dataset allowing <abbr title="FIRST Robotics Competition">FRC</abbr> teams to upload match images, and download object detection datasets.

> [!WARNING]
> This project is in ***pre-alpha*** as of June 24, 2025. Everything is still at the "it works on my machine" point, except it doesn't even work for me! :sweat_smile:

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/FastAPI-%23009485?style=for-the-badge&logo=fastapi&logoColor=%23ffffff)

## Todo:

See [issues](https://github.com/crummyh/frcVisionDataset/issues)

## Developing

If you are interested in helping, read this then take a look at [issues](https://github.com/crummyh/frcVisionDataset/issues) to see what I am working on.

### Libraries Used

* Python 3.10
* FastAPI
* SQLModel
* Jinja
* Bootstrap
* AWS
  * S3
  * PostgreSQL

### Project Structure

```bash
📁 app/                          # Holds the main app
├── 📁 api/                      # The actual endpoints
│  ├─── 🐍 auth.py               # Manages accounts and signin
│  ├─── 🐍 public_v1.py          # Publicly accessible API
│  ├─── 🐍 internal_v1.py        # Management and account API
│  └─── 🐍 web.py                # The website
├── 📁 core/                     # App-level core logic/config
│  ├─── 🐍 config.py             # Constants and configurable values
│  ├─── 🐍 dependencies.py       # Security dependencies
│  └─── 🐍 helpers.py            # Random common helper functions
├── 📁 db/                       # Database managers
│  └─── 🐍 database.py           # Manages the DB connection
├── 📁 models/                   # Data models
│  ├─── 🐍 models.py             # pydantic models for responses and requests
│  └─── 🐍 schemas.py            # SQLModel schemas representing tables
├── 📁 services/                 # Various services and abstractions
│  ├── 📁 email/                 # Email stuff
│  │  ├── 📁 templates/          # Email templates
│  │  └─── 🐍 email.py           # Email server connection and tasks
│  ├─── 🐍 buckets.py            # AWS S3 bucket manager
│  └─── 🐍 monitoring.py         # App status tracking
├── 📁 tasks/                    # Asynchronous background tasks
│  ├─── 🐍 download_packaging.py # Packages images for batch downloading
│  └─── 🐍 image_processing.py   # Processes images for uploading
├── 📁 tests/                    # Tests
├── 📁 web/                      # Files that are for the website
│  ├── 📁 static/                # Static files
│  │  ├── 📁 css/                # CSS files
│  │  ├── 📁 images/             # Images
│  └─── 📁 templates/            # Jinja HTML templates
└── 🐍 main.py                   # The main app entrypoint
📁 frontend/                     # Frontend stuff that needs to be compiled
├── 📁 email_templates/          # MJML emails, and Jinja templates
├── 📁 js/                       # JS to compile
├── 📁 scss/                     # SCSS to override Bootstrap
├── 📦 package.json              # Its a node project
└── 📦 package-lock.py           # Its a node project
```

### Running Locally
Linux:
```bash
# Pre-requirements
# * Have git installed
# * Have Docker Compose installed

# Setup
git clone "https://github.com/crummyh/frcVisionDataset.git" # (Or use ssh)
cd frcVisionDataset
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x setup.sh
./setup.sh

# Rename .env.db.example to .env.db!!!

# Now start working!

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
