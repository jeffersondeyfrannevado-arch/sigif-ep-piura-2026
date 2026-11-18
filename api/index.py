# -*- coding: utf-8 -*-
"""
Entrypoint Serverless para Vercel (@vercel/python)
Expone `handler(BaseHTTPRequestHandler)` integrando toda la lógica de SIGIF-EP Piura 2026.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from analytics_engine import AnalyticsAndReportEngine
from database import DatabaseManager
from network_scanner import NetworkScannerEngine
from web_server import SIGIFRequestHandler

_db = DatabaseManager()
_scanner = NetworkScannerEngine(_db)
_analytics = AnalyticsAndReportEngine(_db)


class handler(SIGIFRequestHandler):
    db = _db
    scanner = _scanner
    analytics = _analytics
