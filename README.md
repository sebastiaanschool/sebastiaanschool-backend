# Sebastiaan School API

## Install

Migrate the database the first boot and after every model change:

```
pip install -r requirements.txt
python manage.py migrate
```

## Run
First activate debug (development) mode:
```
export RUN_WITH_DEBUG=on
```

Next start the server on port 8000 allowing remote machine access:

```
python manage.py runserver 0.0.0.0:8000
```

## API

A REST interface is available. Explore the API by visiting: `/api/` in your browser.

## Admin

Explore the Django admin interface from `/admin/`. You'll need an admin account. Create one with:

```
python manage.py createsuperuser
```