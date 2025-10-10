from fastapi import APIRouter
from app.controllers.ip_api_controller import sensor_list
from app.controllers.home_controller import home
from app.controllers.task_controller import action_create_task_record, action_create_task_predict, action_create_task_upload, action_task_delete, action_execute_record_sample, action_execute_predict, action_execute_record_api, action_execute_upload
from app.controllers.vibration_controller import upload_vibration_excel

router = APIRouter()

router.add_api_route("/",home,response_model=dict,methods=["GET"])

# 0. List sensor
router.add_api_route("/v0/sensors",sensor_list,response_model=dict,methods=["GET"])

# 1. create task
router.add_api_route("/v0/create-task-record",action_create_task_record,response_model=dict,methods=["GET"])
router.add_api_route("/v0/create-task-predict",action_create_task_predict,response_model=dict,methods=["GET"])
router.add_api_route("/v0/create-task-upload",action_create_task_upload,response_model=dict,methods=["GET"])
router.add_api_route("/v0/task-delete",action_task_delete,response_model=dict,methods=["GET"])

# 2. execute task record
router.add_api_route("/v0/execute-record-sample",action_execute_record_sample,response_model=dict,methods=["GET"])
router.add_api_route("/v0/execute-record-api",action_execute_record_api,response_model=dict,methods=["GET"])

# 3. upload vibration
router.add_api_route("/v0/upload-vibration-excel",upload_vibration_excel,response_model=dict,methods=["POST"])

# 4. execute task predict
router.add_api_route("/v0/execute-predict",action_execute_predict,response_model=dict,methods=["GET"])

# 5. execute task upload
router.add_api_route("/v0/execute-upload",action_execute_upload,response_model=dict,methods=["GET"])