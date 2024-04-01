from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ Configuration values pulled from the src/.env file using
    .env.default as a template.
    """
    APP_HOST = environ.get('APP_HOST')
    APP_PORT = environ.get('APP_PORT')

    DATA_DIR = environ.get('DATA_DIR')

    DEBUG = environ.get('DEBUG')

    SECRET_KEY = environ.get('SECRET_KEY')

    CAS_CLIENT_VERSION = environ.get('CAS_CLIENT_VERSION')
    CAS_SERVICE_URL = environ.get('CAS_SERVICE_URL')
    CAS_SERVER_URL = environ.get('CAS_SERVER_URL')

    DATE_COL = environ.get('DATE_COL')
    RATIO_COLS = environ.get('RATIO_COLS').strip(',').split(',') if environ.get('RATIO_COLS') else environ.get('RATIO_COLS')
    DROP_DOWN_COL = environ.get('DROP_DOWN_COL')
    SITE_NAME = environ.get('SITE_NAME')
    AUTHOR = environ.get('AUTHOR')

