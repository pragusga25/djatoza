# Djatoza App

A Django-based portfolio application that allows users to create profiles with location information and view all users on a map.

## Features

- User profiles with additional details (address, phone number, location)
- User profile management (view and edit)
- Full-screen map showing all registered user locations
- User popup information on the map
- Authentication system with restricted access to profiles
- Login/Logout activity logging

## Requirements

- Python 3.8+
- Docker and Docker Compose (for PostgreSQL)

## Setup Instructions

1. Clone the repository

```bash
git clone https://github.com/pragusga25/djatoza.git
cd djatoza
```

2. Create a virtual environment and activate it

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables

```bash
cp .env.example .env
# Edit the .env file if needed with your preferred editor
```

5. Start PostgreSQL using Docker Compose

```bash
docker-compose up -d
```

The repository already includes a `docker-compose.yml` file configured for the application.

6. Run migrations

```bash
python manage.py migrate
```

7. Create a superuser

```bash
python manage.py createsuperuser
```

8. Run the development server

```bash
python manage.py runserver
```

9. Access the application

- Application: <http://127.0.0.1:8000/>
- Admin Interface: <http://127.0.0.1:8000/admin/>

## Running Tests

To run the test suite:

```bash
python manage.py test
```

## Notes

- Users can only see their own profile details, but all user locations are visible on the map
- Only superusers can access the admin interface and view other users' profile details
- Login/Logout activities are logged and viewable in the admin panel
