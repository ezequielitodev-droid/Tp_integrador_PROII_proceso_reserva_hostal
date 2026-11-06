import os
import time

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

t = time.perf_counter()
cnx = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
    ssl_ca="certs/ca.pem",
)
print(f"Abrir conexión: {time.perf_counter() - t:.2f}s")

cur = cnx.cursor()
for _ in range(3):
    t = time.perf_counter()
    cur.execute("SELECT 1")
    cur.fetchall()
    print(f"Una consulta: {time.perf_counter() - t:.2f}s")

cur.close()
cnx.close()