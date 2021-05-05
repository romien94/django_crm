**A small django based CRM project.**

**The .env file must locate in the django_crm folder.**

Once you've cloned the repo, establish a venv for the project, go to
the project root folder and run command pip install -r requirements.txt.

If you want to use the project with a Postgresql database, 
make sure to create it and fill all the db related data in the
.env file. Otherwise, just comment out the Postgresql settings
in the settings.py file and uncomment dbsql settings.

Do not forget to fill in the .env file based on the .template.env

Before launching the app you have to set an environment variable READ_ENV_FILE=True
in order to let the project access variables previously set in the .env file.

Now you can run the classy python manage.py runserver command and apply all migrations.
Do not forget to create a superuser.