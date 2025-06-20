# frcVisionDataset


An *open* dataset allowing <abbr title="FIRST Robotics Competition">FRC</abbr> teams to upload match images, and download object detection datasets.

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge)

## Todo:
* Get a real name :sweat_smile:
* Don't just copy PhotonVision's website
* Finish all alpha endpoints

## Developing

This is mainly just here so that I don't forget

### Libraries Used

* FastAPI
* SQLModel
* SlowAPI
* Jinja
* Bootstrap

### Project Structure

```bash
app/ # The main project dir (like src)
├─ routers/ # API sections for endpoints
│  ├─ api_v1.py # Publicly available API V1
│  ├─ internal.py # Internal API for managing accounts ect.
│  ├─ web.py # The actual webpages (Return HTML files)
├─ services/ # Various process that can be completed on separate threads
├─ static/ # Static files that are hosted in /static
│  ├─ css/
│  ├─ images/
│  ├─ js/
├─ templates/ # Jinja HTML templates
├─ tests/ # Empty right now, but will have tests later
├─ buckets.py # Manages S3 buckets and objects
├─ config.py # Config options and constants
├─ database.py # Manages the database connection and migration
├─ dependencies.py # Security dependencies
├─ helpers.py # Random common functions
├─ main.py # Main entrypoint
├─ models.py # The database schema and return models
```

### Running Locally
Linux:
```bash
# Setup
git clone "https://github.com/crummyh/frcVisionDataset.git"
cd frcVisionDataset
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Now start working!
# To run the app run:
FastAPI dev app/main.py
# When you are done run:
deactivate
```
