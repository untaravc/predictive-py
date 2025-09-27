from typing import List
from fastapi import APIRouter
from app.controllers.ip_api_controller import point_seach, point_interpolated_sample, sensor_list, predictions, collect_interpolated, generate_value_record, set_normal_value, consume_unit3_lstm
from app.controllers.sample_controller import predict_earning, home
from app.controllers.task_controller import action_create_task, action_execute_record, action_execute_predict

router = APIRouter()

router.add_api_route("/",home,response_model=dict,methods=["GET"])
router.add_api_route("/v0/predict-earning",predict_earning,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-value-record",generate_value_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-normal-value",set_normal_value,response_model=dict,methods=["GET"])
router.add_api_route("/v0/consume-unit-3",consume_unit3_lstm,response_model=dict,methods=["GET"])
router.add_api_route("/v0/create-task",action_create_task,response_model=dict,methods=["GET"])
router.add_api_route("/v0/execute-record",action_execute_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/execute-predict",action_execute_predict,response_model=dict,methods=["GET"])

router.add_api_route("/v1/record-sensors",point_seach,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolated",point_interpolated_sample,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolateds",collect_interpolated,response_model=dict,methods=["GET"])
router.add_api_route("/v1/predict",predictions,response_model=dict,methods=["GET"])
router.add_api_route("/v1/sensors",sensor_list,response_model=dict,methods=["GET"])