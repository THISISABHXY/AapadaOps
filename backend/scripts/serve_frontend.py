"""Production SPA static server for AapadaOps Frontend."""

import http.server
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        # Resolve target path
        clean_path = self.path.split("?")[0].lstrip("/")
        target_file = DIST_DIR / clean_path

        # If requesting an asset file or favicon that doesn't exist, let it 404
        if clean_path.startswith("assets/") or clean_path.endswith((".js", ".css", ".svg", ".png", ".ico")):
            return super().do_GET()

        # For all other SPA client-side routes (/login, /dashboard, /incidents, etc.), serve index.html
        if not target_file.is_file():
            self.path = "/index.html"

        return super().do_GET()

    def end_headers(self):
        # Inject standard security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def run():
    print(f"[INFO] Starting AapadaOps Production Frontend server on http://127.0.0.1:{PORT}...")
    print(f"[INFO] Serving static directory: {DIST_DIR}")
    with socketserver.TCPServer(("127.0.0.1", PORT), SPAHandler) as httpd:
        print(f"[READY] Frontend server listening at http://127.0.0.1:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run()

