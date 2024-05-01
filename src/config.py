from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ Configuration values pulled from the src/.env file using
    .env.default as a template.
    """
    DATA_DIR = "./covid_mortality.csv"
    DATE_COL = environ.get('DATE_COL')
    RATIO_COLS = environ.get('RATIO_COLS').strip(',').split(',') if environ.get('RATIO_COLS') else environ.get('RATIO_COLS')
    DROP_DOWN_COL = environ.get('DROP_DOWN_COL')
    SITE_NAME = environ.get('SITE_NAME')
    AUTHOR = environ.get('AUTHOR')

