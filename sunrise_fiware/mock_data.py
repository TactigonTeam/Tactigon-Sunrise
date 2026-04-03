import time
import random
import json
import sys

# "DIRECT_DB" = Scrive i dati finti direttamente nel database Timescale
# "ROS"       = Pubblica i dati finti su singoli topic ROS 2

MODALITA = "DIRECT_DB"

DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "sunrise_db"
DB_USER = "admin"
DB_PASS = "admin"


def genera_dati_mock():
    """Genera un dizionario con i dati finti richiesti dalle specifiche"""
    return {
        "setup_time": random.uniform(5, 15),
        "job_success_rate": random.uniform(90, 100.0),
        "retries": random.randint(0, 3),
        "downtime": random.uniform(1.5, 6.0),
        "time_to_recall_db": random.uniform(15.0, 45.0),
        "ventilator_manufactured": random.randint(50, 100),
        "defect_ventilator": random.randint(1, 3),
        "job_recall_number": random.randint(1, 15),
    }


if MODALITA == "DIRECT_DB":
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print("Errore: Manca la libreria psycopg2. Esegui 'pip install psycopg2-binary'")
        sys.exit(1)

    print("Modalità: DIRECT_DB. Connessione a TimescaleDB...")
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetria_robot (
                time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                nome_metrica TEXT NOT NULL,
                valore FLOAT NOT NULL
            );
        """)
        try:
            cursor.execute("SELECT create_hypertable('telemetria_robot', 'time', if_not_exists => TRUE);")
        except:
            pass 

        print("Inizio salvataggio dati...\n")
        while True:
            dati = genera_dati_mock()
            for nome, valore in dati.items():
                cursor.execute(
                    "INSERT INTO telemetria_robot (nome_metrica, valore) VALUES (%s, %s)",
                    (nome, valore)
                )
            print(f"Salvati {len(dati)} valori finti nel DB.")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n Arrestato dall'utente.")
    except Exception as e:
        print(f"Errore DB: {e}")


elif MODALITA == "ROS":
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import Float64 
    except ImportError:
        print("Errore: Librerie ROS 2 non trovate. Hai fatto 'source /opt/ros/*/setup.bash'?")
        sys.exit(1)

    class MockRosPublisher(Node):
        def __init__(self):
            super().__init__('sunrise_mock_data_generator')
            self.publishers_dict = {}
            
            dati_esempio = genera_dati_mock()
            for chiave in dati_esempio.keys():
                nome_topic = f'/sunrise/telemetry/{chiave}'
                self.publishers_dict[chiave] = self.create_publisher(Float64, nome_topic, 10)
                self.get_logger().info(f"Creato publisher su: {nome_topic}")

            self.timer = self.create_timer(15.0, self.timer_callback)
            self.get_logger().info("Modalità: ROS. Inizio pubblicazione sui topic...")

        def timer_callback(self):
            dati = genera_dati_mock()

            for key, value in dati.items():
                msg = Float64()
                msg.data = float(value) 
                
                if key in self.publishers_dict:
                    self.publishers_dict[key].publish(msg)
            
            self.get_logger().info(f"Inviati {len(dati)} valori sui rispettivi topic ROS.")

    rclpy.init()
    nodo = MockRosPublisher()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        print("\nArrestato dall'utente.")
    finally:
        nodo.destroy_node()
        rclpy.shutdown()

else:
    print(f"Modalità '{MODALITA}' non riconosciuta. Usa 'DIRECT_DB' o 'ROS'.")