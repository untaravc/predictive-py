from typing import List
from fastapi import APIRouter
from app.models.user import User
from app.controllers.user_controller import read_users, create_user

router = APIRouter()

router.add_api_route("/users",read_users,response_model=List[dict],methods=["GET"])
# router.add_api_route("/users/{user_id}",read_user,response_model=dict,methods=["GET"])
router.add_api_route("/users",create_user,response_model=dict,methods=["POST"])
# router.add_api_route("/users/{user_id}",update_user,response_model=dict,methods=["PUT"])
# router.add_api_route("/users/{user_id}",delete_user,response_model=dict,methods=["DELETE"])