# -*- coding: utf-8 -*-
"""
Servidor Web y API RESTful Multihilo
Sistema: SIGIF-EP Piura 2026 (Versión Red Real en Vivo + Tesis UCV)
"""

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from analytics_engine import AnalyticsAndReportEngine
from config import APP_METADATA, NETWORK_CONFIG
from database import DatabaseManager
from network_scanner import NetworkScannerEngine
from ui_template import DASHBOARD_HTML


class SIGIFRequestHandler(BaseHTTPRequestHandler):
    """Controlador HTTP/REST para el dashboard y los endpoints de monitoreo real y gestión."""

    db: DatabaseManager = None
    scanner: NetworkScannerEngine = None
    analytics: AnalyticsAndReportEngine = None

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html_str: str, status: int = 200) -> None:
        payload = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        try:
            if path in ("/", "/index.html"):
                self._send_html(DASHBOARD_HTML)
                return

            if path == "/api/metadata":
                self._send_json(
                    {
                        "app": APP_METADATA,
                        "monitor": self.scanner.get_estado_monitor(),
                    }
                )
                return

            if path == "/api/telemetria_local":
                self._send_json(self.scanner.get_local_network_info())
                return

            if path == "/api/kpis":
                kpis = self.analytics.obtener_kpis_tiempo_real()
                kpis["telemetria_local"] = self.scanner.get_local_network_info()
                self._send_json(kpis)
                return

            if path == "/api/equipos":
                area = qs.get("area", ["SOLO_REALES"])[0]
                estado = qs.get("estado", ["TODOS"])[0]
                solo_reales = area == "SOLO_REALES"
                self._send_json(
                    self.db.get_all_equipos(area=area, estado=estado, solo_reales=solo_reales)
                )
                return

            if path == "/api/tecnicos":
                self._send_json(self.db.get_all_tecnicos())
                return

            if path == "/api/incidencias":
                fase = qs.get("fase", ["POSPRUEBA_O2"])[0]
                estado = qs.get("estado", ["TODOS"])[0]
                area = qs.get("area", ["TODAS"])[0]
                severidad = qs.get("severidad", ["TODAS"])[0]
                self._send_json(
                    self.db.get_incidencias(
                        fase=fase, estado=estado, area=area, severidad=severidad, limit=250
                    )
                )
                return

            if path == "/api/incidencia_detalle":
                inc_id = int(qs.get("id", ["1"])[0])
                detail = self.db.get_incidencia_detail(inc_id)
                if not detail:
                    self._send_json({"error": "No encontrado"}, status=404)
                else:
                    self._send_json(detail)
                return

            if path == "/api/alertas":
                solo_no_leidas = qs.get("no_leidas", ["0"])[0] == "1"
                self._send_json(self.db.get_alertas(solo_no_leidas=solo_no_leidas, limit=80))
                return

            if path == "/api/logs_monitoreo":
                self._send_json(self.db.get_ultimos_logs_monitoreo(limit=55))
                return

            if path == "/api/arp_real":
                entries = self.scanner.read_real_arp_table()
                self._send_json({"entradas": entries, "total": len(entries)})
                return

            if path == "/api/estadistica_tesis":
                self._send_json(self.analytics.obtener_analisis_estadistico_tesis())
                return

            if path == "/api/exportar":
                tipo = qs.get("tipo", ["csv_incidencias"])[0]
                if tipo == "csv_spss":
                    fp = self.analytics.exportar_matriz_spss_jamovi_csv()
                    content = fp.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/csv; charset=utf-8")
                    self.send_header("Content-Disposition", f'attachment; filename="{fp.name}"')
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                elif tipo == "html_ejecutivo":
                    fp = self.analytics.exportar_reporte_ejecutivo_html()
                    self._send_html(fp.read_text(encoding="utf-8"))
                    return
                else:
                    fp = self.analytics.exportar_incidencias_csv(fase="TODAS")
                    content = fp.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/csv; charset=utf-8")
                    self.send_header("Content-Disposition", f'attachment; filename="{fp.name}"')
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return

            self._send_json({"error": f"Ruta no encontrada: {path}"}, status=404)

        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        try:
            if path == "/api/escanear_equipo":
                eq_id = int(body.get("equipo_id", 1))
                res = self.scanner.diagnosticar_host_individual(eq_id, ejecutar_ping_real=True)
                self._send_json(res)
                return

            if path == "/api/descubrir_red_real":
                resumen = self.scanner.descubrir_red_local_en_vivo()
                self._send_json(resumen)
                return

            if path == "/api/escanear_red":
                resumen = self.scanner.ejecutar_barrido_red_completo()
                self._send_json(resumen)
                return

            if path == "/api/simular_equipo":
                eq_id = int(body.get("equipo_id", 1))
                modo = str(body.get("modo", "NORMAL"))
                self.db.configurar_simulacion_equipo(eq_id, modo)
                diag = self.scanner.diagnosticar_host_individual(eq_id, ejecutar_ping_real=True)
                if modo == "NORMAL":
                    abiertos = [
                        inc
                        for inc in self.db.get_incidencias(fase="POSPRUEBA_O2", limit=100)
                        if inc["equipo_id"] == eq_id and inc["estado_atencion"] in ("Pendiente", "En Atención")
                    ]
                    for inc in abiertos:
                        self.db.actualizar_estado_incidencia(
                            incidencia_id=inc["id"],
                            nuevo_estado="Resuelto",
                            responsable="Restauración Automática ICMP/ARP",
                            solucion_o_comentario="Enlace de red restablecido y verificado mediante PING/ARP sin pérdida de paquetes.",
                        )
                self._send_json({"ok": True, "modo": modo, "diagnostico": diag})
                return

            if path == "/api/crear_incidencia":
                eq_id = int(body.get("equipo_id", 1))
                tipo_falla = str(body.get("tipo_falla", "Falla de Conectividad / Pérdida de Enlace ICMP"))
                severidad = str(body.get("severidad", "Alta"))
                tecnico_id = body.get("tecnico_id")
                descripcion = str(body.get("descripcion_tecnica", "Incidencia registrada en el sistema."))
                inc = self.db.crear_incidencia(
                    equipo_id=eq_id,
                    tipo_falla=tipo_falla,
                    severidad=severidad,
                    origen_deteccion="Registro Directo en Sistema SIGIF-EP",
                    descripcion_tecnica=descripcion,
                    tecnico_id=int(tecnico_id) if tecnico_id else None,
                    dimension_asociada="D2",
                )
                self._send_json(inc)
                return

            if path == "/api/actualizar_incidencia":
                inc_id = int(body.get("incidencia_id"))
                nuevo_estado = str(body.get("nuevo_estado", "En Atención"))
                tecnico_id = body.get("tecnico_id")
                solucion = str(body.get("solucion", ""))
                updated = self.db.actualizar_estado_incidencia(
                    incidencia_id=inc_id,
                    nuevo_estado=nuevo_estado,
                    responsable="Soporte Técnico TI",
                    solucion_o_comentario=solucion,
                    tecnico_id=int(tecnico_id) if tecnico_id else None,
                )
                self._send_json(updated)
                return

            if path == "/api/marcar_alertas_leidas":
                alerta_id = body.get("alerta_id")
                count = self.db.marcar_alertas_leidas(int(alerta_id) if alerta_id else None)
                self._send_json({"ok": True, "marcadas": count})
                return

            if path == "/api/ping_real":
                ip = str(body.get("ip", "127.0.0.1"))
                res = self.scanner.execute_real_ping(ip, count=3, timeout_ms=700)
                open_ports, _ = self.scanner.probe_tcp_ports(ip, timeout_sec=0.22)
                res["puertos_abiertos"] = open_ports
                self._send_json(res)
                return

            self._send_json({"error": f"Endpoint POST no válido: {path}"}, status=404)

        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)


def create_http_server(
    db: DatabaseManager,
    scanner: NetworkScannerEngine,
    analytics: AnalyticsAndReportEngine,
    host: str = "127.0.0.1",
    port: int = NETWORK_CONFIG["default_port"],
) -> ThreadingHTTPServer:
    SIGIFRequestHandler.db = db
    SIGIFRequestHandler.scanner = scanner
    SIGIFRequestHandler.analytics = analytics
    server = ThreadingHTTPServer((host, port), SIGIFRequestHandler)
    return server
