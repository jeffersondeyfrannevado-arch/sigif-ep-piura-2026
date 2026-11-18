# SIGIF-EP Piura 2026 — Sistema de Detección y Gestión de Incidencias y Fallas en Equipos Informáticos

**Proyecto de Investigación (Universidad César Vallejo - Filial Piura, 2026):**
> *"Aplicación para la detección y gestión de incidencias y fallas en equipos informáticos de una entidad educativa pública Piura 2026"*

* **Autores:**
  * Toro Agurto, Mario Andre (`0000-0003-4364-647X`)
  * Nevado Fiestas, Jefferson Deyfrank (`0000-0001-5290-3947`)
* **Asesor:** Dr. Ancajima Miñán, Víctor Ángel (`0000-0002-3122-4512`)
* **Línea de investigación:** Sistema de Información y Comunicaciones (ODS 8: Trabajo decente y crecimiento económico)
* **Cumplimiento Legal y Ético:** Ley N.° 29733 — Ley de Protección de Datos Personales (Anexo 8)

---

## 1. Arquitectura del Programa (Python 3)

El sistema está diseñado bajo una arquitectura modular en capas utilizando exclusivamente la biblioteca estándar de Python (sin dependencias externas frágiles), garantizando que funcione de inmediato en cualquier equipo Windows/Linux de la institución:

| Archivo | Rol y Responsabilidad en la Arquitectura |
| :--- | :--- |
| `config.py` | Configuración institucional, umbrales técnicos de red (`PING`, `ARP`, `ICMP`), catálogo de áreas de la entidad educativa pública de Piura, tipos de falla, severidades ITIL v4 y los **16 ítems del Cuestionario (Anexo 2)**. |
| `database.py` | Capa de persistencia relacional en **SQLite3** (`incidencias_piura2026.db`) con modo concurrente WAL. Administra los **35 equipos/usuarios institucionales**, los **10 técnicos de soporte** (Tabla 1, $N=45$), incidencias de Preprueba ($O_1$) y Posprueba ($O_2$), alertas tempranas, bitácora de trazabilidad y matriz de encuestas. |
| `network_scanner.py` | **Motor de Monitoreo de Bajo Nivel (Anexo 8):** Ejecuta comandos reales `ping` (ICMP Echo Request/Reply) y `arp -a` (resolución física IPv4 $\leftrightarrow$ MAC de Capa 2), evalúa latencia en milisegundos, pérdida de paquetes y disponibilidad, e inyecta/detecta fallas en tiempo real generando alertas y tickets automáticamente. |
| `analytics_engine.py` | **Motor Estadístico y Exportador:** Calcula indicadores en tiempo real por las 4 dimensiones, contrasta la hipótesis preexperimental ($G: O_1 \text{ — } X \text{ — } O_2$) mediante **Prueba *t* de Student para muestras relacionadas** y **Rangos con Signo de Wilcoxon**, calcula el **Alfa de Cronbach ($\alpha = 0.924$)** de los 16 ítems y exporta reportes en **CSV (Excel/SPSS/Jamovi)** y **HTML/PDF imprimible**. |
| `ui_template.py` | Interfaz Web Institucional (Single-Page Application) con diseño UCV, mapa interactivo en vivo de los 35 equipos con semáforo de estado, consola `PING`/`ARP`, gestor ITIL de incidencias y módulo estadístico de la tesis. |
| `web_server.py` | Servidor HTTP y API RESTful multihilo (`ThreadingHTTPServer`) que expone todos los servicios JSON en tiempo real (`http://127.0.0.1:8765`). |
| `desktop_app.py` | Interfaz Gráfica de Escritorio Nativa (`Tkinter` / `TTK`) sincronizada con la base de datos SQLite y el servidor web local. |
| `main.py` | Punto de entrada principal que orquesta el motor de monitoreo continuo, el servidor web, la interfaz de escritorio y la suite de verificación (`--verify`). |
| `EJECUTAR_SISTEMA_TESIS.bat` | Lanzador directo para Windows (doble clic). |

---

## 2. Alineación Exacta con los Objetivos, Dimensiones e Instrumentos de la Tesis

1. **Dimensión 1 — Detección automática de fallas (Ítems 7 y 8):**
   * Monitoreo permanente de los **35 equipos informáticos** (*Oficina de SIAGIE*, *Dirección General*, *Subdirección*, *Secretaría*, *Administración*, *Laboratorios de Cómputo 01 y 02*, *Biblioteca*, *Sala de Docentes*, *Tutoría TOE*).
   * Identifica instantáneamente fallas de conectividad (`INOPERATIVO`), lentitud operativa por alta latencia (`LENTO` > 85 ms), anomalías físicas de capa 2 (`ALERTA_ARP`) y reincidencia de fallas.
2. **Dimensión 2 — Registro y clasificación de incidencias (Ítems 11 y 12):**
   * Almacena código lógico (`PC-SIAGIE-01` .. `PC-TOE-03`), dirección IP, dirección MAC, área, tipo de falla, nivel de severidad (*Crítica*, *Alta*, *Media*, *Baja*), fecha/hora exacta y técnico asignado entre los **10 integrantes de soporte técnico**.
3. **Dimensión 3 — Alertas y notificaciones (Ítems 9 y 10):**
   * Dispara avisos automáticos en menos de 2 segundos cuando ocurre una caída o degradación de red, registrando el protocolo (`ICMP/PING + ARP`), el mensaje técnico y el tiempo de notificación.
4. **Dimensión 4 — Seguimiento y reportes técnicos (Ítems 13, 14, 15 y 16):**
   * Bitácora de trazabilidad completa (*Pendiente* $\rightarrow$ *En Atención* $\rightarrow$ *Resuelto* / *Escalado*), registro de la solución aplicada, restauración automática del equipo al resolver el ticket y exportación en un clic a **CSV/Excel**, **Matriz SPSS/Jamovi** e **Informe Ejecutivo HTML/PDF**.

---

## 3. Cómo Ejecutar el Programa

### Opción A: Doble clic en Windows
Haz doble clic sobre el archivo **`EJECUTAR_SISTEMA_TESIS.bat`**.

### Opción B: Desde la terminal
```powershell
python main.py
```
* Esto iniciará el motor de monitoreo ICMP/ARP, abrirá el **Dashboard Web Interactivo** en `http://127.0.0.1:8765` y abrirá el **Centro de Control de Escritorio**.
* Para ejecutar únicamente la suite de verificación y exportar todos los reportes automáticamente:
```powershell
python main.py --verify
```
* Para iniciar únicamente el servidor web en segundo plano:
```powershell
python main.py --web-only
```
