#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os
from pathlib import Path
import platform

import machineid
from nacl.secret import SecretBox
from tomlkit.toml_file import TOMLFile


class RustdeskError(Exception):
    """Base class for RustDesk-related exceptions."""
    pass


def get_config_dir() -> Path:
    match platform.system():
        case 'Windows':
            return Path(os.getenv('APPDATA')) / 'RustDesk' / 'config'
        case 'Linux':
            return Path.home() / '.config' / 'rustdesk'
        case _:
            raise RustdeskError(f'Unsupported platform: {platform.system()}')


def get_id() -> str:
    file = TOMLFile(get_config_dir() / 'RustDesk.toml')
    document = file.read()

    enc_id = document.get('enc_id')
    if enc_id and enc_id.startswith('00'):
        return decrypt(enc_id[2:])

    raise RustdeskError('No valid ID found in RustDesk.toml')


def get_password() -> str:
    file = TOMLFile(get_config_dir() / 'RustDesk.toml')
    document = file.read()

    password = document.get('password')
    if password and password.startswith('00'):
        return decrypt(password[2:])

    raise RustdeskError('No valid password found in RustDesk.toml')


def set_password(password: str) -> None:
    file = TOMLFile(get_config_dir() / 'RustDesk.toml')
    document = file.read()

    if document.get('password').startswith('00'):
        document.update({'password': f'00{encrypt(password)}'})
        file.write(document)
    else:
        raise RustdeskError('No valid password found in RustDesk.toml')


def encrypt(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif not isinstance(data, bytes):
        raise TypeError('Data must be a string or bytes')

    key = machineid.id().encode('utf-8')
    box = SecretBox(key)
    nonce = b'\x00' * SecretBox.NONCE_SIZE
    encrypted = box.encrypt(data, nonce).ciphertext
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt(data: str | bytes) -> str:
    decoded = base64.b64decode(data)
    key = machineid.id().encode('utf-8')
    box = SecretBox(key)
    nonce = b'\x00' * SecretBox.NONCE_SIZE
    decrypted = box.decrypt(decoded, nonce)
    return decrypted.decode('utf-8')
