import app.models as models
from .__init__ import db, logger
from app.utils import randon_hash_string, Response, password_generator, get_cur_date
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
import itertools

class ClientDetails:
    """To perform CRUD operations for the table client_table_m"""

    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            new_client = models.ClientRepo(
                client_id=randon_hash_string(),
                client_name=json_data.get('client_name', None),
                client_email_id=json_data.get('client_email_id', None),
                client_uri=json_data.get('client_uri', '')
            )
            db.session.add(new_client)
            db.session.commit()
            print(new_client)
            self.response.message = 'Client created successfully..!!!'
        except SQLAlchemyError as error:
            print(error)
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def select(self, **json_data):
        self.response.data = list()
        try:
            if not json_data:
                clients = db.session.query(models.ClientRepo).all()
                for client in clients:
                    self.response.data.append(client.get_json())
            elif json_data:
                clients = db.session.query(models.ClientRepo).filter_by(**json_data).first()
                if clients is not None:
                    self.response.data.append({
                        "client_name": clients.client_name,
                        "client_email_id": clients.client_email_id
                    })
                    self.response.status = 200
                else:
                    self.response.status = 400
                    self.response.success = False
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response

    def delete(self, json_data):
        try:
            db.session.query(models.ClientRepo).filter_by(**json_data).delete()
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response


class Employee:
    """To perform CRUD operations for the table employee_details_m"""

    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            if isinstance(json_data, list):
                for emp in json_data:
                    new_emp = models.EmployeeDetailsRepo(
                        emp_id=emp.get('emp_id', None),
                        client_id=emp.get('client_id', None),
                        emp_name=emp.get('emp_name', None),
                        emp_email=emp.get('emp_email', ''),
                        department_id=db.session.query(models.ClientDepartmentsDetailsRepo.department_id).
                            filter(and_(models.ClientDepartmentsDetailsRepo._function == emp.get('function', ''),
                                        models.ClientDepartmentsDetailsRepo.location == emp.get('location', ''),
                                        models.ClientDepartmentsDetailsRepo.band == emp.get('band',''))).first().department_id,
                        role_id=db.session.query(models.UserRoleRepo.role_id).
                            filter_by(role_type=emp.get('assessment_role')).first().role_id,
                        password=password_generator()
                    )
                    db.session.add(new_emp)
                    db.session.commit()
                    self.response.message = 'Employee added successfully..!!!'
            else:
                self.response.status = 400
                self.response.success = False
                self.response.message = 'Invalid data type'
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)

        finally:
            db.session.close()
        return self.response

    def select(self, json_data):
        self.response.data = list()
        try:
            select = db.session.query(models.EmployeeDetailsRepo.emp_id, models.EmployeeDetailsRepo.emp_name,
                                      models.EmployeeDetailsRepo.emp_email,
                                      models.ClientDepartmentsDetailsRepo._function,
                                      models.ClientDepartmentsDetailsRepo.role,
                                      models.ClientDepartmentsDetailsRepo.location,
                                      models.ClientDepartmentsDetailsRepo.band)
            if json_data['assessment_role'].lower() == 'participant':
                employees = select.join(models.ClientDepartmentsDetailsRepo).filter(
                    and_(models.EmployeeDetailsRepo.client_id == json_data['client_id'],
                         models.EmployeeDetailsRepo.role_id .in_((1, 3)))).all()
            elif json_data['assessment_role'].lower() == 'respondant':
                if 'part_id' in json_data:
                    employees = select.join(models.ClientDepartmentsDetailsRepo).filter(
                        and_(models.EmployeeDetailsRepo.client_id == json_data['client_id'],
                             models.EmployeeDetailsRepo.emp_id.in_(json_data['emp_ids']))).all()
                else:
                    employees = select.join(models.ClientDepartmentsDetailsRepo).filter(
                        and_(models.EmployeeDetailsRepo.client_id == json_data['client_id'],
                             models.EmployeeDetailsRepo.role_id.in_((2,3)))).all()
            elif json_data['assessment_role'].lower() == 'both':
                employees = select.join(models.ClientDepartmentsDetailsRepo).filter(
                    and_(models.EmployeeDetailsRepo.client_id == json_data['client_id'],
                         models.EmployeeDetailsRepo.role_id == 3)).all()
            else:
                self.response.status = 400
                self.response.success = False
                self.response.message = "Invalid User Role."
                return self.response
            for employee in employees:
                self.response.data.append({
                    "emp_id": employee.emp_id,
                    "emp_name": employee.emp_name,
                    "emp_email": employee.emp_email,
                    "function": employee._function,
                    "role": employee.role,
                    "location": employee.location,
                    "band": employee.band
                })

        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.message = str(error)
            self.response.success = False
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def update(self, json_data, filter_data):
        try:
            status = models.ParticipantsAssessmentStatus.query.filter_by(emp_id=filter_data['emp_id'],
                                                                         cycle_id=filter_data['cycle_id']).first()
            for key, value in json_data.items():
                setattr(status, key, value)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def delete(self, json_data):
        try:
            db.session.query(models.EmployeeDetailsRepo).filter_by(client_id=json_data['client_id'],
                                                                   emp_id=json_data['emp_id']).delete()
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.message = str(error)
            self.response.success = False
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response


