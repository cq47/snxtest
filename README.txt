You need to change the "settings.py" file from "paper" folder, namely, change the "YOUR_PASSWORD" and similar fields for database authentication. 

You will also need to run the following commands (to initialise database): 
- python3 manage.py makemigrations app
- python3 manage.py migrate

You will then need to do a setup similar to one described here: https://pylessons.com/django-google-oauth (starting from title "Configuring Google APIs:" and ending on the picture that says "Sign in with Google") for Google Signin / Signup to work.

NOTE: The application was supposed to be deployed on Heroku.