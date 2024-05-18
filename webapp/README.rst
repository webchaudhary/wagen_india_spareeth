Instructions
=============

* In a new system (Only tested in Ubuntu server) install the following software

  * PostgreSQL and its developing package
  * PostGIS
  * GRASS GIS
  * redis
  * git
  * GDAL software 
  * Apache
  * Virtualenv
  * Compilers
  * Python3 devel packages


**Install following packages**

Open a terminal and use following commands to install required libraries.

``sudo apt-get install git gdal-bin apache2 postgis redis-server virtualenv build-essential python3-dev libpq-dev pango1.0-tools``

``sudo apt-get install postgresql postgresql-postgis``

* Install grass gis using following commands

``sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable``

``sudo apt-get install grass grass-dev``

* Create a new grass location for wagen_india app

``grass -c EPSG:4326 -e /path/to/grassdata/wagen_india``

(Note that, in settings.py file "GRASS_DB" should be set as "/path/to/grassdata")

* Create an empty PostgreSQL database with PostGIS extension

``sudo -u postgres createuser wagen``

Open psql in the terminal using following command

``sudo -u postgres psql``

In the psql command:

| *# Change password of postgres user*
| ``ALTER USER postgres PASSWORD '*******';``
| ``ALTER USER wagen PASSWORD '********';``
| *# Give more privileges to user wagen*
| ``ALTER USER wagen WITH SUPERUSER;``
| *# quit psql*
| ``\q``

Create a new DB named "wagen":

| ``createdb -U YOURUSER -h YOURHOST wagen``
| ``psql -U YOURUSER -h YOURHOST wagen -c "CREATE EXTENSION postgis"``

* Download this source code and enter in directory wagen/webapp

* Create a Python 3 virtual environment in the webapp directory

``virtualenv -p /usr/bin/python3 venv``

* Activate the virtual environment

``source venv/bin/activate``

* Install dependencies with `pip`

``pip install -r requirements.txt``

* Set connection to the database and create its structure

  ```bash
  cd wagen
  cp wagen/template_settings.py wagen/settings.py
  # add user, password and grass settings in wagen/settings.py
  python manage.py makemigrations webapp
  python manage.py migrate
  # create a new user to access the features of web app
  python manage.py createsuperuser --username admin
  # to see the help
  python manage.py help
  ```

* The first time you run the webapp in the admin page (in testing mode is http://127.0.0.1:8000/admin),
  go to "sites" tab on left panel and Change the Domain name to the
  domain where the webapp is hosted. In case of localhost, change to 127.0.0.1:8000.
  The report will not adapt the template unless this change is made.

TESTING
^^^^^^^

* Start celery worker to use asynchronous requests

  `celery -A wagen worker -l INFO`

* At this point you could run the app

  `python manage.py runserver`

* Open web browser at http://127.0.0.1:8000/

DEPLOYMENT
^^^^^^^^^^^

* Create all the stuff needed to run celery in deployment mode

  ```bash
  # create the pid directory
  sudo mkdir /var/run/celery/
  sudo chown -R wagen.wagen /var/run/celery/
  # copy the systemd configuration file
  ln -s /home/wagen/wagen/webapp/wagen/celery_wagen.service /etc/systemd/system
  # modify the environment file if needed 
  # (for example the timeout for a single job set to 3000 seconds or number of concurrency set to 8)

  # reload the systemd files (this has been done everytime celery_wagen.service is changed)
  sudo systemctl daemon-reload
  # enable the service to be automatically start on boot
  sudo systemctl enable celery_wagen.service
  ```

* Start the celery app

  ```
  sudo systemctl start celery_wagen.service
  # to look if everything is working properly you can

  sudo systemctl status celery_wagen.service
  ls -lh /home/wagen/wagen/log/celery/
  tail -f /home/wagen/wagen/log/celery/worker1.log
  ```

* Copy the template `ini` file and modify the paths

  ```bash
  cp wagen/template_wagen.ini wagen/wagen.ini
  ```

* Copy the template Apache configuration file and modify it, specially the path

  ```bash
  sudo cp wagen/template_apache.conf /etc/apache2/sites-available/wagen.conf
  ```
* Install uwsgi python package in the venv
  (install it in the virtualenv environment)

  `pip install uwsgi`

* Install uwsgi libapache in the ubuntu system

  `sudo apt install libapache2-mod-uwsgi`

* Enable uwsgi and ssl module in apache

  `sudo a2enmod uwsgi`
  `sudo a2enmod ssl`

* Run the Django app using `uwsgi`
  (install it in the virtualenv environment)

  `uwsgi wagen.ini`

* Activate the Apache configuration file

  ```bash
  sudo a2ensite wagen
  sudo systemctl restart apache2
  ```
