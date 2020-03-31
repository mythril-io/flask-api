<p align="center">
  <a href="https://mythril.io/" target="_blank" rel="noopener noreferrer">
    <img width="250" src="https://github.com/mythril-io/mythril-ui/blob/master/src/assets/logo.svg" alt="Mythril logo"></a>
</p>
<p align="center">
  <a href="https://github.com/mythril-io/mythril-api/issues"><img src="https://img.shields.io/github/issues/mythril-io/mythril-api.svg?sanitize=true" alt="Issues"></a>
  <a href="https://discordapp.com/invite/yEbb4B2"><img src="https://img.shields.io/badge/chat-on%20discord-7289da.svg?sanitize=true" alt="Chat"></a>
</p>

# Description

An API built with [Flask](https://github.com/pallets/flask) used to serve content for [mythril.io](https://mythril.io/).

## Project setup
Setup your virtual environment and install required packages with [pipenv](https://github.com/pypa/pipenv).
```
pipenv shell
```
Create a .env file in the root folder
```
# Flask SQLAlchemy
SQLALCHEMY_DATABASE_URI= "mysql+mysqlconnector://username:password@localhost:port/database"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask Praetorian 
PRAETORIAN_SECRET_KEY = "top secret"
PRAETORIAN_CONFIRMATION_SENDER = "no-reply@mythril.io"
PRAETORIAN_CONFIRMATION_URI = "http://localhost/verify"

# Flask Mail
# A free service such as Mailtrap can be used for email testing
MAIL_SERVER = "smtp.mailtrap.io"
MAIL_PORT = port
MAIL_USERNAME = "username"
MAIL_PASSWORD = "password"

# S3/Digital Ocean Spaces
DO_SPACES_REGION = region
DO_SPACES_KEY = key
DO_SPACES_SECRET = secret
DO_SPACES_BUCKET= bucket
```
Run your Flask application.
```
flask run
```

## Database setup
Instructions coming soon.
