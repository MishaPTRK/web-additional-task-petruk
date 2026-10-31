# Socket HTTP Server

A basic HTTP/1.1 server written in Python using only the `socket` module (no web frameworks or HTTP libraries).

## Features

- **GET** – serves static files (HTML/CSS) from `static/` and handles query parameters (`/page?id=5`)
- **Headers** – parses the request line, headers, query string and body (`Content-Length`)
- **POST** – `/api/echo` accepts `application/json`, parses the body and responds with JSON
- **Errors** – returns proper `400`, `403`, `404`, `405`, `415` responses
- `/debug` – returns the parsed method, path, query and headers as JSON

## Run

```bash
python3 server.py
```

Open http://localhost:8080 (Python 3.8+, no dependencies).

## Examples

```bash
curl "http://localhost:8080/page?id=5"
```
