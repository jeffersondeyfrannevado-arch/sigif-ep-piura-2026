# -*- coding: utf-8 -*-
"""
Plantilla HTML5 / CSS3 / JS (Single-Page Application Institucional con Monitoreo de Red Real en Vivo)
Sistema: SIGIF-EP Piura 2026
Muestra en vivo todos los dispositivos reales conectados a la subred LAN/Wi-Fi actual (ej. 192.168.0.0/24),
la telemetría física de hardware/Wi-Fi de la estación local, y toda la gestión ITIL v4 y evaluación
estadística de la tesis (Preprueba O1 vs Posprueba O2, Alfa de Cronbach = 0.9468).
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIGIF-EP Piura 2026 | Escáner de Red Real en Vivo (ICMP/ARP/TCP) y Gestión de Incidencias</title>
<style>
  :root {
    --ucv-navy: #0f2547;
    --ucv-blue: #1d4ed8;
    --ucv-red: #c8102e;
    --bg-main: #f1f5f9;
    --bg-card: #ffffff;
    --text-main: #0f172a;
    --text-muted: #475569;
    --border-col: #cbd5e1;
    --ok-green: #16a34a;
    --ok-bg: #dcfce7;
    --warn-amber: #d97706;
    --warn-bg: #fef3c7;
    --err-red: #dc2626;
    --err-bg: #fee2e2;
    --arp-purple: #7c3aed;
    --arp-bg: #ede9fe;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-main);
    color: var(--text-main);
    display: flex;
    min-height: 100vh;
  }
  .sidebar {
    width: 275px;
    background: linear-gradient(180deg, #0b1d3a 0%, #173463 100%);
    color: #fff;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    box-shadow: 2px 0 12px rgba(0,0,0,0.18);
  }
  .brand {
    padding: 18px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.14);
  }
  .brand-badge {
    display: inline-block;
    background: var(--ucv-red);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  .brand h1 { margin: 0; font-size: 18px; font-weight: 800; }
  .brand p { margin: 4px 0 0 0; font-size: 11.5px; color: #cbd5e1; line-height: 1.35; }
  .nav-menu { padding: 14px 10px; flex: 1; }
  .nav-btn {
    width: 100%;
    background: transparent;
    border: none;
    color: #e2e8f0;
    text-align: left;
    padding: 11px 14px;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px;
    transition: all 0.15s ease;
  }
  .nav-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
  .nav-btn.active {
    background: #2563eb;
    color: #fff;
    box-shadow: 0 2px 8px rgba(37,99,235,0.4);
  }
  .nav-badge {
    background: var(--ucv-red);
    color: #fff;
    font-size: 11px;
    padding: 2px 7px;
    border-radius: 10px;
    font-weight: 700;
  }
  .sidebar-footer {
    padding: 14px 16px;
    background: rgba(0,0,0,0.25);
    font-size: 11px;
    color: #cbd5e1;
    line-height: 1.45;
    border-top: 1px solid rgba(255,255,255,0.1);
  }
  .main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-x: hidden;
  }
  .topbar {
    background: #fff;
    border-bottom: 1px solid var(--border-col);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }
  .topbar-title h2 { margin: 0; font-size: 17px; color: var(--ucv-navy); }
  .topbar-title span { font-size: 12px; color: var(--text-muted); }
  .topbar-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #dcfce7;
    color: #166534;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
  }
  .pulse-dot {
    width: 9px;
    height: 9px;
    background: #16a34a;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(22,163,74,0.7); }
    70% { box-shadow: 0 0 0 8px rgba(22,163,74,0); }
    100% { box-shadow: 0 0 0 0 rgba(22,163,74,0); }
  }
  .btn {
    border: none;
    border-radius: 7px;
    padding: 8px 14px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
  }
  .btn-primary { background: var(--ucv-blue); color: #fff; }
  .btn-primary:hover { background: #1e40af; }
  .btn-danger { background: var(--err-red); color: #fff; }
  .btn-danger:hover { background: #b91c1c; }
  .btn-success { background: var(--ok-green); color: #fff; }
  .btn-success:hover { background: #15803d; }
  .btn-warning { background: var(--warn-amber); color: #fff; }
  .btn-outline { background: #fff; border: 1px solid var(--border-col); color: var(--text-main); }
  .btn-outline:hover { background: #f8fafc; }
  .btn-sm { padding: 5px 9px; font-size: 11.5px; border-radius: 5px; }

  .content-container {
    padding: 18px 24px;
    max-width: 1650px;
    width: 100%;
    margin: 0 auto;
  }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  /* LIVE HARDWARE TELEMETRY BANNER */
  .hw-banner {
    background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);
    color: #fff;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    box-shadow: 0 4px 12px rgba(15,23,42,0.18);
  }
  .hw-item {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 8px;
    padding: 10px 12px;
  }
  .hw-title { font-size: 10.5px; color: #93c5fd; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; }
  .hw-main { font-size: 14.5px; font-weight: 800; color: #fff; margin: 3px 0; }
  .hw-sub { font-size: 11px; color: #cbd5e1; }

  /* KPI CARDS */
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 16px;
  }
  .kpi-card {
    background: var(--bg-card);
    border-radius: 10px;
    padding: 14px 16px;
    border: 1px solid #e2e8f0;
    border-left: 5px solid var(--ucv-blue);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .kpi-card.green { border-left-color: var(--ok-green); }
  .kpi-card.amber { border-left-color: var(--warn-amber); }
  .kpi-card.red { border-left-color: var(--err-red); }
  .kpi-card.purple { border-left-color: var(--arp-purple); }
  .kpi-label { font-size: 11.5px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }
  .kpi-val { font-size: 25px; font-weight: 800; margin: 4px 0 2px 0; color: var(--text-main); }
  .kpi-sub { font-size: 11.5px; color: #64748b; }

  .card {
    background: var(--bg-card);
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    padding: 18px 20px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f1f5f9;
  }
  .card-header h3 { margin: 0; font-size: 15.5px; color: var(--ucv-navy); }
  .filter-bar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
  select, input[type="text"], textarea {
    padding: 7px 11px;
    border: 1px solid var(--border-col);
    border-radius: 6px;
    font-size: 12.5px;
    font-family: inherit;
    background: #fff;
  }

  /* EQUIPOS GRID */
  .equipos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 13px;
  }
  .eq-card {
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 13px 14px;
    background: #fff;
    position: relative;
    transition: transform 0.12s, box-shadow 0.12s;
    border-top: 4px solid var(--ok-green);
  }
  .eq-card.real-device {
    border: 1.5px solid #2563eb;
    border-top: 5px solid #16a34a;
    box-shadow: 0 3px 10px rgba(37,99,235,0.09);
  }
  .eq-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }
  .eq-card.LENTO { border-top-color: var(--warn-amber); background: #fffbeb; }
  .eq-card.INOPERATIVO { border-top-color: var(--err-red); background: #fef2f2; }
  .eq-card.ALERTA_ARP { border-top-color: var(--arp-purple); background: #f5f3ff; }

  .eq-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; gap: 4px; }
  .eq-code { font-weight: 800; font-size: 14px; color: var(--ucv-navy); }
  .real-tag {
    background: #0f172a;
    color: #38bdf8;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    letter-spacing: 0.3px;
  }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10.5px;
    font-weight: 700;
  }
  .badge-OPERATIVO, .badge-Resuelto { background: var(--ok-bg); color: #166534; }
  .badge-LENTO, .badge-Media, .badge-ADVERTENCIA, .badge-EnAtencion { background: var(--warn-bg); color: #92400e; }
  .badge-INOPERATIVO, .badge-Critica, .badge-Alta, .badge-CRITICA, .badge-Pendiente { background: var(--err-bg); color: #991b1b; }
  .badge-ALERTA_ARP, .badge-Escalado { background: var(--arp-bg); color: #5b21b6; }

  .eq-area { font-size: 11.5px; font-weight: 700; color: #1e40af; margin-bottom: 5px; }
  .eq-meta { font-size: 11.5px; color: #334155; line-height: 1.5; margin-bottom: 8px; }
  .eq-metrics {
    display: flex;
    justify-content: space-between;
    background: #f1f5f9;
    padding: 6px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 9px;
    color: #0f172a;
  }
  .eq-actions { display: flex; gap: 5px; flex-wrap: wrap; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th, td { padding: 9px 11px; border-bottom: 1px solid #e2e8f0; text-align: left; }
  th { background: #f8fafc; color: var(--ucv-navy); font-weight: 700; font-size: 11.5px; text-transform: uppercase; }
  tr:hover { background: #f8fafc; }

  .terminal {
    background: #0f172a;
    color: #38bdf8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12.5px;
    padding: 15px;
    border-radius: 8px;
    white-space: pre-wrap;
    max-height: 390px;
    overflow-y: auto;
    line-height: 1.5;
    border: 1px solid #334155;
  }

  .modal-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15,23,42,0.62);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .modal-backdrop.open { display: flex; }
  .modal {
    background: #fff;
    border-radius: 12px;
    max-width: 740px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    padding: 22px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.28);
  }
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 10px;
    margin-bottom: 14px;
  }
  .modal-header h3 { margin: 0; color: var(--ucv-navy); }
  .timeline-item {
    border-left: 3px solid var(--ucv-blue);
    padding-left: 12px;
    margin-bottom: 10px;
    font-size: 12px;
  }
  .toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 2000;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .toast {
    background: #0f172a;
    color: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 12.5px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.28);
    border-left: 5px solid #38bdf8;
    max-width: 400px;
  }
  .toast.crit { border-left-color: #ef4444; background: #450a0a; }
</style>
</head>
<body>

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-badge">UCV PIURA - RED REAL EN VIVO</div>
      <h1>SIGIF-EP Piura</h1>
      <p>Escáner Real LAN/Wi-Fi (PING, ARP, ICMP, TCP) y Gestión ITIL v4</p>
    </div>

    <nav class="nav-menu">
      <button class="nav-btn active" onclick="switchTab('tab-monitoreo', this)">
        <span>1. Red Real en Vivo (LAN/Wi-Fi)</span>
        <span class="nav-badge" style="background:#16a34a" id="nav-real-count">0</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-incidencias', this)">
        <span>2. Gestión de Incidencias</span>
        <span class="nav-badge" id="nav-inc-count">0</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-alertas', this)">
        <span>3. Alertas y Notificaciones</span>
        <span class="nav-badge" id="nav-alert-count">0</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-consola', this)">
        <span>4. Consola PING / ARP / Puertos</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-estadistica', this)">
        <span>5. Evaluación O1-X-O2 y Alfa</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-reportes', this)">
        <span>6. Reportes y Exportación</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <strong>Autores:</strong><br>
      • Toro Agurto, Mario Andre<br>
      • Nevado Fiestas, Jefferson D.<br>
      <strong>Asesor:</strong> Dr. Víctor Á. Ancajima Miñán<br>
      <strong>Privacidad:</strong> Ley N.° 29733 Activa
    </div>
  </aside>

  <!-- MAIN AREA -->
  <div class="main-area">
    <header class="topbar">
      <div class="topbar-title">
        <h2 id="top-subnet-title">Conectado en Vivo a Tu Red Local — Escáner Multihilo ICMP / ARP / TCP</h2>
        <span id="top-adapter-sub">Detectando tarjeta de red activa, puerta de enlace y dispositivos conectados...</span>
      </div>
      <div class="topbar-actions">
        <div class="status-pill">
          <span class="pulse-dot"></span>
          <span id="monitor-status-text">Sondeo Real Activo</span>
        </div>
        <button class="btn btn-success" onclick="descubrirRedRealAhora()" id="btn-scan-real">
          📡 Descubrir Red Real Ahora (1-254)
        </button>
        <button class="btn btn-outline" onclick="abrirModalNuevaIncidencia()">
          + Registrar Incidencia
        </button>
      </div>
    </header>

    <div class="content-container">

      <!-- ================================================================= -->
      <!-- TAB 1: MONITOREO EN TIEMPO REAL DE LA RED REAL Y EQUIPOS          -->
      <!-- ================================================================= -->
      <section id="tab-monitoreo" class="tab-panel active">

        <!-- BANNER DE TELEMETRÍA FÍSICA REAL DE LA ESTACIÓN LOCAL -->
        <div class="hw-banner" id="hw-banner-box">
          <div class="hw-item">
            <div class="hw-title">🖥️ Esta Estación (Monitor Local)</div>
            <div class="hw-main" id="hw-host">Cargando...</div>
            <div class="hw-sub" id="hw-ip-mac">IP: -- | MAC: --</div>
          </div>
          <div class="hw-item">
            <div class="hw-title">🌐 Subred Activa y Gateway</div>
            <div class="hw-main" id="hw-subnet">--</div>
            <div class="hw-sub" id="hw-gw">Gateway: --</div>
          </div>
          <div class="hw-item">
            <div class="hw-title">📶 Enlace Wi-Fi / Tarjeta de Red</div>
            <div class="hw-main" id="hw-wifi">--</div>
            <div class="hw-sub" id="hw-adapter">--</div>
          </div>
          <div class="hw-item">
            <div class="hw-title">🧠 Memoria RAM Física Real</div>
            <div class="hw-main" id="hw-ram">-- GB / -- GB (--%)</div>
            <div class="hw-sub" id="hw-uptime">Tiempo activo: --</div>
          </div>
          <div class="hw-item">
            <div class="hw-title">💾 Almacenamiento Disco Local</div>
            <div class="hw-main" id="hw-disk">-- GB / -- GB (--%)</div>
            <div class="hw-sub" id="hw-cpu">CPU: --</div>
          </div>
        </div>

        <div class="kpi-row">
          <div class="kpi-card green">
            <div class="kpi-label">Dispositivos Reales en Tu Red</div>
            <div class="kpi-val" id="kpi-reales">--</div>
            <div class="kpi-sub" id="kpi-reales-sub">Conectados en vivo a tu Wi-Fi/LAN</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Latencia Real Media LAN</div>
            <div class="kpi-val" id="kpi-lat-real">-- ms</div>
            <div class="kpi-sub">Medición ICMP/TCP en vivo</div>
          </div>
          <div class="kpi-card amber">
            <div class="kpi-label">Tiempo Prom. Detección</div>
            <div class="kpi-val" id="kpi-tdet">-- s</div>
            <div class="kpi-sub">Sondeo multihilo PING + ARP</div>
          </div>
          <div class="kpi-card red">
            <div class="kpi-label">Tickets / Alertas Activas</div>
            <div class="kpi-val" id="kpi-activos">0</div>
            <div class="kpi-sub" id="kpi-activos-sub">Pendientes o En Atención</div>
          </div>
          <div class="kpi-card purple">
            <div class="kpi-label">Población Total Monitoreada</div>
            <div class="kpi-val" id="kpi-disp">--</div>
            <div class="kpi-sub" id="kpi-disp-sub">Red Real + 35 Equipos Tesis</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>Mapa en Vivo de Computadoras y Dispositivos Conectados a Tu Red (ICMP + Tabla Física ARP + Puertos TCP)</h3>
            <div class="filter-bar" style="margin:0;">
              <select id="filtro-area-eq" onchange="cargarEquipos()" style="font-weight:700;border-color:#2563eb;">
                <option value="SOLO_REALES" selected>📡 SOLO DISPOSITIVOS REALES EN MI RED ACTUAL (En Vivo)</option>
                <option value="TODAS">🏛️ Todos (Red Real en Vivo + 35 Equipos Institucionales Tesis)</option>
              </select>
              <select id="filtro-estado-eq" onchange="cargarEquipos()">
                <option value="TODOS">Todos los Estados</option>
                <option value="OPERATIVO">Operativos (En línea)</option>
                <option value="LENTO">Lentitud / Alta Latencia</option>
                <option value="INOPERATIVO">Inoperativos / Desconectados</option>
              </select>
            </div>
          </div>
          <p style="margin:0 0 12px 0;font-size:12.5px;color:#334155;">
            🟢 <strong>Monitoreo 100% Real Activo:</strong> Los equipos listados abajo con la etiqueta <code>EN VIVO - RED REAL</code> son los dispositivos físicos reales descubiertos ahora mismo en tu red local (tu PC, tu router, laptops, celulares y equipos conectados al mismo Wi-Fi/LAN). Si desconectas el Wi-Fi de cualquiera de ellos y presionas <em>"🔍 PING/ARP Real"</em> o <em>"📡 Descubrir Red Real Ahora"</em>, verás cómo el sistema detecta la caída real y genera la alerta e incidencia automáticamente.
          </p>
          <div class="equipos-grid" id="grid-equipos"></div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 2: GESTIÓN DE INCIDENCIAS Y SEGUIMIENTO                       -->
      <!-- ================================================================= -->
      <section id="tab-incidencias" class="tab-panel">
        <div class="card">
          <div class="card-header">
            <h3>Registro, Clasificación y Seguimiento de Incidencias (Dimensiones 2 y 4 - Ítems 11 y 12)</h3>
            <div style="display:flex;gap:8px;">
              <button class="btn btn-primary btn-sm" onclick="abrirModalNuevaIncidencia()">+ Nueva Incidencia</button>
              <button class="btn btn-success btn-sm" onclick="exportarArchivo('csv_incidencias')">📥 Exportar CSV/Excel</button>
            </div>
          </div>
          <div class="filter-bar">
            <label style="font-size:12px;font-weight:700;">Fase:</label>
            <select id="filtro-fase-inc" onchange="cargarIncidencias()">
              <option value="POSPRUEBA_O2">Posprueba O2 (Con Aplicación Python)</option>
              <option value="PREPRUEBA_O1">Preprueba O1 (Línea Base Manual)</option>
              <option value="TODAS">Todas las Fases (O1 + O2)</option>
            </select>
            <label style="font-size:12px;font-weight:700;">Estado:</label>
            <select id="filtro-estado-inc" onchange="cargarIncidencias()">
              <option value="TODOS">Todos los Estados</option>
              <option value="Pendiente">Pendiente</option>
              <option value="En Atención">En Atención</option>
              <option value="Resuelto">Resuelto</option>
              <option value="Escalado">Escalado</option>
            </select>
            <label style="font-size:12px;font-weight:700;">Severidad:</label>
            <select id="filtro-sev-inc" onchange="cargarIncidencias()">
              <option value="TODAS">Todas</option>
              <option value="Crítica">Crítica</option>
              <option value="Alta">Alta</option>
              <option value="Media">Media</option>
              <option value="Baja">Baja</option>
            </select>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Fase</th>
                  <th>Equipo</th>
                  <th>Área / Ubicación</th>
                  <th>Tipo de Falla Clasificada</th>
                  <th>Severidad</th>
                  <th>Fecha / Hora</th>
                  <th>T. Detección</th>
                  <th>T. Respuesta</th>
                  <th>T. Solución</th>
                  <th>Estado</th>
                  <th>Técnico Asignado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody id="tabla-incidencias-body"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 3: CENTRO DE ALERTAS Y NOTIFICACIONES                         -->
      <!-- ================================================================= -->
      <section id="tab-alertas" class="tab-panel">
        <div class="card">
          <div class="card-header">
            <h3>Bandeja de Alertas Tempranas y Notificaciones Automáticas (Dimensión 3 - Ítems 9 y 10)</h3>
            <button class="btn btn-outline btn-sm" onclick="marcarTodasAlertasLeidas()">✔ Marcar Todas como Leídas</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nivel</th>
                  <th>Ticket Asociado</th>
                  <th>Equipo / IP</th>
                  <th>Área</th>
                  <th>Protocolo</th>
                  <th>Mensaje de Alerta Automática</th>
                  <th>T. Notificación</th>
                  <th>Fecha / Hora</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody id="tabla-alertas-body"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 4: CONSOLA DE BAJO NIVEL PING / ARP / ICMP (ANEXO 8)          -->
      <!-- ================================================================= -->
      <section id="tab-consola" class="tab-panel">
        <div class="card">
          <div class="card-header">
            <h3>Consola Técnica Interactiva en Vivo (PING, Tabla Física ARP y Escáner de Puertos TCP - Anexo 8)</h3>
            <span class="badge badge-OPERATIVO">Cumplimiento Ley N.° 29733 Verificado</span>
          </div>
          <div class="filter-bar">
            <input type="text" id="input-ip-ping" value="192.168.0.1" placeholder="Ej. 192.168.0.1 o 192.168.0.127" style="width:240px;">
            <button class="btn btn-primary" onclick="ejecutarPingRealConsola()">▶ Ejecutar PING + Escaneo TCP Real</button>
            <button class="btn btn-success" onclick="ejecutarArpRealConsola()">🔍 Ver Tabla ARP Real de Mi Red (arp -a)</button>
            <button class="btn btn-outline" onclick="descubrirRedRealAhora()">📡 Barrido Completo Subred /24 (1-254)</button>
          </div>
          <div class="terminal" id="consola-output">
[SIGIF-EP Piura 2026 - Motor Python ICMP/ARP/TCP En Vivo]
Presione "Ver Tabla ARP Real" o ingrese cualquier IP de su red para ejecutar el diagnóstico técnico...
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>Bitácora de Telemetría en Vivo (Últimos Escaneos Reales ICMP / ARP)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha / Hora</th>
                  <th>Código Lógico</th>
                  <th>Dirección IP</th>
                  <th>Dirección Física MAC</th>
                  <th>Protocolo / Servicios</th>
                  <th>Estado</th>
                  <th>Latencia</th>
                  <th>Pérdida</th>
                  <th>Resolución ARP</th>
                </tr>
              </thead>
              <tbody id="tabla-logs-body"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 5: EVALUACIÓN CIENTÍFICA DE LA TESIS (O1 - X - O2 Y ALFA)     -->
      <!-- ================================================================= -->
      <section id="tab-estadistica" class="tab-panel">
        <div class="kpi-row">
          <div class="kpi-card green">
            <div class="kpi-label">Alfa de Cronbach (16 Ítems)</div>
            <div class="kpi-val" id="stat-alfa">--</div>
            <div class="kpi-sub">N = 45 (Consistencia Excelente &gt; 0.90)</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Validez V de Aiken</div>
            <div class="kpi-val">1.000</div>
            <div class="kpi-sub">3 Jueces Expertos UCV (100% Acuerdo)</div>
          </div>
          <div class="kpi-card amber">
            <div class="kpi-label">Prueba t de Student (O1 vs O2)</div>
            <div class="kpi-val" id="stat-t">--</div>
            <div class="kpi-sub" id="stat-p">gl = 44, p &lt; 0.001 (Significativo)</div>
          </div>
          <div class="kpi-card purple">
            <div class="kpi-label">Rangos de Wilcoxon (Z)</div>
            <div class="kpi-val" id="stat-w">--</div>
            <div class="kpi-sub">p &lt; 0.001 (Rechaza H0, Acepta Hi)</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>1. Comparación Preexperimental (G: O1 — X — O2) en Indicadores Técnicos y de Gestión</h3>
            <button class="btn btn-primary btn-sm" onclick="exportarArchivo('csv_spss')">📊 Descargar Matriz de 45 Participantes para SPSS / Jamovi</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Indicador / Dimensión</th>
                  <th>Preprueba O1 (Sin Aplicación - Reporte Manual)</th>
                  <th>Posprueba O2 (Con Aplicación Python SIGIF-EP)</th>
                  <th>Variación / Mejora</th>
                  <th>Prueba Estadística y Significancia</th>
                </tr>
              </thead>
              <tbody id="tabla-comparativa-o1-o2"></tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>2. Resultados por Ítem del Cuestionario (Anexo 2: 16 Ítems, Muestra Censal N = 45: 35 Usuarios + 10 Técnicos)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>N°</th>
                  <th>Dimensión</th>
                  <th>Indicador</th>
                  <th>Ítem / Enunciado (Escala Likert 1 a 5)</th>
                  <th>Media Pre (O1)</th>
                  <th>Media Pos (O2)</th>
                  <th>Correlación Ítem-Total (r)</th>
                  <th>V de Aiken</th>
                </tr>
              </thead>
              <tbody id="tabla-items-cuestionario"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 6: REPORTES, EXPORTACIÓN Y EQUIPO DE SOPORTE (10 TÉCNICOS)    -->
      <!-- ================================================================= -->
      <section id="tab-reportes" class="tab-panel">
        <div class="card">
          <div class="card-header">
            <h3>Centro de Generación y Exportación de Reportes para Toma de Decisiones (Ítems 13, 14, 15 y 16)</h3>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;">
            <div class="card" style="margin:0;border-left:4px solid #16a34a;">
              <h4 style="margin:0 0 6px 0;color:#0f2547;">1. Reporte General de Incidencias (CSV / Excel)</h4>
              <p style="font-size:12px;color:#475569;">Contiene todos los tickets registrados (código lógico, IP, área, tipo de falla, tiempos de detección, respuesta, solución y técnico).</p>
              <button class="btn btn-success" onclick="exportarArchivo('csv_incidencias')">📥 Descargar CSV de Incidencias</button>
            </div>
            <div class="card" style="margin:0;border-left:4px solid #2563eb;">
              <h4 style="margin:0 0 6px 0;color:#0f2547;">2. Matriz Estadística N=45 (SPSS / Jamovi)</h4>
              <p style="font-size:12px;color:#475569;">Contiene las respuestas de los 35 usuarios y 10 técnicos en los 16 ítems con Alfa de Cronbach = 0.9468 lista para abrir en Jamovi o SPSS.</p>
              <button class="btn btn-primary" onclick="exportarArchivo('csv_spss')">📊 Descargar Matriz SPSS / Jamovi</button>
            </div>
            <div class="card" style="margin:0;border-left:4px solid #c8102e;">
              <h4 style="margin:0 0 6px 0;color:#0f2547;">3. Informe Técnico Ejecutivo Imprimible (HTML / PDF)</h4>
              <p style="font-size:12px;color:#475569;">Documento oficial con membrete institucional, tablas comparativas Preprueba vs Posprueba y listado de incidencias listo para imprimir en PDF.</p>
              <button class="btn btn-danger" onclick="exportarArchivo('html_ejecutivo')">🖨️ Abrir / Descargar Informe Ejecutivo</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>Plantel de la Unidad de Soporte Técnico TI (10 Integrantes - Tabla 1 de la Tesis)</h3>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombres y Apellidos</th>
                  <th>Especialidad Técnica</th>
                  <th>Turno</th>
                  <th>Estado</th>
                  <th>Incidencias Atendidas</th>
                </tr>
              </thead>
              <tbody id="tabla-tecnicos-body"></tbody>
            </table>
          </div>
        </div>
      </section>

    </div>
  </div>

  <!-- MODAL DIAGNÓSTICO EN VIVO DE EQUIPO -->
  <div class="modal-backdrop" id="modal-diagnostico">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modal-diag-titulo">Diagnóstico Técnico en Vivo (ICMP / ARP / TCP)</h3>
        <button class="btn btn-outline btn-sm" onclick="cerrarModal('modal-diagnostico')">✕ Cerrar</button>
      </div>
      <div id="modal-diag-body"></div>
    </div>
  </div>

  <!-- MODAL DETALLE / ATENCIÓN DE INCIDENCIA -->
  <div class="modal-backdrop" id="modal-incidencia">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modal-inc-titulo">Detalle de Incidencia</h3>
        <button class="btn btn-outline btn-sm" onclick="cerrarModal('modal-incidencia')">✕ Cerrar</button>
      </div>
      <div id="modal-inc-body"></div>
    </div>
  </div>

  <!-- MODAL NUEVA INCIDENCIA -->
  <div class="modal-backdrop" id="modal-nueva-inc">
    <div class="modal">
      <div class="modal-header">
        <h3>Registrar Nueva Incidencia Técnica</h3>
        <button class="btn btn-outline btn-sm" onclick="cerrarModal('modal-nueva-inc')">✕ Cerrar</button>
      </div>
      <div style="display:grid;gap:12px;">
        <div>
          <label style="font-size:12px;font-weight:700;display:block;margin-bottom:4px;">Equipo Informático Afectado:</label>
          <select id="new-inc-equipo" style="width:100%;"></select>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <div>
            <label style="font-size:12px;font-weight:700;display:block;margin-bottom:4px;">Tipo de Falla:</label>
            <select id="new-inc-tipo" style="width:100%;">
              <option value="Falla de Conectividad / Pérdida de Enlace ICMP">Falla de Conectividad / Pérdida de Enlace ICMP</option>
              <option value="Equipo Inoperativo / Sin Respuesta en Red (Host Down)">Equipo Inoperativo / Sin Respuesta en Red (Host Down)</option>
              <option value="Lentitud Operativa / Alta Latencia de Red">Lentitud Operativa / Alta Latencia de Red</option>
              <option value="Conflicto o Anomalía de Resolución Física ARP">Conflicto o Anomalía de Resolución Física ARP</option>
              <option value="Falla de Hardware / Periféricos Críticos">Falla de Hardware / Periféricos Críticos</option>
              <option value="Error de Servicio Tecnológico / Sistema Institucional (SIAGIE)">Error de Servicio Tecnológico / Sistema Institucional (SIAGIE)</option>
            </select>
          </div>
          <div>
            <label style="font-size:12px;font-weight:700;display:block;margin-bottom:4px;">Nivel de Severidad:</label>
            <select id="new-inc-sev" style="width:100%;">
              <option value="Crítica">Crítica</option>
              <option value="Alta">Alta</option>
              <option value="Media">Media</option>
              <option value="Baja">Baja</option>
            </select>
          </div>
        </div>
        <div>
          <label style="font-size:12px;font-weight:700;display:block;margin-bottom:4px;">Técnico de Soporte Asignado (10 Técnicos):</label>
          <select id="new-inc-tecnico" style="width:100%;"></select>
        </div>
        <div>
          <label style="font-size:12px;font-weight:700;display:block;margin-bottom:4px;">Descripción Técnica del Evento:</label>
          <textarea id="new-inc-desc" rows="3" style="width:100%;" placeholder="Describa el síntoma o resultado del diagnóstico ICMP/ARP..."></textarea>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:6px;">
          <button class="btn btn-outline" onclick="cerrarModal('modal-nueva-inc')">Cancelar</button>
          <button class="btn btn-primary" onclick="guardarNuevaIncidencia()">💾 Registrar y Emitir Alerta</button>
        </div>
      </div>
    </div>
  </div>

  <div class="toast-container" id="toast-box"></div>

<script>
  let EQUIPOS_CACHE = [];
  let TECNICOS_CACHE = [];

  function mostrarToast(msg, critico = false) {
    const box = document.getElementById('toast-box');
    const el = document.createElement('div');
    el.className = 'toast' + (critico ? ' crit' : '');
    el.innerHTML = msg;
    box.appendChild(el);
    setTimeout(() => { el.remove(); }, 5000);
  }

  function switchTab(tabId, btnEl) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    if (btnEl) btnEl.classList.add('active');

    if (tabId === 'tab-incidencias') cargarIncidencias();
    if (tabId === 'tab-alertas') cargarAlertas();
    if (tabId === 'tab-consola') cargarLogsMonitoreo();
    if (tabId === 'tab-estadistica') cargarEstadisticaTesis();
    if (tabId === 'tab-reportes') cargarTecnicos();
  }

  async function apiGet(path) {
    const res = await fetch(path);
    return await res.json();
  }

  async function apiPost(path, data = {}) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await res.json();
  }

  async function cargarDashboardKPIs() {
    const data = await apiGet('/api/kpis');
    const red = data.resumen_red;
    const inc = data.resumen_incidencias_o2;
    const tel = data.telemetria_local;

    if (tel) {
      const hw = tel.hardware_local;
      document.getElementById('top-subnet-title').textContent =
        `Red Real Conectada: Subred ${tel.subred_activa} — Estación Monitor: ${tel.nodo_monitor} (${tel.ip_monitor})`;
      document.getElementById('top-adapter-sub').textContent =
        `Adaptador Físico: ${tel.adaptador_red} | MAC: ${tel.mac_monitor} | Puerta de Enlace (Router): ${tel.puerta_enlace}`;

      document.getElementById('hw-host').textContent = `${tel.nodo_monitor} (${tel.ip_monitor})`;
      document.getElementById('hw-ip-mac').textContent = `MAC Física: ${tel.mac_monitor}`;
      document.getElementById('hw-subnet').textContent = `Subred ${tel.subred_activa}`;
      document.getElementById('hw-gw').textContent = `Router / Gateway: ${tel.puerta_enlace}`;
      document.getElementById('hw-wifi').textContent = hw.wifi.conectado
        ? `SSID: ${hw.wifi.ssid} (Señal: ${hw.wifi.senal_pct}%)`
        : `LAN Activa (${hw.wifi.radio})`;
      document.getElementById('hw-adapter').textContent = `${tel.adaptador_red} • Canal ${hw.wifi.canal} (${hw.wifi.rx_mbps})`;
      document.getElementById('hw-ram').textContent = `${hw.ram_usada_gb} GB / ${hw.ram_total_gb} GB (${hw.ram_uso_pct}%)`;
      document.getElementById('hw-uptime').textContent = `Tiempo activo SO: ${hw.uptime}`;
      document.getElementById('hw-disk').textContent = `${hw.disco_usado_gb} GB / ${hw.disco_total_gb} GB (${hw.disco_uso_pct}%)`;
      document.getElementById('hw-cpu').textContent = `${hw.cpu_nucleos} núcleos lógicos • Libre: ${hw.disco_libre_gb} GB`;
    }

    document.getElementById('kpi-reales').textContent = `${red.dispositivos_reales_operativos} / ${red.dispositivos_reales_total}`;
    document.getElementById('kpi-reales-sub').textContent = `Dispositivos físicos reales en tu red actual`;
    document.getElementById('kpi-lat-real').textContent = red.latencia_real_promedio_ms + ' ms';
    document.getElementById('kpi-tdet').textContent = inc.tiempo_deteccion_promedio_seg + ' s';

    const activos = inc.pendientes + inc.en_atencion;
    document.getElementById('kpi-activos').textContent = activos;
    document.getElementById('kpi-activos-sub').textContent = `${inc.pendientes} Pendientes • ${inc.en_atencion} En Atención • ${inc.resueltas} Resueltos`;
    document.getElementById('kpi-disp').textContent = `${red.operativos} / ${red.total_equipos}`;
    document.getElementById('kpi-disp-sub').textContent = `Disponibilidad Global: ${red.disponibilidad_pct}%`;

    document.getElementById('nav-real-count').textContent = red.dispositivos_reales_total;
    document.getElementById('nav-inc-count').textContent = activos;
    document.getElementById('nav-alert-count').textContent = inc.alertas_no_leidas;
  }

  async function cargarEquipos() {
    const area = document.getElementById('filtro-area-eq').value;
    const estado = document.getElementById('filtro-estado-eq').value;
    const list = await apiGet(`/api/equipos?area=${encodeURIComponent(area)}&estado=${encodeURIComponent(estado)}`);
    EQUIPOS_CACHE = list;

    const grid = document.getElementById('grid-equipos');
    if (list.length === 0) {
      grid.innerHTML = `<div class="card">No hay equipos para el filtro seleccionado. Presione <strong>"📡 Descubrir Red Real Ahora (1-254)"</strong>.</div>`;
      return;
    }

    grid.innerHTML = list.map(eq => {
      const esReal = eq.es_dispositivo_real === 1;
      return `
      <div class="eq-card ${eq.estado_actual} ${esReal ? 'real-device' : ''}">
        <div class="eq-top">
          <span class="eq-code">${esReal ? '📡' : '🖥️'} ${eq.codigo_logico}</span>
          <div style="display:flex;gap:4px;align-items:center;">
            ${esReal ? '<span class="real-tag">🟢 EN VIVO - RED REAL</span>' : ''}
            <span class="badge badge-${eq.estado_actual}">${eq.estado_actual}</span>
          </div>
        </div>
        <div class="eq-area">${eq.tipo_equipo} — ${eq.sistema_operativo}</div>
        <div class="eq-meta">
          <strong>IP Real:</strong> <code>${eq.ip_address}</code> | <strong>MAC:</strong> <code>${eq.mac_address}</code><br>
          <strong>Fabricante NIC:</strong> ${eq.fabricante_mac || 'IEEE Ethernet/Wi-Fi'}<br>
          <strong>Hostname / Usuario:</strong> ${eq.hostname} (${eq.usuario_asignado})<br>
          <strong>Servicios / Puertos:</strong> <code>${eq.puertos_abiertos || 'ICMP/ARP'}</code><br>
          <strong>Estado ARP:</strong> ${eq.estado_arp}
        </div>
        <div class="eq-metrics">
          <span>⏱️ Ping: ${eq.latencia_ms} ms</span>
          <span>📊 Jitter: ${eq.jitter_ms || 0.4} ms</span>
          <span>TTL: ${eq.ttl || 64}</span>
          <span>📉 Loss: ${eq.perdida_paquetes_pct}%</span>
        </div>
        <div class="eq-actions">
          <button class="btn btn-primary btn-sm" onclick="diagnosticarEquipo(${eq.id})">🔍 PING / ARP Real en Vivo</button>
          ${eq.estado_actual === 'OPERATIVO' ? `
            <button class="btn btn-danger btn-sm" onclick="simularFallaEquipo(${eq.id}, 'FORZAR_CAIDA')">⚡ Probar Alerta Caída</button>
            <button class="btn btn-warning btn-sm" onclick="simularFallaEquipo(${eq.id}, 'FORZAR_LENTITUD')">🐢 Probar Lentitud</button>
          ` : `
            <button class="btn btn-success btn-sm" onclick="simularFallaEquipo(${eq.id}, 'NORMAL')">✔ Re-sondear / Restaurar</button>
          `}
        </div>
      </div>
    `}).join('');
  }

  async function descubrirRedRealAhora() {
    const btn = document.getElementById('btn-scan-real');
    btn.disabled = true;
    btn.textContent = '⏳ Escaneando 254 IPs de tu red real...';
    mostrarToast('📡 Ejecutando barrido multihilo ICMP + ARP + TCP en toda tu subred local (1 al 254)...');
    try {
      const res = await apiPost('/api/descubrir_red_real');
      mostrarToast(
        `✅ <strong>Descubrimiento de Red Real Completado en ${res.duracion_descubrimiento_seg}s:</strong><br>` +
        `Subred: <code>${res.subred_escaneada}</code> | Gateway: <code>${res.gateway_ip}</code><br>` +
        `<strong>${res.total_hosts_reales_activos} Dispositivos Físicos Reales</strong> detectados en vivo.`
      );
      await cargarDashboardKPIs();
      await cargarEquipos();
    } finally {
      btn.disabled = false;
      btn.textContent = '📡 Descubrir Red Real Ahora (1-254)';
    }
  }

  async function diagnosticarEquipo(equipoId) {
    mostrarToast('🔍 Ejecutando ráfaga PING ICMP (3 paquetes), lectura ARP y sondeo de puertos TCP en vivo...');
    const res = await apiPost('/api/escanear_equipo', { equipo_id: equipoId });
    const eq = res.equipo;
    document.getElementById('modal-diag-titulo').textContent =
      `Diagnóstico Real en Vivo: ${eq.codigo_logico} (IP ${eq.ip_address} / MAC ${eq.mac_address})`;
    document.getElementById('modal-diag-body').innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12.5px;background:#f8fafc;padding:12px;border-radius:8px;margin-bottom:12px;">
        <div><strong>Dirección IPv4:</strong> <code>${eq.ip_address}</code></div>
        <div><strong>Dirección Física MAC:</strong> <code>${eq.mac_address}</code></div>
        <div><strong>Fabricante OUI:</strong> ${eq.fabricante_mac}</div>
        <div><strong>Estado Detectado:</strong> <span class="badge badge-${res.estado_detectado}">${res.estado_detectado}</span></div>
        <div><strong>Latencia ICMP/TCP:</strong> ${res.latencia_ms} ms (Jitter: ${res.jitter_ms} ms)</div>
        <div><strong>Pérdida de Paquetes:</strong> ${res.perdida_paquetes_pct}% (TTL: ${res.ttl})</div>
        <div><strong>Puertos / Servicios:</strong> <code>${eq.puertos_abiertos}</code></div>
        <div><strong>Tiempo de Detección:</strong> ${res.tiempo_deteccion_seg} seg</div>
      </div>
      ${res.incidencia_generada ? `
        <div style="background:#fee2e2;color:#991b1b;padding:10px 12px;border-radius:8px;margin-bottom:12px;font-size:12.5px;font-weight:700;">
          🚨 ¡ALERTA E INCIDENCIA GENERADA AUTOMÁTICAMENTE! Ticket: ${res.incidencia_generada.codigo_ticket} — ${res.incidencia_generada.tipo_falla}
        </div>
      ` : ''}
      <div class="terminal">${res.consola_diagnostico}</div>
    `;
    document.getElementById('modal-diagnostico').classList.add('open');
    document.getElementById('consola-output').textContent = res.consola_diagnostico;
    await cargarDashboardKPIs();
    await cargarEquipos();
  }

  async function simularFallaEquipo(equipoId, modo) {
    const res = await apiPost('/api/simular_equipo', { equipo_id: equipoId, modo: modo });
    const eq = res.diagnostico.equipo;
    if (modo === 'NORMAL') {
      mostrarToast(`✅ Equipo <strong>${eq.codigo_logico} (${eq.ip_address})</strong> re-sondeado en vivo: ${res.diagnostico.estado_detectado} (${res.diagnostico.latencia_ms} ms).`, false);
    } else {
      const inc = res.diagnostico.incidencia_generada;
      mostrarToast(
        `🚨 <strong>¡Falla Detectada Automáticamente!</strong><br>` +
        `Equipo: ${eq.codigo_logico} (${eq.ip_address})<br>` +
        `Estado: ${res.diagnostico.estado_detectado} | Detección: ${res.diagnostico.tiempo_deteccion_seg}s<br>` +
        (inc ? `Ticket Creado: <strong>${inc.codigo_ticket}</strong>` : ''),
        true
      );
    }
    await cargarDashboardKPIs();
    await cargarEquipos();
  }

  async function cargarIncidencias() {
    const fase = document.getElementById('filtro-fase-inc').value;
    const estado = document.getElementById('filtro-estado-inc').value;
    const sev = document.getElementById('filtro-sev-inc').value;
    const list = await apiGet(`/api/incidencias?fase=${fase}&estado=${encodeURIComponent(estado)}&severidad=${encodeURIComponent(sev)}`);
    const tbody = document.getElementById('tabla-incidencias-body');
    tbody.innerHTML = list.map(inc => {
      const stClass = inc.estado_atencion.replace(' ', '').replace('ó', 'o');
      const sevClass = inc.severidad.replace('í', 'i');
      return `
        <tr>
          <td><strong>${inc.codigo_ticket}</strong>${inc.es_reincidente ? ' <span class="badge badge-Escalado">Reincidente</span>' : ''}</td>
          <td><span class="badge">${inc.fase_estudio === 'POSPRUEBA_O2' ? 'Posprueba O2' : 'Preprueba O1'}</span></td>
          <td><strong>${inc.codigo_logico_equipo}</strong></td>
          <td>${inc.area}</td>
          <td>${inc.tipo_falla}</td>
          <td><span class="badge badge-${sevClass}">${inc.severidad}</span></td>
          <td>${inc.fecha_hora_evento}</td>
          <td>${inc.tiempo_deteccion_seg} s</td>
          <td>${inc.tiempo_respuesta_min !== null ? inc.tiempo_respuesta_min + ' min' : '<em>En espera</em>'}</td>
          <td>${inc.tiempo_solucion_min !== null ? inc.tiempo_solucion_min + ' min' : '<em>En curso</em>'}</td>
          <td><span class="badge badge-${stClass}">${inc.estado_atencion}</span></td>
          <td>${inc.tecnico_nombre || '-'}</td>
          <td>
            <button class="btn btn-primary btn-sm" onclick="verDetalleIncidencia(${inc.id})">Gestionar / Trazabilidad</button>
          </td>
        </tr>
      `;
    }).join('');
  }

  async function verDetalleIncidencia(incId) {
    const inc = await apiGet(`/api/incidencia_detalle?id=${incId}`);
    if (TECNICOS_CACHE.length === 0) {
      TECNICOS_CACHE = await apiGet('/api/tecnicos');
    }
    const tecOptions = TECNICOS_CACHE.map(t =>
      `<option value="${t.id}" ${t.id === inc.tecnico_id ? 'selected' : ''}>${t.codigo_tecnico} - ${t.nombres_apellidos} (${t.especialidad})</option>`
    ).join('');

    const histHtml = (inc.historial || []).map(h => `
      <div class="timeline-item">
        <strong>${h.fecha_hora} — ${h.accion}</strong> (${h.estado_anterior || 'N/A'} ➔ <strong>${h.estado_nuevo}</strong>)<br>
        <span style="color:#475569;">Responsable: ${h.responsable} | ${h.detalle}</span>
      </div>
    `).join('');

    document.getElementById('modal-inc-titulo').textContent = `Ficha Técnica y Seguimiento: ${inc.codigo_ticket} (${inc.codigo_logico_equipo})`;
    document.getElementById('modal-inc-body').innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12.5px;background:#f8fafc;padding:12px;border-radius:8px;margin-bottom:14px;">
        <div><strong>Equipo Afectado:</strong> ${inc.codigo_logico_equipo}</div>
        <div><strong>Área:</strong> ${inc.area}</div>
        <div><strong>Tipo de Falla:</strong> ${inc.tipo_falla}</div>
        <div><strong>Severidad:</strong> ${inc.severidad} ${inc.es_reincidente ? '(Falla Reincidente)' : ''}</div>
        <div><strong>Origen Detección:</strong> ${inc.origen_deteccion}</div>
        <div><strong>Comando Diagnóstico:</strong> <code>${inc.comando_diagnostico}</code></div>
        <div><strong>Tiempo Detección:</strong> ${inc.tiempo_deteccion_seg} seg</div>
        <div><strong>Tiempo Notificación:</strong> ${inc.tiempo_notificacion_seg} seg</div>
        <div><strong>Tiempo Respuesta:</strong> ${inc.tiempo_respuesta_min !== null ? inc.tiempo_respuesta_min + ' min' : 'Pendiente'}</div>
        <div><strong>Tiempo Solución:</strong> ${inc.tiempo_solucion_min !== null ? inc.tiempo_solucion_min + ' min' : 'Pendiente'}</div>
      </div>

      <div style="font-size:12.5px;margin-bottom:14px;">
        <strong>Descripción Técnica:</strong><br>
        <div style="background:#fff;border:1px solid #e2e8f0;padding:8px;border-radius:6px;margin-top:4px;">${inc.descripcion_tecnica}</div>
      </div>

      <h4 style="margin:0 0 8px 0;color:#0f2547;font-size:13.5px;">Actualizar Estado y Registrar Solución Técnica (ITIL v4)</h4>
      <div style="display:grid;gap:10px;background:#f1f5f9;padding:12px;border-radius:8px;margin-bottom:16px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <div>
            <label style="font-size:11.5px;font-weight:700;">Nuevo Estado de Atención:</label>
            <select id="upd-inc-estado" style="width:100%;">
              <option value="Pendiente" ${inc.estado_atencion === 'Pendiente' ? 'selected' : ''}>Pendiente</option>
              <option value="En Atención" ${inc.estado_atencion === 'En Atención' ? 'selected' : ''}>En Atención</option>
              <option value="Resuelto" ${inc.estado_atencion === 'Resuelto' ? 'selected' : ''}>Resuelto (Restaurar Equipo)</option>
              <option value="Escalado" ${inc.estado_atencion === 'Escalado' ? 'selected' : ''}>Escalado</option>
            </select>
          </div>
          <div>
            <label style="font-size:11.5px;font-weight:700;">Técnico Responsable:</label>
            <select id="upd-inc-tec" style="width:100%;">${tecOptions}</select>
          </div>
        </div>
        <div>
          <label style="font-size:11.5px;font-weight:700;">Acción / Solución Técnica Aplicada:</label>
          <textarea id="upd-inc-sol" rows="2" style="width:100%;" placeholder="Ingrese el procedimiento técnico o solución aplicada...">${inc.solucion_aplicada || ''}</textarea>
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end;">
          <button class="btn btn-warning btn-sm" onclick="cambiarEstadoIncidencia(${inc.id}, 'En Atención')">🔧 Pasar a En Atención</button>
          <button class="btn btn-success btn-sm" onclick="cambiarEstadoIncidencia(${inc.id}, 'Resuelto')">✅ Marcar como Resuelto y Restaurar Equipo</button>
          <button class="btn btn-primary btn-sm" onclick="cambiarEstadoIncidencia(${inc.id}, null)">💾 Guardar Cambios</button>
        </div>
      </div>

      <h4 style="margin:0 0 8px 0;color:#0f2547;font-size:13.5px;">Historial de Trazabilidad del Caso</h4>
      <div>${histHtml}</div>
    `;
    document.getElementById('modal-incidencia').classList.add('open');
  }

  async function cambiarEstadoIncidencia(incId, forzarEstado) {
    const nuevoEstado = forzarEstado || document.getElementById('upd-inc-estado').value;
    const tecId = parseInt(document.getElementById('upd-inc-tec').value, 10);
    let sol = document.getElementById('upd-inc-sol').value.trim();
    if (!sol && nuevoEstado === 'Resuelto') {
      sol = 'Restablecimiento de enlace de red, verificación de tabla ARP y validación de paquetes ICMP sin pérdida (0% loss).';
    }
    await apiPost('/api/actualizar_incidencia', {
      incidencia_id: incId,
      nuevo_estado: nuevoEstado,
      tecnico_id: tecId,
      solucion: sol
    });
    mostrarToast(`✅ Ticket actualizado a estado <strong>${nuevoEstado}</strong>.`);
    cerrarModal('modal-incidencia');
    await cargarDashboardKPIs();
    await cargarIncidencias();
    await cargarEquipos();
  }

  async function abrirModalNuevaIncidencia() {
    const allEq = await apiGet('/api/equipos?area=TODAS&estado=TODOS');
    if (TECNICOS_CACHE.length === 0) TECNICOS_CACHE = await apiGet('/api/tecnicos');

    document.getElementById('new-inc-equipo').innerHTML = allEq.map(e =>
      `<option value="${e.id}">${e.es_dispositivo_real ? '🟢 [RED REAL]' : '🏛️'} ${e.codigo_logico} (${e.ip_address} / ${e.mac_address}) — ${e.area}</option>`
    ).join('');
    document.getElementById('new-inc-tecnico').innerHTML = TECNICOS_CACHE.map(t =>
      `<option value="${t.id}">${t.codigo_tecnico} - ${t.nombres_apellidos} (${t.especialidad})</option>`
    ).join('');
    document.getElementById('new-inc-desc').value = '';
    document.getElementById('modal-nueva-inc').classList.add('open');
  }

  async function guardarNuevaIncidencia() {
    const eqId = parseInt(document.getElementById('new-inc-equipo').value, 10);
    const tipo = document.getElementById('new-inc-tipo').value;
    const sev = document.getElementById('new-inc-sev').value;
    const tecId = parseInt(document.getElementById('new-inc-tecnico').value, 10);
    const desc = document.getElementById('new-inc-desc').value.trim() || `Incidencia reportada y verificada por monitoreo ICMP/ARP (${tipo}).`;

    const inc = await apiPost('/api/crear_incidencia', {
      equipo_id: eqId,
      tipo_falla: tipo,
      severidad: sev,
      tecnico_id: tecId,
      descripcion_tecnica: desc
    });
    mostrarToast(`🚨 Ticket <strong>${inc.codigo_ticket}</strong> registrado y alerta emitida en ${inc.tiempo_notificacion_seg}s.`, true);
    cerrarModal('modal-nueva-inc');
    await cargarDashboardKPIs();
    await cargarIncidencias();
    await cargarEquipos();
  }

  function cerrarModal(id) {
    document.getElementById(id).classList.remove('open');
  }

  async function cargarAlertas() {
    const list = await apiGet('/api/alertas');
    const tbody = document.getElementById('tabla-alertas-body');
    tbody.innerHTML = list.map(a => `
      <tr style="${a.leida ? 'opacity:0.72;' : 'font-weight:600;background:#fffbeb;'}">
        <td>#${a.id}</td>
        <td><span class="badge badge-${a.nivel.replace('Í', 'I')}">${a.nivel}</span></td>
        <td><strong>${a.codigo_ticket || '-'}</strong></td>
        <td>${a.codigo_logico_equipo} (<code>${a.ip_address}</code>)</td>
        <td>${a.area}</td>
        <td><code>${a.protocolo}</code></td>
        <td>${a.mensaje}</td>
        <td>${a.tiempo_notificacion_seg} s</td>
        <td>${a.fecha_hora}</td>
        <td>${a.leida ? '<span class="badge badge-OPERATIVO">Atendida/Leída</span>' : '<span class="badge badge-Pendiente">Nueva Alerta</span>'}</td>
      </tr>
    `).join('');
  }

  async function marcarTodasAlertasLeidas() {
    await apiPost('/api/marcar_alertas_leidas', {});
    mostrarToast('✔ Todas las alertas han sido marcadas como leídas.');
    await cargarAlertas();
    await cargarDashboardKPIs();
  }

  async function ejecutarPingRealConsola() {
    const ip = document.getElementById('input-ip-ping').value.trim() || '192.168.0.1';
    const box = document.getElementById('consola-output');
    box.textContent = `Ejecutando ráfaga PING ICMP real y escaneo de puertos TCP hacia ${ip}...\n`;
    const res = await apiPost('/api/ping_real', { ip: ip });
    box.textContent = `$ ${res.command}\n\n${res.raw_output}\n\n` +
      `[Resultado Motor Python en Vivo]:\n` +
      `  • Alcanzable ICMP : ${res.reachable}\n` +
      `  • Latencia Media  : ${res.latency_ms} ms (Jitter: ${res.jitter_ms} ms)\n` +
      `  • Pérdida Paquetes: ${res.packet_loss_pct}% | TTL: ${res.ttl}\n` +
      `  • Puertos TCP     : ${(res.puertos_abiertos || []).join(', ') || 'Ningún puerto común expuesto'}`;
  }

  async function ejecutarArpRealConsola() {
    const box = document.getElementById('consola-output');
    box.textContent = `Consultando tabla ARP física (Capa 2) del sistema operativo (arp -a)...\n`;
    const res = await apiGet('/api/arp_real');
    let txt = `$ arp -a\nTotal de dispositivos físicos reales resueltos en Capa 2 ARP: ${res.entradas.length}\n\n`;
    txt += `DIRECCIÓN IPv4        DIRECCIÓN FÍSICA (MAC)     TIPO         FABRICANTE OUI IDENTIFICADO\n`;
    txt += `------------------------------------------------------------------------------------------------------\n`;
    res.entradas.forEach(e => {
      txt += `${e.ip.padEnd(22)}${e.mac.padEnd(27)}${e.tipo.padEnd(13)}${e.fabricante || ''}\n`;
    });
    box.textContent = txt;
  }

  async function cargarLogsMonitoreo() {
    const list = await apiGet('/api/logs_monitoreo');
    const tbody = document.getElementById('tabla-logs-body');
    tbody.innerHTML = list.map(l => `
      <tr>
        <td>${l.fecha_hora}</td>
        <td><strong>${l.codigo_logico}</strong></td>
        <td><code>${l.ip_address}</code></td>
        <td><code>${l.mac_address}</code></td>
        <td>${l.protocolo}</td>
        <td><span class="badge badge-${l.resultado}">${l.resultado}</span></td>
        <td>${l.latencia_ms} ms</td>
        <td>${l.perdida_pct}%</td>
        <td>${l.estado_arp}</td>
      </tr>
    `).join('');
  }

  async function cargarEstadisticaTesis() {
    const st = await apiGet('/api/estadistica_tesis');
    const kpis = await apiGet('/api/kpis');
    const comp = kpis.comparativa_pre_vs_pos;

    const cron = st.confiabilidad_alfa_cronbach;
    const tGlob = st.contraste_hipotesis_encuesta_global.t_student;
    const wGlob = st.contraste_hipotesis_encuesta_global.wilcoxon;
    const tResp = st.contraste_tiempos_respuesta_min.t_student;
    const tSol = st.contraste_tiempos_solucion_min.t_student;

    document.getElementById('stat-alfa').textContent = cron.alfa_cronbach;
    document.getElementById('stat-t').textContent = 't = ' + tGlob.t_student;
    document.getElementById('stat-p').textContent = `gl = ${tGlob.grados_libertad}, p ${tGlob.p_texto}`;
    document.getElementById('stat-w').textContent = 'Z = ' + wGlob.z_aprox;

    document.getElementById('tabla-comparativa-o1-o2').innerHTML = `
      <tr>
        <td><strong>D1: Tiempo Promedio de Detección de Fallas</strong></td>
        <td>${comp.tiempo_deteccion_min.pre_o1} min (Reporte manual usuario)</td>
        <td><strong>${comp.tiempo_deteccion_min.pos_o2_seg} seg</strong> (${comp.tiempo_deteccion_min.pos_o2} min - ICMP/ARP)</td>
        <td><span class="badge badge-OPERATIVO">-${comp.tiempo_deteccion_min.mejora_pct}%</span></td>
        <td>p &lt; 0.001 (Mejora altamente significativa)</td>
      </tr>
      <tr>
        <td><strong>D2/D3: Cobertura de Alertas Automáticas Oportunas</strong></td>
        <td>${comp.cobertura_alertas_pct.pre_o1}% (Sin alertas automáticas)</td>
        <td><strong>${comp.cobertura_alertas_pct.pos_o2}%</strong> (Notificación en ~1.4 seg)</td>
        <td><span class="badge badge-OPERATIVO">+100.0%</span></td>
        <td>Cobertura censal en la red monitoreada</td>
      </tr>
      <tr>
        <td><strong>D3/D4: Tiempo Promedio de Respuesta de Soporte TI</strong></td>
        <td>${tResp.media_pre} min (DE: ${tResp.sd_pre})</td>
        <td><strong>${tResp.media_pos} min</strong> (DE: ${tResp.sd_pos})</td>
        <td><span class="badge badge-OPERATIVO">-${comp.tiempo_respuesta_min.mejora_pct}%</span></td>
        <td>t = ${tResp.t_student}, p ${tResp.p_texto}</td>
      </tr>
      <tr>
        <td><strong>D4: Tiempo Promedio de Solución de Incidencias</strong></td>
        <td>${tSol.media_pre} min (DE: ${tSol.sd_pre})</td>
        <td><strong>${tSol.media_pos} min</strong> (DE: ${tSol.sd_pos})</td>
        <td><span class="badge badge-OPERATIVO">-${comp.tiempo_solucion_min.mejora_pct}%</span></td>
        <td>t = ${tSol.t_student}, p ${tSol.p_texto}</td>
      </tr>
      <tr>
        <td><strong>D4: Tasa de Reincidencia de Fallas</strong></td>
        <td>${comp.tasa_reincidencia_pct.pre_o1}%</td>
        <td><strong>${comp.tasa_reincidencia_pct.pos_o2}%</strong></td>
        <td><span class="badge badge-OPERATIVO">Reducción de fallas recurrentes</span></td>
        <td>Control preventivo por historial de equipo</td>
      </tr>
      <tr>
        <td><strong>Cuestionario Global (16 Ítems Likert, N = 45)</strong></td>
        <td>${tGlob.media_pre} pts (DE: ${tGlob.sd_pre})</td>
        <td><strong>${tGlob.media_pos} pts</strong> (DE: ${tGlob.sd_pos}) de 80 máx.</td>
        <td><span class="badge badge-OPERATIVO">+${tGlob.diferencia_media} pts</span></td>
        <td>t = ${tGlob.t_student} (gl=44), Wilcoxon Z = ${wGlob.z_aprox}, p &lt; 0.001</td>
      </tr>
    `;

    document.getElementById('tabla-items-cuestionario').innerHTML = st.items_cuestionario_evaluados.map(it => `
      <tr>
        <td><strong>Ítem ${it.num}</strong></td>
        <td>${it.dimension}</td>
        <td>${it.indicador}</td>
        <td>${it.texto}</td>
        <td>${it.media_pre_o1}</td>
        <td><strong>${it.media_pos_o2}</strong></td>
        <td><span class="badge badge-OPERATIVO">r = ${it.correlacion_item_total}</span></td>
        <td><strong>${it.v_aiken.toFixed(2)}</strong></td>
      </tr>
    `).join('');
  }

  async function cargarTecnicos() {
    const list = await apiGet('/api/tecnicos');
    TECNICOS_CACHE = list;
    document.getElementById('tabla-tecnicos-body').innerHTML = list.map(t => `
      <tr>
        <td><strong>${t.codigo_tecnico}</strong></td>
        <td>${t.nombres_apellidos}</td>
        <td>${t.especialidad}</td>
        <td>${t.turno}</td>
        <td><span class="badge badge-OPERATIVO">${t.estado_disponibilidad}</span></td>
        <td><strong>${t.casos_atendidos} casos resueltos</strong></td>
      </tr>
    `).join('');
  }

  function exportarArchivo(tipo) {
    window.open(`/api/exportar?tipo=${encodeURIComponent(tipo)}`, '_blank');
    mostrarToast('📥 Reporte generado y exportado correctamente.');
  }

  window.addEventListener('DOMContentLoaded', async () => {
    await cargarDashboardKPIs();
    await cargarEquipos();
    // Si aún no hay dispositivos reales cargados, lanzar descubrimiento automático al abrir
    const kpis = await apiGet('/api/kpis');
    if (kpis.resumen_red.dispositivos_reales_total === 0) {
      await descubrirRedRealAhora();
    }
    setInterval(async () => {
      await cargarDashboardKPIs();
      const activeTab = document.querySelector('.tab-panel.active');
      if (activeTab && activeTab.id === 'tab-monitoreo') {
        await cargarEquipos();
      }
    }, 6000);
  });
</script>
</body>
</html>
"""
