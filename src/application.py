from flask import Flask, redirect, url_for, render_template, session
from functools import wraps
from logging.config import dictConfig
from config import Config
from auth import generate_session, kill_session
from dash_app import init_dashboard
import argparse


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {
            "level": "DEBUG", 
            "handlers": ["console"]
        }
    }
)


app = Flask(__name__)
app.config.from_object(Config)


def login_required(f):
    """ Apply this decorator to require an active login session when accessing
    the associated view, otherwise display a "login required" message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return render_template('login_required.html')
    return decorated_function


def anonymous_required(f):
    """ Apply this decorator to require an anonymous session when accessing the
    associated view, otherwise redirect to the app landing page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return decorated_function


@app.route('/')
def index():
    return render_template('app_landing.html')


@app.route('/login')
def login():
    """ Send a user to Rice CAS to start the creation of a new user session.
    """
    location = generate_session()
    return redirect(location)


@app.route('/logout')
def logout():
    """ Kill the local user session and redirect to Rice CAS to do the same
    there.
    """
    location = kill_session()
    return redirect(location)


@app.route('/logout_callback')
def logout_callback():
    """ Rice CAS does not currently utilize a logout callback. Leaving
    this here for thoroughness.
    """
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def account():
    """ Require an active login session for this route.
    """
    return render_template('profile.html',
                           username=session['username'])
                    

def protect_dashviews(dash_app):
    for view_func in app.view_functions:
        if view_func.startswith(dash_app.config.routes_pathname_prefix):
            app.view_functions[view_func] = login_required(app.view_functions[view_func])


if __name__ == '__main__':
    # arg parse
    parser = argparse.ArgumentParser(description='Specify the Host and Port for run the web application')
    parser.add_argument('--host', type=str, default=app.config['APP_HOST'], help='The host on which the web server will listen')
    parser.add_argument('--port', type=int, default=app.config['APP_PORT'], help='The port on which the web server will listen')
    parser.add_argument('--datadir', type=str, default=app.config["DATA_DIR"], help='The directory of data source')
    parser.add_argument('--debug', type=bool, default=app.config["DEBUG"], help='The DEBUG option of Flask.run')
    args = parser.parse_args()

    dash_app = init_dashboard(app, args.datadir)
    protect_dashviews(dash_app)

    app.run(
        debug=args.debug,
        host=args.host, 
        port=args.port, 
    )

