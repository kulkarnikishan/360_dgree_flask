from sqlalchemy.orm import relationship
from sqlalchemy import exc as sqlexc
from sqlalchemy import desc
from app.__init__ import db, logger
import time

# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    #archived = db.Column(db.Boolean, default=False)

    @staticmethod
    def get_by_columns(obj, matches, archived=False, ignorearchived=False, filters={}):
        headers = {}
        got_error = False
        # try connection 3 times
        if not ignorearchived:
            ar = [x['col'] for x in matches]
            if 'archived' not in ar:
                matches.append({'col': 'archived', 'val': archived})
        session = db.session
        for i in range(3):
            try:
                qry = session.query(obj)
                for item in matches:
                    col = item['col']
                    val = item['val']
                    qry = qry.filter(getattr(obj, col) == val)

                try:
                    for f in filters.get('filter_by', []):
                        column = f['column']
                        operator = f['operator']
                        value = f['value']
                        if operator == 'eq':
                            qry = qry.filter(getattr(obj, column) == value)
                        elif operator == 'neq':
                            qry = qry.filter(getattr(obj, column) != value)
                        elif operator == 'like':
                            qry = qry.filter(getattr(obj, column).like('%{}%'.format(value)))
                        else:
                            raise ("Unsupported operator {}".format(operator))

                except Exception as ec:
                    logger.error("error processing filter_eq- {}".format(str(ec)))

                # Default is ascending
                asc = True
                order_str = filters.get('order')
                if order_str and order_str.lower() == 'desc':
                    asc = False

                # First sort fields
                if 'sort' in filters:
                    k = filters['sort']
                    if type(obj) == dict and hasattr(obj, k):
                        if asc:
                            qry = qry.order_by(getattr(obj, k))
                        else:
                            qry = qry.order_by(desc(getattr(obj, k)))

                # Next, check for pagination
                items = None
                page = filters.get('page')
                perPage = filters.get('perPage')
                if page and perPage:
                    qry = qry.paginate(page, perPage, False)
                    items = qry.items
                    headers['X-Total-Count'] = qry.total
                if not items:
                    items = qry.all()
                    headers['X-Total-Count'] = len(items)
                session.rollback()
                if not items:
                    logger.debug(
                        ": db get returned 0 items matching value {}".format(matches))
                    if got_error:
                        # we got an error in previous iteration.. print some debug info
                        print("Iteration {}: return empty result".format(i))
                    return None, headers
                else:
                    if got_error:
                        logger.debug("Iteration {}: return valid result".format(i))
                    return items, headers

            except sqlexc.DBAPIError as excp:
                if excp.connection_invalidated:
                    logger.error(
                        "Iteration {}: Connection to database was lost trying again".format(i))
                    time.sleep(0.5)
                    got_error = True
                    continue
            except (sqlexc.InvalidRequestError, sqlexc.SQLAlchemyError) as ec:
                session.rollback()
                time.sleep(0.2)
                logger.error(": Iteration {} : Performed rollback on getting exception {}".format(i, str(ec)))
                got_error = True
                continue
            except Exception as ec:
                session.rollback()
                logger.error(
                    "Iteration {}: Exception: db get return 0 items matching val {} - {}".format(i, matches, ec))
                return None, headers
        else:
            pass
        return None, headers


class ClientRepo(Base):
    __tablename__ = 'client_table_m'

    client_id = db.Column(db.String(64), primary_key=True)
    client_name = db.Column(db.String(64), nullable=False)
    client_email_id = db.Column(db.String(64), nullable=False, unique=True)
    client_uri = db.Column(db.String(64))

    cycle = relationship("ClientCycleRepo", backref='clientrepo',cascade="all,delete", lazy='dynamic')
    employee = relationship("EmployeeDetailsRepo", backref='clientrepo', cascade="all,delete", lazy='dynamic')
    ClientAdminRepo = relationship("ClientAdminRepo", backref='clientrepo', cascade="all,delete", lazy='dynamic')
    def __repr__(self):
        return "<Clients(client_id='{}',client_name='{}',client_email_id='{}',client_uri='{}')>".format(
            self.client_id, self.client_name, self.client_email_id, self.client_uri)

    def get_json(self):
        body = {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "client_email_id": self.client_email_id,
            "client_uri": self.client_uri
        }
        return body


