# Warrrrrbler

Warrrrrbler is a twitter clone written in Python using Flask as a framework. Users can signup/login, follow other users, be followed by other users, and warrrrrble to their heart's content (aka tweet). 

  - User authentication and authorization is done with bcrypt.
  - Sessions are used to store current user information.
  - Jinja2 is used as the templating system.
  - The database is PostgreSQL.
  - Tests are written for the views and models using the unittest module. 

See a live demo here: https://warrrrrbler.herokuapp.com/

## Setup

To clone the repository, run the following command in your terminal: 
```
git clone https://github.com/KatieJessupMcd/warbler.git
```

Create a virtual environment - I use [virtualenv](https://virtualenv.pypa.io/) and install the requirements from:
```
requirements.txt
```

Run the following command to start the app: 
```
flask run
```

Copy and paste the http adress into your url bar
```
http://127.0.0.1:5000/
```