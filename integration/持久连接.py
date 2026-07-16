#!/usr/bin/env python3
"""Drive a real pipelined HTTP/1.1 connection against the YanXu fixture."""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time
from pathlib import Path


SUCCESS_MARKER = "言讯持久连接通过"
UPGRADE_MARKER = "言讯升级通过"
PIPELINED_REQUEST = (
    b"POST /one?q=1 HTTP/1.1\r\n"
    b"Host: localhost\r\n"
    b"Content-Length: 1\r\n"
    b"\r\n"
    b"h"
    b"POST /two HTTP/1.1\r\n"
    b"Host: localhost\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"Trailer: X-Check\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    b"1\r\nW\r\n"
    b"0\r\n"
    b"X-Check: ok\r\n"
    b"\r\n"
)
EXPECTED_RESPONSE = (
    b"HTTP/1.1 103 Early Hints\r\n"
    b"link: </style.css>; rel=preload\r\n"
    b"\r\n"
    b"HTTP/1.1 200 OK\r\n"
    b"content-type: text/plain; charset=utf-8\r\n"
    b"content-length: 3\r\n"
    b"\r\n"
    b"one"
    b"HTTP/1.1 200 OK\r\n"
    b"content-type: text/plain; charset=utf-8\r\n"
    b"transfer-encoding: chunked\r\n"
    b"connection: close\r\n"
    b"\r\n"
    b"2\r\ntw\r\n"
    b"1\r\no\r\n"
    b"0\r\n\r\n"
)
WEBSOCKET_PREFIX = bytes((129, 128, 1, 2, 3, 4))
WEBSOCKET_REQUEST = (
    b"GET /socket HTTP/1.1\r\n"
    b"Host: localhost\r\n"
    b"Upgrade: websocket\r\n"
    b"Connection: Upgrade\r\n"
    b"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
    b"Sec-WebSocket-Version: 13\r\n"
    b"Sec-WebSocket-Protocol: chat\r\n"
    b"\r\n"
    + WEBSOCKET_PREFIX
)
EXPECTED_WEBSOCKET_RESPONSE = (
    b"HTTP/1.1 101 Switching Protocols\r\n"
    b"upgrade: websocket\r\n"
    b"connection: Upgrade\r\n"
    b"sec-websocket-accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n"
    b"sec-websocket-protocol: chat\r\n"
    b"\r\n"
    + WEBSOCKET_PREFIX
)


def reserve_loopback_address() -> tuple[str, int]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()


def connect_when_ready(process: subprocess.Popen[str], port: int) -> socket.socket:
    deadline = time.monotonic() + 5
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise RuntimeError(
                "fixture exited before accepting a connection\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        try:
            client.connect(("127.0.0.1", port))
            return client
        except OSError as error:
            last_error = error
            client.close()
            time.sleep(0.02)
    raise RuntimeError(f"fixture did not listen within five seconds: {last_error}")


def run_persistent_fixture(yanxu: Path, backend: str) -> None:
    repository = Path(__file__).resolve().parents[1]
    fixture = repository / "integration" / "持久连接服务器.yx"
    _, port = reserve_loopback_address()
    address = f"127.0.0.1:{port}"
    command = [str(yanxu)]
    if backend == "vm":
        command.append("字节")
    command.extend([str(fixture), "--", address])

    process = subprocess.Popen(
        command,
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        with connect_when_ready(process, port) as client:
            client.sendall(PIPELINED_REQUEST)
            response = bytearray()
            while received := client.recv(4096):
                response.extend(received)
        stdout, stderr = process.communicate(timeout=5)
    except Exception:
        process.kill()
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout, file=sys.stderr, end="")
        if stderr:
            print(stderr, file=sys.stderr, end="")
        raise

    if process.returncode != 0:
        raise RuntimeError(
            f"fixture exited with {process.returncode}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if bytes(response) != EXPECTED_RESPONSE:
        raise RuntimeError(
            f"unexpected HTTP response: {bytes(response)!r}; "
            f"expected: {EXPECTED_RESPONSE!r}"
        )
    if stdout.strip() != SUCCESS_MARKER:
        raise RuntimeError(
            f"unexpected fixture output: {stdout!r}; stderr: {stderr!r}"
        )


def run_websocket_fixture(yanxu: Path, backend: str) -> None:
    repository = Path(__file__).resolve().parents[1]
    fixture = repository / "integration" / "WebSocket升级服务器.yx"
    _, port = reserve_loopback_address()
    address = f"127.0.0.1:{port}"
    command = [str(yanxu)]
    if backend == "vm":
        command.append("字节")
    command.extend([str(fixture), "--", address])

    process = subprocess.Popen(
        command,
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        with connect_when_ready(process, port) as client:
            client.sendall(WEBSOCKET_REQUEST)
            response = bytearray()
            while received := client.recv(4096):
                response.extend(received)
        stdout, stderr = process.communicate(timeout=5)
    except Exception:
        process.kill()
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout, file=sys.stderr, end="")
        if stderr:
            print(stderr, file=sys.stderr, end="")
        raise

    if process.returncode != 0:
        raise RuntimeError(
            f"upgrade fixture exited with {process.returncode}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if bytes(response) != EXPECTED_WEBSOCKET_RESPONSE:
        raise RuntimeError(
            f"unexpected WebSocket response: {bytes(response)!r}; "
            f"expected: {EXPECTED_WEBSOCKET_RESPONSE!r}"
        )
    if stdout.strip() != UPGRADE_MARKER:
        raise RuntimeError(
            f"unexpected upgrade fixture output: {stdout!r}; stderr: {stderr!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yanxu", type=Path, required=True)
    parser.add_argument("--backend", choices=("tree", "vm"), required=True)
    arguments = parser.parse_args()
    run_persistent_fixture(arguments.yanxu.resolve(), arguments.backend)
    run_websocket_fixture(arguments.yanxu.resolve(), arguments.backend)
    print(f"{SUCCESS_MARKER}（{arguments.backend}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
