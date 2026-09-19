"""Minimal stdlib PNG encoder (8-bit grayscale) used to render 'what an agent screenshot sees'."""

import struct
import zlib


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_gray_png(pixels: bytes | bytearray, width: int, height: int) -> bytes:
    """pixels: row-major, one byte per pixel (0=black, 255=white)."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None) per scanline
        raw += pixels[y * width : (y + 1) * width]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)  # 8-bit, grayscale
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


def render_frame_png(points, width=160, height=160, dot=2, scale=3, bg=12, fg=235) -> bytes:
    """Rasterise one MDG frame exactly like the browser canvas does, scaled up like a screenshot."""
    W, H = width * scale, height * scale
    px = bytearray([bg]) * (W * H)
    d = dot * scale
    for x, y in points:
        x0, y0 = x * scale, y * scale
        for yy in range(y0, min(y0 + d, H)):
            row = yy * W
            px[row + x0 : row + min(x0 + d, W)] = bytes([fg]) * (min(x0 + d, W) - x0)
    return encode_gray_png(px, W, H)
