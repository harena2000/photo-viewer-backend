# Photo Viewer Backend

## Setup Instructions

### 1. Fill the `.env` file

Create a `.env` file in the project root with the following content:

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=photo-viewer-db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432
ACCESS_TOKEN_LIFETIME_MINUTES=5
REFRESH_TOKEN_LIFETIME_DAYS=1
FRONT_URL=http://localhost:3001
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Build and run the app with Docker Compose

```bash
docker compose up --build
```

### 3. Create the custom user model

```bash
docker exec -it photo-viewer-backend python manage.py makemigrations authentification
```

### 4. Run migrations inside the backend container

```bash
docker exec -it photo-viewer-backend python manage.py migrate
```

### 5. Create a superuser (optional)

```bash
docker exec -it photo-viewer-backend python manage.py createsuperuser
```

### 6. Access the app

- Backend API: http://localhost:8000
- Admin panel: http://localhost:8000/admin

---

**Note:**

- Make sure your frontend URL is set correctly in `.env` as `FRONT_URL`.
- Database credentials in `.env` must match those in `docker-compose.yml`.
