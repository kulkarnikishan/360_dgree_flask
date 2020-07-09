from flask import request
from app.participants import participants
from app.utils import Response
from cerberus import Validator
from app import helpers as hp

validator = Validator()


@participants.route('/details',methods=['GET'])
def paticipant_details():
    data = {
        'client_id': request.args.get('client_id'),
        'cycle_id': request.args.get('cycle_id')
    }
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
        return response.response_json()
    data["assessment_role"]="participant"
    employee = hp.Employee()
    response = employee.select(data)
    if response.success:
        response.message = "Employe details added "
        response.data = {
                            "participant_details":response.data
        }
    elif not response.success:
        response.success = False
        response.status = 400
        response.errors = "Participants details not fetched."
    return response.response_json()


@participants.route('/assessment/status',methods=['GET'])
def get_assessment_status():
    data = {
        'client_id': request.args.get('client_id'),
        'cycle_id': request.args.get('cycle_id')
    }
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
        return response.response_json()
    status = hp.Participant()
    status_response = status.get_participant_assessment_status(data)
    if status_response.success:
        status_response.message = "Employe details added "
    elif not status_response.success:
        status_response.success = False
        status_response.status = 400
        status_response.errors = "Participants details not fetched."
    return status_response.response_json()



@participants.route('/store/feedbacks', methods=['POST'])
def store_feedback():
    data = request.get_json()
    response = Response()
    schema = {
        'client_id': {'required':True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'integer'},
        'map_id': {'required': True, 'type': 'integer'},
        'level_id': {'required': True, 'type': 'integer'},
        'feedback_text': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.message = "Required data not found"
    store_feed = hp.StoreFeedback()
    response = store_feed.create(data)
    if response.success:
        response.success = True
        response.status = 200
        response.data = {}
        response.message = "Success"
    elif not response:
        response.success = False
        response.status = 400
        response.message = "Failure"
    return response.response_json()