class EmployeeRelationMapping:
    """To perform CRUD operations for the table employee_relation_mapping_t"""

    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            new_mapings = models.EmployeRelationMapping(
                cycle_id=json_data.get('cycle_id', ''),
                pat_emp_id=json_data.get('emp_id', ''),
                relation_id=db.session.query(models.UserRelationRepo.relation_id).filter_by(
                            relation_type=json_data['relation_type']).first().relation_id,
                target_emp_id=json_data.get('target_emp_id', '')
            )
            db.session.add(new_mapings)
            db.session.commit()
            db.session.flush()
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def select(self, json_data):
        self.response.data = list()
        try:
            if 'part_id' not in json_data:
                results = db.session.query(models.EmployeRelationMapping).filter_by(cycle_id=json_data['cycle_id']).all()

            elif 'part_id' in json_data:
                results = db.session.query(models.EmployeRelationMapping).filter(models.EmployeRelationMapping.
                                     cycle_id==json_data['cycle_id'],and_(models.EmployeRelationMapping.target_emp_id==json_data['part_id'],
                                     models.EmployeRelationMapping.relation_id > 0)).all()

            else:
                results = []
                self.response.status = 400
                self.response.success = False
            for item in results:
                self.response.data.append(item.get_json())
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response

    def delete(self, json_data):
        try:
            db.session.query(models.ClientRepo).filter_by(**json_data).delete()
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response

class EmployeeStatus:
    """To perform CRUD operations for the table participant_ass_status_t"""

    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            new_emp_status = models.ParticipantsAssessmentStatus(
                emp_id=json_data.get('emp_id', None),
                cycle_id=json_data.get('cycle_id', None),
                total_respondant_count=json_data.get('total_respondant_count', 0),
                seniors_count=json_data.get('seniors_count', 0),
                subordinates_count=json_data.get('subordinates_count', 0),
                peer_count=json_data.get('peer_count', 0),
                others_count=json_data.get('others_count', 0)
            )
            db.session.add(new_emp_status)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def update(self, json_data):
        try:
            status = models.ParticipantsAssessmentStatus.query.filter_by(emp_id=json_data['emp_id'],
                                                                         cycle_id=json_data['cycle_id']).first()
            for key, value in json_data.items():
                setattr(status, key, value)
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response

    def select(self, json_data):
        self.response.data = list()
        if 'id' in json_data:
            status = models.ParticipantsAssessmentStatus.query.filter_by(id=json_data['id']).all()
            for item in status:
                self.response.data.append(item.get_json())
        elif 'emp_id' in json_data and 'cycle_id' in json_data:
            status = models.ParticipantsAssessmentStatus.query.filter_by(emp_id=json_data['emp_id'],
                                                                         cycle_id=json_data['cycle_id']).all()
            for item in status:
                self.response.data.append(item.get_json())


class Participant:
    """Contains methods required for participant routing"""

    def __init__(self):
        self.response = Response()

    def get_participant_assessment_status(self,json_data):
        try:
            self.response.data = list()
            select = db.session.query(models.EmployeeDetailsRepo.emp_id, models.EmployeeDetailsRepo.emp_name,
                                          models.EmployeeDetailsRepo.emp_email,
                                          models.ClientDepartmentsDetailsRepo._function,
                                          models.ClientDepartmentsDetailsRepo.role,
                                          models.ClientDepartmentsDetailsRepo.location,
                                          models.ClientDepartmentsDetailsRepo.band,
                                          models.AssessmentCompletionStatusRepo.status_type).filter_by(client_id = json_data['client_id'])
            status = select.join(models.ClientDepartmentsDetailsRepo,models.ClientDepartmentsDetailsRepo.department_id == models.EmployeeDetailsRepo.department_id) \
                .join(models.ParticipantsAssessmentStatus, models.ParticipantsAssessmentStatus.emp_id==models.EmployeeDetailsRepo.emp_id) \
                .join(models.AssessmentCompletionStatusRepo,models.AssessmentCompletionStatusRepo.status_id==models.ParticipantsAssessmentStatus.completion_status_id).\
                filter(models.EmployeeDetailsRepo.role_id.in_((1,3))).all()
            if len(status) > 0:
                for items in status:
                    self.response.data.append({
                        "emp_id":items.emp_id,
                        "emp_name":items.emp_name,
                        "emp_email":items.emp_email,
                        "function":items._function,
                        "role":items.role,
                        "location":items.location,
                        "band":items.band,
                        "status_type":items.status_type
                    })
            else:
                self.response.success = False
                self.response.status = 400
                self.response.message = "Participant status not retrieved."
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response



