# -*- coding: utf-8 -*-
"""
Interfaz Gráfica de Escritorio Nativa (Tkinter / TTK) con Escáner de Red Real en Vivo
Sistema: SIGIF-EP Piura 2026
Muestra en vivo todos los dispositivos físicos reales descubiertos en la subred local
(ej. 192.168.0.0/24), la telemetría de hardware/Wi-Fi de la estación local, y la gestión
completa de incidencias ITIL v4 y evaluación estadística de la tesis.
"""

import threading
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from typing import Optional

from analytics_engine import AnalyticsAndReportEngine
from config import APP_METADATA, NETWORK_CONFIG
from database import DatabaseManager
from network_scanner import NetworkScannerEngine


class SIGIFDesktopApp:
    """Aplicación nativa de escritorio para el monitoreo real LAN/Wi-Fi y gestión de incidencias TI."""

    def __init__(
        self,
        db: DatabaseManager,
        scanner: NetworkScannerEngine,
        analytics: AnalyticsAndReportEngine,
        web_url: str = f"http://127.0.0.1:{NETWORK_CONFIG['default_port']}",
    ):
        self.db = db
        self.scanner = scanner
        self.analytics = analytics
        self.web_url = web_url
        self.mostrar_solo_reales = tk.BooleanVar(value=True)

        self.root = tk.Tk()
        self.root.title(f"{APP_METADATA['nombre_sistema']} [RED REAL EN VIVO] — {APP_METADATA['titulo_tesis']}")
        self.root.geometry("1280x780")
        self.root.minsize(1060, 680)
        self.root.configure(bg="#f1f5f9")

        self._configure_styles()
        self._build_ui()
        self.refresh_all()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="#f1f5f9")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0", foreground="#0f2547")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)

    def _build_ui(self) -> None:
        # Encabezado Institucional
        header = tk.Frame(self.root, bg="#0f2547", padx=18, pady=11)
        header.pack(fill="x")

        left_h = tk.Frame(header, bg="#0f2547")
        left_h.pack(side="left", fill="x", expand=True)
        tk.Label(
            left_h,
            text=f"UCV PIURA 2026 | {APP_METADATA['nombre_sistema']} — Escáner de Red Real en Vivo (ICMP / ARP / Puertos TCP)",
            bg="#0f2547",
            fg="#ffffff",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).pack(fill="x")
        self.lbl_hw_banner = tk.Label(
            left_h,
            text="Detectando tarjeta de red activa y telemetría de hardware local...",
            bg="#0f2547",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.lbl_hw_banner.pack(fill="x", pady=(2, 0))

        right_h = tk.Frame(header, bg="#0f2547")
        right_h.pack(side="right")
        tk.Button(
            right_h,
            text="🌐 Abrir Dashboard Web en Vivo",
            bg="#2563eb",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: webbrowser.open(self.web_url),
        ).pack(side="left", padx=5)
        tk.Button(
            right_h,
            text="📡 Descubrir Mi Red Real Ahora (1-254)",
            bg="#16a34a",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._run_real_discovery_async,
        ).pack(side="left", padx=5)

        # Fila de KPIs
        kpi_frame = tk.Frame(self.root, bg="#f1f5f9", padx=16, pady=9)
        kpi_frame.pack(fill="x")
        self.kpi_vars = {
            "reales": tk.StringVar(value="--"),
            "lat_real": tk.StringVar(value="-- ms"),
            "ram_local": tk.StringVar(value="--"),
            "activos": tk.StringVar(value="0"),
            "alfa": tk.StringVar(value="--"),
        }
        kpi_defs = [
            ("DISPOSITIVOS REALES EN TU RED", "reales", "#16a34a"),
            ("LATENCIA REAL MEDIA LAN", "lat_real", "#2563eb"),
            ("RAM / DISCO ESTACIÓN LOCAL", "ram_local", "#0f172a"),
            ("TICKETS / ALERTAS ACTIVAS", "activos", "#dc2626"),
            ("ALFA DE CRONBACH (N=45)", "alfa", "#7c3aed"),
        ]
        for idx, (title, key, color) in enumerate(kpi_defs):
            card = tk.Frame(kpi_frame, bg="#ffffff", bd=1, relief="solid", padx=12, pady=7)
            card.grid(row=0, column=idx, sticky="nsew", padx=4)
            kpi_frame.grid_columnconfigure(idx, weight=1)
            tk.Frame(card, bg=color, height=4).pack(fill="x", pady=(0, 5))
            tk.Label(card, text=title, bg="#ffffff", fg="#475569", font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(card, textvariable=self.kpi_vars[key], bg="#ffffff", fg="#0f172a", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(2, 0))

        # Notebook de Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self._build_tab_equipos()
        self._build_tab_incidencias()
        self._build_tab_estadistica_reportes()

    def _build_tab_equipos(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 1. Dispositivos Reales en Tu Red Local (En Vivo ICMP / ARP / TCP) ")

        toolbar = tk.Frame(tab, bg="#ffffff", pady=8, padx=10)
        toolbar.pack(fill="x")
        tk.Checkbutton(
            toolbar,
            text="📡 Mostrar SOLO Dispositivos Reales Conectados a Mi Red Actual (desmarcar para ver también los 35 de plantilla)",
            variable=self.mostrar_solo_reales,
            bg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            fg="#1e3a8a",
            command=self.refresh_all,
        ).pack(side="left")

        tk.Button(toolbar, text="✔ Re-sondear / Restaurar", bg="#16a34a", fg="#fff", relief="flat", padx=9, pady=4, command=lambda: self._simular_seleccionado("NORMAL")).pack(side="right", padx=4)
        tk.Button(toolbar, text="🐢 Probar Alerta Lentitud", bg="#d97706", fg="#fff", relief="flat", padx=9, pady=4, command=lambda: self._simular_seleccionado("FORZAR_LENTITUD")).pack(side="right", padx=4)
        tk.Button(toolbar, text="⚡ Probar Alerta Caída", bg="#dc2626", fg="#fff", relief="flat", padx=9, pady=4, command=lambda: self._simular_seleccionado("FORZAR_CAIDA")).pack(side="right", padx=4)
        tk.Button(toolbar, text="🔍 PING / ARP Real en Vivo", bg="#1d4ed8", fg="#fff", relief="flat", padx=9, pady=4, command=self._diagnosticar_seleccionado).pack(side="right", padx=4)

        cols = ("id", "origen", "codigo", "ip", "mac", "fabricante", "hostname", "tipo", "puertos", "estado", "latencia", "arp")
        self.tree_eq = ttk.Treeview(tab, columns=cols, show="headings", height=20)
        headers = [
            ("id", "ID", 38),
            ("origen", "Origen", 95),
            ("codigo", "Código Lógico", 120),
            ("ip", "IP Real", 105),
            ("mac", "MAC Física (ARP)", 125),
            ("fabricante", "Fabricante NIC (OUI)", 175),
            ("hostname", "Hostname", 130),
            ("tipo", "Perfil / SO Detectado", 170),
            ("puertos", "Puertos / Servicios", 130),
            ("estado", "Estado", 85),
            ("latencia", "Ping (ms)", 75),
            ("arp", "Resolución Capa 2 ARP", 175),
        ]
        for col, text, w in headers:
            self.tree_eq.heading(col, text=text)
            self.tree_eq.column(col, width=w, anchor="center" if col in ("id", "origen", "estado", "latencia") else "w")

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.tree_eq.yview)
        self.tree_eq.configure(yscrollcommand=sb.set)
        self.tree_eq.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _build_tab_incidencias(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 2. Gestión de Incidencias y Alertas ITIL v4 ")

        toolbar = tk.Frame(tab, bg="#ffffff", pady=8, padx=10)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Gestión del Ciclo de Vida de Incidencias (Posprueba O2):", bg="#ffffff", font=("Segoe UI", 9, "bold")).pack(side="left")

        tk.Button(toolbar, text="✅ Marcar Resuelto y Restaurar Equipo", bg="#16a34a", fg="#fff", relief="flat", padx=10, pady=4, command=lambda: self._cambiar_estado_inc_seleccionada("Resuelto")).pack(side="right", padx=4)
        tk.Button(toolbar, text="🔧 Pasar a En Atención", bg="#d97706", fg="#fff", relief="flat", padx=10, pady=4, command=lambda: self._cambiar_estado_inc_seleccionada("En Atención")).pack(side="right", padx=4)
        tk.Button(toolbar, text="🔄 Actualizar Tabla", bg="#475569", fg="#fff", relief="flat", padx=10, pady=4, command=self.refresh_all).pack(side="right", padx=4)

        cols = ("id", "ticket", "equipo", "area", "tipo", "sev", "fecha", "tdet", "tresp", "tsol", "estado", "tecnico")
        self.tree_inc = ttk.Treeview(tab, columns=cols, show="headings", height=20)
        headers = [
            ("id", "ID", 40),
            ("ticket", "Ticket", 105),
            ("equipo", "Equipo", 110),
            ("area", "Área / Ubicación", 170),
            ("tipo", "Tipo de Falla", 210),
            ("sev", "Severidad", 75),
            ("fecha", "Fecha / Hora", 130),
            ("tdet", "Detección", 75),
            ("tresp", "Respuesta", 80),
            ("tsol", "Solución", 80),
            ("estado", "Estado", 90),
            ("tecnico", "Técnico Responsable", 170),
        ]
        for col, text, w in headers:
            self.tree_inc.heading(col, text=text)
            self.tree_inc.column(col, width=w, anchor="center" if col in ("id", "sev", "tdet", "tresp", "tsol", "estado") else "w")

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.tree_inc.yview)
        self.tree_inc.configure(yscrollcommand=sb.set)
        self.tree_inc.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _build_tab_estadistica_reportes(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 3. Evaluación Estadística (O1-X-O2 / Alfa Cronbach) y Exportación ")

        btn_bar = tk.Frame(tab, bg="#ffffff", pady=10, padx=12)
        btn_bar.pack(fill="x")
        tk.Button(btn_bar, text="📥 Exportar Incidencias (CSV/Excel)", bg="#16a34a", fg="#fff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, command=self._export_csv_inc).pack(side="left", padx=5)
        tk.Button(btn_bar, text="📊 Exportar Matriz N=45 (SPSS / Jamovi)", bg="#2563eb", fg="#fff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, command=self._export_csv_spss).pack(side="left", padx=5)
        tk.Button(btn_bar, text="🖨️ Generar y Abrir Informe Ejecutivo HTML/PDF", bg="#c8102e", fg="#fff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, command=self._export_html_exec).pack(side="left", padx=5)

        self.txt_stats = tk.Text(tab, bg="#0f172a", fg="#e2e8f0", font=("Consolas", 10), padx=14, pady=12)
        self.txt_stats.pack(fill="both", expand=True, padx=10, pady=8)

    def refresh_all(self) -> None:
        kpis = self.analytics.obtener_kpis_tiempo_real()
        stats = self.analytics.obtener_analisis_estadistico_tesis()
        tel = self.scanner.get_local_network_info()
        hw = tel["hardware_local"]
        red = kpis["resumen_red"]
        inc_o2 = kpis["resumen_incidencias_o2"]
        cron = stats["confiabilidad_alfa_cronbach"]

        wifi_txt = f"Wi-Fi SSID: {hw['wifi']['ssid']} ({hw['wifi']['senal_pct']}%)" if hw["wifi"]["conectado"] else "Red Cableada LAN"
        self.lbl_hw_banner.configure(
            text=(
                f"🟢 CONECTADO EN VIVO | Estación: {tel['nodo_monitor']} | IP Real: {tel['ip_monitor']} | "
                f"MAC: {tel['mac_monitor']} | Subred: {tel['subred_activa']} | Gateway: {tel['puerta_enlace']} | "
                f"{wifi_txt} | Adaptador: {tel['adaptador_red']}"
            )
        )

        self.kpi_vars["reales"].set(f"{red['dispositivos_reales_operativos']} / {red['dispositivos_reales_total']} en vivo")
        self.kpi_vars["lat_real"].set(f"{red['latencia_real_promedio_ms']} ms")
        self.kpi_vars["ram_local"].set(f"RAM {hw['ram_uso_pct']}% | Disco {hw['disco_uso_pct']}%")
        self.kpi_vars["activos"].set(f"{inc_o2['pendientes'] + inc_o2['en_atencion']} activos")
        self.kpi_vars["alfa"].set(f"α = {cron['alfa_cronbach']}")

        for item in self.tree_eq.get_children():
            self.tree_eq.delete(item)
        solo_reales = self.mostrar_solo_reales.get()
        for eq in self.db.get_all_equipos(solo_reales=solo_reales):
            es_real = eq.get("es_dispositivo_real") == 1
            self.tree_eq.insert(
                "",
                "end",
                values=(
                    eq["id"],
                    "🟢 RED REAL" if es_real else "🏛️ TESIS",
                    eq["codigo_logico"],
                    eq["ip_address"],
                    eq["mac_address"],
                    eq.get("fabricante_mac", "Adaptador IEEE"),
                    eq["hostname"],
                    f"{eq['tipo_equipo']} ({eq['sistema_operativo']})",
                    eq.get("puertos_abiertos", "ICMP/ARP"),
                    eq["estado_actual"],
                    f"{eq['latencia_ms']} ms",
                    eq["estado_arp"],
                ),
            )

        for item in self.tree_inc.get_children():
            self.tree_inc.delete(item)
        for inc in self.db.get_incidencias(fase="POSPRUEBA_O2", limit=150):
            self.tree_inc.insert(
                "",
                "end",
                values=(
                    inc["id"],
                    inc["codigo_ticket"],
                    inc["codigo_logico_equipo"],
                    inc["area"],
                    inc["tipo_falla"],
                    inc["severidad"],
                    inc["fecha_hora_evento"],
                    f"{inc['tiempo_deteccion_seg']} s",
                    f"{inc['tiempo_respuesta_min']} m" if inc["tiempo_respuesta_min"] is not None else "Pendiente",
                    f"{inc['tiempo_solucion_min']} m" if inc["tiempo_solucion_min"] is not None else "En curso",
                    inc["estado_atencion"],
                    inc["tecnico_nombre"] or "-",
                ),
            )

        comp = kpis["comparativa_pre_vs_pos"]
        t_glob = stats["contraste_hipotesis_encuesta_global"]["t_student"]
        w_glob = stats["contraste_hipotesis_encuesta_global"]["wilcoxon"]
        resumen_txt = (
            f"=========================================================================================\n"
            f" TELEMETRÍA EN VIVO DE LA RED REAL ({tel['subred_activa']}) Y RESULTADOS ESTADÍSTICOS\n"
            f"=========================================================================================\n"
            f"Estación Monitor Local : {tel['nodo_monitor']} (IP: {tel['ip_monitor']} / MAC: {tel['mac_monitor']})\n"
            f"Tarjeta de Red Activa  : {tel['adaptador_red']} | Gateway: {tel['puerta_enlace']}\n"
            f"Recursos Hardware Local: RAM {hw['ram_usada_gb']}/{hw['ram_total_gb']} GB ({hw['ram_uso_pct']}%) | Disco {hw['disco_usado_gb']}/{hw['disco_total_gb']} GB ({hw['disco_uso_pct']}%) | {hw['uptime']}\n"
            f"Dispositivos Reales LAN: {red['dispositivos_reales_total']} hosts físicos detectados en tu red actual\n\n"
            f"1. CONFIABILIDAD Y VALIDEZ DEL INSTRUMENTO (16 ÍTEMS ESCALA LIKERT - ANEXO 2):\n"
            f"   • Coeficiente Alfa de Cronbach : α = {cron['alfa_cronbach']} ({cron['interpretacion']})\n"
            f"   • Coeficiente V de Aiken       : V = 1.000 (Acuerdo unánime de 3 Jueces Expertos UCV)\n\n"
            f"2. COMPARACIÓN DE INDICADORES TÉCNICOS (PREPRUEBA O1 vs POSPRUEBA O2):\n"
            f"   • Tiempo Promedio Detección    : O1 = {comp['tiempo_deteccion_min']['pre_o1']} min  ➔  O2 = {comp['tiempo_deteccion_min']['pos_o2_seg']} seg (-{comp['tiempo_deteccion_min']['mejora_pct']}%)\n"
            f"   • Tiempo Promedio Respuesta TI : O1 = {comp['tiempo_respuesta_min']['pre_o1']} min  ➔  O2 = {comp['tiempo_respuesta_min']['pos_o2']} min (-{comp['tiempo_respuesta_min']['mejora_pct']}%)\n"
            f"   • Tiempo Promedio Solución TI  : O1 = {comp['tiempo_solucion_min']['pre_o1']} min  ➔  O2 = {comp['tiempo_solucion_min']['pos_o2']} min (-{comp['tiempo_solucion_min']['mejora_pct']}%)\n\n"
            f"3. CONTRASTE DE HIPÓTESIS INFERENCIAL (PRUEBA t DE STUDENT Y WILCOXON):\n"
            f"   • Prueba t de Student Pareada  : t = {t_glob['t_student']}, gl = {t_glob['grados_libertad']}, p {t_glob['p_texto']}, d de Cohen = {t_glob['d_cohen']}\n"
            f"   • Prueba Rangos de Wilcoxon    : W = {w_glob['w_wilcoxon']}, Z = {w_glob['z_aprox']}, p {w_glob['p_texto']}\n"
        )
        self.txt_stats.delete("1.0", tk.END)
        self.txt_stats.insert(tk.END, resumen_txt)

    def _get_selected_equipo_id(self) -> Optional[int]:
        sel = self.tree_eq.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Seleccione primero un dispositivo de la tabla.")
            return None
        vals = self.tree_eq.item(sel[0], "values")
        return int(vals[0])

    def _diagnosticar_seleccionado(self) -> None:
        eq_id = self._get_selected_equipo_id()
        if not eq_id:
            return
        res = self.scanner.diagnosticar_host_individual(eq_id, ejecutar_ping_real=True)
        self.refresh_all()
        messagebox.showinfo(
            f"Diagnóstico Real ICMP/ARP - {res['equipo']['codigo_logico']} ({res['equipo']['ip_address']})",
            f"{res['consola_diagnostico']}\n\nEstado: {res['estado_detectado']} | Detección: {res['tiempo_deteccion_seg']}s",
        )

    def _simular_seleccionado(self, modo: str) -> None:
        eq_id = self._get_selected_equipo_id()
        if not eq_id:
            return
        self.db.configurar_simulacion_equipo(eq_id, modo)
        res = self.scanner.diagnosticar_host_individual(eq_id, ejecutar_ping_real=True)
        self.refresh_all()
        if res["incidencia_generada"]:
            messagebox.showwarning(
                "¡Falla Detectada y Alerta Emitida!",
                f"Se detectó {res['estado_detectado']} en {res['equipo']['codigo_logico']} ({res['equipo']['ip_address']}).\n"
                f"Ticket automático generado: {res['incidencia_generada']['codigo_ticket']}",
            )

    def _cambiar_estado_inc_seleccionada(self, nuevo_estado: str) -> None:
        sel = self.tree_inc.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Seleccione una incidencia de la tabla.")
            return
        inc_id = int(self.tree_inc.item(sel[0], "values")[0])
        self.db.actualizar_estado_incidencia(
            incidencia_id=inc_id,
            nuevo_estado=nuevo_estado,
            responsable="Soporte Técnico TI (Consola Desktop)",
            solucion_o_comentario="Enlace de red verificado por PING/ARP en vivo y operatividad restaurada.",
        )
        self.refresh_all()

    def _run_real_discovery_async(self) -> None:
        def _job():
            res = self.scanner.descubrir_red_local_en_vivo()
            self.root.after(0, self.refresh_all)
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Descubrimiento de Red Real Completado",
                    f"Subred Escaneada: {res['subred_escaneada']} (Gateway: {res['gateway_ip']})\n"
                    f"Adaptador: {res['adaptador_activo']}\n"
                    f"Dispositivos Físicos Reales Activos: {res['total_hosts_reales_activos']}\n"
                    f"Tiempo de barrido (254 IPs): {res['duracion_descubrimiento_seg']} seg.",
                ),
            )

        threading.Thread(target=_job, daemon=True).start()

    def _export_csv_inc(self) -> None:
        fp = self.analytics.exportar_incidencias_csv("TODAS")
        messagebox.showinfo("Reporte Exportado", f"Archivo CSV guardado en:\n{fp}")

    def _export_csv_spss(self) -> None:
        fp = self.analytics.exportar_matriz_spss_jamovi_csv()
        messagebox.showinfo("Matriz SPSS/Jamovi Exportada", f"Matriz de 45 participantes guardada en:\n{fp}")

    def _export_html_exec(self) -> None:
        fp = self.analytics.exportar_reporte_ejecutivo_html()
        webbrowser.open(fp.as_uri())

    def run(self) -> None:
        self.root.mainloop()
