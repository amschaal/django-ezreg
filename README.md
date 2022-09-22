# django-ezreg
Django Ezreg is a registration system which allows in depth customization of events, from registration forms, to info pages, prices, and payment processors.


## Test install

To quickly test out the system or for development purposes, a simple docker configuration is included.  To deploy locally and load some test data, simply run:

```
# Clone it recursively
git clone --recursive https://github.com/amschaal/django-ezreg.git ezreg
cd ezreg
cp ezreg/config.py.example ezreg/config.py # copy this then make necessary modifications

# Build in docker
docker compose up --build

# Run migrations and add some basic data and a superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py loaddata test_fixture.json
docker compose exec web python manage.py createsuperuser
```