class ClientCycleRepo(Base):
    __tablename__ = 'client_cycle_details_m'

    cycle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(64), db.ForeignKey(ClientRepo.client_id), nullable=False)
    cycle_name = db.Column(db.String(64), nullable=False)
    created_date = db.Column(db.Date, nullable=False)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    departments = relationship("ClientDepartmentsDetailsRepo", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    EmployeRelationMapping = relationship("EmployeRelationMapping", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    ParticipantsAssessmentStatus = relationship("ParticipantsAssessmentStatus", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    IndividualScores = relationship("IndividualScores", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    CompetancyScores = relationship("CompetancyScores", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    ClientAdminRepo = relationship("ClientAdminRepo", cascade="all,delete", backref="clientcyclerepo", lazy='dynamic')
    def __repr__(self):
        return "<ClientCycleRepo(cycle_id='{}',client_id='{}',cycle_name='{}',from_date='{}',to_date='{}'," \
               "is_active='{}')>".format(self.cycle_id, self.client_id, self.cycle_name, self.from_date, self.to_date,
                                         self.is_active)

    def get_json(self):
        body = {
            "cycle_id": self.cycle_id,
            "client_id": self.client_id,
            "cycle_name": self.cycle_name,
            "created_date": self.created_date,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "is_active": self.is_active,
        }
        return body


class ClientDepartmentsDetailsRepo(Base):
    __tablename__ = 'client_department_details_m'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.client_id))
    _function = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    band = db.Column(db.String(10), nullable=False)

    EmployeeDetailsRepo = relationship("EmployeeDetailsRepo", cascade="all,delete", backref="ClientDepartmentsDetailsRepo",
                                       lazy='joined')

    def __repr__(self):
        return "<ClientDepartmentsDetailsRepo(department_id='{}',cycle_id='{}',_function='{}',role='{}',location='{}'," \
               "band='{}')>".format(self.department_id, self.cycle_id, self._function, self.role, self.location,
                                    self.band)

    def get_json(self):
        body = {
            "department_id": self.department_id,
            "cycle_id": self.cycle_id,
            "function": self._function,
            "role": self.role,
            "location": self.location,
            "band": self.band
        }
        return body


class CompetencyTypeRepo(Base):
    __tablename__ = 'competency_type_m'

    competency_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competency_type = db.Column(db.String(64), nullable=False)

    AssessmentQuestionsRepo = relationship("AssessmentQuestionsRepo", cascade="all,delete", backref="CompetencyTypeRepo")
    CompetancyScores = relationship("CompetancyScores", cascade="all,delete", backref="CompetencyTypeRepo")

    def __repr__(self):
        return "<CompetencyTypeRepo(competency_id='{}',competency_type='{}')>".format(self.competency_id,
                                                                                      self.competency_type)

    def get_json(self):
        body = {
            "competency_id": self.competency_id,
            "competency_type": self.competency_type
        }
        return body


class UserRoleRepo(Base):
    __tablename__ = 'user_roles_m'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_type = db.Column(db.String(64), nullable=False)

    EmployeeDetailsRepo = relationship("EmployeeDetailsRepo", cascade="all,delete", backref="UserRoleRepo", lazy='joined')

    def __repr__(self):
        return "<UserRoleRepo(role_id='{}',role_type='{}')>".format(self.role_id, self.role_type)

    def get_json(self):
        body = {
            "role_id": self.role_id,
            "role_type": self.role_type
        }
        return body


class UserRelationRepo(Base):
    __tablename__ = 'user_relation_m'

    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    relation_type = db.Column(db.String(64), nullable=False)

    EmployeRelationMapping = relationship("EmployeRelationMapping", cascade="all,delete", backref="UserRelationRepo")

    def __repr__(self):
        return "<UserRelationRepo(relation_id='{}',relation_type='{}')>".format(self.relation_id, self.relation_type)

    def get_json(self):
        body = {
            "relation_id": self.relation_id,
            "relation_type": self.relation_type
        }
        return body


class AssessmentCompletionStatusRepo(Base):
    __tablename__ = 'assessment_completion_status_m'

    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_type = db.Column(db.String(20), nullable=False)

    ParticipantsAssessmentStatus = relationship("ParticipantsAssessmentStatus", cascade="all,delete", backref="AssessmentCompletionStatusRepo")

    def __repr__(self):
        return "<AssessmentCompletionStatusRepo(status_id='{}',status_type='{}')>".format(self.status_id,
                                                                                          self.status_type)

    def get_json(self):
        body = {
            "status_id": self.status_id,
            "status_type": self.status_type
        }
        return body


class EmployeeDetailsRepo(Base):
    __tablename__ = 'employee_details_m'

    emp_id = db.Column(db.String(20), primary_key=True)
    client_id = db.Column(db.String(64), db.ForeignKey(ClientRepo.client_id), nullable=False)
    emp_name = db.Column(db.String(64), nullable=False)
    emp_email = db.Column(db.String(64), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey(ClientDepartmentsDetailsRepo.department_id), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(UserRoleRepo.role_id), nullable=False)
    password = db.Column(db.Text, nullable=False)

    ParticipantsAssessmentStatus = relationship("ParticipantsAssessmentStatus", cascade="all,delete", backref="EmployeeDetailsRepo")
    IndividualScores = relationship("IndividualScores", cascade="all,delete", backref="EmployeeDetailsRepo")
    CompetancyScores = relationship("CompetancyScores", cascade="all,delete", backref="EmployeeDetailsRepo")
    ClientAdminRepo = relationship("ClientAdminRepo", cascade="all,delete", backref="EmployeeDetailsRepo")
    def __repr__(self):
        return "<EmployeeDetailsRepo(emp_id='{}',client_id='{}',emp_name='{}',emp_email='{}')>".format(self.emp_id,
                                                                       self.client_id, self.emp_name, self.emp_email)

    def get_json(self):
        body = {
            "emp_id": self.emp_id,
            "client_id": self.client_id,
            "emp_name": self.emp_name,
            "emp_email": self.emp_email,
            "department_id": self.department_id,
            "role_id": self.role_id
        }
        return body


class ClientAdminRepo(Base):
    __tablename__ = 'client_admin_details_m'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientRepo.client_id))
    client_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.client_id), nullable=False)
    emp_id = db.Column(db.String(64), db.ForeignKey(EmployeeDetailsRepo.emp_id), nullable=False)
    password_ = db.Column(db.Text)
    is_super_admin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<ClientAdminRepo(cycle_id='{}',client_id='{}',emp_id='{}',password_='{}'," \
               "is_super_admin='{}')>".format(self.cycle_id, self.client_id, self.emp_id, self.password_,
                                         self.is_super_admin)

    def get_json(self):
        body = {
            "cycle_id": self.cycle_id,
            "client_id": self.client_id,
            "emp_id": self.emp_id,
            "password": self.password_,
            "is_super_admin": self.is_super_admin
        }
        return body


