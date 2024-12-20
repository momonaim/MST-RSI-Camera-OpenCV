from flask import Flask, jsonify, render_template_string
import psutil
import time

app = Flask(__name__)


@app.route('/metrics', methods=['GET'])
def get_metrics():
    # Collecter les données de performances
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    net_io = psutil.net_io_counters()

    # Conversion des bytes en kilooctets (Ko)
    bytes_sent_kb = net_io.bytes_sent / 1024
    bytes_received_kb = net_io.bytes_recv / 1024

    data = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory,
        'bytes_sent_kb': bytes_sent_kb,
        'bytes_received_kb': bytes_received_kb,
        'timestamp': time.time()
    }
    return jsonify(data)


@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Moniteur de Performances</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f4f6f9;
                color: #333;
                margin: 0;
                padding: 0;
            }
            h1 {
                text-align: center;
                color: #4CAF50;
                margin-top: 50px;
            }
            .container {
                width: 80%;
                margin: 50px auto;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                padding: 30px;
            }
            .metric {
                font-size: 18px;
                color: #555;
                margin-bottom: 20px;
            }
            .metric span {
                font-weight: bold;
                font-size: 20px;
                color: #333;
            }
            .metric.cpu {
                color: #f44336;
            }
            .metric.memory {
                color: #3f51b5;
            }
            .metric.bytes {
                color: #009688;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                color: #777;
            }
            .refresh {
                display: block;
                text-align: center;
                margin-top: 30px;
                font-size: 16px;
                color: #2196F3;
                cursor: pointer;
            }

            /* Classes pour les couleurs de performance */
            span.good { color: #4CAF50; }  
            span.bad { color: #F44336; }   
        </style>
        <script>
            function fetchMetrics() {
                fetch('/metrics')
                    .then(response => response.json())
                    .then(data => {
                        // CPU
                        const cpuElement = document.getElementById('cpu');
                        cpuElement.innerText = data.cpu_usage + '%';
                        // Si l'utilisation CPU est inférieure à 50, on la met en vert, sinon en rouge
                        if (data.cpu_usage < 50) {
                            cpuElement.classList.add('good');
                            cpuElement.classList.remove('bad');
                        } else {
                            cpuElement.classList.add('bad');
                            cpuElement.classList.remove('good');
                        }

                        // Mémoire
                        const memoryElement = document.getElementById('memory');
                        memoryElement.innerText = data.memory_usage + '%';
                        // Si l'utilisation mémoire est inférieure à 50, on la met en vert, sinon en rouge
                        if (data.memory_usage < 50) {
                            memoryElement.classList.add('good');
                            memoryElement.classList.remove('bad');
                        } else {
                            memoryElement.classList.add('bad');
                            memoryElement.classList.remove('good');
                        }

                        // Bytes envoyés et reçus
                        document.getElementById('bytes_sent').innerText = 'Bytes envoyés : ' + data.bytes_sent_kb.toFixed(2) + ' Ko';
                        document.getElementById('bytes_received').innerText = 'Bytes reçus : ' + data.bytes_received_kb.toFixed(2) + ' Ko';
                    })
                    .catch(error => console.error('Erreur lors de la récupération des métriques:', error));
            }

            setInterval(fetchMetrics, 1000); // Actualisation toutes les secondes
        </script>
    </head>
    <body onload="fetchMetrics()">
        <h1>Moniteur de Performances</h1>
        <div class="container">
            <div class="metric cpu">
                <span>Utilisation CPU : </span>
                <span id="cpu"></span>
            </div>
            <div class="metric memory">
                <span>Utilisation mémoire : </span>
                <span id="memory"></span>
            </div>
            <div class="metric bytes">
                <span id="bytes_sent">Bytes envoyés : </span>
            </div>
            <div class="metric bytes">
                <span id="bytes_received">Bytes reçus : </span>
            </div>
        </div>
        <div class="footer">
            <span>Mis à jour toutes les secondes</span>
        </div>
    </body>
    </html>
    ''')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
