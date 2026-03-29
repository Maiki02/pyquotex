"""Decode Quotex websocket binary payloads from .bin dumps."""

import argparse
import json
import zlib
from pathlib import Path

import msgpack


def _preview_text(data: bytes, limit: int = 240) -> str:
    text = data.decode("utf-8", errors="replace")
    compact = " ".join(text.split())
    return compact[:limit]


def _try_zlib(raw: bytes) -> bytes | None:
    try:
        decompressed = zlib.decompress(raw)
        print(f"[zlib] OK: {len(decompressed)} bytes")
        print(f"[zlib] Preview: {_preview_text(decompressed)}")
        return decompressed
    except Exception as exc:
        print(f"[zlib] ERROR: {exc}")
        return None


def _try_msgpack(raw: bytes, label: str) -> None:
    try:
        unpacked = msgpack.unpackb(raw, raw=False, strict_map_key=False)
        print(f"[msgpack:{label}] OK: {type(unpacked)}")
        if isinstance(unpacked, (dict, list)):
            rendered = json.dumps(unpacked, ensure_ascii=False)[:500]
            print(f"[msgpack:{label}] JSON-like preview: {rendered}")
        else:
            print(f"[msgpack:{label}] Value preview: {str(unpacked)[:500]}")
    except Exception as exc:
        print(f"[msgpack:{label}] ERROR: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Try zlib/msgpack decoding for Quotex websocket .bin payloads")
    parser.add_argument("bin_path", help="Path to the .bin file")
    args = parser.parse_args()

    bin_path = Path(args.bin_path)
    raw = bin_path.read_bytes()
    print(f"Loaded {len(raw)} bytes from {bin_path}")
    print(f"Raw preview: {_preview_text(raw)}")

    inflated = _try_zlib(raw)
    _try_msgpack(raw, "raw")
    if inflated is not None:
        _try_msgpack(inflated, "zlib")


if __name__ == "__main__":
    main()
