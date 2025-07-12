import struct
from dataclasses import dataclass
from typing import Optional
import sys

@dataclass
class PacketHeader:
    m_packetFormat: int
    m_gameYear: int
    m_gameMajorVersion: int
    m_gameMinorVersion: int
    m_packetVersion: int
    m_packetId: int
    m_sessionUID: int
    m_sessionTime: float
    m_frameIdentifier: int
    m_overallFrameIdentifier: int
    m_playerCarIndex: int
    m_secondaryPlayerCarIndex: int

    HEADER_SIZE = 29

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['PacketHeader']:
        """
        Parses the packet header from bytes.
        The header is 29 bytes long.
        """
        if len(data) < cls.HEADER_SIZE:
            print(f"Error: Received header with invalid size. Expected {cls.HEADER_SIZE}, got {len(data)}.", file=sys.stderr)
            return None

        try:
            (
                m_packetFormat,
                m_gameYear,
                m_gameMajorVersion,
                m_gameMinorVersion,
                m_packetVersion,
                m_packetId,
                m_sessionUID,
                m_sessionTime,
                m_frameIdentifier,
                m_overallFrameIdentifier,
                m_playerCarIndex,
                m_secondaryPlayerCarIndex
            ) = struct.unpack('<HBBBBBQfIIBB', data[0:cls.HEADER_SIZE])
            return cls(
                m_packetFormat,
                m_gameYear,
                m_gameMajorVersion,
                m_gameMinorVersion,
                m_packetVersion,
                m_packetId,
                m_sessionUID,
                m_sessionTime,
                m_frameIdentifier,
                m_overallFrameIdentifier,
                m_playerCarIndex,
                m_secondaryPlayerCarIndex
            )
        except struct.error as e:
            print(f"Error parsing PacketHeader: {e}", file=sys.stderr)
            return None 