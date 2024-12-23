![Static Badge](https://img.shields.io/badge/Python-%23?style=for-the-badge&logo=python&logoColor=white&labelColor=%230a0a0a&color=%233776AB)
![Static Badge](https://img.shields.io/badge/Django-%23?style=for-the-badge&logo=django&logoColor=white&labelColor=%230a0a0a&color=%23092E20)
![Static Badge](https://img.shields.io/badge/Django%20REST%20Framework-%23?style=for-the-badge&logo=django&logoColor=white&labelColor=%230a0a0a&color=b81414)
![Static Badge](https://img.shields.io/badge/DRF%20Channels-%23?style=for-the-badge&logo=django&labelColor=%230a0a0a&color=%23b81414)
![Static Badge](https://img.shields.io/badge/Swagger-%23?style=for-the-badge&logo=swagger&logoColor=white&labelColor=%230a0a0a&color=%2385EA2D)
![Static Badge](https://img.shields.io/badge/Postgres-%23?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=%230a0a0a&color=%234169E1)
![Static Badge](https://img.shields.io/badge/Docker-%23?style=for-the-badge&logo=docker&logoColor=white&labelColor=%230a0a0a&color=%232496ED)
![Static Badge](https://img.shields.io/badge/%20pre%20commit-%23?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=%230a0a0a&color=%23FAB040)
![Static Badge](https://img.shields.io/badge/Ruff-%23?style=for-the-badge&logo=ruff&logoColor=white&labelColor=%230a0a0a&color=%23D7FF64)
![Static Badge](https://img.shields.io/badge/nginx-%23?style=for-the-badge&logo=nginx&logoColor=white&labelColor=%230a0a0a&color=%23009639)
![Static Badge](https://img.shields.io/badge/poetry-%23?style=for-the-badge&logo=poetry&logoColor=white&labelColor=%230a0a0a&color=%2360A5FA)
![Static Badge](https://img.shields.io/badge/JavaScript-%23?style=for-the-badge&logo=javascript&logoColor=white&labelColor=%230a0a0a&color=%23F7DF1E)
![Static Badge](https://img.shields.io/badge/jQuery-%23?style=for-the-badge&logo=jquery&logoColor=white&labelColor=%230a0a0a&color=%230769AD)

***

# SPA: Web Comments
This application allows users to create topics, comment on them, engage in discussions, and share images or text files.
Topics are displayed in a table, and comments on each topic are shown in a cascading order.

##### Main features:
- Publish topics
- Comment on any topic or comment
- Edit your own topics or comments
- Delete your own topics or comments
- Read topics and comments without register account

# How to run with docker
- Copy by renaming `environments/template.env` > `environments/.env.`
- Create a secret key using the command `openssl rand -base64 64` and add it to `DJANGO_SECRET_KEY`.
- Add the allowed hosts/domains (e.g., 'domain1 domain2') to `DJANGO_ALLOWED_HOSTS`.
- If necessary, modify other environment variables.
- Go to the folder with the downloaded project.
- Run the command `docker compose -f ./docker/docker-compose.yml up -d`.


# Environments
## Description
- **DJANGO_SECRET_KEY** - a secret key used for cryptographic signing.
- **DJANGO_DEBUG** - a boolean that determines whether Django should run in debug mode.
- **DJANGO_ALLOWED_HOSTS** - a string of host/domain names separated by spaces, app will serve only them.
- **DJANGO_SUPERUSER_USERNAME** - the username for the default superuser account.
- **DJANGO_SUPERUSER_EMAIL** - the email for the default superuser account.
- **DJANGO_SUPERUSER_PASSWORD** - the password for the default superuser account
- **POSTGRES_DB** - the name of the PostgreSQL database used by the app.
- **POSTGRES_HOST** - the hostname of the PostgreSQL database used by the app. This can be set `localhost` or docker container name.
- **POSTGRES_PORT** - the port on which the PostgreSQL database is listening.
- **POSTGRES_USER** - the username used to connect to the PostgreSQL database.
- **POSTGRES_PASSWORD** - the password for the PostgreSQL user.

## Default values
```dotenv
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=123

POSTGRES_DB=web_comments
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=web_comments_user
POSTGRES_PASSWORD=web_comments_password_123
```

# URLS
`localhost` must be replaced to your domain if you run it on a hosting.
- http://localhost/ - home page
- http://localhost/admin/ - admin site
- http://localhost/api/ - api
- http://localhost/api/docs/ - swagger docs
- http://localhost/api/redoc/ - redoc docs
