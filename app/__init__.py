from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_raw_jwt
)
import os, logging
from flask_sqlalchemy import SQLAlchemy

from app.main.controllers import main
from app.admin.controllers import admin
from app.general.controllers import general
from app.participants.controllers import participants
from app.respondants.controllers import respondants

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '#0rK-X@v!3R-$3cr3!K3y'
app.config['JWT_BLACKLIST_ENABLED'] = False
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

CORS(app)
jwt = JWTManager(app)

app.config.from_object('config')

# Setup logging
LOG_FOLDER = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                           os.pardir, os.pardir,
                                           'var', 'log'))
LOG_FILE = ("{}/mod_360_assessment_survey.log".format(LOG_FOLDER))
print(LOG_FILE)
logger = logging.getLogger('@mod_360_assessment_survey.route')
hdlr = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(general, url_prefix='/api/v1/general')
app.register_blueprint(admin, url_prefix='/api/v1/admin')
app.register_blueprint(participants, url_prefix='/api/v1/participants')
app.register_blueprint(respondants, url_prefix='/api/v1/respondants')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


@app.errorhandler(404)
def not_found(error):
    print('404 error for url:', request.url)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def internal_error(exception):
    # logger.error(exception)
    print('Error handler => ' + str(exception))
    return make_response(jsonify({'error': 'Server Fatal Error! Kindly Hang on!'}), 404)


@app.errorhandler(Exception)
def unhandled_exception(exception):
    print('Unhandled Error handler => ' + str(exception))
    return make_response(jsonify({'error': 'Server Fatal Error! Kindly Hang on!!'}), 404)