class AssessmentQuestionsRepo(Base):
    __tablename__ = 'assessment_questions_m'

    que_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    que_statement = db.Column(db.Text, nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey(CompetencyTypeRepo.competency_id))

    AssessmentTestAnswers = relationship("AssessmentTestAnswers", cascade="all,delete", backref="AssessmentQuestionsRepo")
    IndividualScores = relationship("IndividualScores", cascade="all,delete", backref="AssessmentQuestionsRepo")
    QuestionOptionsMapping = relationship("QuestionOptionsMapping", cascade="all,delete", backref="AssessmentQuestionsRepo")

    def __repr__(self):
        return "<AssessmentQuestionsRepo(que_id='{}',que_statement='{}',competency_id='{}')>".format(self.que_id,
                                                                                                     self.que_statement,
                                                                                                     self.competency_id)

    def get_json(self):
        body = {
            "que_id": self.que_id,
            "que_statement": self.que_statement,
            "competency_id": self.competency_id
        }
        return body


class FeedBackLevelRepo(Base):
    __tablename__ = 'feedback_level_m'

    level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_type = db.Column(db.String(20), nullable=False)

    FeedBackStatements = relationship("FeedBackStatements", cascade="all,delete",
                                         backref="FeedBackLevelRepo", lazy='joined')

    def __repr__(self):
        return "<FeedBackLevelRepo(level_id='{}',level_type='{}')>".format(self.level_id, self.level_type)

    def get_json(self):
        body = {
            "level_id": self.level_id,
            "level_type": self.level_type
        }
        return body


