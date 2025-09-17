from typing import List
from fastapi import APIRouter
from app.controllers.ip_api_controller import point_seach, point_interpolated

router = APIRouter()

router.add_api_route("/v1/record-sensors",point_seach,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolated",point_interpolated,response_model=dict,methods=["GET"])