# Pengaturan Aplikasi

# Nama prefix sensor aktif
SENSOR_NAME_QUERY = "SKR1%" 
PREDICT_UNIT = 1
SENSOR_NAME_QUERY_VIBRATION = "SKR1.Generator%"

# Flow
# 1. Create Task
# 1.a Membuat task untuk pemanggilan API Record tiap sensor

# Berapa periode pemanggilan api dilakukan (dalam menit). 
# Misalkan setiap 12 jam sekali maka dimasukan nilai 60 * 12. 
# Dilakukan tiap jam maka dimasukan nilai 60
RECORD_TIME_PERIOD = 720
PREDICT_TIME_PERIOD = 720
UPLOAD_TIME_PERIOD = 720

# 1.b Membuat task untuk menjalankan model predict
# 1.c Membuat task untuk menjalankan upload data prediksi ke PI Vision
# 2. Execute Task
# 2.a Memanggil API Record tiap sensor
# 2.b Menjalankan model predict
# 2.c Menjalankan upload data prediksi ke PI Vision