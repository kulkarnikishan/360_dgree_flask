import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.getenv("DEBUG", False)

PRODUCTION = os.getenv("PRODUCTION", False)

SERVER_HOST = os.getenv("SERVER_HOST", '0.0.0.0')
SERVER_PORT = int(os.getenv("SERVER_PORT", 8090))
SECRET_KEY="ewfretwa"

SESSION_TIME = 86400 # 1 day = 24*60*60

# Define the database - we are working with
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:!000Assessment@assessment360.ccctxzvfcty8.us-east-2.rds.amazonaws.com/360_degree_assessment'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_ECHO=False
SQLALCHEMY_POOL_RECYCLE=3600

# Logs
LOG_DIR = 'logs'
LOCAL_LOGGING_FILENAME = 'logging.log'

PRESERVE_CONTEXT_ON_EXCEPTION = True

# Platform General Info
PLATFORM_NAME= os.getenv("PLATFORM_NAME", '360Degree Assessment Survey')