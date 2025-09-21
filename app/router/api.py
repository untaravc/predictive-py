from typing import List
from fastapi import APIRouter
from app.controllers.ip_api_controller import point_seach, point_interpolated_sample, collect_interpolated, generate_value_record, set_normal_value
from app.controllers.sample_controller import predict_earning, home

router = APIRouter()

router.add_api_route("/",home,response_model=dict,methods=["GET"])
router.add_api_route("/v0/predict-earning",predict_earning,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-value-record",generate_value_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-normal-value",set_normal_value,response_model=dict,methods=["GET"])

router.add_api_route("/v1/record-sensors",point_seach,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolated",point_interpolated_sample,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolateds",collect_interpolated,response_model=dict,methods=["GET"])