# django-ezreg

## Test install

To quickly test out the system or for development purposes, a simple docker configuration is included.  To deploy locally and load some test data, simply run:

```
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py loaddata test_fixture.json
docker compose exec web python manage.py createsuperuser
```