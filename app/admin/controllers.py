from flask import request
from app.admin import admin
from cerberus import Validator
from app.utils import Response
from app import helpers as hp

validator = Validator()


@admin.route('/add', methods=['POST'])
def add():
    pass


@admin.route('/get/cycle/details', methods=['GET'])
def get_cycle_details():
    data = {
        'client_id': request.args.get('client_id')
    }
    response = Response()
    schema = {
        'client_id': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.message = "Required data not found"
        return response.response_json()
    cycle_details = hp.ClientCycleDetails()
    cycle_response = cycle_details.select(data)
    if not cycle_response.success:
        cycle_response.success = False
        cycle_response.status = 400
        cycle_response.data = list()
        cycle_response.message = "Failed to load client cycle details"
    return cycle_response.response_json()


@admin.route('/add/cycle/details', methods=['POST'])
def add_cycle_details():
    data = request.get_json()
    response = Response()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_name': {'required': True, 'type': 'string'},
        'from_date': {'required': True, 'type': 'string'},
        'to_date': {'required': True, 'type': 'string'}
    }

    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.message = "Required data not found"
    client_cycle = hp.ClientCycleDetails()
    response = client_cycle.create(data)
    if response.success:
        response.status = 200
        response.data = {
            "client_id": response.data['client_id'],
            "cycle_id": response.data['cycle_id']
        }
        response.message = "Success"
    elif not response:
        response.success = False
        response.status = 400
        response.message = "Failure"
    return response.response_json()


@admin.route('/add/department/details', methods=['POST'])
def add_dept_details():
    data = request.get_json()
    response = Response()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'integer'},
        'function': {'required': True, 'type': 'string'},
        'role': {'required': True, 'type': 'string'},
        'location': {'required': True, 'type': 'string'},
        'band': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.message = "Required data not found"
    department = hp.ClientDeptDetails()
    add_dept = department.create(data)
    if add_dept:
        response.success = True
        response.status = 200
        response.message = "Success"
    elif not add_dept:
        response.success = False
        response.status = 400
        response.message = "Failure"
    return response.response_json()


@admin.route('/get/department/details', methods=['GET'])
def get_dept_details():
    data = {
        'client_id': request.args.get('client_id'),
        'cycle_id': request.args.get('cycle_id')
    }
    response = Response()
    schema = {
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response.success = False
        response.status = 400
        response.message = "Required data not found"
        return response.response_json()
    department = hp.ClientDeptDetails()
    dept_response = department.select(data)
    if not dept_response.success:
        dept_response.success = False
        dept_response.status = 400
        dept_response.message = "Department Details not fetched."
    return dept_response.response_json()


@admin.route('/set/survey/date', methods=['POST'])
def set_survey_date():
    pass


@admin.route('/add/bulk/employee/details', methods=['POST'])
def add_bulk_emp_details():
    pass


@admin.route('/add/employee/details', methods=['POST'])
def add_emp_details():
    data = request.get_json()
    schema = {
        'emp_id': {'required': True, 'type': 'string'},
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': True, 'type': 'string'},
        'emp_name': {'required': True, 'type': 'string'},
        'emp_email': {'required': True, 'type': 'string'},
        'function': {'required': True, 'type': 'string'},
        'location': {'required': True, 'type': 'string'},
        'band': {'required': True, 'type': 'string'},
        'role': {'required': True, 'type': 'string'},
        'assessment_role': {'required': True, 'type': 'string'},
        'relationship': {'required': True, 'type': 'dict','schema':{
            'relation_type': {'type': 'string'},
            'target_emp_id': {'type': 'string'}
        }}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
    employee = hp.Employee()
    response = employee.create([data])
    if response.success:
        maping = hp.EmployeeRelationMapping()
        db_res = maping.create({
            "emp_id": data["emp_id"], "cycle_id": data["cycle_id"],
            "relation_type": data['relationship']["relation_type"], "target_emp_id": data['relationship']["target_emp_id"]
        })
        if not db_res.success:
            response.success = False
            response.status = 400
            response.errors = "Employee relation not added"
    elif not response.success:
        response.success = False
        response.status = 400
        response.errors = "Employee relation not added"
    return response.response_json()


@admin.route('/generate/report', methods=['POST'])
def generate_report():
    pass

@admin.route('/block/report', methods=['POST'])
def block_report():
    pass


@admin.route('/unblock/report', methods=['POST'])
def unblock_report():
    pass


@admin.route('/assessment/completion', methods=['GET'])
def assessment_completion():
    pass


@admin.route('/details', methods=['GET'])
def details():
    pass


@admin.route('/<id>', methods=['PUT'])
def update_admin(id):
    pass


@admin.route('/<id>', methods=['DELETE'])
def delete_admin(id):
    pass


@admin.route('/employee/details', methods=['PUT'])
def update_employee():
    data = request.get_json()
    schema = {
        'emp_id': {'required': True, 'type': 'string'},
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': False, 'type': 'string'},
        'update_json': {'required': True, 'type': 'dict'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
    employee = hp.Employee()
    response = employee.update(data,data['update_json'])
    if not response.success:
        response.success = False
        response.status = 400
        response.errors = "Employee relation not added"
    return response.response_json()


@admin.route('/employee/details', methods=['DELETE'])
def employee_details():
    data = request.get_json()
    schema = {
        'emp_id': {'required': True, 'type': 'string'},
        'client_id': {'required': True, 'type': 'string'},
        'cycle_id': {'required': False, 'type': 'string'}
    }
    res = validator.validate(data, schema)
    if not res:
        response = Response()
        response.success = False
        response.status = 400
        response.errors = "Required data not provided."
    employee = hp.Employee()
    response = employee.delete(data)
    if not response.success:
        response.success = False
        response.status = 400
        response.errors = "Employee relation not added"
    return response.response_json()


