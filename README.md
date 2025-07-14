# frcVisionDataset

An *open* dataset allowing <abbr title="FIRST Robotics Competition">FRC</abbr> teams to upload match images, and download object detection datasets.

> [!WARNING]
> This project is in ***pre-alpha*** as of June 24, 2025. Everything is still at the "it works on my machine" point, except it doesn't even work for me! :sweat_smile:

![Static Badge](https://img.shields.io/badge/Licence-MIT-blue?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/FastAPI-%23009485?style=for-the-badge&logo=fastapi&logoColor=%23ffffff)
![Static Badge](https://img.shields.io/badge/SQLModel-%237e56c2?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8%2BCjxzdmcgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpjYz0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbnMjIiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6c29kaXBvZGk9Imh0dHA6Ly9zb2RpcG9kaS5zb3VyY2Vmb3JnZS5uZXQvRFREL3NvZGlwb2RpLTAuZHRkIiB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiB2aWV3Qm94PSIwIDAgMjQgMjQiIHZlcnNpb249IjEuMSIgaWQ9InN2ZzYiIHNvZGlwb2RpOmRvY25hbWU9Imljb24td2hpdGUuc3ZnIiBpbmtzY2FwZTp2ZXJzaW9uPSIxLjAuMiAoMS4wLjIrcjc1KzEpIj4KICA8c29kaXBvZGk6bmFtZWR2aWV3IHBhZ2Vjb2xvcj0iI2ZmZmZmZiIgYm9yZGVyY29sb3I9IiM2NjY2NjYiIGJvcmRlcm9wYWNpdHk9IjEiIG9iamVjdHRvbGVyYW5jZT0iMTAiIGdyaWR0b2xlcmFuY2U9IjEwIiBndWlkZXRvbGVyYW5jZT0iMTAiIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwIiBpbmtzY2FwZTpwYWdlc2hhZG93PSIyIiBpbmtzY2FwZTp3aW5kb3ctd2lkdGg9IjE3NjEiIGlua3NjYXBlOndpbmRvdy1oZWlnaHQ9IjE0MTIiIGlkPSJuYW1lZHZpZXcxOCIgc2hvd2dyaWQ9ImZhbHNlIiBpbmtzY2FwZTp6b29tPSIxNiIgaW5rc2NhcGU6Y3g9IjE3LjQ5NzQ2MiIgaW5rc2NhcGU6Y3k9IjIuMDM5ODczOCIgaW5rc2NhcGU6d2luZG93LXg9IjE2NzkiIGlua3NjYXBlOndpbmRvdy15PSIwIiBpbmtzY2FwZTp3aW5kb3ctbWF4aW1pemVkPSIwIiBpbmtzY2FwZTpjdXJyZW50LWxheWVyPSJzdmc2Ii8%2BCiAgPG1ldGFkYXRhIGlkPSJtZXRhZGF0YTEyIj4KICAgIDxyZGY6UkRGPgogICAgICA8Y2M6V29yayByZGY6YWJvdXQ9IiI%2BCiAgICAgICAgPGRjOmZvcm1hdD5pbWFnZS9zdmcreG1sPC9kYzpmb3JtYXQ%2BCiAgICAgICAgPGRjOnR5cGUgcmRmOnJlc291cmNlPSJodHRwOi8vcHVybC5vcmcvZGMvZGNtaXR5cGUvU3RpbGxJbWFnZSIvPgogICAgICAgIDxkYzp0aXRsZS8%2BCiAgICAgIDwvY2M6V29yaz4KICAgIDwvcmRmOlJERj4KICA8L21ldGFkYXRhPgogIDxkZWZzIGlkPSJkZWZzMTAiLz4KICA8cGF0aCBpZD0icGF0aDEyMjUtNiIgc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MS44MjA3OTtzdHJva2UtbWl0ZXJsaW1pdDo0O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxO3N0b3AtY29sb3I6IzAwMDAwMCIgZD0ibSAyMy4zMDY5NzIsMTQuMDAzNTkyIGMgLTAuMzI3OTQ0LDEuNTI2NDExIC01LjE5OTA1LDIuNjI0ODAyIC0xMS4wNzYxNzEsMi42MjUgLTUuODc5ODY0OSwtMi41NWUtNCAtMTAuNzU0MDE0MywtMS4wOTc4MiAtMTEuMDc4MTI1NSwtMi42MjUgdiA1Ljc2MTcxOSBjIC0wLjAwMjgxLDEuNTkyMDA2IDQuOTU3OTk2MSwyLjg4MjkzNCAxMS4wNzgxMjU1LDIuODgyODEzIDYuMTE5MzY0LC0xLjZlLTQgMTEuMDc4OTc4LC0xLjI5MTAwNiAxMS4wNzYxNzEsLTIuODgyODEzIHogbSAtMy44OTA2MjUsMy4yNDYwOTQgYyAwLjg4MjcyNCw5LjY1ZS00IDEuNTk3NzcsMC43MTY4ODUgMS41OTc2NTcsMS41OTk2MSAxLjEzZS00LDAuODgyNzI0IC0wLjcxNDkzMywxLjU5ODY0NCAtMS41OTc2NTcsMS41OTk2MDkgLTAuODgzNDg2LDEuMTJlLTQgLTEuNTk5NzIxLC0wLjcxNjEyMyAtMS41OTk2MDksLTEuNTk5NjA5IC0xLjEzZS00LC0wLjg4MzQ4NiAwLjcxNjEyMywtMS41OTk3MjIgMS41OTk2MDksLTEuNTk5NjEgeiIgc29kaXBvZGk6bm9kZXR5cGVzPSJjY2NjY2NjY2NjY2MiLz4KICA8cGF0aCBpZD0icGF0aDEyMjUiIHN0eWxlPSJmaWxsOiNmZmZmZmY7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjEuODIwNzk7c3Ryb2tlLW1pdGVybGltaXQ6NDtzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MTtzdG9wLWNvbG9yOiMwMDAwMDAiIGQ9Im0gMjMuMjg3MTA5LDYuMTE3MTg3NSBjIC0wLjMyNzk0NCwxLjUyNjQxMDQgLTUuMTk5MDUsMi42MjQ4MDIxIC0xMS4wNzYxNzEsMi42MjUgQyA2LjMzMTA3MzQsOC43NDE5MzIxIDEuNDU2OTI0LDcuNjQ0MzY3NiAxLjEzMjgxMjgsNi4xMTcxODcyIHYgNS43NjE3MTg4IGMgLTAuMDAyODEsMS41OTIwMDYgNC45NTc5OTYxLDIuODgyOTM0IDExLjA3ODEyNTIsMi44ODI4MTMgNi4xMTkzNjQsLTEuNmUtNCAxMS4wNzg5NzgsLTEuMjkxMDA2IDExLjA3NjE3MSwtMi44ODI4MTMgeiBtIC0zLjg5MDYyNSwzLjI0NjA5MzcgYyAwLjg4MjcyNCw5LjY1MmUtNCAxLjU5Nzc3LDAuNzE2ODg0OCAxLjU5NzY1NywxLjU5OTYwOTggMS4xM2UtNCwwLjg4MjcyNCAtMC43MTQ5MzMsMS41OTg2NDQgLTEuNTk3NjU3LDEuNTk5NjA5IC0wLjg4MzQ4NiwxLjEyZS00IC0xLjU5OTcyMSwtMC43MTYxMjMgLTEuNTk5NjA5LC0xLjU5OTYwOSAtMS4xM2UtNCwtMC44ODM0ODYgMC43MTYxMjMsLTEuNTk5NzIyMSAxLjU5OTYwOSwtMS41OTk2MDk4IHoiIHNvZGlwb2RpOm5vZGV0eXBlcz0iY2NjY2NjY2NjY2NjIi8%2BCiAgPGVsbGlwc2Ugc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MS44MjA3OTtzdHJva2UtbWl0ZXJsaW1pdDo0O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxO3N0b3AtY29sb3I6IzAwMDAwMCIgaWQ9InBhdGgxMjI1LTItOSIgY3g9IjEyLjIxMDU5NSIgY3k9IjMuODk0NTQ5NiIgcng9IjExLjA3NzI4NiIgcnk9IjIuODgxNDkwNSIvPgo8L3N2Zz4%3D)

## Todo:

See [issues](https://github.com/crummyh/frcVisionDataset/issues)

## Developing

If you are interested in helping, read this then take a look at [issues](https://github.com/crummyh/frcVisionDataset/issues) to see what I am working on.

Notes to self:
* To access the PostgreSQL database, run `sudo -u postgres psql`
* Try to use `git pull --rebase` instead of just pull

### Libraries Used

* Python 3
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
│  └─── 🐍 buckets.py            # AWS S3 bucket manager
├── 📁 tasks/                    # Asynchronous background tasks
│  ├─── 🐍 download_packaging.py # Packages images for batch downloading
│  └─── 🐍 image_processing.py   # Processes images for uploading
├── 📁 tests/                    # Tests
├── 📁 web/                      # Files that are for the website
│  ├── 📁 static/                # Static files
│  │  ├── 📁 css/                # CSS files
│  │  ├── 📁 images/             # Images
│  │  └── 📁 js/                 # JS files
│  └─── 📁 templates/            # Jinja HTML templates
└── 🐍 main.py                   # The main app entrypoint
```

### Running Locally
Linux:
```bash
# Pre-requirements
# * Have git installed
# * Have Python 3.10+ installed

# Setup
git clone "https://github.com/crummyh/frcVisionDataset.git" # (Or use ssh)
cd frcVisionDataset
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x setup.sh
./setup.sh
# Now start working!
# To run the app run:
fastapi dev app/main.py
# And if you need to send emails run this in a separate window
sudo python3 -m smtpd -c DebuggingServer -n localhost:1025
# When you are done run:
deactivate
```

Windows:
Good luck, have fun!

Mac:
Probably similar to the Linux instructions, good luck!
