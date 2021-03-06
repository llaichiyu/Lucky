from flask import Blueprint
from flask_restful import Api

api_blue = Blueprint('api', __name__)
api = Api(api_blue)


def init_api(app):
    app.register_blueprint(blueprint=api_blue, url_prefix='/api/v1')


from .login import Login
from .product import ProductApi
from .project import ProjectApi
from .object import ObjectApi
from .user import UserApi
from .role import RoleApi
from .suite import SuiteApi
from .case import CaseApi
from .step import StepApi
from .user_keyword import UserKeywordSuiteApi, UserKeywordApi
from .keyword import KeywordApi
from .var import VarApi
from .help import HelpApi
from .task import TaskApi
from .trigger import TriggerApi
from .stats import StatsApi


api.add_resource(Login, '/login/')
api.add_resource(ProductApi, '/product/')
api.add_resource(ProjectApi, '/project/')
api.add_resource(ObjectApi, "/object/")
api.add_resource(UserApi, '/user/')
api.add_resource(RoleApi, '/role/')
api.add_resource(CaseApi, '/case/')
api.add_resource(StepApi, '/step/')
api.add_resource(SuiteApi, '/suite/')
api.add_resource(UserKeywordSuiteApi, '/user_keyword_suite/')
api.add_resource(UserKeywordApi, '/user_keyword/')
api.add_resource(KeywordApi, '/keyword/')
api.add_resource(VarApi, '/var/')
api.add_resource(HelpApi, '/help/')
api.add_resource(TaskApi, '/task/')
api.add_resource(TriggerApi, '/trigger/')
api.add_resource(StatsApi, '/stats/')
