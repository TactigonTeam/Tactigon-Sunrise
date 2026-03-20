# 🌅 Tactigon Sunrise DB + grafana

* **TimescaleDB**: Database relazionale ottimizzato per serie storiche (Time-Series).
* **Grafana**: Piattaforma di visualizzazione dati real-time.
* **ROS 2**: Middleware per la comunicazione robotica.

## 🐳 1. Setup dell'Infrastruttura (Docker Compose)

Tutti i servizi necessari sono definiti nel file `docker-compose.yaml`.

### Avvio dei servizi
posizionarsi nella cartella `sunrise_fiware` ed eseguire:

docker compose up -d

(Per spegnere e rimuovere i container: docker compose down)
Container Attivi

    TimescaleDB (sunrise_timescaledb):

        Porta: 5432

        Database: sunrise_db

        User / Password: admin / admin

        Persistenza: I dati sono salvati nel volume locale timescale_data.

    Grafana (grafana):

        Interfaccia Web: http://localhost:3000

        User / Password default: admin / admin

    ROS 2 (sunrise_ros2):

        Container pronto per ospitare i nodi di comunicazione. Condivide la rete hostnet con il database e la dashboard.

## 2. Generazione e Acquisizione Dati (ROS 2 & Bridge)

L'architettura di comunicazione è modulare e basata sulle best practice di ROS 2: ogni singola metrica viaggia su un topic dedicato utilizzando messaggi di tipo std_msgs/Float64. Questo permette a qualsiasi nodo del sistema di iscriversi solo ai dati di cui ha effettivamente bisogno.

I topic disponibili sono:

    /sunrise/telemetry/setup_time

    /sunrise/telemetry/job_success_rate

    /sunrise/telemetry/retries

    /sunrise/telemetry/downtime

    /sunrise/telemetry/time_to_recall_db

    /sunrise/telemetry/ventilator_manufactured

    /sunrise/telemetry/defect_ventilator

    /sunrise/telemetry/job_recall_number

Per testare il flusso dati verso la Dashboard, utilizziamo due script Python paralleli: uno simula il robot che pubblica i dati, l'altro fa da "ponte" (Bridge) per salvarli nel database.
Programma 1: Il Generatore Mock (test_save_db_for_grafana.py)

Questo script simula la telemetria del robot. Modificando la variabile MODALITA all'interno del file, può funzionare in due modi:

    MODALITA = "DIRECT_DB": Scrive i dati finti direttamente in TimescaleDB (utile per test rapidi senza ROS).

    MODALITA = "ROS": (Raccomandata) Pubblica i dati in tempo reale sui singoli topic ROS 2 elencati sopra.

Programma 2: Il Bridge verso il DB (ros_to_db_bridge.py)

Questo è il nodo Subscriber vero e proprio. Rimane in ascolto su tutti i topic /sunrise/telemetry/*. Non appena intercetta un messaggio su un topic, ne estrae il valore e lo inserisce automaticamente nella tabella telemetria_robot di TimescaleDB.
(Nota: Quando il robot reale sarà pronto, basterà spegnere lo script Mock; questo Bridge continuerà a funzionare senza alcuna modifica ascoltando i dati veri).

### Come avviare la simulazione completa

Aprire due terminali separati sul PC Host (assicurandosi di aver fatto il source di ROS 2 e attivato l'ambiente virtuale se presente).

Terminale 1 (Avvio del Bridge):
Bash

python ros_to_db_bridge.py

(Il nodo rimarrà in attesa, indicando di essersi connesso al DB).

Terminale 2 (Avvio del Robot Mock):
Assicurarsi che MODALITA = "ROS" nello script, poi lanciare:
Bash

python mock_data.py

A questo punto, i dati inizieranno a fluire tramite ROS 2 fino al Database, pronti per essere letti da Grafana in tempo reale.

### Configurazione di Grafana e Query SQL

Una volta avviato lo stack, accedere a Grafana (http://localhost:3000) e configurare il database:

    Andare su Connections -> Data Sources -> Add data source -> PostgreSQL.

    Host: timescaledb:5432 (o 127.0.0.1:5432 se si è fuori da Docker)

    Database: sunrise_db

    User / Password: admin / admin

    TLS Mode: disable

    Abilitare l'interruttore TimescaleDB in basso e cliccare su Save & Test.

Creazione della Dashboard (Query di Riferimento)

Di seguito le query SQL esatte da incollare nei vari pannelli (Panels) della Dashboard per visualizzare i KPI richiesti:

## Pannello 1: Performance & Timing (Visualizzazione: Time series)

Monitoraggio dei tempi operativi e dei ritentativi del robot.
SQL

SELECT
  time AS "time",
  valore AS "Setup Time (s)"
FROM telemetria_robot
WHERE nome_metrica = 'setup_time' AND $__timeFilter(time)
ORDER BY time ASC

-----

SELECT
  time AS "time",
  valore AS "Downtime (s)"
FROM telemetria_robot
WHERE nome_metrica = 'downtime' AND $__timeFilter(time)
ORDER BY time ASC

------

SELECT
  time AS "time",
  valore AS "Time to recall DB (s)"
FROM telemetria_robot
WHERE nome_metrica = 'time_to_recall_db' AND $__timeFilter(time)
ORDER BY time ASC


## Pannello 2: Produzione e Difetti (Visualizzazione: Time series o Bar chart)

Visualizza la quantità assoluta di ventilatori prodotti e quanti di questi sono difettosi.
SQL

SELECT
  time AS "time",
  valore AS "Quantità danneggiata",
  nome_metrica AS metric
FROM telemetria_robot
WHERE
  nome_metrica IN ('defect_ventilator') AND
  $__timeFilter(time)
ORDER BY time ASC

-----

SELECT
  time AS "time",
  valore AS "Quantità totale",
  nome_metrica AS metric
FROM telemetria_robot
WHERE
  nome_metrica IN ('ventilator_manufactured') AND
  $__timeFilter(time)
ORDER BY time ASC

## Pannello 3: Percentuale Pezzi Sani (Visualizzazione: Gauge o Stat)

Calcola dinamicamente la percentuale di successo della produzione (100 - % difetti) allineando i dati al secondo esatto tramite time_bucket.
SQL

SELECT
  time_bucket('5s', time) AS "time",
  100 - ((MAX(valore) FILTER (WHERE nome_metrica = 'defect_ventilator') / 
   NULLIF(MAX(valore) FILTER (WHERE nome_metrica = 'ventilator_manufactured'), 0)) * 100) AS "Pezzi Sani (%)"
FROM telemetria_robot
WHERE
  nome_metrica IN ('defect_ventilator', 'ventilator_manufactured') AND
  $__timeFilter(time)
GROUP BY 1
ORDER BY 1 ASC

per il Gauge: Nelle opzioni di Grafana a destra, impostare Min: 0, Max: 100 e la Unit su Percent (0-100) per una visualizzazione corretta.
per i colori invece : Base = rosso, threshold 60 = giallo, threshold 90 = verde
Pannello 4: Job Success & Accuracy (Visualizzazione: Gauge)

Indicatori di precisione del lavoro del robot.
SQL

SELECT
  time AS "time",
  valore AS "Job Accuracy (%)"
FROM telemetria_robot
WHERE nome_metrica = 'job_accuracy' AND $__timeFilter(time)
ORDER BY time ASC