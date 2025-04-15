#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import json


def get_password():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
          sock.connect('/tmp/RustDesk/ipc')
          payload = json.dumps({"t": "Config", "c": ["permanent-password", None]}).encode()
          header = (len(payload) << 2).to_bytes(1, byteorder="little")
          sock.send(header + payload)
          print(f"Received:", sock.recv(1024))


def set_password(password: str):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
          sock.connect('/tmp/RustDesk/ipc')
          payload = json.dumps({"t": "Config", "c": ["permanent-password", password]}).encode()
          header = (len(payload) << 2).to_bytes(1, byteorder="little")
          sock.send(header + payload)
