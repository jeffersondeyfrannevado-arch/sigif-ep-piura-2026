# -*- coding: utf-8 -*-
"""
Configuración general del sistema:
"Aplicación para la detección y gestión de incidencias y fallas en equipos
informáticos de una entidad educativa pública Piura 2026"
Autores:
  - Toro Agurto, Mario Andre
  - Nevado Fiestas, Jefferson Deyfrank
Asesor:
  - Dr. Ancajima Miñán, Víctor Ángel
Universidad César Vallejo (UCV) - Filial Piura, 2026
"""

import os
import shutil
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# En entornos serverless (como Vercel), el sistema de archivos raíz es de solo lectura y /tmp es escribible
if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK):
    WRITABLE_DIR = Path(tempfile.gettempdir()) / "sigif_ep_piura2026"
    WRITABLE_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = WRITABLE_DIR / "incidencias_piura2026.db"
    BUNDLED_DB = BASE_DIR / "incidencias_piura2026.db"
    if BUNDLED_DB.exists() and not DB_PATH.exists():
        try:
            shutil.copy2(BUNDLED_DB, DB_PATH)
        except Exception:
            pass
    REPORTS_DIR = WRITABLE_DIR / "reportes_exportados"
else:
    DB_PATH = BASE_DIR / "incidencias_piura2026.db"
    REPORTS_DIR = BASE_DIR / "reportes_exportados"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

APP_METADATA = {
    "titulo_tesis": (
        "Aplicación para la detección y gestión de incidencias y fallas en "
        "equipos informáticos de una entidad educativa pública Piura 2026"
    ),
    "nombre_sistema": "SIGIF-EP Piura 2026",
    "subtitulo_sistema": (
        "Sistema Inteligente de Monitoreo ICMP/ARP, Detección Automática "
        "y Gestión de Incidencias TI (ITIL v4 / NIST SP 800-61)"
    ),
    "institucion_objetivo": "Entidad Educativa Pública - Piura (Oficina SIAGIE y Áreas Administrativas/Educativas)",
    "universidad": "Universidad César Vallejo - Facultad de Ingeniería y Arquitectura",
    "escuela": "Escuela Profesional de Ingeniería de Sistemas",
    "autores": [
        "Toro Agurto, Mario Andre (ORCID: 0000-0003-4364-647X)",
        "Nevado Fiestas, Jefferson Deyfrank (ORCID: 0000-0001-5290-3947)",
    ],
    "asesor": "Dr. Ancajima Miñán, Víctor Ángel (ORCID: 0000-0002-3122-4512)",
    "ods": "ODS 8: Trabajo decente y crecimiento económico",
    "ley_privacidad": "Ley N.° 29733 - Ley de Protección de Datos Personales (Perú)",
    "version": "2.6.0-UCV",
    "anio": 2026,
}

# Parámetros técnicos de monitoreo de red (Anexo 8: PING, ARP, ICMP)
NETWORK_CONFIG = {
    "ping_timeout_ms": 1200,
    "latency_warning_ms": 85.0,      # Umbral de lentitud / bajo rendimiento (ms)
    "latency_critical_ms": 180.0,    # Umbral crítico de degradación de red (ms)
    "packet_loss_warning_pct": 20.0,
    "packet_loss_critical_pct": 100.0,
    "reincidence_threshold": 2,      # N° de fallas previas para clasificar como falla recurrente
    "scan_interval_seconds": 15,     # Intervalo de monitoreo automático en segundo plano
    "default_port": 8765,
}

# Áreas de la Entidad Educativa Pública de Piura (distribución de los 35 equipos/usuarios)
AREAS_INSTITUCIONALES = [
    "Oficina de SIAGIE",
    "Dirección General",
    "Subdirección Académica",
    "Secretaría General y Mesa de Partes",
    "Administración y Logística",
    "Laboratorio de Cómputo 01",
    "Laboratorio de Cómputo 02",
    "Biblioteca Institucional",
    "Sala de Docentes",
    "Coordinación de Tutoría (TOE)",
    "Unidad de Soporte Técnico TI",
]

# Clasificación de tipos de falla (alineado con Dimensiones 1 y 2 de la tesis)
TIPOS_FALLA = [
    "Falla de Conectividad / Pérdida de Enlace ICMP",
    "Equipo Inoperativo / Sin Respuesta en Red (Host Down)",
    "Lentitud Operativa / Alta Latencia de Red",
    "Conflicto o Anomalía de Resolución Física ARP",
    "Falla de Hardware / Periféricos Críticos",
    "Error de Servicio Tecnológico / Sistema Institucional (SIAGIE)",
    "Error Recurrente de Estación de Trabajo",
]

NIVELES_SEVERIDAD = [
    "Crítica",
    "Alta",
    "Media",
    "Baja",
]

ESTADOS_ATENCION = [
    "Pendiente",
    "En Atención",
    "Resuelto",
    "Escalado",
]

