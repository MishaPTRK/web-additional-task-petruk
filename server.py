import json
import socket
from urllib.parse import parse_qs, urlparse

BIND_ADDR = "127.0.0.1"
BIND_PORT = 8080


def decode_http(raw):
    chunks = raw.split("\r\n\r\n", 1)
    head = chunks[0]
    payload = chunks[1] if len(chunks) > 1 else ""

    head_lines = head.split("\r\n")
    if not head_lines or not head_lines[0]:
        return None

    start_line = head_lines[0].split(" ")
    verb = start_line[0]
    target = start_line[1] if len(start_line) > 1 else "/"

    parsed = urlparse(target)
    route = parsed.path
    params = parse_qs(parsed.query)

    meta = {}
    for entry in head_lines[1:]:
        if ":" in entry:
            name, val = entry.split(":", 1)
            meta[name.strip().lower()] = val.strip()

    return {
        "method": verb,
        "path": route,
        "query_params": params,
        "headers": meta,
        "body": payload,
    }


def make_reply(code, reason, mime, payload):
    raw_body = (
        json.dumps(payload) if isinstance(payload, dict) else payload
    ).encode("utf-8")

    head_lines = [
        f"HTTP/1.1 {code} {reason}",
        f"Content_type: {mime}; charset=utf-8",
        f"Content-len : {len(raw_body)}",
        "Connection: close",
        "",
        "",
    ]

    return "\r\n".join(head_lines).encode("utf-8") + raw_body


def serve_connection(conn):
    incoming = conn.recv(4096).decode("utf-8", errors="ignore")
    if not incoming:
        conn.close()
        return

    req = decode_http(incoming)
    if not req:
        conn.close()
        return

    verb = req["method"]
    route = req["path"]

    if verb == "GET":
        if route in ("/", "/index.html"):
            page = "<html><body><h1>Server Works!</h1></body></html>"
            reply = make_reply(200, "OK", "text/html", page)
        elif route == "/page":
            ident = req["query_params"].get("id", ["N/A"])[0]
            page = f"<html><body><h1>Page ID: {ident}</h1></body></html>"
            reply = make_reply(200, "OK", "text/html", page)
        else:
            reply = make_reply(
                404, "Not Found", "text/html", "<h1>404 Not Found</h1>"
            )
    elif verb == "POST":
        try:
            data = json.loads(req["body"]) if req["body"] else {}
            answer = {
                "message": "Data received successfully!",
                "received_data": data,
                "headers_received": req["headers"],
            }
            reply = make_reply(200, "OK", "application/json", answer)
        except json.JSONDecodeError:
            reply = make_reply(
                400,
                "Bad Request",
                "application/json",
                {"error": "Invalid JSON"},
            )
    else:
        reply = make_reply(
            405, "Method not provided", "text/plain", "Method Not Allow"
        )

    conn.sendall(reply)
    conn.close()


def start():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((BIND_ADDR, BIND_PORT))
    listener.listen(5)

    print(f"Server listen http://{BIND_ADDR}:{BIND_PORT}")

    try:
        while True:
            conn, _ = listener.accept()
            serve_connection(conn)
    except KeyboardInterrupt:
        print("\nStop server")
    finally:
        listener.close()


if __name__ == "__main__":
    start()