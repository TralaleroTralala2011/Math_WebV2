"""MATH_WEB local frontend server with optional gzip for HTML/CSS/JS/JSON.

Keeps the same files, URLs, layout and port as `python -m http.server`.
Modern browsers negotiate gzip automatically. Files still revalidate after edits.
"""
from __future__ import annotations

import argparse
import functools
import gzip
import os
from email.utils import formatdate, parsedate_to_datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
COMPRESSIBLE = {'.html', '.css', '.js', '.json', '.svg', '.txt', '.xml'}
PRIVATE_DIRS = {'backend', 'mathweb_work', 'scripts', '__pycache__', '.git', '.venv', 'venv'}
PRIVATE_SUFFIXES = {'.db', '.sqlite', '.sqlite3', '.py', '.pyc', '.pem', '.key'}


@functools.lru_cache(maxsize=128)
def _compressed_file(path: str, mtime_ns: int, size: int) -> bytes:
    """Keep only up to 128 recently requested compressed assets in memory."""
    return gzip.compress(Path(path).read_bytes(), compresslevel=5, mtime=0)


class MathWebStaticHandler(SimpleHTTPRequestHandler):
    def _private_request(self) -> bool:
        # A frontend server must never publish the DB or login signing key.
        # This applies to GET, HEAD and gzip, including URL-encoded requests.
        path = unquote(urlsplit(self.path).path).replace('\\', '/')
        pieces = [piece for piece in path.split('/') if piece]
        return any(piece in ('..', '.') or piece.startswith('.') for piece in pieces) or (
            bool(pieces) and pieces[0].lower() in PRIVATE_DIRS
        ) or any(Path(piece).suffix.lower() in PRIVATE_SUFFIXES for piece in pieces)

    def list_directory(self, path):
        self.send_error(404, 'Directory listing disabled')
        return None

    def end_headers(self):
        # Revalidate when source files change, including during development.
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def send_head(self):
        if self._private_request():
            self.send_error(404, 'Not found')
            return None
        path = Path(self.translate_path(self.path))
        if (
            path.suffix.lower() not in COMPRESSIBLE
            or not path.is_file()
            or 'gzip' not in self.headers.get('Accept-Encoding', '').lower()
            or self.headers.get('Range')
        ):
            return super().send_head()
        try:
            stat = path.stat()
            if stat.st_size < 1024 or stat.st_size > 4 * 1024 * 1024:
                return super().send_head()

            etag = f'W/"{stat.st_mtime_ns:x}-{stat.st_size:x}"'
            last_modified = formatdate(stat.st_mtime, usegmt=True)
            not_modified = self.headers.get('If-None-Match', '').strip() == etag
            if not self.headers.get('If-None-Match') and self.headers.get('If-Modified-Since'):
                try:
                    ims = parsedate_to_datetime(self.headers['If-Modified-Since'])
                    not_modified = int(ims.timestamp()) >= int(stat.st_mtime)
                except (ValueError, OverflowError, TypeError):
                    pass
            if not_modified:
                self.send_response(304)
                self.send_header('ETag', etag)
                self.send_header('Vary', 'Accept-Encoding')
                self.send_header('Last-Modified', last_modified)
                self.end_headers()
                return None

            content = _compressed_file(str(path), stat.st_mtime_ns, stat.st_size)
            self.send_response(200)
            self.send_header('Content-Type', self.guess_type(str(path)))
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('ETag', etag)
            self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Last-Modified', last_modified)
            self.end_headers()
            # A BytesIO stream lets SimpleHTTPRequestHandler.do_GET copy the
            # compressed body without keeping sockets or files open afterward.
            from io import BytesIO
            return BytesIO(content)
        except OSError:
            return super().send_head()


def main():
    parser = argparse.ArgumentParser(description='MATH_WEB frontend HTTP server')
    parser.add_argument('port', type=int, nargs='?', default=5500)
    parser.add_argument('--bind', default='127.0.0.1')
    args = parser.parse_args()
    handler = functools.partial(MathWebStaticHandler, directory=str(ROOT))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'MATH_WEB frontend: http://{args.bind}:{server.server_port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