class AssessmentOptionsRepo(Base):
    __tablename__ = 'assessment_options_m'

    opt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opt_statement = db.Column(db.Text, nullable=False)
    opt_score = db.Column(db.Integer, nullable=False)
    AssessmentTestAnswers = relationship("AssessmentTestAnswers", cascade="all,delete",
                                      backref="AssessmentOptionsRepo", lazy='joined')
    QuestionOptionsMapping = relationship("QuestionOptionsMapping", cascade="all,delete",
                                      backref="AssessmentOptionsRepo", lazy='joined')
    def __repr__(self):
        return "<AssessmentOptionsRepo(opt_id='{}',opt_statement='{}',opt_score='{}')>".format(self.opt_id,
                                                                                self.opt_statement,self.opt_score)

    def get_json(self):
        body = {
            "opt_id": self.opt_id,
            "opt_statement": self.opt_statement,
            "opt_score": self.opt_score
        }
        return body


class EmployeRelationMapping(Base):
    __tablename__ = 'employee_relation_mapping_t'

    map_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.cycle_id), nullable=False)
    pat_emp_id = db.Column(db.String(20), nullable=False)
    relation_id = db.Column(db.Integer, db.ForeignKey(UserRelationRepo.relation_id), nullable=False)
    target_emp_id = db.Column(db.String(20), nullable=False)

    AssessmentTestAnswers = relationship("AssessmentTestAnswers", cascade="all,delete",
                                         backref="EmployeRelationMapping", lazy='joined')
    FeedBackStatements = relationship("FeedBackStatements", cascade="all,delete",
                                         backref="EmployeRelationMapping", lazy='joined')
    def __repr__(self):
        return "<EmployeRelationMapping(map_id='{}',cycle_id='{}',pat_emp_id='{}',relation_id='{}'," \
               "target_emp_id='{}')>".format(self.map_id, self.cycle_id, self.pat_emp_id, self.relation_id, self.target_emp_id)

    def get_json(self):
        body = {
            "map_id": self.map_id,
            "cycle_id": self.cycle_id,
            "pat_emp_id": self.pat_emp_id,
            "relation_id": self.relation_id,
            "target_emp_id": self.target_emp_id
        }
        return body


class ParticipantsAssessmentStatus(Base):
    __tablename__ = 'participant_ass_status_t'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_id = db.Column(db.String(20), db.ForeignKey(EmployeeDetailsRepo.emp_id))
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.cycle_id))
    is_respondant_selective = db.Column(db.Boolean, default=False)
    is_block_report = db.Column(db.Boolean, default=False)
    total_respondant_count = db.Column(db.Integer)
    seniors_count = db.Column(db.Integer)
    subordinates_count = db.Column(db.Integer)
    peer_count = db.Column(db.Integer)
    others_count = db.Column(db.Integer)
    ass_com_seniors_count = db.Column(db.Integer, default=0)
    ass_com_subordinates_count = db.Column(db.Integer, default=0)
    ass_com_peer_count = db.Column(db.Integer, default=0)
    ass_com_others_count = db.Column(db.Integer, default=0)
    ass_com_respondant_count = db.Column(db.Integer, default=0)
    completion_status_id = db.Column(db.Integer, db.ForeignKey(AssessmentCompletionStatusRepo.status_id), default=1)
    is_generate_report = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<ParticipantsAssessmentStatus(id='{}')>".format(self.id)


class AssessmentTestAnswers(Base):
    __tablename__ = 'assessment_question_answered_t'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    que_id = db.Column(db.Integer, db.ForeignKey(AssessmentQuestionsRepo.que_id))
    opt_id = db.Column(db.Integer, db.ForeignKey(AssessmentOptionsRepo.opt_id))
    map_id = db.Column(db.Integer, db.ForeignKey(EmployeRelationMapping.map_id))
    answer_score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<AssessmentTestAnswers(id='{}')>".format(self.id)

    def get_json(self):
        body = {
            "id": self.id,
            "que_id": self.que_id,
            "opt_id": self.opt_id,
            "map_id": self.map_id,
            "answer_score": self.answer_score
        }
        return body


