#!/usr/bin/env python3
"""Local web interface for the Word Hunt solver.

    python3 server.py            # then open http://localhost:8000
    python3 server.py --port 9000 --dict words.txt
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from wordhunt import DEFAULT_DICT, build_trie, load_words, parse_board, score, solve

HERE = Path(__file__).resolve().parent
INDEX = HERE / "static" / "index.html"
MAX_SIZE = 5  # largest board side the server accepts


class Handler(BaseHTTPRequestHandler):
    trie = None

    def _send(self, status, body, content_type):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            self._send(200, INDEX.read_text(encoding="utf-8"), "text/html; charset=utf-8")
        elif url.path == "/solve":
            text = parse_qs(url.query).get("board", [""])[0]
            try:
                board = parse_board(text)
            except ValueError as e:
                return self._json(400, {"error": str(e)})
            if len(board) > MAX_SIZE:
                return self._json(400, {"error": f"Board is larger than {MAX_SIZE}x{MAX_SIZE}."})
            found = solve(board, self.trie)
            words = sorted(found, key=lambda w: (-score(w), w))
            self._json(200, {
                "size": len(board),
                "total": sum(score(w) for w in words),
                "words": [{"word": w, "score": score(w), "path": found[w]} for w in words],
            })
        else:
            self._json(404, {"error": "Not found"})

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def main():
    ap = argparse.ArgumentParser(description="Word Hunt solver web interface")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("-d", "--dict", default=DEFAULT_DICT, help="word list file")
    args = ap.parse_args()

    Handler.trie = build_trie(load_words(args.dict, MAX_SIZE * MAX_SIZE))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Word Hunt solver running at http://localhost:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
