from pathlib import Path
import pandas as pd
from datetime import datetime
import numpy as np
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import warnings
from app.utils.oracle_db import execute_query
warnings.filterwarnings('ignore')

def run_prescriptive(task):
    excel_path = "/Users/macbookpro/Documents/Projects/Pse/code/storage/prescriptive/FMEA.xlsx"
    threshold_file = "/Users/macbookpro/Documents/Projects/Pse/code/storage/prescriptive/THRESHOLD.xlsx"
    output_dir = "/Users/macbookpro/Documents/Projects/Pse/code/storage/prescriptive/"

    execute_prescriptive(excel_path, threshold_file, output_dir)

def execute_prescriptive(excel_path, threshold_file, output_dir):
    """
    Initialize Crisp Monitoring System
    
    Parameters:
    -----------
    excel_path : str
        Path to FMEA Excel file
    threshold_file : str
        Path to threshold Excel file
    output_dir : str
        Path untuk menyimpan output Excel (opsional)
    """
    # output_dir = Path(output_dir) if output_dir else Path.cwd()
    # output_dir.mkdir(parents=True, exist_ok=True)
    
    # Dictionary untuk menyimpan variabel dan parameternya
    components = {}
    
    variable_list = [
        "SKR1.LO GUIDE BRGOIL TEMP U1",
        "SKR1.METAL TEMP 1 U1",
        "SKR1.OIL TEMP. U1",
        "SKR1.UP GD&TH BRGOIL TEMP U1",
        "SKR1.THRUST BRG METAL 1 U1",
        "SKR1.THRUST BRG METAL 2 U1",
        "SKR1.THRUST BRG METAL 3 U1",
        "SKR1.STATOR CORE TEMP1 U1",
        "SKR1.STATOR CORE TEMP2 U1",
        "SKR1.STATOR WIND TEMP1 U1",
        "SKR1.STATOR WIND TEMP2 U1",
        "SKR1.STATOR WIND TEMP3 U1",
        "SKR1.STATOR WIND TEMP4 U1",
        "SKR1.STATOR WIND TEMP5 U1",
        "SKR1.STATOR WIND TEMP6 U1",
        "SKR1.UPPER VIBRASI HORIZONTAL",
        "SKR1.UPPER VIBRASI VERTIKAL",
        "SKR1.UPPER VIBRASI AXIAL",
        "SKR1.LOWER VIBRASI HORIZONTAL",
        "SKR1.LOWER VIBRASI VERTIKAL",
        "SKR1.LOWER VIBRASI AXIAL",
        "SKR1.TURBIN VIBRASI HORIZONTAL",
        "SKR1.TURBIN VIBRASI VERTIKAL",
        "SKR1.TURBIN VIBRASI AXIAL"
    ]
    
    # Load threshold and FMEA data
    load_threshold_data(threshold_file, components, variable_list)
    df_fmea = load_excel_data(excel_path)

    print("Data loaded and processed successfully.")

    dummy_input = {
        "SKR1.LO GUIDE BRGOIL TEMP U1": [45.2, 50.1, 48.3, 52.0],
        "SKR1.METAL TEMP 1 U1": [60.5, 62.3, 58.9, 61.2],
        "SKR1.OIL TEMP. U1": [70.0, 75.5, 72.3, 78.2],
        "SKR1.UP GD&TH BRGOIL TEMP U1": [55.0, 57.2, 54.8, 56.5],
        "SKR1.THRUST BRG METAL 1 U1": [68.5, 70.2, 69.8, 71.5],
        "SKR1.THRUST BRG METAL 2 U1": [65.2, 67.8, 66.5, 68.9],
        "SKR1.UPPER VIBRASI HORIZONTAL": [40.5, 42.3, 41.8, 43.2],
        "SKR1.UPPER VIBRASI VERTIKAL": [38.9, 40.1, 39.5, 41.0],
        "SKR1.LOWER VIBRASI HORIZONTAL": [85.0, 87.2, 86.5, 88.3],
    }
    
    result = process_input(dummy_input, components,df_fmea)

    print("Prediction completed successfully.")
    save_to_excel(result, output_dir)
    print("Result saved to Excel successfully.")
    
