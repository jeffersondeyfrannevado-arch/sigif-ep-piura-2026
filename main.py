# -*- coding: utf-8 -*-
"""
Punto de Entrada Principal — SIGIF-EP Piura 2026 (Local Windows + Cloud Render/Vercel)
"Aplicación para la detección y gestión de incidencias y fallas en equipos
informáticos de una entidad educativa pública Piura 2026"
"""

import argparse
import os
import socket
import threading
import webbrowser

from analytics_engine import AnalyticsAndReportEngine
from config import APP_METADATA, NETWORK_CONFIG
from database import DatabaseManager
from network_scanner import NetworkScannerEngine
from web_server import create_http_server


def find_available_port(preferred_port: int = NETWORK_CONFIG["default_port"], host: str = "127.0.0.1") -> int:
    if os.environ.get("PORT"):
        return int(os.environ["PORT"])
    for port in range(preferred_port, preferred_port + 25):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return preferred_port


def run_verification_suite(
    db: DatabaseManager,
    scanner: NetworkScannerEngine,
    analytics: AnalyticsAndReportEngine,
) -> None:
    print("=" * 94)
    print(f" {APP_METADATA['nombre_sistema']} — DESCUBRIMIENTO DE RED REAL EN VIVO Y VERIFICACIÓN")
    print("=" * 94)

    tel = scanner.get_local_network_info()
    hw = tel["hardware_local"]
    print(f"[ESTACIÓN LOCAL] Hostname : {tel['nodo_monitor']} | IP Real: {tel['ip_monitor']} | MAC: {tel['mac_monitor']}")
    print(f"[TARJETA ACTIVA] Adaptador: {tel['adaptador_red']} | Subred: {tel['subred_activa']} | Gateway: {tel['puerta_enlace']}")
    print(f"[HARDWARE REAL ] RAM      : {hw['ram_usada_gb']}/{hw['ram_total_gb']} GB ({hw['ram_uso_pct']}%) | Disco: {hw['disco_usado_gb']}/{hw['disco_total_gb']} GB ({hw['disco_uso_pct']}%) | {hw['uptime']}")
    if hw["wifi"]["conectado"]:
        print(f"[ENLACE WI-FI  ] SSID     : {hw['wifi']['ssid']} | Señal: {hw['wifi']['senal_pct']}% | Radio: {hw['wifi']['radio']} | Canal: {hw['wifi']['canal']}")

    print("\nEscaneando en vivo los 254 hosts de tu subred real (" + tel["subred_activa"] + ")...")
    live = scanner.descubrir_red_local_en_vivo()
    print(f"[OK] Descubrimiento en vivo completado en {live['duracion_descubrimiento_seg']}s: {live['total_hosts_reales_activos']} DISPOSITIVOS FÍSICOS REALES ACTIVOS:")
    print("-" * 94)
    print(f"{'CÓDIGO':<18} {'IP REAL':<16} {'MAC FÍSICA (ARP)':<19} {'PING':<9} {'FABRICANTE OUI / PERFIL':<30}")
    print("-" * 94)
    for dev in live["dispositivos_reales"]:
        print(
            f"{dev['codigo_logico']:<18} {dev['ip_address']:<16} {dev['mac_address']:<19} "
            f"{str(dev['latencia_ms'])+'ms':<9} {dev['fabricante_mac']} ({dev['puertos_abiertos']})"
        )
    print("-" * 94)

    stats = analytics.obtener_analisis_estadistico_tesis()
    cron = stats["confiabilidad_alfa_cronbach"]
    t_glob = stats["contraste_hipotesis_encuesta_global"]["t_student"]
    print(f"[OK] Alfa de Cronbach (16 ítems, N=45): {cron['alfa_cronbach']} | Prueba t = {t_glob['t_student']} (p {t_glob['p_texto']})")

    fp_csv = analytics.exportar_incidencias_csv("TODAS")
    fp_spss = analytics.exportar_matriz_spss_jamovi_csv()
    fp_html = analytics.exportar_reporte_ejecutivo_html()
    print(f"[OK] Reportes actualizados en: {fp_csv.parent}")
    print("=" * 94)


def main() -> None:
    is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT") or os.environ.get("VERCEL"))
    default_host = "0.0.0.0" if is_cloud else "127.0.0.1"
    default_port = int(os.environ.get("PORT", NETWORK_CONFIG["default_port"]))

    parser = argparse.ArgumentParser(description=APP_METADATA["titulo_tesis"])
    parser.add_argument("--verify", action="store_true", help="Ejecuta descubrimiento de red real y verificación")
    parser.add_argument("--web-only", action="store_true", default=is_cloud, help="Ejecuta solo el servidor web")
    parser.add_argument("--no-browser", action="store_true", default=is_cloud, help="No abrir automáticamente el navegador web")
    parser.add_argument("--host", type=str, default=default_host, help="Host HTTP (127.0.0.1 o 0.0.0.0)")
    parser.add_argument("--port", type=int, default=default_port, help="Puerto HTTP")
    args = parser.parse_args()

    db = DatabaseManager()
    scanner = NetworkScannerEngine(db)
    analytics = AnalyticsAndReportEngine(db)

    if args.verify:
        run_verification_suite(db, scanner, analytics)
        return

    reales_existentes = db.get_all_equipos(solo_reales=True)
    if not reales_existentes and not is_cloud:
        print("Descubriendo dispositivos reales conectados a tu red local...")
        live_info = scanner.descubrir_red_local_en_vivo()
        total_reales = live_info["total_hosts_reales_activos"]
        subred_str = live_info["subred_escaneada"]
    else:
        iface = scanner.get_active_network_interface()
        total_reales = len(reales_existentes)
        subred_str = iface["subnet_cidr"]

    analytics.exportar_incidencias_csv("TODAS")
    analytics.exportar_matriz_spss_jamovi_csv()
    analytics.exportar_reporte_ejecutivo_html()

    port = find_available_port(args.port, host=args.host)
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    web_url = f"http://{display_host}:{port}"
    server = create_http_server(db, scanner, analytics, host=args.host, port=port)

    if not is_cloud:
        scanner.iniciar_monitoreo_continuo(intervalo_seg=25)

    print("=" * 84)
    print(f" {APP_METADATA['nombre_sistema']} — SISTEMA EN EJECUCIÓN")
    print(f" Escuchando en             : http://{args.host}:{port}")
    print(f" Subred Monitoreada        : {subred_str} ({total_reales} hosts reales registrados)")
    print(f" Dashboard Web Interactivo : {web_url}")
    print("=" * 84)

    if not args.no_browser and not is_cloud:
        threading.Timer(0.6, lambda: webbrowser.open(web_url)).start()

    if args.web_only or is_cloud:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            scanner.detener_monitoreo_continuo()
            server.shutdown()
    else:
        srv_thread = threading.Thread(target=server.serve_forever, name="SIGIF-HTTPServer", daemon=True)
        srv_thread.start()
        try:
            from desktop_app import SIGIFDesktopApp
            app = SIGIFDesktopApp(db=db, scanner=scanner, analytics=analytics, web_url=web_url)
            app.run()
        except Exception as exc:
            print(f"Aviso GUI Desktop ({exc}). Servidor Web activo en {web_url} ...")
            try:
                while True:
                    srv_thread.join(timeout=1.0)
            except KeyboardInterrupt:
                pass
        finally:
            scanner.detener_monitoreo_continuo()
            server.shutdown()


if __name__ == "__main__":
    main()
