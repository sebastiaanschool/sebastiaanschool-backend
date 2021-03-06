# Sebastiaan School API
[![Build Status](https://travis-ci.org/sebastiaanschool/sebastiaanschool-backend.svg?branch=master)](https://travis-ci.org/sebastiaanschool/sebastiaanschool-backend)

## Python Virtual Env recommended

```
pip install virtualenv
virtualenv <DIR>
source <DIR>/bin/activate
```

To deactiveate:

```
deactivate
```

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

## Openshift

### ALLOWED_HOSTS

For Django deployed to a production environment, make sure the server URL is added to the ALLOWED_HOSTS setting in the file ```sebastiaanschool/settings.py``` and that ```DEBUG``` is ```False```.

### DJANGO_SECRET_KEY

On Openshift and other deployment environments, a fresh secret key should be set. This key must be kept private.

###Instructions

Start with a Python 2.7 cartridge.

```
rhc create <app-name>
```

Next set some configuration items on the new app:

```
rhc set-env DJANGO_SECRET_KEY=<new secret key> --app <app-name>
rhc set-env OPENSHIFT_PYTHON_WSGI_APPLICATION=sebastiaanschool/wsgi.py --app <app-name>
```

Add openshift as a remote

```
git remote add openshift <openshift ssh push URL>
```

Force push this repository. (Force to overwrite default checkout)

```
git push openshift --force
```

Connect over SSH to the cartridge:

```
rhc ssh <app name>
```

Then run these commands:

```
cd $OPENSHIFT_REPO_DIR
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata defaultdata.json
```

Next, logout from the RHC ssh console. And restart your app:

```
rhc app restart <app name>
```

### Data persistence

You can deploy this application without a configured database in your OpenShift project, in which case Django will use a SQLite database that will live inside your application's data container, and persist only between redeploys of your container. This makes the gear non-scalable.

For production it is recommended to use a properly configured database server or ask your OpenShift administrator to add one for you. Then use oc env to update the DATABASE_* environment variables in your DeploymentConfig to match your database settings.

Redeploy your application to have your changes applied, and open the welcome page again to make sure your application is successfully connected to the database server.