def load_threshold_data(threshold_file, components, variable_list):
    """Load dan proses data threshold dari file Excel"""
    try:
        # Baca file threshold
        df_threshold = pd.read_excel(threshold_file, header=4)
        
        # Default values untuk variabel yang tidak ada di threshold
        default_config = {
            "unit": "mm/s",
            "alarm": 65,
            "trip": 80
        }
        
        # Populate components dari variable_list
        for var_name in variable_list:
            # Cari variabel di threshold file
            threshold_row = df_threshold[df_threshold["TAG NAME"] == var_name]
            
            if len(threshold_row) > 0:
                # Variabel ada di threshold file
                row = threshold_row.iloc[0]
                alarm = float(row["ALARM"])
                trip = float(row["TRIP"])
                
                components[var_name] = {
                    "unit": row["SATUAN"] if pd.notna(row["SATUAN"]) else default_config["unit"],
                    "alarm": alarm,
                    "trip": trip
                }
            else:
                # Variabel tidak ada di threshold file, gunakan default
                print(f"Variabel '{var_name}' tidak ditemukan di file threshold. Menggunakan nilai default.")
                components[var_name] = default_config.copy()
                
    except Exception as e:
        print(f"Error loading threshold data: {str(e)}")
        # Set default values jika ada error
        for var_name in variable_list:
            components[var_name] = {
                "unit": "mm/s",
                "alarm": 65,
                "trip": 80
            }
    
def load_excel_data(excel_path):
    """Load data dari Excel FMEA"""
    try:
        # Baca file Excel dengan ketentuan: header di baris 8, skip baris 9, data mulai baris 10
        df = pd.read_excel(
            excel_path,
            header=7,  # 0-based index, jadi 7 untuk baris 8
            skiprows=[8]  # Skip baris 9 (0-based index 8)
        )
        df_fmea = df.ffill()  # Mengatasi sel NaN karena merged
        
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan: {excel_path}")
        df_fmea = None
    except Exception as e:
        print(f"Error membaca Excel: {str(e)}")
        df_fmea = None

    return df_fmea

def process_input(input_data, components, df_fmea):
        """
        Process input dataframe dan generate output
        
        Parameters:
        -----------
        input_data : dict
            Dictionary dengan format {"var_name": [list angka], ...}
        
        Returns:
        --------
        dict : Dictionary dengan hasil analisis
            {
                "status_variables": DataFrame,
                "triggered_fmea": DataFrame,
                "overall_status": str,
                "summary": dict
            }
        """
        # Validasi input
        if not isinstance(input_data, dict):
            raise ValueError("Input harus berupa dictionary")
        
        # Extract max values dari setiap variabel
        max_values = {}
        for var_name, values in input_data.items():
            if var_name in components:
                if isinstance(values, list) and len(values) > 0:
                    max_values[var_name] = max(values)
                else:
                    max_values[var_name] = values
        
        # Evaluasi status setiap variabel
        variable_status = []
        trip_vars = []
        alarm_vars = []
        
        for var_name, max_val in max_values.items():
            if var_name in components:
                params = components[var_name]
                status = evaluate_crisp(max_val, params)
                
                variable_status.append({
                    "Variable": var_name,
                    "Max_Value": max_val,
                    "Unit": params["unit"],
                    "Alarm_Threshold": params["alarm"],
                    "Trip_Threshold": params["trip"],
                    "Status": status
                })
                
                if status == "Trip":
                    trip_vars.append(var_name)
                elif status == "Alarm":
                    alarm_vars.append(var_name)
        
        df_status = pd.DataFrame(variable_status)
        
        # Evaluasi FMEA triggers dengan logika AND
        triggered_fmea = []
        
        if df_fmea is not None:
            for row_idx in range(9, 247):  # Baris 10-247 (index 9-246)
                if row_idx >= len(df_fmea):
                    break
                
                related_vars = df_fmea.iloc[row_idx]["Related Variable"]
                
                if pd.isna(related_vars):
                    continue
                
                # Parse variabel dari sel
                cell_str = str(related_vars)
                lines = [line.strip() for line in cell_str.split('\n') if line.strip()]
                
                if not lines:
                    continue
                
                # Cek apakah semua variabel ada di max_values
                all_vars_exist = all(var in max_values for var in lines)
                if not all_vars_exist:
                    continue
                
                # Logika AND: SEMUA variabel harus >= alarm untuk trigger
                all_alarm_or_trip = all(
                    is_alarm_or_trip(max_values[var], components[var]) 
                    for var in lines if var in components
                )
                
                if all_alarm_or_trip:
                    excel_row = row_idx + 10
                    display_row = excel_row + 9
                    
                    # Ambil RPN untuk sorting
                    rpn_val = None
                    if "RPN" in df_fmea.columns:
                        try:
                            rpn_val = df_fmea.iloc[row_idx]["RPN"]
                            rpn_num = float(rpn_val) if pd.notna(rpn_val) else float("-inf")
                        except:
                            rpn_num = float("-inf")
                    else:
                        rpn_num = float("-inf")
                    
                    # Kolom yang ingin ditampilkan
                    columns_to_extract = [
                        "LEVEL", "Item identification", "Failure mode",
                        "Related Variable", "RPN", "Recommended Action",
                        "CAUSE OF CATEGORY", "RECOMMENDATION", "PROCEDURE"
                    ]
                    
                    fmea_item = {
                        "Excel_Row": display_row,
                        "RPN": rpn_val if pd.notna(rpn_val) else "No RPN",
                        "RPN_Numeric": rpn_num
                    }
                    
                    for col in columns_to_extract:
                        if col in df_fmea.columns:
                            value = df_fmea.iloc[row_idx][col]
                            fmea_item[col] = value if pd.notna(value) else "No Information"
                        else:
                            fmea_item[col] = "No Information"
                    
                    triggered_fmea.append(fmea_item)
        
        # Sort triggered FMEA by RPN (descending)
        triggered_fmea.sort(key=lambda x: x["RPN_Numeric"], reverse=True)
        
        # Buat DataFrame untuk triggered FMEA
        df_triggered = pd.DataFrame(triggered_fmea)
        if not df_triggered.empty:
            # Remove RPN_Numeric column (hanya untuk sorting)
            df_triggered = df_triggered.drop(columns=["RPN_Numeric"])
        
        # Determine overall status
        if trip_vars:
            overall_status = "TRIP"
        elif alarm_vars:
            overall_status = "ALARM"
        else:
            overall_status = "NORMAL"
        
        # Summary
        summary = {
            "total_variables": len(max_values),
            "trip_count": len(trip_vars),
            "alarm_count": len(alarm_vars),
            "normal_count": len(max_values) - len(trip_vars) - len(alarm_vars),
            "triggered_fmea_count": len(triggered_fmea),
            "trip_variables": trip_vars,
            "alarm_variables": alarm_vars
        }
        
        return {
            "status_variables": df_status,
            "triggered_fmea": df_triggered,
            "overall_status": overall_status,
            "summary": summary
        }

