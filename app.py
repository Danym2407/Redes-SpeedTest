from flask import Flask, render_template, request, jsonify
import openai
import time
import speedtest
import subprocess
import re
import requests
import psutil  # Importar psutil para monitorear el uso del ancho de banda
import plotly.express as px
import plotly.io as pio
import nmap  # Biblioteca para interactuar con nmap
from scapy.all import ARP, Ether, srp, IP, TCP, sr1
from geopy.geocoders import Nominatim # type: ignore
import requests
import time
import subprocess
import re
import speedtest
import subprocess
import re
import time
import speedtest
import requests



app = Flask(__name__)

# Configura tu clave API de OpenAI
openai.api_key = "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"

# Función para clasificar métricas
def categorize_metric(value, thresholds, categories):
    """Clasifica un valor según los umbrales y categorías proporcionados."""
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return categories[i]
    return categories[-1]
# Función para realizar el análisis de red

# Función para categorizar métricas
def categorize_metric(value, thresholds, descriptions):
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return descriptions[i]
    return descriptions[-1]

# Función para realizar el análisis de red
# Función para analizar la red
def analyze_network():
    """Analiza la red localmente, obteniendo datos de IP, ISP y conexión activa."""
    try:
        # Obtener IP pública
        try:
            ip_response = requests.get("https://api.ipify.org?format=json")
            ip_response.raise_for_status()
            ip_address = ip_response.json().get("ip", "Desconocida")
        except Exception as e:
            ip_address = f"Error al obtener IP: {e}"

        # Obtener información de IP y proveedor de internet
        try:
            location_data = requests.get(f"https://ipapi.co/{ip_address}/json/")
            location_data.raise_for_status()
            location_info = location_data.json()

            isp = location_info.get("org", "Proveedor desconocido")
            city = location_info.get("city", "Ciudad desconocida")
            region = location_info.get("region", "Región desconocida")
            coordinates = f"{location_info.get('latitude', 'N/A')}, {location_info.get('longitude', 'N/A')}"

            # Geolocalización precisa usando Geopy
            geolocator = Nominatim(user_agent="network_analysis")
            detailed_location = geolocator.reverse(coordinates, exactly_one=True).address if "N/A" not in coordinates else None

            location = detailed_location if detailed_location else f"{city}, {region}"
        except Exception as e:
            isp, location = f"Error al obtener ISP: {e}", f"Error al obtener ubicación: {e}"

        # Medir velocidad y latencia con Speedtest
        try:
            test = speedtest.Speedtest()
            test.get_best_server()

            # Mide el tiempo de descarga
            start_download = time.time()
            download_speed = test.download() / 1_000_000  # Mbps
            download_latency = round((time.time() - start_download) * 1000, 2)  # ms

            # Mide el tiempo de subida
            start_upload = time.time()
            upload_speed = test.upload() / 1_000_000  # Mbps
            upload_latency = round((time.time() - start_upload) * 1000, 2)  # ms

            # Latencia en reposo
            latency_idle = test.results.ping  # ms
        except Exception as e:
            download_speed = upload_speed = latency_idle = download_latency = upload_latency = f"Error en Speedtest: {e}"

        # Obtener conexiones activas (local)
        try:
            result = subprocess.run(['ss', '-an'], capture_output=True, text=True)
            active_connections = {
                'established_count': len(re.findall(r'ESTAB', result.stdout)),
                'listen_count': len(re.findall(r'LISTEN', result.stdout)),
                'time_wait_count': len(re.findall(r'TIME-WAIT', result.stdout)),
                'total': len(re.findall(r'ESTAB|LISTEN|TIME-WAIT', result.stdout))
            }
            active_connections_total = active_connections['total']
        except Exception as e:
            active_connections = {"error": str(e)}
            active_connections_total = "No disponible"

        # Clasificaciones
        download_description = categorize_metric(
            download_speed, [2, 10, 25],
            ["Muy Mala", "Deficiente", "Aceptable", "Buena"]
        )
        upload_description = categorize_metric(
            upload_speed, [1, 3, 10],
            ["Muy Mala", "Deficiente", "Aceptable", "Buena"]
        )
        latency_description = categorize_metric(
            latency_idle, [20, 50, 100],
            ["Buena", "Aceptable", "Deficiente", "Muy Mala"]
        )

        # Timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        return {
            "ip_address": ip_address,
            "location": location,
            "isp": isp,
            "download_speed": round(download_speed, 2) if isinstance(download_speed, (float, int)) else download_speed,
            "download_latency": download_latency,
            "download_description": download_description,
            "upload_speed": round(upload_speed, 2) if isinstance(upload_speed, (float, int)) else upload_speed,
            "upload_latency": upload_latency,
            "upload_description": upload_description,
            "idle_latency": round(latency_idle, 2) if isinstance(latency_idle, (float, int)) else latency_idle,
            "latency_description": latency_description,
            "active_connections": active_connections,
            "timestamp": timestamp,
            "status": "Estable" if isinstance(download_speed, (float, int)) and download_speed > 10 else "Inestable"
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "Disconnected",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

           
# Función para simular errores en la red
def simulate_network_errors(error_type):
    """Simula errores de red según el tipo seleccionado."""
    simulation_result = analyze_network()  # Usa la función existente como base
    if "error" in simulation_result:
        return simulation_result  # Retorna error si el análisis básico falla

    # Simulaciones según el tipo de error
    if error_type == "high_latency":
        simulation_result["idle_latency"] += 500  # Aumenta la latencia en ms
        simulation_result["latency_description"] = "Muy Alta (Simulada)"
    elif error_type == "low_speed":
        simulation_result["download_speed"] = max(0.5, simulation_result["download_speed"] * 0.1)
        simulation_result["upload_speed"] = max(0.2, simulation_result["upload_speed"] * 0.1)
        simulation_result["download_description"] = "Muy Baja (Simulada)"
        simulation_result["upload_description"] = "Muy Baja (Simulada)"
    elif error_type == "packet_loss":
        simulation_result["active_connections"] = "No disponible (Pérdida de paquetes simulada)"
        simulation_result["connections_description"] = "Problema de conectividad (Simulado)"
    else:
        return {"error": "Tipo de error no soportado"}

    simulation_result["status"] = "Simulación de Error"
    return simulation_result