class IndividualScores(Base):
    __tablename__ = 'individual_question_answer_score_t'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.cycle_id))
    emp_id = db.Column(db.String(20), db.ForeignKey(EmployeeDetailsRepo.emp_id))
    que_id = db.Column(db.Integer, db.ForeignKey(AssessmentQuestionsRepo.que_id))
    self_score = db.Column(db.Integer)
    avg_senior_score = db.Column(db.DECIMAL(4, 2))
    avg_peer_score = db.Column(db.DECIMAL(4, 2))
    avg_subordinates_score = db.Column(db.DECIMAL(4, 2))
    avg_respondants_score = db.Column(db.DECIMAL(4, 2))

    def __repr__(self):
        return "<IndividualScores(id='{}')>".format(self.id)

    def get_json(self):
        body = {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "emp_id": self.emp_id,
            "que_id": self.que_id,
            "self_score": self.self_score,
            "avg_senior_score": self.avg_senior_score,
            "avg_peer_score": self.avg_peer_score,
            "avg_subordinates_score": self.avg_subordinates_score,
            "avg_others_score": self.avg_others_score,
            "avg_respondants_score": self.avg_respondants_score
        }
        return body


class FeedBackStatements(Base):
    __tablename__ = 'store_feedback_statements_t'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    map_id = db.Column(db.Integer, db.ForeignKey(EmployeRelationMapping.map_id))
    level_id = db.Column(db.Integer, db.ForeignKey(FeedBackLevelRepo.level_id))
    feedback_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<FeedBackStatements(id='{}')>".format(self.id)

    def get_json(self):
        body = {
            "id": self.id,
            "level_id": self.level_id,
            "feedback_text": self.feedback_text,
            "map_id": self.map_id
        }
        return body


class CompetancyScores(Base):
    __tablename__ = 'competancy_question_answer_score_t'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey(ClientCycleRepo.cycle_id))
    emp_id = db.Column(db.String(20), db.ForeignKey(EmployeeDetailsRepo.emp_id))
    competency_id = db.Column(db.Integer, db.ForeignKey(CompetencyTypeRepo.competency_id))
    avg_self_score = db.Column(db.DECIMAL(4, 2))
    avg_senior_score = db.Column(db.DECIMAL(4, 2))
    avg_peer_score = db.Column(db.DECIMAL(4, 2))
    avg_subordinates_score = db.Column(db.DECIMAL(4, 2))
    avg_others_score = db.Column(db.DECIMAL(4, 2))
    avg_respondants_score = db.Column(db.DECIMAL(4, 2))
    gap_analysis_score = db.Column(db.DECIMAL(6, 2))

    def __repr__(self):
        return "<CompetancyScores(id='{}')>".format(self.id)

    def get_json(self):
        body = {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "emp_id": self.emp_id,
            "competency_id": self.competency_id,
            "avg_self_score": self.avg_self_score,
            "avg_senior_score": self.avg_senior_score,
            "avg_peer_score": self.avg_peer_score,
            "avg_subordinates_score": self.avg_subordinates_score,
            "avg_others_score": self.avg_others_score,
            "avg_respondants_score": self.avg_respondants_score,
            "gap_analysis_score": self.gap_analysis_score
        }
        return body


class QuestionOptionsMapping(db.Model):
    __tablename__ = 'assessment_question_options_t'

    id = db.Column(db.Integer, primary_key=True)
    que_id = db.Column(db.Integer, db.ForeignKey(AssessmentQuestionsRepo.que_id), nullable=False)
    opt_id = db.Column(db.Integer, db.ForeignKey(AssessmentOptionsRepo.opt_id), nullable=False)

    def __repr__(self):
        return "<QuestionOptionsMapping(id='{}',que_id='{}',opt_id='{}')>".format(self.id,self.que_id,self.opt_id)