def evaluate_crisp(value, params):
        """
        Evaluasi crisp logic: return status berdasarkan threshold
        
        Returns:
        --------
        str : "Normal", "Alarm", atau "Trip"
        """
        if value >= params["trip"]:
            return "Trip"
        elif value >= params["alarm"]:
            return "Alarm"
        else:
            return "Normal"
    
def is_alarm_or_trip(value, params):
    """
    Helper function untuk cek apakah nilai >= alarm threshold
    
    Returns:
    --------
    bool : True jika >= alarm, False jika normal
    """
    return value >= params["alarm"]

def save_to_excel(result, output_dir, filename=None):
        """
        Simpan hasil analisis ke file Excel dengan multiple sheets
        
        Parameters:
        -----------
        result : dict
            Output dari process_input()
        filename : str
            Nama file output (opsional, default: "monitoring_report_TIMESTAMP.xlsx")
        
        Returns:
        --------
        str : Path ke file yang disimpan
        """
        # Generate filename jika tidak diberikan
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_report_{timestamp}.xlsx"
        
        output_path = output_dir + "/" + filename
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # ===== SHEET 1: STATUS VARIABLES =====
            summary = result["summary"]
            df_status = result["status_variables"]
            
            # Buat summary section
            summary_data = {
                "Metric": [
                    "Overall Status",
                    "Total Variables",
                    "Trip Count",
                    "Alarm Count",
                    "Normal Count",
                    "Triggered FMEA Items"
                ],
                "Value": [
                    result["overall_status"],
                    summary["total_variables"],
                    summary["trip_count"],
                    summary["alarm_count"],
                    summary["normal_count"],
                    summary["triggered_fmea_count"]
                ]
            }
            df_summary_section = pd.DataFrame(summary_data)
            df_summary_section.to_excel(writer, sheet_name="Status Variables", index=False, startrow=0)
            
            # Tulis status variables table dibawahnya
            df_status.to_excel(writer, sheet_name="Status Variables", index=False, startrow=len(df_summary_section) + 2)
            
            # Format sheet Status Variables
            ws_status = writer.sheets["Status Variables"]
            ws_status.column_dimensions['A'].width = 35
            ws_status.column_dimensions['B'].width = 15
            ws_status.column_dimensions['C'].width = 12
            ws_status.column_dimensions['D'].width = 18
            ws_status.column_dimensions['E'].width = 15
            ws_status.column_dimensions['F'].width = 12
            
            # Add color formatting untuk status
            fill_trip = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            fill_alarm = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
            fill_normal = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
            font_white = Font(color="FFFFFF", bold=True)
            
            status_col = 6 + 1  # Column F (Status)
            for row in range(len(df_summary_section) + 3, len(df_summary_section) + 3 + len(df_status)):
                cell = ws_status.cell(row=row, column=status_col)
                if cell.value == "Trip":
                    cell.fill = fill_trip
                    cell.font = font_white
                elif cell.value == "Alarm":
                    cell.fill = fill_alarm
                    cell.font = font_white
                elif cell.value == "Normal":
                    cell.fill = fill_normal
                    cell.font = font_white
            
            # ===== SHEET 2: TRIGGERED FMEA =====
            df_triggered = result["triggered_fmea"]
            if not df_triggered.empty:
                save_to_prescriptions(df_triggered)
                df_triggered.to_excel(writer, sheet_name="Triggered FMEA", index=False)
                
                # Format sheet Triggered FMEA
                ws_fmea = writer.sheets["Triggered FMEA"]
                ws_fmea.column_dimensions['A'].width = 12
                ws_fmea.column_dimensions['B'].width = 8
                
                # Set column widths untuk semua kolom
                for col_idx, col_name in enumerate(df_triggered.columns, 1):
                    ws_fmea.column_dimensions[chr(64 + col_idx)].width = 20
                
                # Add header formatting
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in ws_fmea[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                # Buat sheet kosong dengan pesan
                df_no_trigger = pd.DataFrame({"Message": ["No triggered FMEA items"]})
                df_no_trigger.to_excel(writer, sheet_name="Triggered FMEA", index=False)
            
            # ===== SHEET 3: SUMMARY =====
            summary_data_detail = {
                "Overall Status": [result["overall_status"]],
                "Total Variables": [summary["total_variables"]],
                "Trip Count": [summary["trip_count"]],
                "Alarm Count": [summary["alarm_count"]],
                "Normal Count": [summary["normal_count"]],
                "Triggered FMEA Items": [summary["triggered_fmea_count"]]
            }
            
            # Trip variables list
            if summary["trip_variables"]:
                trip_vars_str = ", ".join(summary["trip_variables"])
            else:
                trip_vars_str = "None"
            
            # Alarm variables list
            if summary["alarm_variables"]:
                alarm_vars_str = ", ".join(summary["alarm_variables"])
            else:
                alarm_vars_str = "None"
            
            summary_data_detail["Trip Variables"] = [trip_vars_str]
            summary_data_detail["Alarm Variables"] = [alarm_vars_str]
            
            df_summary = pd.DataFrame(summary_data_detail)
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            
            # Format sheet Summary
            ws_summary = writer.sheets["Summary"]
            for col_idx in range(1, len(df_summary.columns) + 1):
                ws_summary.column_dimensions[chr(64 + col_idx)].width = 20
            
            # Add header formatting
            for cell in ws_summary[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        print(f"\n✅ Excel report saved: {output_path}")
        return str(output_path)

def save_to_prescriptions(df):
    records = df.to_dict(orient="records")
    version = datetime.now().strftime("%Y%m%d%H%M")
    version = "202511191313"

    for record in records:
        sql = """
            MERGE INTO ugm25_prescriptions t
            USING (
                SELECT :version AS version,
                    :excel_row AS excel_row,
                    :rpn AS rpn,
                    :data_level AS data_level,
                    :item_identification AS item_identification,
                    :failure_mode AS failure_mode,
                    :related_variable AS related_variable,
                    :recommended_action AS recommended_action,
                    :cause_category AS cause_category,
                    :recommendation AS recommendation,
                    :procedure AS procedure
                FROM dual
            ) s
            ON (t.version = s.version AND t.excel_row = s.excel_row)

            WHEN MATCHED THEN
                UPDATE SET
                    t.rpn = s.rpn,
                    t.data_level = s.data_level,
                    t.item_identification = s.item_identification,
                    t.failure_mode = s.failure_mode,
                    t.related_variable = s.related_variable,
                    t.recommended_action = s.recommended_action,
                    t.cause_category = s.cause_category,
                    t.recommendation = s.recommendation,
                    t.procedure = s.procedure,
                    t.updated_at = SYSDATE

            WHEN NOT MATCHED THEN
                INSERT (
                    version, excel_row, rpn, data_level, item_identification,
                    failure_mode, related_variable, recommended_action,
                    cause_category, recommendation, procedure
                )
                VALUES (
                    s.version, s.excel_row, s.rpn, s.data_level, s.item_identification,
                    s.failure_mode, s.related_variable, s.recommended_action,
                    s.cause_category, s.recommendation, s.procedure
                )
            """


        insert = {
            "version": version,
            "excel_row": record["Excel_Row"],
            "rpn": record["RPN"],
            "data_level": record["LEVEL"],
            "item_identification": record["Item identification"],
            "failure_mode": record["Failure mode"],
            "related_variable": record["Related Variable"],
            "recommended_action": record["Recommended Action"],
            "cause_category": record["CAUSE OF CATEGORY"],
            "recommendation": record["RECOMMENDATION"],
            "procedure": record["PROCEDURE"]
        }

        execute_query(sql, insert)