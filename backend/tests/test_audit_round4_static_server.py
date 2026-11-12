"""End-to-end local static HTTP smoke tests for compression and caching."""
import functools
import gzip
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'serve_frontend.py'


def test_gzip_static_js_and_conditional_revalidation():
    spec = importlib.util.spec_from_file_location('mw_static', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(module.MathWebStaticHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f'http://127.0.0.1:{server.server_port}/js/battle.js'
        with urlopen(Request(url, headers={'Accept-Encoding': 'gzip'})) as response:
            assert response.status == 200
            assert response.headers['Content-Encoding'] == 'gzip'
            assert response.headers['Cache-Control'] == 'no-cache'
            compressed = response.read()
            assert gzip.decompress(compressed) == (ROOT / 'js/battle.js').read_bytes()
            assert len(compressed) < len(gzip.decompress(compressed)) * 0.5
            etag = response.headers['ETag']
        try:
            urlopen(Request(url, headers={'Accept-Encoding': 'gzip', 'If-None-Match': etag}))
            assert False, 'Conditional request should return HTTP 304'
        except HTTPError as error:
            assert error.code == 304
        with urlopen(Request(url)) as response:
            assert response.status == 200
            assert response.headers.get('Content-Encoding') is None
            assert response.read() == (ROOT / 'js/battle.js').read_bytes()
        with urlopen(Request(f'http://127.0.0.1:{server.server_port}/index.html', method='HEAD')) as response:
            assert response.status == 200
            assert not response.read()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
