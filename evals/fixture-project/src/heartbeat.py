"""Synthetic 8-byte wire example; no network or native ABI claims."""
import struct

FRAME = struct.Struct('!BBHI')
ALLOWED_FLAGS = 0x03


def encode_heartbeat(flags, sequence):
    if flags < 0 or flags & ~ALLOWED_FLAGS or not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError('invalid fields')
    return FRAME.pack(1, flags, FRAME.size, sequence)


def decode_heartbeat(payload):
    if len(payload) != FRAME.size:
        raise ValueError('invalid size')
    version, flags, length, sequence = FRAME.unpack(payload)
    if version != 1 or length != FRAME.size or flags & ~ALLOWED_FLAGS:
        raise ValueError('invalid frame')
    return {'version': version, 'flags': flags, 'length': length, 'sequence': sequence}
