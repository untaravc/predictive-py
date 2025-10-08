from fastapi import File, UploadFile
import pandas as pd
import io
from app.services.vibration_proccess_service import process_excel

async def upload_vibration_excel(file: UploadFile = File(...)):
    # Read file contents into memory
    contents = await file.read()

    # Convert bytes to a file-like object for pandas
    excel_data = io.BytesIO(contents)

    # Read Excel file into a pandas DataFrame
    df = pd.read_excel(excel_data)

    result = process_excel(df)

    return {
        "success": True,
        "result": result
    }