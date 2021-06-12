from ninja import NinjaAPI
from django_ninja_auth.api import router

api = NinjaAPI()

api.add_router('', router)