class Respondent:
    """Contains methods required for participant routing"""

    def __init__(self):
        self.response = Response()

    def get_respondent_assessment_status(self,json_data):
        try:
            self.response.data = list()
            select = db.session.query(models.EmployeeDetailsRepo.emp_id, models.EmployeeDetailsRepo.emp_name,
                                          models.EmployeeDetailsRepo.emp_email,
                                          models.ClientDepartmentsDetailsRepo._function,
                                          models.ClientDepartmentsDetailsRepo.role,
                                          models.ClientDepartmentsDetailsRepo.location,
                                          models.ClientDepartmentsDetailsRepo.band,
                                          models.AssessmentCompletionStatusRepo.status_type).filter_by(client_id = json_data['client_id'])
            if 'part_ids' in json_data:
                status = select.join(models.ClientDepartmentsDetailsRepo,
                                     models.ClientDepartmentsDetailsRepo.department_id == models.EmployeeDetailsRepo.department_id) \
                    .join(models.ParticipantsAssessmentStatus,
                          models.ParticipantsAssessmentStatus.emp_id == models.EmployeeDetailsRepo.emp_id) \
                    .join(models.AssessmentCompletionStatusRepo,
                          models.AssessmentCompletionStatusRepo.status_id == models.ParticipantsAssessmentStatus.completion_status_id). \
                    filter(models.EmployeeDetailsRepo.emp_id.in_(json_data['part_ids'])).all()
            else:
                status = select.join(models.ClientDepartmentsDetailsRepo,models.ClientDepartmentsDetailsRepo.department_id == models.EmployeeDetailsRepo.department_id) \
                    .join(models.ParticipantsAssessmentStatus,
                          models.ParticipantsAssessmentStatus.emp_id==models.EmployeeDetailsRepo.emp_id) \
                    .join(models.AssessmentCompletionStatusRepo,
                          models.AssessmentCompletionStatusRepo.status_id==models.ParticipantsAssessmentStatus.completion_status_id).\
                    filter(models.EmployeeDetailsRepo.role_id.in_((2,3))).all()
            if len(status) > 0:
                for items in status:
                    self.response.data.append({
                        "emp_id":items.emp_id,
                        "emp_name":items.emp_name,
                        "emp_email":items.emp_email,
                        "function":items._function,
                        "role":items.role,
                        "location":items.location,
                        "band":items.band,
                        "status_type":items.status_type
                    })
            else:
                self.response.success = False
                self.response.status = 400
                self.response.message = "Participant status not retrieved."
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response



class Questions:
    """To fetch assessment questions and options"""

    def __init__(self):
        self.response = Response()

    def select(self):
        pass


class ClientAdminDetails:
    """To perform CRUD operations for the table client_table_m"""

    def __init__(self):
        self.response = Response()


    def select(self, json_data):
        try:
            admins = db.session.query(models.ClientAdminRepo,models.EmployeeDetailsRepo).join(
                models.EmployeeDetailsRepo,models.EmployeeDetailsRepo.emp_id == models.ClientAdminRepo.emp_id
            ).join(models.ClientCycleRepo,
                models.ClientCycleRepo.cycle_id == models.ClientAdminRepo.cycle_id
            ).filter(and_(
                models.ClientCycleRepo.client_id == json_data['client_id'],
                models.ClientCycleRepo.is_active == True,
                models.ClientAdminRepo.emp_id == json_data['emp_id']
            )).first()
            if admins is not None:
                self.response.data={
                                    "name": admins.EmployeeDetailsRepo.emp_name,
                                    "emp_id":admins.EmployeeDetailsRepo.emp_id,
                                    "email_id": admins.EmployeeDetailsRepo.emp_email,
                                    "cycle_id":admins.ClientAdminRepo.cycle_id
                                }
                print(self.response.response_json())
                self.response.status = 200
            else:
                self.response.status = 400
                self.response.success = False
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.message = str(error)
            self.response.success = False
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response


