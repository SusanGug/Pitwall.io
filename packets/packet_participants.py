import struct
from typing import List, Optional
from dataclasses import dataclass
from .packet_header import PacketHeader
import sys

@dataclass
class ParticipantData:
    m_aiControlled: int
    m_driverId: int
    m_networkId: int
    m_teamId: int
    m_myTeam: int
    m_raceNumber: int
    m_nationality: int
    m_name: str
    m_yourTelemetry: int
    m_showOnlineNames: int
    m_techLevel: int
    m_platform: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ParticipantData':
        name_bytes = data[7:55]
        name = name_bytes.decode('utf-8', errors='ignore').rstrip('\\x00')
        
        unpacked_data = struct.unpack('<BBBBBBB48sBBHB', data)
        return cls(
            m_aiControlled=unpacked_data[0],
            m_driverId=unpacked_data[1],
            m_networkId=unpacked_data[2],
            m_teamId=unpacked_data[3],
            m_myTeam=unpacked_data[4],
            m_raceNumber=unpacked_data[5],
            m_nationality=unpacked_data[6],
            m_name=name,
            m_yourTelemetry=unpacked_data[8],
            m_showOnlineNames=unpacked_data[9],
            m_techLevel=unpacked_data[10],
            m_platform=unpacked_data[11],
        )

@dataclass
class PacketParticipantsData:
    m_header: PacketHeader
    m_numActiveCars: int
    m_participants: List[ParticipantData]

    PACKET_SIZE = 1350
    HEADER_SIZE = 29
    PARTICIPANT_DATA_SIZE = 60 # 59 bytes of data + 1 byte of padding

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['PacketParticipantsData']:
        if len(data) < cls.PACKET_SIZE:
            print(f"Error: Received Participants packet with invalid size. Expected {cls.PACKET_SIZE}, got {len(data)}.", file=sys.stderr)
            return None
        
        try:
            header = PacketHeader.from_bytes(data)
            if not header:
                return None
            num_active_cars = struct.unpack('<B', data[29:30])[0]
            
            participants = []
            for i in range(22):
                offset = cls.HEADER_SIZE + 1 + (i * cls.PARTICIPANT_DATA_SIZE)
                participant_bytes = data[offset:offset + cls.PARTICIPANT_DATA_SIZE]
                participants.append(ParticipantData.from_bytes(participant_bytes))
            
            return cls(
                m_header=header,
                m_numActiveCars=num_active_cars,
                m_participants=participants
            )
        except (struct.error, IndexError) as e:
            print(f"Error parsing PacketParticipantsData: {e}", file=sys.stderr)
            return None 