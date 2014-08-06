
from flask import Flask

from flask_raven import raven_auth

app = Flask(__name__)

app.config.update(
    SECRET_KEY='super-secret-key'
)


@app.route('/')
@raven_auth()
def home():
    return "Logged in"

if __name__ == '__main__':
    app.run(debug=True)