class LogIn:
    def __init__(self):
        self.response = Response()

    def validate(self,json_data):
        try:
            if json_data.get('user_role','').lower() == 'admin':
                admins = db.session.query(models.ClientAdminRepo, models.EmployeeDetailsRepo).join(
                    models.EmployeeDetailsRepo, models.EmployeeDetailsRepo.emp_id == models.ClientAdminRepo.emp_id
                ).join(models.ClientCycleRepo,
                       models.ClientCycleRepo.cycle_id == models.ClientAdminRepo.cycle_id
                       ).filter(and_(
                    models.ClientCycleRepo.client_id == json_data['client_id'],
                    models.ClientCycleRepo.is_active == True,
                    models.ClientAdminRepo.emp_id == json_data['emp_id']
                )).first()
                if admins is not None and admins.ClientAdminRepo.password_ == json_data['password']:
                    self.response.data = {
                        "name": admins.EmployeeDetailsRepo.emp_name,
                        "emp_id": admins.EmployeeDetailsRepo.emp_id,
                        "email_id": admins.EmployeeDetailsRepo.emp_email,
                        "cycle_id": admins.ClientAdminRepo.cycle_id,
                        "client_id": admins.ClientAdminRepo.client_id
                    }
                    self.response.status = 200
                else:
                    self.response.success = False
                    self.response.status = 400
                    self.response.errors = "Invalid UserId and Password"
            elif json_data.get('user_role','').lower() == 'participant' or json_data.get('user_role','').lower() == 'respondant':
                user = db.session.query(models.EmployeeDetailsRepo).filter_by(client_id=json_data['client_id'],emp_id=json_data['emp_id']).first()
                if user is not None and user.password == json_data['password']:
                    self.response.status = 200
                    self.response.data = {
                        "name": user.emp_name,
                        "emp_id": user.emp_id,
                        "email_id": user.emp_email,
                        "client_id": user.client_id,
                        "cycle_id": db.session.query(models.ClientCycleRepo.cycle_id).
                            filter_by(client_id=json_data['client_id'], is_active=True).first().cycle_id
                    }
                    self.response.status = 200
                else:
                    self.response.status = 400
                    self.response.success = False
                    self.response.errors = "Invalid UserId and Password"
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)

        return self.response


class AssessmentQuestions:
    def __init__(self):
        self.response = Response()

    def get_question_and_option(self):
        self.response.data = list()
        try:
            question = db.session.query(models.AssessmentQuestionsRepo.que_id,models.AssessmentQuestionsRepo.que_statement)
            for ques in question:
                option_fields = ["opt_id","opt_statement","opt_score"]
                options = db.session.query(models.QuestionOptionsMapping.opt_id,models.AssessmentOptionsRepo.opt_statement,
                                           models.AssessmentOptionsRepo.opt_score).join(
                    models.AssessmentOptionsRepo,models.AssessmentOptionsRepo.opt_id == models.QuestionOptionsMapping.opt_id
                ).filter(models.QuestionOptionsMapping.que_id == ques.que_id).all()
                self.response.data.append(
                    {
                        "que_id": ques.que_id,
                        "que_statement": ques.que_statement,
                        "options": [dict(zip(option_fields, d)) for d in options]
                    }
                )

        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)

        return self.response


class ClientCycleDetails:
    """ To perform crud operations for the table client_cycle_details_m"""
    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        created_date = get_cur_date()
        try:
            client_cycle = models.ClientCycleRepo(
                client_id=json_data.get('client_id', None),
                cycle_name=json_data.get('cycle_name', None),
                created_date=created_date,
                from_date=json_data.get('from_date', None),
                to_date=json_data.get('to_date', None),
                is_active=True
            )
            db.session.add(client_cycle)
            db.session.commit()
            db.session.flush()
            self.response.data = {
                "client_id": client_cycle.client_id,
                "cycle_id": client_cycle.cycle_id
            }
            self.response.success = True

        except SQLAlchemyError as error:
            print(error)
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)

        finally:
            db.session.close()
        return self.response

    def select(self, json_data):
        try:
            if not json_data:
                cycles = db.session.query(models.ClientCycleRepo).all()
                for cycle in cycles:
                    self.response.data.append(cycle.get_json())
            elif json_data:
                cycles = db.session.query(models.ClientCycleRepo).filter(models.ClientCycleRepo.client_id == json_data['client_id']).all()
                if cycles is not None:
                    self.response.data = {
                        "client_id": cycles[0].client_id,
                        "cycle_details": list()
                    }
                    for cycle in cycles:
                        self.response.data["cycle_details"].append({
                            "cycle_id": cycle.cycle_id,
                            "cycle_name": cycle.cycle_name,
                            "from_date": str(cycle.from_date),
                            "to_date": str(cycle.to_date)
                        })
                    self.response.status = 200
                else:
                    self.response.status = 400
                    self.response.success = False
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response

    def delete(self,json_data):
        try:
            db.session.query(models.ClientCycleRepo).filter_by(**json_data).delete()
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response


