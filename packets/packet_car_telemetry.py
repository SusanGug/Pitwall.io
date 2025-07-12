import struct
from typing import List, Optional
from dataclasses import dataclass
from enum import IntEnum
from .packet_header import PacketHeader
import sys

class DRSStatus(IntEnum):
    OFF = 0
    ON = 1

class SurfaceType(IntEnum):
    TARMAC = 0
    RUMBLE_STRIP = 1
    CONCRETE = 2
    ROCK = 3
    GRAVEL = 4
    MUD = 5
    SAND = 6
    GRASS = 7
    WATER = 8
    COBBLESTONE = 9
    METAL = 10
    RIDGED = 11

@dataclass
class CarTelemetryData:
    m_speed: int
    m_throttle: float
    m_steer: float
    m_brake: float
    m_clutch: int
    m_gear: int
    m_engineRPM: int
    m_drs: int
    m_revLightsPercent: int
    m_revLightsBitValue: int
    m_brakesTemperature: List[int]
    m_tyresSurfaceTemperature: List[int]
    m_tyresInnerTemperature: List[int]
    m_engineTemperature: int
    m_tyresPressure: List[float]
    m_surfaceType: List[int]

    STRUCT_FORMAT = '<HfffBbHBBH' + 'H'*4 + 'B'*4 + 'B'*4 + 'H' + 'f'*4 + 'B'*4
    SIZE = struct.calcsize(STRUCT_FORMAT)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'CarTelemetryData':
        unpacked_data = struct.unpack(cls.STRUCT_FORMAT, data)
        return cls(
            m_speed=unpacked_data[0],
            m_throttle=unpacked_data[1],
            m_steer=unpacked_data[2],
            m_brake=unpacked_data[3],
            m_clutch=unpacked_data[4],
            m_gear=unpacked_data[5],
            m_engineRPM=unpacked_data[6],
            m_drs=unpacked_data[7],
            m_revLightsPercent=unpacked_data[8],
            m_revLightsBitValue=unpacked_data[9],
            m_brakesTemperature=list(unpacked_data[10:14]),
            m_tyresSurfaceTemperature=list(unpacked_data[14:18]),
            m_tyresInnerTemperature=list(unpacked_data[18:22]),
            m_engineTemperature=unpacked_data[22],
            m_tyresPressure=list(unpacked_data[23:27]),
            m_surfaceType=list(unpacked_data[27:31])
        )

@dataclass
class PacketCarTelemetryData:
    m_header: PacketHeader
    m_carTelemetryData: List[CarTelemetryData]
    m_mfdPanelIndex: int
    m_mfdPanelIndexSecondaryPlayer: int
    m_suggestedGear: int

    PACKET_SIZE = 1352
    HEADER_SIZE = 29
    CAR_TELEMETRY_DATA_SIZE = 60

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['PacketCarTelemetryData']:
        if len(data) < cls.PACKET_SIZE:
            print(f"Error: Received CarTelemetry packet with invalid size. Expected {cls.PACKET_SIZE}, got {len(data)}.", file=sys.stderr)
            return None
        
        try:
            header = PacketHeader.from_bytes(data)
            if not header:
                return None
            
            car_telemetry_data = []
            for i in range(22):
                offset = cls.HEADER_SIZE + (i * cls.CAR_TELEMETRY_DATA_SIZE)
                car_data_bytes = data[offset:offset + cls.CAR_TELEMETRY_DATA_SIZE]
                car_telemetry_data.append(CarTelemetryData.from_bytes(car_data_bytes))

            mfd_offset = cls.HEADER_SIZE + (22 * cls.CAR_TELEMETRY_DATA_SIZE)
            m_mfdPanelIndex, m_mfdPanelIndexSecondaryPlayer, m_suggestedGear = struct.unpack('<BBb', data[mfd_offset:mfd_offset + 3])

            return cls(
                m_header=header,
                m_carTelemetryData=car_telemetry_data,
                m_mfdPanelIndex=m_mfdPanelIndex,
                m_mfdPanelIndexSecondaryPlayer=m_mfdPanelIndexSecondaryPlayer,
                m_suggestedGear=m_suggestedGear
            )
        except struct.error as e:
            print(f"Error parsing CarTelemetryData: {e}", file=sys.stderr)
            return None 