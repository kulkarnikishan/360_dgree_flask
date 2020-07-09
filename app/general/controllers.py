from flask import request,jsonify
from app.general import general
from cerberus import Validator
from app.utils import Response
from app import helpers as hp
import json

validator = Validator()

@general.route('/add/client', methods=['POST'])
def index():
    req_data = request.get_json()
    client = hp.ClientDetails()
    db_res = client.create(req_data)
    return db_res


@general.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    schema = {
        'emp_id': {'required': True, 'type': 'string'},
        'client_id': {'required': True, 'type': 'string'},
        'password': {'required': True, 'type': 'string'},
        'user_role': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
    login = hp.LogIn()
    response = login.validate(data)
    if response.success:
        response.data = {
            "client_id":response.data['client_id'],
            "cycle_id":response.data['cycle_id'],
            "user_type":data["user_role"],
            "user_info":{
                            "name": response.data['name'],
                            "emp_id": response.data['emp_id'],
                            "email_id": response.data['email_id']
            }
        }
        response.message = "Login Success!!"
    return response.response_json()


@general.route('/send/alert/bulk/mail', methods=['POST'])
def send_bulk_mail():
    data = request.get_json()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'},
        'dept_id': {'required': True, 'type': 'list'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.message = "Required data not found"
    bulk_mail = hp.BulkMailEmp()
    bulk_mail_resp = bulk_mail.send_alert_mail_emp(data)
    if not bulk_mail_resp.success:
        bulk_mail_resp.success = False
        bulk_mail_resp.status = 400
        bulk_mail_resp.message = "Employee details not found"
    return bulk_mail_resp.response_json()


@general.route('/send/remainder/mail', methods=['POST'])
def remainder_mail():
    pass


@general.route('/send/bulk/mail/employees', methods=['POST'])
def bulk_mail_employees():
    data = request.get_json()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'},
        'emp_id': {'required': True, 'type': 'list'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.message = "Required data not found"
    bulk_mail = hp.BulkMailEmp()
    bulk_mail_resp = bulk_mail.send_mail_emp(data)
    if not bulk_mail_resp.success:
        bulk_mail_resp.success = False
        bulk_mail_resp.status = 400
        bulk_mail_resp.message = "Employee details not found"
    return bulk_mail_resp.response_json()


@general.route('/assessment/questions', methods=['GET'])
def questions():
    ques = hp.AssessmentQuestions()
    response = ques.get_question_and_option()
    if response.success:
        response.data = {
            "questions":response.data
        }
        response.message = "Assessment Questions fetched successfully..!!!"
    return response.response_json()


@general.route('/store/assessment/answers', methods=['POST'])
def store_assessment_answers():
    data = request.get_json()
    schema = {
        'que_id': {'required': True, 'type': 'string'},
        'opt_id': {'required': True, 'type': 'string'},
        'map_id': {'required': True, 'type': 'string'},
        'answer_score': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
    store = hp.StoreAssessmentAnswers()
    store_response = store.insert(data)
    if not store_response.success:
        store_response.status = 400
        store_response.success = False
        store_response.message = "Assessment Answer Not stored!!"
    return store_response.response_json()

@general.route('/add/emp',methods=['POST'])
def emp():
    emp = [{"emp_id": "Emp1011", "emp_name": "Chandrakanth", "emp_email": "chandrak@fork.com", "function": "IT",
           "role": "Both","location": "Bangalore", "band": "B1"}]
    client = hp.Employee()
    emp = {"emp_id": "Emp1011", "cycle_id": "8", "relation_type": "Senior", "target_emp_id": "Emp1012"}
    client = hp.EmployeeRelationMapping()
    db_res = client.create(emp)
    return db_res.response_json()

@general.route('/select/client',methods=['GET'])
def select():
    emp = {"emp_id": "Emp1011", "emp_name": "Chandrakanth", "emp_email": "chandrak@fork.com", "function": "IT",
            "role": "Both", "location": "Bangalore", "band": "B1"}
    client = hp.ClientDetails()
    db_res = client.select(client_id='2')
    return db_res.response_json()

@general.route('/add/status',methods=['GET'])
def status():
    emp = {"emp_id": "Emp1011", "cycle_id": "1", "ass_com_seniors_count": 1, "ass_com_subordinates_count": 1,
            "ass_com_peer_count": 1, "ass_com_others_count": 0, "ass_com_respondant_count": 3}
    client = hp.EmployeeStatus()
    db_res = client.update(emp)
    return db_res.response_json()

@general.route('/select/emp',methods=['GET'])
def select_emp():
    emp = {"emp_id": "Emp1011", "emp_name": "Chandrakanth", "emp_email": "chandrak@fork.com", "function": "IT",
           "role": "both","location": "Bangalore", "client_id": "2","part_id":""}
    client = hp.Employee()
    db_res = client.select(emp)
    return db_res.response_json()
