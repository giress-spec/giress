"""Minimal static file server for the Base44 sandbox preview.

The repo is a single static index.html with no build step, so this serves the
bind-mounted source directory directly (edits appear on refresh). It exists
instead of stock nginx because the mounted repo root is only readable by root,
and it keeps repository metadata such as .git and .base44 off the preview.
"""
import http.server
import os
import posixpath
import socketserver

ROOT = "/app"
PORT = 3000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        resolved = super().translate_path(path)
        relative = os.path.relpath(resolved, ROOT)
        parts = [] if relative == "." else posixpath.normpath(relative).split("/")
        if any(part.startswith(".") for part in parts):
            self.path = "/__not_found__"
            return os.path.join(ROOT, "__not_found__")
        return resolved

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("Serving %s on port %d" % (ROOT, PORT), flush=True)
    httpd.serve_forever()
