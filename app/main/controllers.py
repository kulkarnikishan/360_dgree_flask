from flask import Flask,Blueprint
import config

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return 'Welcome to '+config.PLATFORM_NAME+' Platform'