#Las 4 dimensiones metodológicas del estudio (Págs. 20-21 y Anexo 1)
DIMENSIONES_ESTUDIO = [
    {
        "codigo": "D1",
        "nombre": "Detección automática de fallas",
        "descripcion": (
            "Capacidad de la aplicación para identificar interrupciones de conectividad, "
            "equipos inoperativos, lentitud operativa y fallas recurrentes mediante PING, ARP e ICMP."
        ),
        "indicadores": [
            "Identificación de fallas de conectividad",
            "Detección de equipos inoperativos",
            "Reconocimiento de lentitud o bajo rendimiento",
            "Identificación de fallas recurrentes",
            "Oportunidad en la detección de eventos técnicos",
        ],
    },
    {
        "codigo": "D2",
        "nombre": "Registro y clasificación de incidencias",
        "descripcion": (
            "Capacidad para almacenar código lógico del equipo afectado, área, tipo de falla, "
            "fecha/hora del evento y estado inicial de atención."
        ),
        "indicadores": [
            "Registro del equipo afectado",
            "Identificación del área donde ocurrió la incidencia",
            "Clasificación del tipo de falla",
            "Registro de fecha y hora del evento",
            "Organización del estado inicial de atención",
        ],
    },
    {
        "codigo": "D3",
        "nombre": "Alertas y notificaciones",
        "descripcion": (
            "Envío oportuno de avisos automáticos al área de soporte técnico cuando se detectan "
            "fallas o interrupciones que afectan la continuidad operativa."
        ),
        "indicadores": [
            "Emisión automática de alertas tempranas",
            "Tiempo de notificación al soporte técnico",
            "Claridad y utilidad del aviso técnico",
            "Priorización por nivel de criticidad",
        ],
    },
    {
        "codigo": "D4",
        "nombre": "Seguimiento y reportes técnicos",
        "descripcion": (
            "Capacidad para mostrar el avance de cada incidencia, registrar la solución aplicada, "
            "conservar el historial de fallas por equipo y exportar reportes para la toma de decisiones."
        ),
        "indicadores": [
            "Seguimiento del estado de la incidencia",
            "Registro de la solución aplicada",
            "Tiempo de atención y resolución del caso",
            "Historial de fallas por equipo y control de reincidencia",
            "Generación y exportación de reportes para toma de decisiones",
        ],
    },
]

# Los 16 ítems exactos del Cuestionario (Anexo 2 y Anexo 3 del PDF)
CUESTIONARIO_ITEMS = [
    # Dimensión 1 del instrumento: Manejo de la interfaz
    {"num": 1, "dimension": "Manejo de la interfaz", "indicador": "Facilidad de uso de la interfaz",
     "texto": "La aplicación es fácil de usar durante mis actividades laborales."},
    {"num": 2, "dimension": "Manejo de la interfaz", "indicador": "Facilidad de uso de la interfaz",
     "texto": "Aprender a utilizar la aplicación no me ha resultado complicado."},
    {"num": 3, "dimension": "Manejo de la interfaz", "indicador": "Accesibilidad de la interfaz",
     "texto": "Puedo acceder con facilidad a las funciones principales de la aplicación."},
    {"num": 4, "dimension": "Manejo de la interfaz", "indicador": "Accesibilidad de la interfaz",
     "texto": "La interfaz de la aplicación me permite encontrar rápidamente las opciones que necesito."},
    {"num": 5, "dimension": "Manejo de la interfaz", "indicador": "Comprensión visual del sistema",
     "texto": "La presentación visual de la aplicación me ayuda a comprender mejor la información mostrada."},
    {"num": 6, "dimension": "Manejo de la interfaz", "indicador": "Comprensión visual del sistema",
     "texto": "Los elementos visuales de la aplicación son claros y fáciles de interpretar."},
    # Dimensión 2 del instrumento: Funcionalidad del sistema
    {"num": 7, "dimension": "Funcionalidad del sistema", "indicador": "Monitoreo en tiempo real",
     "texto": "La aplicación permite conocer en tiempo real el estado de los equipos informáticos."},
    {"num": 8, "dimension": "Funcionalidad del sistema", "indicador": "Monitoreo en tiempo real",
     "texto": "El monitoreo en tiempo real de la aplicación facilita identificar problemas apenas ocurren."},
    {"num": 9, "dimension": "Funcionalidad del sistema", "indicador": "Generación de alertas",
     "texto": "La aplicación genera alertas oportunas cuando detecta una falla o incidencia."},
    {"num": 10, "dimension": "Funcionalidad del sistema", "indicador": "Generación de alertas",
     "texto": "Las alertas emitidas por la aplicación son útiles para actuar rápidamente ante un problema."},
    {"num": 11, "dimension": "Funcionalidad del sistema", "indicador": "Registro de incidencias",
     "texto": "La aplicación facilita el registro ordenado de las incidencias detectadas en los equipos."},
    {"num": 12, "dimension": "Funcionalidad del sistema", "indicador": "Registro de incidencias",
     "texto": "El registro de incidencias en la aplicación permite llevar un mejor control de los problemas reportados."},
    {"num": 13, "dimension": "Funcionalidad del sistema", "indicador": "Emisión de reportes",
     "texto": "La aplicación genera reportes útiles para conocer el estado de las incidencias."},
    {"num": 14, "dimension": "Funcionalidad del sistema", "indicador": "Emisión de reportes",
     "texto": "Los reportes emitidos por la aplicación apoyan el seguimiento de las fallas informáticas."},
    {"num": 15, "dimension": "Funcionalidad del sistema", "indicador": "Exportación de reportes",
     "texto": "La aplicación permite exportar reportes de manera sencilla cuando se requiere."},
    {"num": 16, "dimension": "Funcionalidad del sistema", "indicador": "Exportación de reportes",
     "texto": "La exportación de reportes facilita compartir la información con otras áreas o responsables."},
]
