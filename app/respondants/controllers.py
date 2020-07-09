from flask import Flask,request
from app.respondants import respondants
import config
from app import helpers as hp
from cerberus import Validator
from app.utils import Response

validator = Validator()

@respondants.route('/details', methods=['GET'])
def all_respondant_details():
    data = {
        'client_id': request.args.get('client_id'),
        'cycle_id': request.args.get('cycle_id')
    }
    if request.args.get('part_id') is not None:
        data['part_id'] = request.args.get('part_id')
    response = Response()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'}
    }
    validator.allow_unknown = True
    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
        return response.response_json()
    data["assessment_role"]="respondant"
    emp_ids = hp.EmployeeRelationMapping()
    emp_ids_response = emp_ids.select(data)
    if emp_ids_response.success:
        data['emp_ids'] = list()
        for ids in emp_ids_response.data:
            data['emp_ids'].append(ids['pat_emp_id'])
        employee = hp.Employee()
        employee_response = employee.select(data)
        if employee_response.success:
            response.message = "Respondents details fetched."
            response.status = 200
            response.data = {
                                "respondants_details":employee_response.data
            }
        elif not employee_response.success:
            response.success = False
            response.status = 400
            response.errors = "Respondents details not fetched."
    else:
        emp_ids.success = False
        emp_ids.status = 400
        emp_ids.errors = "Respondents details not fetched."

    return response.response_json()



@respondants.route('/assessment/status', methods=['GET'])
def assessment_status():
    data = {
        'client_id':request.args.get('client_id'),
        'cycle_id':request.args.get('cycle_id')
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
    data['part_ids'] = ['Emp1011', 'Emp1012']
    status = hp.Respondent()
    status_response = status.get_respondent_assessment_status(data)
    if status_response.success:
        status_response.message = "Participants details fetched."
    elif not status_response.success:
        status_response.success = False
        status_response.status = 400
        status_response.errors = "Participants details not fetched."
    return status_response.response_json()


@respondants.route('/assessment/status/<emp_id>', methods=['GET'])
def emp_assessment_status(emp_id):
    pass


@respondants.route('/store/feedbacks', methods=['POST'])
def store_feed_backs():
    pass
