-- =============================================================================
-- ESQUEMA POSTGRESQL PARA SUPABASE — SIGIF-EP PIURA 2026
-- Tesis: Aplicación para la detección y gestión de incidencias y fallas en
--        equipos informáticos de una entidad educativa pública Piura 2026
-- Autores: Toro Agurto, Mario Andre & Nevado Fiestas, Jefferson Deyfrank
-- Universidad César Vallejo (UCV) - Filial Piura, 2026
-- =============================================================================

CREATE TABLE IF NOT EXISTS personal_soporte (
    id SERIAL PRIMARY KEY,
    codigo_tecnico VARCHAR(20) UNIQUE NOT NULL,
    nombres_apellidos VARCHAR(150) NOT NULL,
    especialidad VARCHAR(180) NOT NULL,
    turno VARCHAR(30) NOT NULL,
    estado_disponibilidad VARCHAR(40) DEFAULT 'Disponible',
    casos_atendidos INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    codigo_logico VARCHAR(40) UNIQUE NOT NULL,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    mac_address VARCHAR(30) NOT NULL,
    area VARCHAR(150) NOT NULL,
    usuario_asignado VARCHAR(150) NOT NULL,
    cargo_usuario VARCHAR(150) NOT NULL,
    tipo_equipo VARCHAR(100) NOT NULL,
    sistema_operativo VARCHAR(100) NOT NULL,
    estado_actual VARCHAR(30) DEFAULT 'OPERATIVO',
    latencia_ms NUMERIC(8,2) DEFAULT 5.0,
    jitter_ms NUMERIC(8,2) DEFAULT 0.8,
    ttl INTEGER DEFAULT 64,
    perdida_paquetes_pct NUMERIC(5,2) DEFAULT 0.0,
    estado_arp VARCHAR(120) DEFAULT 'RESUELTO (Dinámico)',
    fabricante_mac VARCHAR(150) DEFAULT 'Adaptador Ethernet/Wi-Fi',
    puertos_abiertos VARCHAR(200) DEFAULT 'ICMP Echo',
    es_dispositivo_real INTEGER DEFAULT 0,
    fallas_acumuladas INTEGER DEFAULT 0,
    es_monitoreado INTEGER DEFAULT 1,
    modo_simulacion VARCHAR(30) DEFAULT 'NORMAL',
    ultimo_escaneo TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incidencias (
    id SERIAL PRIMARY KEY,
    codigo_ticket VARCHAR(30) UNIQUE NOT NULL,
    equipo_id INTEGER REFERENCES equipos(id) ON DELETE CASCADE,
    codigo_logico_equipo VARCHAR(40) NOT NULL,
    area VARCHAR(150) NOT NULL,
    tipo_falla VARCHAR(180) NOT NULL,
    dimension_asociada VARCHAR(10) NOT NULL,
    severidad VARCHAR(30) NOT NULL,
    origen_deteccion VARCHAR(120) NOT NULL,
    descripcion_tecnica TEXT NOT NULL,
    comando_diagnostico VARCHAR(250) NOT NULL,
    fecha_hora_evento TIMESTAMP DEFAULT NOW(),
    fecha_hora_alerta TIMESTAMP,
    fecha_hora_atencion TIMESTAMP,
    fecha_hora_solucion TIMESTAMP,
    tiempo_deteccion_seg NUMERIC(8,2) NOT NULL,
    tiempo_notificacion_seg NUMERIC(8,2) NOT NULL,
    tiempo_respuesta_min NUMERIC(8,2),
    tiempo_solucion_min NUMERIC(8,2),
    alerta_emitida INTEGER DEFAULT 1,
    es_reincidente INTEGER DEFAULT 0,
    estado_atencion VARCHAR(30) DEFAULT 'Pendiente',
    tecnico_id INTEGER REFERENCES personal_soporte(id),
    tecnico_nombre VARCHAR(150),
    solucion_aplicada TEXT,
    fase_estudio VARCHAR(30) DEFAULT 'POSPRUEBA_O2'
);

CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER REFERENCES incidencias(id) ON DELETE CASCADE,
    codigo_ticket VARCHAR(30),
    codigo_logico_equipo VARCHAR(40) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    area VARCHAR(150) NOT NULL,
    nivel VARCHAR(30) NOT NULL,
    protocolo VARCHAR(80) NOT NULL,
    mensaje TEXT NOT NULL,
    tiempo_notificacion_seg NUMERIC(8,2) NOT NULL,
    fecha_hora TIMESTAMP DEFAULT NOW(),
    leida INTEGER DEFAULT 0,
    destinatario VARCHAR(150) DEFAULT 'Unidad de Soporte Técnico TI'
);

CREATE TABLE IF NOT EXISTS usuarios_sistema (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    password_hint VARCHAR(50) NOT NULL,
    nombres_apellidos VARCHAR(150) NOT NULL,
    rol VARCHAR(30) NOT NULL, -- ADMINISTRADOR, SUB_ADMINISTRADOR, USUARIO
    area VARCHAR(150) NOT NULL,
    cargo VARCHAR(150) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    ultimo_acceso TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auditoria_accesos (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    nombres_apellidos VARCHAR(150) NOT NULL,
    rol VARCHAR(30) NOT NULL,
    accion VARCHAR(200) NOT NULL,
    ip_origen VARCHAR(50) NOT NULL,
    fecha_hora TIMESTAMP DEFAULT NOW()
);

