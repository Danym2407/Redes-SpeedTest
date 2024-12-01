from pyparsing import line
import speedtest
import mysql.connector
import psutil
import socket
import requests
import time
from datetime import datetime
import random
import platform
import subprocess
import re

class SpeedTestMonitor:
    def __init__(self):
        # Configuración de la base de datos
        self.db_config = {
            'host': 'srv650006.hstgr.cloud',  # Dirección IP pública de tu VPS
            'user': 'root',  # Usuario MySQL que creaste
            'password': 'Dony247***Daniela',  # Contraseña del usuario MySQL
            'database': 'speedtest_db'  # Nombre de la base de datos
        }

    def crear_tablas(self):
        """Crear tablas en la base de datos si no existen"""
        conexion = mysql.connector.connect(**self.db_config)
        cursor = conexion.cursor()

        # Crear tabla de edificios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS edificios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_edificio VARCHAR(10),
            nivel VARCHAR(20),
            descripcion TEXT
        )
        """)

        # Crear tabla de speedtest_results con una clave foránea
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS speedtest_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            edificio_id INT,  -- Relación con la tabla edificios
            local_ip VARCHAR(50),
            download_speed FLOAT,
            upload_speed FLOAT,
            idle_latency FLOAT,
            active_connections INT,
            packet_loss_data VARCHAR(255),
            location VARCHAR(255),
            isp VARCHAR(255),
            download_description TEXT,
            upload_description TEXT,
            latency_description TEXT,
            status VARCHAR(50),
            bytes_sent BIGINT,
            bytes_recv BIGINT,
            errin INT,
            errout INT,
            interfaces TEXT,
            traceroute_hops INT,
            timestamp DATETIME,
            FOREIGN KEY (edificio_id) REFERENCES edificios (id) ON DELETE CASCADE
        )
        """)

        conexion.commit()
        cursor.close()
        conexion.close()

    def insertar_edificios(self):
        """Insertar edificios en la base de datos"""
        edificios = [
            ('A', 'Planta baja', 'Descripción de la planta baja de A'),
            ('A', 'Piso 1', 'Descripción del piso 1 de A'),
            ('A', 'Piso 2', 'Descripción del piso 2 de A'),

            ('B', 'Planta baja', 'Descripción de la planta baja de B'),
            ('B', 'Piso 1', 'Descripción del piso 1 de B'),
            ('B', 'Piso 2', 'Descripción del piso 2 de B'),

            ('C', 'Planta baja', 'Descripción de la planta baja de C'),
            ('C', 'Piso 1', 'Descripción del piso 1 de C'),
            ('C', 'Piso 2', 'Descripción del piso 2 de C'),

            ('D', 'Planta baja', 'Descripción de la planta baja de D'),
            ('D', 'Piso 1', 'Descripción del piso 1 de D'),
            ('D', 'Piso 2', 'Descripción del piso 2 de D'),

            ('E', 'Planta baja', 'Descripción de la planta baja de E'),
            ('E', 'Piso 1', 'Descripción del piso 1 de E'),
            ('E', 'Piso 2', 'Descripción del piso 2 de E'),

            ('T', 'Planta baja', 'Descripción de la planta baja de T'),
            ('T', 'Piso 1', 'Descripción del piso 1 de T'),
            ('T', 'Piso 2', 'Descripción del piso 2 de T'),

            ('N', 'Planta baja', 'Descripción de la planta baja de N'),
            ('N', 'Piso 1', 'Descripción del piso 1 de N'),
            ('N', 'Piso 2', 'Descripción del piso 2 de N'),

            ('P', 'Planta baja', 'Descripción de la planta baja de P'),
            ('P', 'Piso 1', 'Descripción del piso 1 de P'),
            ('P', 'Piso 2', 'Descripción del piso 2 de P'),

            ('Q', 'Planta baja', 'Descripción de la planta baja de Q'),
            ('Q', 'Piso 1', 'Descripción del piso 1 de Q'),
            ('Q', 'Piso 2', 'Descripción del piso 2 de Q'),

            ('R', 'Planta baja', 'Descripción de la planta baja de R'),
            ('R', 'Piso 1', 'Descripción del piso 1 de R'),
            ('R', 'Piso 2', 'Descripción del piso 2 de R'),

            ('S', 'Planta baja', 'Descripción de la planta baja de S'),
            ('S', 'Piso 1', 'Descripción del piso 1 de S'),
            ('S', 'Piso 2', 'Descripción del piso 2 de S'),

            ('K', 'Planta baja', 'Descripción de la planta baja de K'),
            ('K', 'Piso 1', 'Descripción del piso 1 de K'),
            ('K', 'Piso 2', 'Descripción del piso 2 de K'),

            ('L', 'Planta baja', 'Descripción de la planta baja de L'),
            ('L', 'Piso 1', 'Descripción del piso 1 de L'),
            ('L', 'Piso 2', 'Descripción del piso 2 de L'),

            ('H', 'Planta baja', 'Descripción de la planta baja de H'),
            ('H', 'Piso 1', 'Descripción del piso 1 de H'),
            ('H', 'Piso 2', 'Descripción del piso 2 de H'),

            ('F', 'Planta baja', 'Descripción de la planta baja de F'),
            ('F', 'Piso 1', 'Descripción del piso 1 de F'),
            ('F', 'Piso 2', 'Descripción del piso 2 de F')
        ]

        conexion = mysql.connector.connect(**self.db_config)
        cursor = conexion.cursor()

        # Verificar si ya existen edificios
        cursor.execute("SELECT COUNT(*) FROM edificios")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO edificios (nombre_edificio, nivel, descripcion) VALUES (%s, %s, %s)", 
                edificios
            )
            conexion.commit()

        cursor.close()
        conexion.close()

    def _obtener_conexiones_activas(self):
        """Obtener número de conexiones de red activas"""
        try:
            if platform.system() == "Windows":
                # Para Windows
                netstat_output = subprocess.check_output(["netstat", "-an"], universal_newlines=True)
                conexiones_activas = len([linea for linea in netstat_output.split('\n') if "ESTABLISHED" in linea])
            elif platform.system() in ["Linux", "Darwin"]:  # Linux o macOS
                netstat_output = subprocess.check_output(["netstat", "-an"], universal_newlines=True)
                conexiones_activas = len([linea for linea in netstat_output.split('\n') if "ESTABLISHED" in linea])
            else:
                # Usar psutil como respaldo
                conexiones_activas = len(psutil.net_connections(kind='inet'))
            
            return conexiones_activas
        except Exception as e:
            print(f"Error al obtener conexiones activas: {e}")
            return 0

    def _obtener_perdida_paquetes(self):
        """Obtener porcentaje de pérdida de paquetes de manera más robusta"""
        try:
            # Ping a un sitio confiable para medir pérdida de paquetes
            target = "8.8.8.8"  # DNS de Google
            
            if platform.system() == "Windows":
                # Para Windows, usar más intentos y capturar la salida completa
                ping_output = subprocess.check_output(["ping", "-n", "10", target], universal_newlines=True)
                
                # Buscar patrones de pérdida de paquetes en Windows
                for linea in ping_output.split('\n'):
                    if "Packets:" in linea or "Lost =" in linea:
                        # Extraer el porcentaje de pérdida
                        partes = linea.split(',')
                        for parte in partes:
                            if "Lost" in parte:
                                try:
                                    # Extraer el número antes de la palabra "Lost"
                                    perdida = parte.split()[0]
                                    return float(perdida)
                                except (ValueError, IndexError):
                                    pass
            else:
                # Para Linux y macOS
                ping_output = subprocess.check_output(["ping", "-c", "10", target], universal_newlines=True)
                
                # Buscar patrones de pérdida de paquetes en sistemas Unix
                for linea in ping_output.split('\n'):
                    if "packet loss" in linea:
                        try:
                            # Extraer el porcentaje de pérdida
                            perdida = linea.split(',')[2].strip().split()[0].replace('%', '')
                            return float(perdida)
                        except (ValueError, IndexError):
                            pass
            
            # Si no se encuentra el porcentaje, imprimir la salida completa para diagnóstico
            print("Salida de ping no reconocida:")
            print(ping_output)
            return 0.0
        
        except Exception as e:
            print(f"Error al obtener pérdida de paquetes: {e}")
            return 0.0
    
    def realizar_traceroute(self, destino='8.8.8.8'):
        """
        Realizar traceroute a un destino específico
        
        Returns:
            int: Número de saltos
        """
        try:
            sistema = platform.system().lower()
            
            if sistema == 'windows':
                comando = ['tracert', '-d', destino]
            elif sistema in ['linux', 'darwin']:
                comando = ['traceroute', '-n', destino]
            else:
                print("Sistema operativo no compatible")
                return 0

            resultado = subprocess.check_output(comando, universal_newlines=True, stderr=subprocess.STDOUT)
            
            saltos = []
            for linea in resultado.split('\n'):
                partes = linea.strip().split()
                
                if sistema == 'windows':
                    # Para Windows, busca líneas con números de salto y direcciones IP válidas
                    if len(partes) >= 3 and partes[0].isdigit():
                        try:
                            ip = partes[-1]
                            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
                                # Evitar duplicados y '*'
                                if ip != '*' and ip not in saltos:
                                    saltos.append(ip)
                        except:
                            pass
                else:
                    # Para Linux/macOS
                    if len(partes) >= 2 and re.match(r'\d+', partes[0]):
                        try:
                            ip = partes[1]
                            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
                                # Evitar duplicados y '*'
                                if ip != '*' and ip not in saltos:
                                    saltos.append(ip)
                        except:
                            pass

            # Devolver número de saltos únicos
            return len(set(saltos))
        
        except Exception as e:
            print(f"Error en traceroute: {e}")
            return 0
    
    def realizar_speedtest(self):
        """Realizar speedtest completo"""
        try:
            st = speedtest.Speedtest()
            
            # Obtener velocidad de descarga
            download_speed = st.download() / 1_000_000  # Convertir a Mbps
            
            # Obtener velocidad de subida
            upload_speed = st.upload() / 1_000_000  # Convertir a Mbps
            
            # Latencia
            st.get_best_server()
            latency_value = st.results.ping

            # Información de red adicional
            local_ip = socket.gethostbyname(socket.gethostname())
            net_io = psutil.net_io_counters()
            
            # Obtener conexiones activas y pérdida de paquetes
            active_connections = self._obtener_conexiones_activas()
            packet_loss_data = f"{self._obtener_perdida_paquetes():.2f}%"

            # Información de ubicación e ISP
            location, isp = self._obtener_ubicacion_y_isp()

            # Descripciones
            download_description = self._evaluar_velocidad(download_speed, 'download')
            upload_description = self._evaluar_velocidad(upload_speed, 'upload')
            latency_description = self._evaluar_latencia(latency_value)

            # Estado general
            status = 'Bueno' if download_speed > 50 and upload_speed > 25 and latency_value < 50 else 'Regular'

            # Interfaces de red
            net_stats = ', '.join(psutil.net_if_stats().keys())
            
            # Obtener traceroute y cantidad de saltos
            traceroute_hops = self.realizar_traceroute()

            return {
                'local_ip': local_ip,
                'download_speed': round(download_speed, 2),
                'upload_speed': round(upload_speed, 2),
                'idle_latency': round(latency_value, 2),
                'active_connections': active_connections,
                'packet_loss_data': packet_loss_data,
                'location': location,
                'isp': isp,
                'download_description': download_description,
                'upload_description': upload_description,
                'latency_description': latency_description,
                'status': status,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'interfaces': net_stats,
                'traceroute_hops': traceroute_hops
            }
        except Exception as e:
            print(f"Error en speedtest: {e}")
            return None

    def _obtener_ubicacion_y_isp(self):
        """Obtener ubicación e ISP de varias fuentes confiables"""
        apis = [
            'https://ipapi.co/json/',
            'https://ipinfo.io/json/',
            'https://geoipify.whoisxmlapi.com/api/v1?apiKey=YOUR_API_KEY'
        ]
        
        # Obtener la IP pública
        try:
            ip_publica = requests.get('https://api64.ipify.org?format=json', timeout=5).json().get('ip', None)
        except Exception as e:
            print(f"Error al obtener IP pública: {e}")
            ip_publica = None

        for api in apis:
            try:
                response = requests.get(api, params={'ip': ip_publica} if ip_publica else None, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    location = f"{data.get('city', 'Desconocido')}, {data.get('region', 'Desconocido')}, {data.get('country_name', data.get('country', 'Desconocido'))}"
                    isp = data.get('org', data.get('isp', 'Desconocido'))
                    # Validar que no haya campos vacíos
                    if location and isp:
                        return location, isp
            except Exception as e:
                print(f"Error al conectar con la API {api}: {e}")
        
        # Si todo falla, devolver valores predeterminados
        return "Ubicación desconocida", "ISP desconocido"

    def _evaluar_velocidad(self, speed, tipo):
        """Evaluar la velocidad de internet"""
        if tipo == 'download':
            if speed > 100: return "Velocidad de descarga excelente"
            if speed > 50: return "Velocidad de descarga buena"
            if speed > 25: return "Velocidad de descarga aceptable"
            return "Velocidad de descarga lenta"
        else:
            if speed > 50: return "Velocidad de subida excelente"
            if speed > 25: return "Velocidad de subida buena"
            if speed > 10: return "Velocidad de subida aceptable"
            return "Velocidad de subida lenta"

    def _evaluar_latencia(self, latencia):
        """Evaluar la latencia"""
        if latencia < 20: return "Latencia muy baja"
        if latencia < 50: return "Latencia baja"
        if latencia < 100: return "Latencia moderada"
        return "Latencia alta"

    def guardar_resultado(self, resultado, nombre_edificio, nivel):
        """Guardar resultado del speedtest en la base de datos"""
        if not resultado:
            print("No se pudo guardar el resultado. Speedtest fallido.")
            return

        conexion = mysql.connector.connect(**self.db_config)
        cursor = conexion.cursor()

        # Buscar el id del edificio correspondiente
        cursor.execute("""
        SELECT id FROM edificios WHERE nombre_edificio = %s AND nivel = %s
        """, (nombre_edificio, nivel))
        edificio_data = cursor.fetchone()

        if not edificio_data:
            print(f"No se encontró el edificio '{nombre_edificio}' con nivel '{nivel}'.")
            conexion.close()
            return

        edificio_id = edificio_data[0]

        # Inserción en speedtest_results
        consulta = """
        INSERT INTO speedtest_results 
        (edificio_id, local_ip, download_speed, upload_speed, idle_latency, 
        active_connections, packet_loss_data, location, isp, download_description, 
        upload_description, latency_description, status, bytes_sent, bytes_recv, 
        errin, errout, interfaces, traceroute_hops, timestamp)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """

        valores = (
            edificio_id,
            resultado['local_ip'], 
            resultado['download_speed'], 
            resultado['upload_speed'], 
            resultado['idle_latency'], 
            resultado['active_connections'], 
            resultado['packet_loss_data'], 
            resultado['location'], 
            resultado['isp'], 
            resultado['download_description'], 
            resultado['upload_description'], 
            resultado['latency_description'], 
            resultado['status'], 
            resultado['bytes_sent'], 
            resultado['bytes_recv'], 
            resultado['errin'], 
            resultado['errout'], 
            resultado['interfaces'], 
            resultado['traceroute_hops']
        )

        cursor.execute(consulta, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        print(f"Resultado guardado para {nombre_edificio} - {nivel}")

    def monitoreo_continuo(self, edificio, nivel, duracion_horas=1, intervalo_minutos=5):
        """Realizar monitoreo continuo de speedtest"""
        inicio = time.time()
        fin = inicio + (duracion_horas * 3600)

        print(f"Iniciando monitoreo para {edificio} - {nivel}")
        print(f"Duración: {duracion_horas} horas")
        print(f"Intervalo entre pruebas: {intervalo_minutos} minutos")

        while time.time() < fin:
            resultado = self.realizar_speedtest()
            self.guardar_resultado(resultado, edificio, nivel)
            time.sleep(intervalo_minutos * 60)


    # Método opcional para integrar en la clase SpeedTestMonitor
    def monitoreo_completo(self, edificio, nivel):
        """
        Realizar monitoreo completo incluyendo speedtest y traceroute
        """
        # Realizar speedtest
        resultado_speedtest = self.realizar_speedtest()
        
        # Realizar traceroute
        resultado_traceroute = self.realizar_traceroute()
        
        # Combinar resultados si es necesario
        if resultado_speedtest and resultado_traceroute:
            resultado_combinado = {
                **resultado_speedtest,
                'traceroute': resultado_traceroute
            }
            
            # Guardar en base de datos o procesar según necesidad
            self.guardar_resultado(resultado_combinado, edificio, nivel)
        
        return resultado_combinado

def main():
    monitor = SpeedTestMonitor()
    
    # Crear tablas
    monitor.crear_tablas()
    
    # Insertar edificios
    monitor.insertar_edificios()

    # Solicitar detalles al usuario
    print("Edificios disponibles: A, B, C, D, E, T, N, P, Q, R, S, K, L, H, F")
    edificio = input("Seleccione un edificio: ").upper()
    nivel = input("Seleccione un nivel (Planta baja, Piso 1, Piso 2): ")
    duracion = float(input("Duración del monitoreo en horas: "))
    intervalo = int(input("Intervalo entre pruebas (minutos): "))

    # Realizar monitoreo
    monitor.monitoreo_continuo(edificio, nivel, duracion, intervalo)

if __name__ == "__main__":
    main()