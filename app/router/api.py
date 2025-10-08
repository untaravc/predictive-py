from typing import List
from fastapi import APIRouter
from app.controllers.ip_api_controller import point_seach, point_interpolated_sample, sensor_list, predictions, collect_interpolated,access_interpolated_data_ip, generate_value_record, set_normal_value, post_interpolated_data_ip
from app.controllers.sample_controller import predict_earning, home
from app.controllers.task_controller import action_create_task, action_execute_record, action_execute_predict
from app.controllers.prediction_controller import consume_unit1_lstm

router = APIRouter()

router.add_api_route("/",home,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-value-record",generate_value_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/generate-normal-value",set_normal_value,response_model=dict,methods=["GET"])
router.add_api_route("/v0/create-task",action_create_task,response_model=dict,methods=["GET"])
router.add_api_route("/v0/execute-record",action_execute_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/execute-predict",action_execute_predict,response_model=dict,methods=["GET"])
router.add_api_route("/v0/access-interpolated-data-ip",access_interpolated_data_ip,response_model=dict,methods=["GET"])
router.add_api_route("/v0/post-interpolated-data-ip",post_interpolated_data_ip,response_model=dict,methods=["GET"])
router.add_api_route("/v0/prediction-unit-1",consume_unit1_lstm,response_model=dict,methods=["GET"])

router.add_api_route("/v1/record-sensors",point_seach,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolated",point_interpolated_sample,response_model=dict,methods=["GET"])
router.add_api_route("/v1/record-interpolateds",collect_interpolated,response_model=dict,methods=["GET"])
router.add_api_route("/v1/predict",predictions,response_model=dict,methods=["GET"])
router.add_api_route("/v1/sensors",sensor_list,response_model=dict,methods=["GET"])