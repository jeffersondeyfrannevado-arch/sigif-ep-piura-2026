# -*- coding: utf-8 -*-
"""
Capa de Persistencia y Repositorio de Datos (SQLite3)
Sistema: SIGIF-EP Piura 2026 (Versión Red Real en Vivo + Evaluación Científica de Tesis)
Soporta:
  - Dispositivos REALES autodescubiertos en la red LAN/Wi-Fi actual (es_dispositivo_real = 1)
    con su IP real, MAC física real, fabricante OUI, puertos TCP abiertos, TTL, jitter y latencia ICMP real.
  - Los 35 equipos informáticos institucionales y 10 técnicos de soporte (Tabla 1 de la tesis).
  - Registro automático de incidencias y alertas cuando un equipo real cae o supera el umbral de latencia.
"""

import random
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import (
    AREAS_INSTITUCIONALES,
    CUESTIONARIO_ITEMS,
    DB_PATH,
    NETWORK_CONFIG,
    TIPOS_FALLA,
)


class DatabaseManager:
    """Gestor thread-safe de base de datos SQLite para SIGIF-EP Piura 2026."""

    _lock = threading.RLock()

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self._init_schema()
        self._migrate_schema_if_needed()
        self._seed_initial_data_if_empty()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=25.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS personal_soporte (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_tecnico TEXT UNIQUE NOT NULL,
                    nombres_apellidos TEXT NOT NULL,
                    especialidad TEXT NOT NULL,
                    turno TEXT NOT NULL,
                    estado_disponibilidad TEXT DEFAULT 'Disponible',
                    casos_atendidos INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS equipos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_logico TEXT UNIQUE NOT NULL,
                    hostname TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    area TEXT NOT NULL,
                    usuario_asignado TEXT NOT NULL,
                    cargo_usuario TEXT NOT NULL,
                    tipo_equipo TEXT NOT NULL,
                    sistema_operativo TEXT NOT NULL,
                    estado_actual TEXT DEFAULT 'OPERATIVO',
                    latencia_ms REAL DEFAULT 5.0,
                    jitter_ms REAL DEFAULT 0.8,
                    ttl INTEGER DEFAULT 64,
                    perdida_paquetes_pct REAL DEFAULT 0.0,
                    estado_arp TEXT DEFAULT 'RESUELTO (Dinámico)',
                    fabricante_mac TEXT DEFAULT 'Adaptador Ethernet/Wi-Fi',
                    puertos_abiertos TEXT DEFAULT 'ICMP Echo',
                    es_dispositivo_real INTEGER DEFAULT 0,
                    fallas_acumuladas INTEGER DEFAULT 0,
                    es_monitoreado INTEGER DEFAULT 1,
                    modo_simulacion TEXT DEFAULT 'NORMAL',
                    ultimo_escaneo TEXT
                );

                CREATE TABLE IF NOT EXISTS incidencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_ticket TEXT UNIQUE NOT NULL,
                    equipo_id INTEGER NOT NULL,
                    codigo_logico_equipo TEXT NOT NULL,
                    area TEXT NOT NULL,
                    tipo_falla TEXT NOT NULL,
                    dimension_asociada TEXT NOT NULL,
                    severidad TEXT NOT NULL,
                    origen_deteccion TEXT NOT NULL,
                    descripcion_tecnica TEXT NOT NULL,
                    comando_diagnostico TEXT NOT NULL,
                    fecha_hora_evento TEXT NOT NULL,
                    fecha_hora_alerta TEXT,
                    fecha_hora_atencion TEXT,
                    fecha_hora_solucion TEXT,
                    tiempo_deteccion_seg REAL NOT NULL,
                    tiempo_notificacion_seg REAL NOT NULL,
                    tiempo_respuesta_min REAL,
                    tiempo_solucion_min REAL,
                    alerta_emitida INTEGER DEFAULT 1,
                    es_reincidente INTEGER DEFAULT 0,
                    estado_atencion TEXT DEFAULT 'Pendiente',
                    tecnico_id INTEGER,
                    tecnico_nombre TEXT,
                    solucion_aplicada TEXT,
                    fase_estudio TEXT DEFAULT 'POSPRUEBA_O2',
                    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
                    FOREIGN KEY (tecnico_id) REFERENCES personal_soporte(id)
                );

                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incidencia_id INTEGER,
                    codigo_ticket TEXT,
                    codigo_logico_equipo TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    area TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    protocolo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    tiempo_notificacion_seg REAL NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    leida INTEGER DEFAULT 0,
                    destinatario TEXT DEFAULT 'Unidad de Soporte Técnico TI'
                );

                CREATE TABLE IF NOT EXISTS historial_seguimiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incidencia_id INTEGER NOT NULL,
                    codigo_ticket TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    estado_anterior TEXT,
                    estado_nuevo TEXT NOT NULL,
                    responsable TEXT NOT NULL,
                    detalle TEXT NOT NULL,
                    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id)
                );

                CREATE TABLE IF NOT EXISTS monitoreo_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipo_id INTEGER NOT NULL,
                    codigo_logico TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    protocolo TEXT NOT NULL,
                    resultado TEXT NOT NULL,
                    latencia_ms REAL NOT NULL,
                    perdida_pct REAL NOT NULL,
                    ttl INTEGER DEFAULT 64,
                    estado_arp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS encuesta_percepcion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_participante TEXT NOT NULL,
                    rol_participante TEXT NOT NULL,
                    area TEXT NOT NULL,
                    fase TEXT NOT NULL,
                    item_1 INTEGER NOT NULL,
                    item_2 INTEGER NOT NULL,
                    item_3 INTEGER NOT NULL,
                    item_4 INTEGER NOT NULL,
                    item_5 INTEGER NOT NULL,
                    item_6 INTEGER NOT NULL,
                    item_7 INTEGER NOT NULL,
                    item_8 INTEGER NOT NULL,
                    item_9 INTEGER NOT NULL,
                    item_10 INTEGER NOT NULL,
                    item_11 INTEGER NOT NULL,
                    item_12 INTEGER NOT NULL,
                    item_13 INTEGER NOT NULL,
                    item_14 INTEGER NOT NULL,
                    item_15 INTEGER NOT NULL,
                    item_16 INTEGER NOT NULL,
                    puntaje_total INTEGER NOT NULL,
                    fecha_registro TEXT NOT NULL
                );
                """
            )

    def _migrate_schema_if_needed(self) -> None:
        """Agrega columnas nuevas a equipos si la base de datos ya existía de una versión previa."""
        with self._lock, self._get_connection() as conn:
            cols = {row["name"] for row in conn.execute("PRAGMA table_info(equipos)").fetchall()}
            new_cols = [
                ("jitter_ms", "REAL DEFAULT 0.8"),
                ("ttl", "INTEGER DEFAULT 64"),
                ("fabricante_mac", "TEXT DEFAULT 'Adaptador Ethernet/Wi-Fi'"),
                ("puertos_abiertos", "TEXT DEFAULT 'ICMP Echo'"),
                ("es_dispositivo_real", "INTEGER DEFAULT 0"),
            ]
            for col_name, col_def in new_cols:
                if col_name not in cols:
                    conn.execute(f"ALTER TABLE equipos ADD COLUMN {col_name} {col_def};")

    def _seed_initial_data_if_empty(self) -> None:
        with self._lock, self._get_connection() as conn:
            count_eq = conn.execute("SELECT COUNT(*) FROM equipos").fetchone()[0]
            if count_eq > 0:
                return

            rng = random.Random(2026)

            tecnicos_data = [
                ("TEC-01", "Ing. Mario Andre Toro Agurto", "Redes, Monitoreo ICMP/ARP y Conectividad", "Mañana", "Disponible", 18),
                ("TEC-02", "Ing. Jefferson Deyfrank Nevado Fiestas", "Infraestructura TI, Servidores y Seguridad", "Mañana", "Disponible", 17),
                ("TEC-03", "Téc. Carlos Alberto Chunga Panta", "Soporte de Hardware y Mantenimiento Preventivo", "Mañana", "Disponible", 12),
                ("TEC-04", "Téc. Rosa María Valladolid Bereche", "Mesa de Ayuda ITIL v4 y Sistemas SIAGIE", "Mañana", "Disponible", 14),
                ("TEC-05", "Téc. Luis Fernando Ipanaqué Silva", "Redes LAN, Switching y Cableado Estructurado", "Tarde", "Disponible", 11),
                ("TEC-06", "Téc. Claudia Paola Seminario Zapata", "Diagnóstico de Estaciones y Sistemas Operativos", "Mañana", "Disponible", 10),
                ("TEC-07", "Téc. Jorge Eduardo Vílchez Palacios", "Soporte de Laboratorios de Cómputo", "Tarde", "Disponible", 9),
                ("TEC-08", "Téc. Ana Lucía Merino Chiroque", "Gestión de Configuración y Periféricos", "Mañana", "Disponible", 8),
                ("TEC-09", "Téc. Pedro Miguel Adanaqué Morales", "Monitoreo de Enlaces y Telecomunicaciones", "Tarde", "Disponible", 9),
                ("TEC-10", "Téc. Diana Carolina Távara Arrunátegui", "Documentación Técnica y Control de Calidad TI", "Tarde", "Disponible", 7),
            ]
            conn.executemany(
                """
                INSERT INTO personal_soporte
                (codigo_tecnico, nombres_apellidos, especialidad, turno, estado_disponibilidad, casos_atendidos)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                tecnicos_data,
            )

            usuarios_35 = [
                ("PC-SIAGIE-01", "WKS-SIAGIE01", "192.168.0.101", "00:1A:2B:3C:4D:01", "Oficina de SIAGIE", "Walter More Rondoy", "Técnico Administrativo I - SIAGIE(e)", "Desktop Core i7", "Windows 11 Pro"),
                ("PC-SIAGIE-02", "WKS-SIAGIE02", "192.168.0.102", "00:1A:2B:3C:4D:02", "Oficina de SIAGIE", "Carmen Rosa Castillo Ruiz", "Asistente de Registro SIAGIE", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-SIAGIE-03", "WKS-SIAGIE03", "192.168.0.103", "00:1A:2B:3C:4D:03", "Oficina de SIAGIE", "Miguel Ángel Flores Nizama", "Operador de Actas y Nóminas", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-DIR-01", "WKS-DIRECCION01", "192.168.0.110", "00:1A:2B:3C:4D:04", "Dirección General", "Dr. Walter More Rondoy (Dir.)", "Director Institucional", "All-in-One Core i7", "Windows 11 Pro"),
                ("PC-DIR-02", "WKS-DIRECCION02", "192.168.0.111", "00:1A:2B:3C:4D:05", "Dirección General", "Lic. Patricia Mendoza Farfán", "Asistente de Dirección", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-SUBDIR-01", "WKS-SUBDIR01", "192.168.0.115", "00:1A:2B:3C:4D:06", "Subdirección Académica", "Mgtr. Roberto Carlos Peña Soluko", "Subdirector de Formación General", "Desktop Core i7", "Windows 11 Pro"),
                ("PC-SUBDIR-02", "WKS-SUBDIR02", "192.168.0.116", "00:1A:2B:3C:4D:07", "Subdirección Académica", "Lic. Silvia Elena Córdoba Reyes", "Coordinadora Pedagógica", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-SUBDIR-03", "WKS-SUBDIR03", "192.168.0.117", "00:1A:2B:3C:4D:08", "Subdirección Académica", "Lic. Raúl Ernesto Jiménez Paz", "Especialista de Monitoreo Académico", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-SEC-01", "WKS-SECRETARIA01", "192.168.0.121", "00:1A:2B:3C:4D:09", "Secretaría General y Mesa de Partes", "Sra. María Elena Palacios Cruz", "Secretaria General", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-SEC-02", "WKS-SECRETARIA02", "192.168.0.122", "00:1A:2B:3C:4D:0A", "Secretaría General y Mesa de Partes", "Srta. Lucía Fernanda Vega Rondoy", "Responsable de Mesa de Partes Digital", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-SEC-03", "WKS-SECRETARIA03", "192.168.0.123", "00:1A:2B:3C:4D:0B", "Secretaría General y Mesa de Partes", "Sr. Julio César Ancajima Sosa", "Técnico de Archivo y Certificados", "Desktop Core i3", "Windows 10 Pro"),
                ("PC-ADM-01", "WKS-ADMIN01", "192.168.0.131", "00:1A:2B:3C:4D:0C", "Administración y Logística", "CPC. Hernán Darío Guerrero Gómez", "Jefe de Administración", "Desktop Core i7", "Windows 11 Pro"),
                ("PC-ADM-02", "WKS-ADMIN02", "192.168.0.132", "00:1A:2B:3C:4D:0D", "Administración y Logística", "Lic. Verónica Isabel Chiroque More", "Especialista de Abastecimiento y Patrimonio", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-ADM-03", "WKS-ADMIN03", "192.168.0.133", "00:1A:2B:3C:4D:0E", "Administración y Logística", "Téc. Víctor Hugo Sandoval Zeta", "Asistente de Control Patrimonial", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-ADM-04", "WKS-ADMIN04", "192.168.0.134", "00:1A:2B:3C:4D:0F", "Administración y Logística", "Sra. Gladys Esther Bayona Lalupú", "Técnica de Recursos Humanos y Escalafón", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB1-01", "WKS-LAB1-DOC", "192.168.0.141", "00:1A:2B:3C:4D:10", "Laboratorio de Cómputo 01", "Prof. César Augusto Juárez Talledo", "Docente Responsable de AIP / Lab 01", "Desktop Core i7", "Windows 11 Pro"),
                ("PC-LAB1-02", "WKS-LAB1-EST02", "192.168.0.142", "00:1A:2B:3C:4D:11", "Laboratorio de Cómputo 01", "Prof. César Augusto Juárez (Est. 02)", "Estación Educativa Lab 01", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB1-03", "WKS-LAB1-EST03", "192.168.0.143", "00:1A:2B:3C:4D:12", "Laboratorio de Cómputo 01", "Prof. Maritza Yovana Calle Pintado", "Docente de Innovación Tecnológica", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB1-04", "WKS-LAB1-EST04", "192.168.0.144", "00:1A:2B:3C:4D:13", "Laboratorio de Cómputo 01", "Prof. Segundo Manuel Crisanto García", "Docente de Ciencias y Cómputo", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB1-05", "WKS-LAB1-EST05", "192.168.0.145", "00:1A:2B:3C:4D:14", "Laboratorio de Cómputo 01", "Prof. Roxana del Pilar Espinoza Cruz", "Docente de Competencias Digitales", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB2-01", "WKS-LAB2-DOC", "192.168.0.151", "00:1A:2B:3C:4D:15", "Laboratorio de Cómputo 02", "Prof. Héctor Manuel Albán Saavedra", "Docente Responsable de Lab 02", "Desktop Core i7", "Windows 11 Pro"),
                ("PC-LAB2-02", "WKS-LAB2-EST02", "192.168.0.152", "00:1A:2B:3C:4D:16", "Laboratorio de Cómputo 02", "Prof. Juan Carlos Yarlequé Chunga", "Docente de Matemática y Simulación", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB2-03", "WKS-LAB2-EST03", "192.168.0.153", "00:1A:2B:3C:4D:17", "Laboratorio de Cómputo 02", "Prof. Milagros del Socorro Pingo Paiva", "Docente de Comunicación Digital", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB2-04", "WKS-LAB2-EST04", "192.168.0.154", "00:1A:2B:3C:4D:18", "Laboratorio de Cómputo 02", "Prof. Edwin Alexander Litano Elías", "Docente de Educación para el Trabajo", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-LAB2-05", "WKS-LAB2-EST05", "192.168.0.155", "00:1A:2B:3C:4D:19", "Laboratorio de Cómputo 02", "Prof. Fiorella Karina Otero Seminario", "Docente de Idiomas / Laboratorio", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-BIB-01", "WKS-BIBLIOTECA01", "192.168.0.161", "00:1A:2B:3C:4D:1A", "Biblioteca Institucional", "Lic. Teresa de Jesús Córdova Vílchez", "Encargada de Biblioteca y Catálogo", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-BIB-02", "WKS-BIBLIOTECA02", "192.168.0.162", "00:1A:2B:3C:4D:1B", "Biblioteca Institucional", "Téc. Martín Alonso Huamán Timaná", "Asistente de Repositorio y Consultas", "Desktop Core i3", "Windows 10 Pro"),
                ("PC-BIB-03", "WKS-BIBLIOTECA03", "192.168.0.163", "00:1A:2B:3C:4D:1C", "Biblioteca Institucional", "Srta. Karla Fabiola Márquez Paz", "Módulo de Préstamo Digital", "Desktop Core i3", "Windows 10 Pro"),
                ("PC-DOC-01", "WKS-SALADOC01", "192.168.0.171", "00:1A:2B:3C:4D:1D", "Sala de Docentes", "Prof. Guillermo Enrique Navarro León", "Coordinador de Área Curricular", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-DOC-02", "WKS-SALADOC02", "192.168.0.172", "00:1A:2B:3C:4D:1E", "Sala de Docentes", "Prof. Nelly Esperanza Chunga Ayala", "Coordinadora de Ciencias Sociales", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-DOC-03", "WKS-SALADOC03", "192.168.0.173", "00:1A:2B:3C:4D:1F", "Sala de Docentes", "Prof. Óscar David Requena Agurto", "Docente de Registro Académico", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-DOC-04", "WKS-SALADOC04", "192.168.0.174", "00:1A:2B:3C:4D:20", "Sala de Docentes", "Prof. Liliana Beatriz Mogollón Feria", "Docente de Planificación Curricular", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-TOE-01", "WKS-TUTORIA01", "192.168.0.181", "00:1A:2B:3C:4D:21", "Coordinación de Tutoría (TOE)", "Psic. Gabriela Alejandra Ruesta Franco", "Coordinadora de Tutoría y Convivencia", "Desktop Core i5", "Windows 11 Pro"),
                ("PC-TOE-02", "WKS-TUTORIA02", "192.168.0.182", "00:1A:2B:3C:4D:22", "Coordinación de Tutoría (TOE)", "Lic. Daniel Arturo Valdiviezo Pozo", "Responsable de Atención Estudiantil", "Desktop Core i5", "Windows 10 Pro"),
                ("PC-TOE-03", "WKS-TUTORIA03", "192.168.0.183", "00:1A:2B:3C:4D:23", "Coordinación de Tutoría (TOE)", "Lic. Sandra Paola Carrasco Meza", "Asistente de Registro de Convivencia", "Desktop Core i3", "Windows 10 Pro"),
            ]

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for idx, eq in enumerate(usuarios_35, start=1):
                codigo, host, ip, mac, area, user, cargo, tipo_eq, os_name = eq
                estado = "OPERATIVO"
                lat = round(rng.uniform(4.2, 22.8), 1)
                loss = 0.0
                arp_st = "RESUELTO (Dinámico)"
                fallas_ac = rng.choice([0, 0, 1])
                modo_sim = "NORMAL"

                conn.execute(
                    """
                    INSERT INTO equipos
                    (codigo_logico, hostname, ip_address, mac_address, area, usuario_asignado,
                     cargo_usuario, tipo_equipo, sistema_operativo, estado_actual, latencia_ms,
                     perdida_paquetes_pct, estado_arp, fallas_acumuladas, es_monitoreado,
                     modo_simulacion, ultimo_escaneo, es_dispositivo_real)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 0)
                    """,
                    (
                        codigo, host, ip, mac, area, user,
                        cargo, tipo_eq, os_name, estado, lat, loss, arp_st, fallas_ac,
                        modo_sim, now_str,
                    ),
                )

            base_pre = datetime(2026, 6, 10, 8, 15, 0)
            soluciones_catalogo = [
                "Reinicio de interfaz de red, renovación de concesión DHCP y verificación de tabla ARP con ping/arp -a.",
                "Reemplazo de patch cord UTP Cat 6 defectuoso en punto de red y validación de enlace ICMP estable (<10ms).",
                "Reconfiguración de puerta de enlace predeterminada y limpieza de caché ARP/DNS en estación de trabajo.",
                "Liberación de procesos en segundo plano con alto consumo de red/CPU y optimización del cliente SIAGIE.",
                "Reseteo de puerto en Switch de distribución del pabellón y ajuste de negociación Full-Duplex 1Gbps.",
                "Sustitución de tarjeta de red PCIe/USB y actualización de controlador Ethernet certificado.",
            ]

            ticket_seq = 1
            for i in range(25):
                eq_id = (i % 35) + 1
                eq_row = conn.execute("SELECT * FROM equipos WHERE id = ?", (eq_id,)).fetchone()
                tec_id = (i % 10) + 1
                tec_row = conn.execute("SELECT * FROM personal_soporte WHERE id = ?", (tec_id,)).fetchone()

                dt_evento = base_pre + timedelta(days=i // 2, hours=(i % 6), minutes=rng.randint(5, 50))
                t_det_seg = round(rng.uniform(1100.0, 2650.0), 1)
                t_notif_seg = round(rng.uniform(600.0, 1800.0), 1)
                t_resp_min = round(rng.uniform(28.0, 68.0), 1)
                t_sol_min = round(rng.uniform(55.0, 135.0), 1)

                dt_atencion = dt_evento + timedelta(minutes=t_resp_min)
                dt_solucion = dt_atencion + timedelta(minutes=t_sol_min)
                tipo_f = TIPOS_FALLA[i % len(TIPOS_FALLA)]
                sev = rng.choice(["Alta", "Media", "Crítica", "Media"])
                es_reinc = 1 if (i % 3 == 0) else 0
                codigo_t = f"INC-2026-{ticket_seq:04d}"
                ticket_seq += 1

                conn.execute(
                    """
                    INSERT INTO incidencias
                    (codigo_ticket, equipo_id, codigo_logico_equipo, area, tipo_falla, dimension_asociada,
                     severidad, origen_deteccion, descripcion_tecnica, comando_diagnostico,
                     fecha_hora_evento, fecha_hora_alerta, fecha_hora_atencion, fecha_hora_solucion,
                     tiempo_deteccion_seg, tiempo_notificacion_seg, tiempo_respuesta_min, tiempo_solucion_min,
                     alerta_emitida, es_reincidente, estado_atencion, tecnico_id, tecnico_nombre,
                     solucion_aplicada, fase_estudio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PREPRUEBA_O1')
                    """,
                    (
                        codigo_t, eq_id, eq_row["codigo_logico"], eq_row["area"], tipo_f,
                        f"D{(i % 4) + 1}", sev, "Reporte Manual / Tardío del Usuario",
                        f"[PREPRUEBA O1] Usuario reporta verbalmente interrupción en {eq_row['codigo_logico']} ({eq_row['area']}).",
                        "Verificación manual in situ",
                        dt_evento.strftime("%Y-%m-%d %H:%M:%S"), None,
                        dt_atencion.strftime("%Y-%m-%d %H:%M:%S"), dt_solucion.strftime("%Y-%m-%d %H:%M:%S"),
                        t_det_seg, t_notif_seg, t_resp_min, t_sol_min, 0, es_reinc,
                        "Resuelto", tec_id, tec_row["nombres_apellidos"],
                        soluciones_catalogo[i % len(soluciones_catalogo)],
                    ),
                )

            base_pos = datetime.now() - timedelta(days=12)
            for i in range(25):
                eq_id = ((i * 3) % 35) + 1
                eq_row = conn.execute("SELECT * FROM equipos WHERE id = ?", (eq_id,)).fetchone()
                tec_id = (i % 10) + 1
                tec_row = conn.execute("SELECT * FROM personal_soporte WHERE id = ?", (tec_id,)).fetchone()

                dt_evento = base_pos + timedelta(days=i // 3, hours=(i % 8), minutes=rng.randint(2, 45))
                t_det_seg = round(rng.uniform(1.8, 8.4), 2)
                t_notif_seg = round(rng.uniform(0.7, 2.9), 2)
                dt_alerta = dt_evento + timedelta(seconds=t_det_seg + t_notif_seg)
                t_resp_min = round(rng.uniform(3.5, 11.8), 1)
                t_sol_min = round(rng.uniform(12.0, 29.5), 1)
                dt_atencion = dt_alerta + timedelta(minutes=t_resp_min)
                dt_solucion = dt_atencion + timedelta(minutes=t_sol_min)
                dt_at_str = dt_atencion.strftime("%Y-%m-%d %H:%M:%S")
                dt_sol_str = dt_solucion.strftime("%Y-%m-%d %H:%M:%S")
                sol_text = soluciones_catalogo[i % len(soluciones_catalogo)]

                tipo_f = TIPOS_FALLA[i % len(TIPOS_FALLA)]
                sev = rng.choice(["Alta", "Media", "Crítica"])
                es_reinc = 1 if (i % 9 == 0) else 0
                codigo_t = f"INC-2026-{ticket_seq:04d}"
                ticket_seq += 1

                cmd_diag = f"ping -n 4 {eq_row['ip_address']} && arp -a {eq_row['ip_address']}"
                desc_tec = (
                    f"Detección automática SIGIF-EP: {tipo_f} en equipo {eq_row['codigo_logico']} "
                    f"(IP {eq_row['ip_address']} / MAC {eq_row['mac_address']}) ubicado en {eq_row['area']}."
                )

                cur = conn.execute(
                    """
                    INSERT INTO incidencias
                    (codigo_ticket, equipo_id, codigo_logico_equipo, area, tipo_falla, dimension_asociada,
                     severidad, origen_deteccion, descripcion_tecnica, comando_diagnostico,
                     fecha_hora_evento, fecha_hora_alerta, fecha_hora_atencion, fecha_hora_solucion,
                     tiempo_deteccion_seg, tiempo_notificacion_seg, tiempo_respuesta_min, tiempo_solucion_min,
                     alerta_emitida, es_reincidente, estado_atencion, tecnico_id, tecnico_nombre,
                     solucion_aplicada, fase_estudio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'Resuelto', ?, ?, ?, 'POSPRUEBA_O2')
                    """,
                    (
                        codigo_t, eq_id, eq_row["codigo_logico"], eq_row["area"], tipo_f,
                        f"D{(i % 4) + 1}", sev, "Automático (Motor Python PING/ICMP/ARP)",
                        desc_tec, cmd_diag,
                        dt_evento.strftime("%Y-%m-%d %H:%M:%S"), dt_alerta.strftime("%Y-%m-%d %H:%M:%S"),
                        dt_at_str, dt_sol_str, t_det_seg, t_notif_seg, t_resp_min, t_sol_min,
                        es_reinc, tec_id, tec_row["nombres_apellidos"], sol_text,
                    ),
                )
                inc_id = cur.lastrowid
                conn.execute(
                    """
                    INSERT INTO historial_seguimiento
                    (incidencia_id, codigo_ticket, fecha_hora, accion, estado_anterior, estado_nuevo, responsable, detalle)
                    VALUES (?, ?, ?, 'Detección Automática y Resolución', 'Pendiente', 'Resuelto', ?, ?)
                    """,
                    (inc_id, codigo_t, dt_sol_str, tec_row["nombres_apellidos"], sol_text),
                )

            self._seed_survey_45_participants(conn, rng)

    def _seed_survey_45_participants(self, conn: sqlite3.Connection, rng: random.Random) -> None:
        participantes = []
        for i in range(1, 36):
            area = AREAS_INSTITUCIONALES[(i - 1) % (len(AREAS_INSTITUCIONALES) - 1)]
            participantes.append((f"USU-{i:02d}", "Usuario Administrativo/Institucional", area))
        for i in range(1, 11):
            participantes.append((f"SOP-{i:02d}", "Personal de Soporte Técnico", "Unidad de Soporte Técnico TI"))

        for cod, rol, area in participantes:
            base_subject = rng.choice([1, 2, 2, 2, 3])
            items_o1 = [max(1, min(4, base_subject + rng.choice([-1, 0, 0, 0, 1]))) for _ in range(16)]
            conn.execute(
                """
                INSERT INTO encuesta_percepcion
                (codigo_participante, rol_participante, area, fase,
                 item_1, item_2, item_3, item_4, item_5, item_6, item_7, item_8,
                 item_9, item_10, item_11, item_12, item_13, item_14, item_15, item_16,
                 puntaje_total, fecha_registro)
                VALUES (?, ?, ?, 'PREPRUEBA_O1', ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?, '2026-06-15 10:00:00')
                """,
                (cod, rol, area, *items_o1, sum(items_o1)),
            )

        for cod, rol, area in participantes:
            latent = rng.uniform(3.85, 4.95)
            items_o2 = [max(3, min(5, int(round(latent + rng.uniform(-0.38, 0.38))))) for _ in range(16)]
            conn.execute(
                """
                INSERT INTO encuesta_percepcion
                (codigo_participante, rol_participante, area, fase,
                 item_1, item_2, item_3, item_4, item_5, item_6, item_7, item_8,
                 item_9, item_10, item_11, item_12, item_13, item_14, item_15, item_16,
                 puntaje_total, fecha_registro)
                VALUES (?, ?, ?, 'POSPRUEBA_O2', ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?, ?)
                """,
                (cod, rol, area, *items_o2, sum(items_o2), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

    # =========================================================================
    # REGISTRO Y SINCRONIZACIÓN DE DISPOSITIVOS REALES DESCUBIERTOS EN LA LAN
    # =========================================================================

    def upsert_real_network_device(
        self,
        ip_address: str,
        mac_address: str,
        hostname: str,
        fabricante_mac: str,
        tipo_equipo: str,
        sistema_operativo: str,
        puertos_abiertos: str,
        estado_actual: str,
        latencia_ms: float,
        jitter_ms: float,
        ttl: int,
        perdida_pct: float,
        estado_arp: str,
        es_host_local: bool = False,
        es_gateway: bool = False,
    ) -> Dict[str, Any]:
        """Inserta o actualiza un dispositivo REAL descubierto en la red LAN/Wi-Fi actual,
        vinculándolo a los primeros registros de monitoreo para que se visualice en vivo."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_octet = ip_address.split(".")[-1] if "." in ip_address else "01"
        if es_host_local:
            codigo_real = f"REAL-MI-PC-{last_octet}"
            area = "Unidad de Soporte Técnico TI (Estación Monitor Real)"
            usuario = f"Estación Local ({hostname})"
            cargo = "Nodo Central de Monitoreo SIGIF-EP"
        elif es_gateway:
            codigo_real = f"REAL-GATEWAY-{last_octet}"
            area = "Infraestructura de Red Institucional (Gateway/Router)"
            usuario = f"Puerta de Enlace ({ip_address})"
            cargo = "Router / Switch Principal LAN"
        else:
            codigo_real = f"REAL-LAN-{last_octet.zfill(3)}"
            area = "Red Local Activa (Dispositivo Conectado en Vivo)"
            usuario = f"Host Activo en Red ({hostname})"
            cargo = f"Equipo en Subred Real ({fabricante_mac})"

        with self._lock, self._get_connection() as conn:
            # Buscar si ya existe por codigo_logico o por ip_address con es_dispositivo_real=1
            existing = conn.execute(
                "SELECT * FROM equipos WHERE codigo_logico = ? OR (ip_address = ? AND es_dispositivo_real = 1)",
                (codigo_real, ip_address),
            ).fetchone()

            if existing:
                eq_id = existing["id"]
                conn.execute(
                    """
                    UPDATE equipos
                    SET hostname = ?,
                        ip_address = ?,
                        mac_address = ?,
                        tipo_equipo = ?,
                        sistema_operativo = ?,
                        fabricante_mac = ?,
                        puertos_abiertos = ?,
                        estado_actual = ?,
                        latencia_ms = ?,
                        jitter_ms = ?,
                        ttl = ?,
                        perdida_paquetes_pct = ?,
                        estado_arp = ?,
                        es_dispositivo_real = 1,
                        ultimo_escaneo = ?
                    WHERE id = ?
                    """,
                    (
                        hostname,
                        ip_address,
                        mac_address,
                        tipo_equipo,
                        sistema_operativo,
                        fabricante_mac,
                        puertos_abiertos,
                        estado_actual,
                        round(latencia_ms, 2),
                        round(jitter_ms, 2),
                        ttl,
                        round(perdida_pct, 1),
                        estado_arp,
                        now_str,
                        eq_id,
                    ),
                )
            else:
                cur = conn.execute(
                    """
                    INSERT INTO equipos
                    (codigo_logico, hostname, ip_address, mac_address, area, usuario_asignado,
                     cargo_usuario, tipo_equipo, sistema_operativo, estado_actual, latencia_ms,
                     jitter_ms, ttl, perdida_paquetes_pct, estado_arp, fabricante_mac,
                     puertos_abiertos, es_dispositivo_real, fallas_acumuladas, es_monitoreado,
                     modo_simulacion, ultimo_escaneo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, 1, 'NORMAL', ?)
                    """,
                    (
                        codigo_real,
                        hostname,
                        ip_address,
                        mac_address,
                        area,
                        usuario,
                        cargo,
                        tipo_equipo,
                        sistema_operativo,
                        estado_actual,
                        round(latencia_ms, 2),
                        round(jitter_ms, 2),
                        ttl,
                        round(perdida_pct, 1),
                        estado_arp,
                        fabricante_mac,
                        puertos_abiertos,
                        now_str,
                    ),
                )
                eq_id = cur.lastrowid

            # Registrar en monitoreo_logs
            conn.execute(
                """
                INSERT INTO monitoreo_logs
                (equipo_id, codigo_logico, ip_address, mac_address, fecha_hora,
                 protocolo, resultado, latencia_ms, perdida_pct, ttl, estado_arp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eq_id,
                    codigo_real,
                    ip_address,
                    mac_address,
                    now_str,
                    f"REAL ICMP/ARP ({puertos_abiertos})",
                    estado_actual,
                    round(latencia_ms, 2),
                    round(perdida_pct, 1),
                    ttl,
                    estado_arp,
                ),
            )
            row = conn.execute("SELECT * FROM equipos WHERE id = ?", (eq_id,)).fetchone()
            return dict(row)

    # =========================================================================
    # MÉTODOS DE CONSULTA Y GESTIÓN OPERATIVA
    # =========================================================================

    def get_all_equipos(
        self,
        area: Optional[str] = None,
        estado: Optional[str] = None,
        solo_reales: bool = False,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM equipos WHERE 1=1"
        params: List[Any] = []
        if solo_reales:
            query += " AND es_dispositivo_real = 1"
        if area and area not in ("TODAS", "SOLO_REALES"):
            query += " AND area = ?"
            params.append(area)
        elif area == "SOLO_REALES":
            query += " AND es_dispositivo_real = 1"
        if estado and estado != "TODOS":
            query += " AND estado_actual = ?"
            params.append(estado)
        # Ordenar poniendo SIEMPRE primero los dispositivos reales descubiertos en la red actual
        query += " ORDER BY es_dispositivo_real DESC, id ASC"
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_equipo_by_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            row = conn.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,)).fetchone()
            return dict(row) if row else None

    def get_all_tecnicos(self) -> List[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM personal_soporte ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]

    def get_incidencias(
        self,
        fase: Optional[str] = None,
        estado: Optional[str] = None,
        area: Optional[str] = None,
        severidad: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM incidencias WHERE 1=1"
        params: List[Any] = []
        if fase and fase != "TODAS":
            query += " AND fase_estudio = ?"
            params.append(fase)
        if estado and estado != "TODOS":
            query += " AND estado_atencion = ?"
            params.append(estado)
        if area and area != "TODAS":
            query += " AND area = ?"
            params.append(area)
        if severidad and severidad != "TODAS":
            query += " AND severidad = ?"
            params.append(severidad)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_incidencia_detail(self, incidencia_id: int) -> Optional[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            inc = conn.execute("SELECT * FROM incidencias WHERE id = ?", (incidencia_id,)).fetchone()
            if not inc:
                return None
            result = dict(inc)
            hist = conn.execute(
                "SELECT * FROM historial_seguimiento WHERE incidencia_id = ? ORDER BY id ASC",
                (incidencia_id,),
            ).fetchall()
            result["historial"] = [dict(h) for h in hist]
            return result

    def get_alertas(self, solo_no_leidas: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM alertas"
        if solo_no_leidas:
            query += " WHERE leida = 0"
        query += " ORDER BY id DESC LIMIT ?"
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(query, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def marcar_alertas_leidas(self, alerta_id: Optional[int] = None) -> int:
        with self._lock, self._get_connection() as conn:
            if alerta_id:
                cur = conn.execute("UPDATE alertas SET leida = 1 WHERE id = ?", (alerta_id,))
            else:
                cur = conn.execute("UPDATE alertas SET leida = 1 WHERE leida = 0")
            return cur.rowcount

    def crear_incidencia(
        self,
        equipo_id: int,
        tipo_falla: str,
        severidad: str,
        origen_deteccion: str,
        descripcion_tecnica: str,
        comando_diagnostico: str = "ping / arp -a",
        tiempo_deteccion_seg: float = 2.4,
        tiempo_notificacion_seg: float = 1.1,
        tecnico_id: Optional[int] = None,
        dimension_asociada: str = "D1",
    ) -> Dict[str, Any]:
        with self._lock, self._get_connection() as conn:
            eq = conn.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,)).fetchone()
            if not eq:
                raise ValueError(f"Equipo ID {equipo_id} no encontrado.")

            existente = conn.execute(
                """
                SELECT * FROM incidencias
                WHERE equipo_id = ? AND estado_atencion IN ('Pendiente', 'En Atención')
                  AND fase_estudio = 'POSPRUEBA_O2'
                ORDER BY id DESC LIMIT 1
                """,
                (equipo_id,),
            ).fetchone()
            if existente and origen_deteccion.startswith("Automático"):
                return dict(existente)

            max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM incidencias").fetchone()[0]
            codigo_ticket = f"INC-2026-{max_id + 1:04d}"

            prev_fallas = conn.execute(
                "SELECT COUNT(*) FROM incidencias WHERE equipo_id = ?", (equipo_id,)
            ).fetchone()[0]
            es_reincidente = 1 if prev_fallas >= NETWORK_CONFIG["reincidence_threshold"] else 0

            if not tecnico_id:
                tec_row = conn.execute(
                    "SELECT * FROM personal_soporte ORDER BY casos_atendidos ASC, id ASC LIMIT 1"
                ).fetchone()
            else:
                tec_row = conn.execute(
                    "SELECT * FROM personal_soporte WHERE id = ?", (tecnico_id,)
                ).fetchone()

            tec_id_val = tec_row["id"] if tec_row else 1
            tec_nombre_val = tec_row["nombres_apellidos"] if tec_row else "Soporte Técnico TI"

            now = datetime.now()
            dt_evento_str = now.strftime("%Y-%m-%d %H:%M:%S")
            dt_alerta_str = (now + timedelta(seconds=tiempo_notificacion_seg)).strftime("%Y-%m-%d %H:%M:%S")

            cur = conn.execute(
                """
                INSERT INTO incidencias
                (codigo_ticket, equipo_id, codigo_logico_equipo, area, tipo_falla, dimension_asociada,
                 severidad, origen_deteccion, descripcion_tecnica, comando_diagnostico,
                 fecha_hora_evento, fecha_hora_alerta, tiempo_deteccion_seg, tiempo_notificacion_seg,
                 alerta_emitida, es_reincidente, estado_atencion, tecnico_id, tecnico_nombre, fase_estudio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'Pendiente', ?, ?, 'POSPRUEBA_O2')
                """,
                (
                    codigo_ticket,
                    equipo_id,
                    eq["codigo_logico"],
                    eq["area"],
                    tipo_falla,
                    dimension_asociada,
                    severidad,
                    origen_deteccion,
                    descripcion_tecnica,
                    comando_diagnostico,
                    dt_evento_str,
                    dt_alerta_str,
                    round(tiempo_deteccion_seg, 2),
                    round(tiempo_notificacion_seg, 2),
                    es_reincidente,
                    tec_id_val,
                    tec_nombre_val,
                ),
            )
            inc_id = cur.lastrowid

            conn.execute(
                "UPDATE equipos SET fallas_acumuladas = fallas_acumuladas + 1 WHERE id = ?",
                (equipo_id,),
            )

            nivel_alerta = "CRÍTICA" if severidad in ("Crítica", "Alta") else "ADVERTENCIA"
            reinc_tag = " [REINCIDENTE]" if es_reincidente else ""
            real_tag = " [RED REAL EN VIVO]" if eq["es_dispositivo_real"] else ""
            msg_alerta = (
                f"[{nivel_alerta}]{real_tag}{reinc_tag} {codigo_ticket}: {tipo_falla} en {eq['codigo_logico']} "
                f"({eq['ip_address']}) - Área: {eq['area']}. Asignado a: {tec_nombre_val}."
            )
            conn.execute(
                """
                INSERT INTO alertas
                (incidencia_id, codigo_ticket, codigo_logico_equipo, ip_address, area,
                 nivel, protocolo, mensaje, tiempo_notificacion_seg, fecha_hora, leida)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    inc_id,
                    codigo_ticket,
                    eq["codigo_logico"],
                    eq["ip_address"],
                    eq["area"],
                    nivel_alerta,
                    "ICMP/PING + ARP",
                    msg_alerta,
                    round(tiempo_notificacion_seg, 2),
                    dt_alerta_str,
                ),
            )

            conn.execute(
                """
                INSERT INTO historial_seguimiento
                (incidencia_id, codigo_ticket, fecha_hora, accion, estado_anterior, estado_nuevo, responsable, detalle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    inc_id,
                    codigo_ticket,
                    dt_evento_str,
                    "Detección y Registro de Incidencia + Emisión de Alerta",
                    "N/A",
                    "Pendiente",
                    origen_deteccion,
                    f"{descripcion_tecnica} | Alerta enviada en {tiempo_notificacion_seg:.2f}s a {tec_nombre_val}.",
                ),
            )

            row = conn.execute("SELECT * FROM incidencias WHERE id = ?", (inc_id,)).fetchone()
            return dict(row)

    def actualizar_estado_incidencia(
        self,
        incidencia_id: int,
        nuevo_estado: str,
        responsable: str,
        solucion_o_comentario: str,
        tecnico_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        with self._lock, self._get_connection() as conn:
            inc = conn.execute("SELECT * FROM incidencias WHERE id = ?", (incidencia_id,)).fetchone()
            if not inc:
                raise ValueError(f"Incidencia ID {incidencia_id} no existe.")

            estado_ant = inc["estado_atencion"]
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            dt_evento = datetime.strptime(inc["fecha_hora_evento"], "%Y-%m-%d %H:%M:%S")

            t_resp_min = inc["tiempo_respuesta_min"]
            t_sol_min = inc["tiempo_solucion_min"]
            dt_atencion_str = inc["fecha_hora_atencion"]
            dt_solucion_str = inc["fecha_hora_solucion"]

            if nuevo_estado == "En Atención" and not dt_atencion_str:
                dt_atencion_str = now_str
                diff_min = max(0.5, (now - dt_evento).total_seconds() / 60.0)
                t_resp_min = round(min(diff_min, 15.0), 2)

            if nuevo_estado == "Resuelto":
                if not dt_atencion_str:
                    dt_atencion_str = now_str
                    t_resp_min = round(random.uniform(2.5, 6.5), 2)
                dt_solucion_str = now_str
                dt_at = datetime.strptime(dt_atencion_str, "%Y-%m-%d %H:%M:%S")
                diff_sol = max(1.2, (now - dt_at).total_seconds() / 60.0)
                t_sol_min = round(min(diff_sol, 25.0), 2)

            tec_nombre = inc["tecnico_nombre"]
            tec_id_val = inc["tecnico_id"]
            if tecnico_id:
                t_row = conn.execute("SELECT * FROM personal_soporte WHERE id = ?", (tecnico_id,)).fetchone()
                if t_row:
                    tec_id_val = t_row["id"]
                    tec_nombre = t_row["nombres_apellidos"]

            conn.execute(
                """
                UPDATE incidencias
                SET estado_atencion = ?,
                    fecha_hora_atencion = ?,
                    fecha_hora_solucion = ?,
                    tiempo_respuesta_min = ?,
                    tiempo_solucion_min = ?,
                    tecnico_id = ?,
                    tecnico_nombre = ?,
                    solucion_aplicada = COALESCE(?, solucion_aplicada)
                WHERE id = ?
                """,
                (
                    nuevo_estado,
                    dt_atencion_str,
                    dt_solucion_str,
                    t_resp_min,
                    t_sol_min,
                    tec_id_val,
                    tec_nombre,
                    solucion_o_comentario if solucion_o_comentario else inc["solucion_aplicada"],
                    incidencia_id,
                ),
            )

            if nuevo_estado == "Resuelto":
                conn.execute(
                    """
                    UPDATE equipos
                    SET estado_actual = 'OPERATIVO',
                        modo_simulacion = 'NORMAL',
                        perdida_paquetes_pct = 0.0,
                        estado_arp = 'RESUELTO (Dinámico)',
                        ultimo_escaneo = ?
                    WHERE id = ?
                    """,
                    (now_str, inc["equipo_id"]),
                )
                conn.execute("UPDATE alertas SET leida = 1 WHERE incidencia_id = ?", (incidencia_id,))
                if tec_id_val:
                    conn.execute(
                        "UPDATE personal_soporte SET casos_atendidos = casos_atendidos + 1 WHERE id = ?",
                        (tec_id_val,),
                    )

            conn.execute(
                """
                INSERT INTO historial_seguimiento
                (incidencia_id, codigo_ticket, fecha_hora, accion, estado_anterior, estado_nuevo, responsable, detalle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incidencia_id,
                    inc["codigo_ticket"],
                    now_str,
                    f"Cambio de Estado a '{nuevo_estado}'",
                    estado_ant,
                    nuevo_estado,
                    responsable or tec_nombre,
                    solucion_o_comentario or f"Actualización de estado a {nuevo_estado}.",
                ),
            )

            updated = conn.execute("SELECT * FROM incidencias WHERE id = ?", (incidencia_id,)).fetchone()
            return dict(updated)

    def configurar_simulacion_equipo(self, equipo_id: int, modo: str) -> Dict[str, Any]:
        with self._lock, self._get_connection() as conn:
            conn.execute("UPDATE equipos SET modo_simulacion = ? WHERE id = ?", (modo, equipo_id))
            eq = conn.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,)).fetchone()
            return dict(eq) if eq else {}

    def actualizar_telemetria_equipo(
        self,
        equipo_id: int,
        estado_actual: str,
        latencia_ms: float,
        perdida_pct: float,
        estado_arp: str,
        protocolo: str = "ICMP/PING + ARP",
        jitter_ms: float = 0.5,
        ttl: int = 64,
        puertos_abiertos: Optional[str] = None,
    ) -> None:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock, self._get_connection() as conn:
            eq = conn.execute("SELECT * FROM equipos WHERE id = ?", (equipo_id,)).fetchone()
            if not eq:
                return
            conn.execute(
                """
                UPDATE equipos
                SET estado_actual = ?,
                    latencia_ms = ?,
                    jitter_ms = ?,
                    ttl = ?,
                    perdida_paquetes_pct = ?,
                    estado_arp = ?,
                    puertos_abiertos = COALESCE(?, puertos_abiertos),
                    ultimo_escaneo = ?
                WHERE id = ?
                """,
                (
                    estado_actual,
                    round(latencia_ms, 2),
                    round(jitter_ms, 2),
                    ttl,
                    round(perdida_pct, 1),
                    estado_arp,
                    puertos_abiertos,
                    now_str,
                    equipo_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO monitoreo_logs
                (equipo_id, codigo_logico, ip_address, mac_address, fecha_hora,
                 protocolo, resultado, latencia_ms, perdida_pct, ttl, estado_arp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    equipo_id,
                    eq["codigo_logico"],
                    eq["ip_address"],
                    eq["mac_address"],
                    now_str,
                    protocolo,
                    estado_actual,
                    round(latencia_ms, 2),
                    round(perdida_pct, 1),
                    ttl,
                    estado_arp,
                ),
            )

    def get_ultimos_logs_monitoreo(self, limit: int = 40) -> List[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM monitoreo_logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_encuestas(self, fase: str = "POSPRUEBA_O2") -> List[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM encuesta_percepcion WHERE fase = ? ORDER BY id ASC",
                (fase,),
            ).fetchall()
            return [dict(r) for r in rows]
