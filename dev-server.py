#!/usr/bin/env python3
"""Serveur local sans mise en cache (évite les réponses 304 sur styles.css pendant le dev)."""
import http.server
import os
import socketserver

PORT = 8765

# Toujours servir les fichiers depuis le dossier de CE script (évite d’afficher un autre index.html si le
# terminal n’était pas dans Yoni-Noy_Wedding — d’où Noy / Yoni encore visibles).
_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_ROOT)


class DevHandler(http.server.SimpleHTTPRequestHandler):
    def _strip_conditional_headers(self):
        """Empêche Python de répondre 304 (If-Modified-Since / ETag)."""
        for h in ("If-Modified-Since", "If-None-Match"):
            if h in self.headers:
                del self.headers[h]

    def do_GET(self):
        self._strip_conditional_headers()
        super().do_GET()

    def do_HEAD(self):
        self._strip_conditional_headers()
        super().do_HEAD()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    idx = os.path.join(_ROOT, "index.html")
    try:
        with open(idx, "r", encoding="utf-8") as f:
            raw = f.read()
        if "Yoni & Noy" in raw or 'title>Yoni' in raw:
            print("index.html: contenu Yoni & Noy (OK).")
        elif "Alon & Elsa" in raw or "alone-elsa" in raw:
            print("!!! ATTENTION: index.html contient le faire-part Alon & Elsa — mauvais dépôt pour ce serveur.")
        else:
            print("index.html: type de faire-part non reconnu.")
    except OSError as e:
        print(f"Impossible de lire index.html: {e}")
    print(f"Dossier servi: {_ROOT}")
    print(f"http://127.0.0.1:{PORT}/  (évite le 304 — rechargement complet des fichiers)")
    with socketserver.TCPServer(("127.0.0.1", PORT), DevHandler) as httpd:
        httpd.serve_forever()