# Función para obtener el consumo de ancho de banda por dispositivo
def analyze_bandwidth():
    """Obtiene el consumo de ancho de banda por dispositivo en la red."""
    network_info = psutil.net_io_counters(pernic=True)  # Obtiene información de red por interfaz de red
    bandwidth_usage = {}

    for interface, stats in network_info.items():
        # El campo stats.bytes_sent y stats.bytes_recv nos dan el consumo en bytes enviados y recibidos
        bandwidth_usage[interface] = {
            'bytes_sent': stats.bytes_sent / 1_000_000,  # Convertimos a MB
            'bytes_recv': stats.bytes_recv / 1_000_000,  # Convertimos a MB
        }
    
    # Ordenar las interfaces de mayor a menor consumo de ancho de banda recibido (bytes_recv)
    sorted_bandwidth_usage = sorted(bandwidth_usage.items(), key=lambda x: x[1]['bytes_recv'], reverse=True)

    return sorted_bandwidth_usage

# Rutas existentes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Ruta para el análisis
@app.route('/analisis')
def analisis():
    # Llamar a la función de análisis de red
    network_data = analyze_network()

    # Si el análisis tiene un error, se retorna el mensaje de error
    if "error" in network_data:
        return render_template('analisis.html', error=network_data["error"])

    # Datos para las gráficas (puedes reemplazar con los datos reales)
    download_speed = [network_data['download_speed'], 20, 15, 30, 10]  # Velocidad de descarga en Mbps
    latency = [network_data['idle_latency'], 60, 50, 45, 55]  # Latencia en ms
    time = ['1', '2', '3', '4', '5']  # Tiempo (puede ser horas, días, etc.)

    # Crear un gráfico para la velocidad de descarga
    download_speed_fig = px.line(x=time, y=download_speed, labels={'x': 'Tiempo', 'y': 'Velocidad de Descarga (Mbps)'}, title='Historial de Velocidad de Descarga')

    # Crear un gráfico para la latencia
    latency_fig = px.line(x=time, y=latency, labels={'x': 'Tiempo', 'y': 'Latencia (ms)'}, title='Historial de Latencia')

    # Convertir las gráficas a HTML para incluirlas en el template
    download_speed_graph = pio.to_html(download_speed_fig, full_html=False)
    latency_graph = pio.to_html(latency_fig, full_html=False)

    return render_template('analisis.html', 
                           download_speed_graph=download_speed_graph, 
                           latency_graph=latency_graph, 
                           network_data=network_data)
    

def scan_local_network(network="192.168.1.0/24"):
    """Escanea dispositivos y servicios activos en la red local utilizando scapy."""
    try:
        # Escaneo ARP para detectar dispositivos activos
        arp_request = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp_request
        answered_list = srp(packet, timeout=2, verbose=0)[0]

        devices = []
        for sent, received in answered_list:
            device_info = {
                "ip": received.psrc,
                "mac": received.hwsrc,
                "services": []  # Servicios serán detectados en un paso posterior
            }

            # Escaneo de servicios (puertos comunes)
            common_ports = [21, 22, 80, 443]
            for port in common_ports:
                tcp_packet = IP(dst=received.psrc) / TCP(dport=port, flags="S")
                response = sr1(tcp_packet, timeout=1, verbose=0)
                if response and response.haslayer(TCP) and response[TCP].flags == "SA":
                    device_info["services"].append({
                        "port": port,
                        "state": "open",
                        "service": "Desconocido"  # Puedes usar una lista para mapear nombres de servicios
                    })
            devices.append(device_info)

        return devices
    except Exception as e:
        return {"error": str(e)}

@app.route('/servicios/wifi_analyzer')
def wifi_analyzer():
    return render_template('wifi_analyzer.html')

@app.route('/servicios/network_simulator')
def network_simulator():
    return render_template('network_simulator.html')

@app.route('/servicios/analyze_bandwidth')
def analyze_bandwidth_route():
    bandwidth_data = analyze_bandwidth()  # Llamada a la función de análisis
    return render_template('analyze_bandwidth.html', bandwidth_data=bandwidth_data)

@app.route('/servicios/network_services')
def network_services():
    network = request.args.get('network', '192.168.1.0/24')  # Red por defecto
    services = scan_local_network(network)
    if "error" in services:
        return render_template('network_services.html', error=services["error"])
    return render_template('network_services.html', devices=services)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

# Ruta para manejar el chat
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres Nibble, un asistente experto en redes y pruebas de velocidad..."},
                {"role": "user", "content": user_message}
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para datos de análisis de red
@app.route('/api/network_data')
def network_data():
    return jsonify(analyze_network())

# Ruta para simular errores de red
@app.route('/api/simulate_network_error', methods=['POST'])
def simulate_error():
    error_type = request.json.get("error_type", "")
    result = simulate_network_errors(error_type)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
