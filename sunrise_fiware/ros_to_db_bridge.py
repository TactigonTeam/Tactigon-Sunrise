#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from functools import partial
import sys

# Credenziali TimescaleDB
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "sunrise_db"
DB_USER = "admin"
DB_PASS = "admin"

# Lista delle metriche (i topic) da ascoltare
METRICHE = [
    "setup_time", "job_success_rate", "retries", "downtime",
    "time_to_recall_db", "ventilator_manufactured",
    "defect_ventilator", "job_recall_number"
]

class RosToDbBridge(Node):
    def __init__(self):
        super().__init__('sunrise_db_bridge')

        # 1. Connessione al Database
        try:
            self.conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.conn.cursor()
            self.get_logger().info("Connesso a TimescaleDB con successo.")
            
            # Creiamo la tabella se non esiste (sicurezza extra)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetria_robot (
                    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    nome_metrica TEXT NOT NULL,
                    valore FLOAT NOT NULL
                );
            """)
            try:
                self.cursor.execute("SELECT create_hypertable('telemetria_robot', 'time', if_not_exists => TRUE);")
            except:
                pass
                
        except Exception as e:
            self.get_logger().error(f"Errore connessione DB: {e}")
            sys.exit(1)

        # 2. Creazione dinamica dei Subscriber
        self.subs = []
        for metrica in METRICHE:
            topic_name = f'/sunrise/telemetry/{metrica}'
            
            # MAGIA PYTHON: Usiamo 'partial' per dire alla callback quale metrica ha scatenato l'evento
            sub = self.create_subscription(
                Float64,
                topic_name,
                partial(self.callback_salvataggio, nome_metrica=metrica),
                10
            )
            self.subs.append(sub)
            self.get_logger().info(f"In ascolto sul topic: {topic_name}")

    # 3. La Callback che fa l'inserimento
    def callback_salvataggio(self, msg, nome_metrica):
        try:
            self.cursor.execute(
                "INSERT INTO telemetria_robot (nome_metrica, valore) VALUES (%s, %s)",
                (nome_metrica, msg.data)
            )
            self.get_logger().info(f"Salvato a DB -> {nome_metrica}: {msg.data:.2f}")
        except Exception as e:
            self.get_logger().error(f"Errore salvataggio DB: {e}")


def main(args=None):
    rclpy.init(args=args)
    nodo = RosToDbBridge()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        nodo.get_logger().info("\nBridge interrotto dall'utente.")
    finally:
        if hasattr(nodo, 'conn') and nodo.conn:
            nodo.cursor.close()
            nodo.conn.close()
        nodo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()