class ClientDeptDetails:
    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            client_dept = models.ClientDepartmentsDetailsRepo(
                cycle_id=json_data.get('cycle_id', None),
                _function=json_data.get('function', ''),
                role=json_data.get('role',''),
                location=json_data.get('location',''),
                band=json_data.get('band','')
            )

            db.session.add(client_dept)
            db.session.commit()
            # self.response.message = "Client department created successfully"
        except SQLAlchemyError as error:
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            print(error)

        finally:
            db.session.close()
        return self.response.response_json()

    def select(self, json_data):
        try:
            client_depts = db.session.query(models.ClientDepartmentsDetailsRepo).filter_by(
                cycle_id=json_data['cycle_id']).all()
            if len(client_depts)>0:
                self.response.data = {
                    "client_id": json_data['client_id'],
                    "department_details" : list()
                }
                for dept in client_depts:
                    self.response.data["department_details"].append({
                        "department_id": dept.department_id,
                        "function": dept._function,
                        "role": dept.role,
                        "location": dept.location,
                        "band": dept.band
                    })
                self.response.message = "Department Details Fetched."
            else:
                self.response.success = False
                self.response.status = 400
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response

    def update(self, json_data):
        try:
            status = models.ClientDepartmentsDetailsRepo.query.filter_by(department_id=json_data['department_id']).first()
            for key, value in json_data.items():
                setattr(status, key, value)
            db.session.commit()
            self.response.message = "department details updated successfully"
        except SQLAlchemyError as error:
            db.session.rollback()
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response.response_json()

    def delete(self, json_data):
        try:
            db.session.query(models.ClientDepartmentsDetailsRepo).filter_by(department_id=json_data['department_id']).delete()
            db.session.commit()
            self.response.message = "department details deleted successfully"
        except SQLAlchemyError as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        return self.response


class StoreFeedback:
    def __init__(self):
        self.response = Response()

    def create(self, json_data):
        try:
            feedback = models.FeedBackStatements(
                map_id=json_data.get('map_id', None),
                level_id=json_data.get('level_id', None),
                feedback_text=json_data.get('feedback_text', '')
            )
            db.session.add(feedback)
            db.session.commit()
            self.response.success = True
        except SQLAlchemyError as error:
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        except Exception as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response


class StoreAssessmentAnswers:
    def __init__(self):
        self.response = Response()

    def insert(self,json_data):
        try:
            new_ans = models.AssessmentTestAnswers(
                que_id=json_data.get('que_id',''),
                opt_id=json_data.get('opt_id',''),
                map_id=json_data.get('map_id',''),
                answer_score=json_data.get('answer_score','')
            )
            db.session.add(new_ans)
            db.session.commit()
            db.session.flush()
            self.response.message = 'Assessment Answer Stored Successfully..!!!'
        except SQLAlchemyError as error:
            logger.exception(error)
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)

        except Exception as error:
            self.response.status = 400
            self.response.success = False
            self.response.message = str(error)
        finally:
            db.session.close()
        return self.response


class BulkMailEmp:
    def __init__(self):
        self.response = Response()

    def send_mail_emp(self, json_data):
        try:
            emps = db.session.query(models.EmployeeDetailsRepo).filter(models.EmployeeDetailsRepo.emp_id.in_(json_data['emp_id'])).all()
            db.session.commit()
        except SQLAlchemyError as error:
            logger.exception(error)
            self.response.status = 400
            self.response.message = str(error)
        except Exception as error:
            print(error)
        finally:
            db.session.close()
        return self.response

    def send_alert_mail_emp(self, json_data):
        try:
            emps = db.session.query(models.EmployeeDetailsRepo).filter(models.EmployeeDetailsRepo.department_id.in_(json_data['dept_id'])).all()
            db.session.commit()
        except SQLAlchemyError as error:
            logger.exception(error)
            self.response.status = 400
            self.response.message = str(error)
        except Exception as error:
            print(error)
        finally:
            db.session.close()
        return self.response