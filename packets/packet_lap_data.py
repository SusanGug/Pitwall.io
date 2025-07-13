import struct
from typing import List, Optional
from dataclasses import dataclass
from .packet_header import PacketHeader
import sys

@dataclass
class LapData:
    m_lastLapTimeInMS: int
    m_currentLapTimeInMS: int
    m_sector1TimeMSPart: int
    m_sector1TimeMinutesPart: int
    m_sector2TimeMSPart: int
    m_sector2TimeMinutesPart: int
    m_deltaToCarInFrontMSPart: int
    m_deltaToCarInFrontMinutesPart: int
    m_deltaToRaceLeaderMSPart: int
    m_deltaToRaceLeaderMinutesPart: int
    m_lapDistance: float
    m_totalDistance: float
    m_safetyCarDelta: float
    m_carPosition: int
    m_currentLapNum: int
    m_pitStatus: int
    m_numPitStops: int
    m_sector: int
    m_currentLapInvalid: int
    m_penalties: int
    m_totalWarnings: int
    m_cornerCuttingWarnings: int
    m_numUnservedDriveThroughPens: int
    m_numUnservedStopGoPens: int
    m_gridPosition: int
    m_driverStatus: int
    m_resultStatus: int
    m_pitLaneTimerActive: int
    m_pitLaneTimeInLaneInMS: int
    m_pitStopTimerInMS: int
    m_pitStopShouldServePen: int
    m_speedTrapFastestSpeed: float
    m_speedTrapFastestLap: int

    # This class uses a robust field-by-field unpacking method
    # inspired by the user's reference file.

    @classmethod
    def from_bytes(cls, data: bytes) -> 'LapData':
        values = {}
        offset = 0
        
        # Define fields and their formats in order
        FIELD_FORMATS = [
            ('m_lastLapTimeInMS', 'I'), ('m_currentLapTimeInMS', 'I'),
            ('m_sector1TimeMSPart', 'H'), ('m_sector1TimeMinutesPart', 'B'),
            ('m_sector2TimeMSPart', 'H'), ('m_sector2TimeMinutesPart', 'B'),
            ('m_deltaToCarInFrontMSPart', 'H'), ('m_deltaToCarInFrontMinutesPart', 'B'),
            ('m_deltaToRaceLeaderMSPart', 'H'), ('m_deltaToRaceLeaderMinutesPart', 'B'),
            ('m_lapDistance', 'f'), ('m_totalDistance', 'f'), ('m_safetyCarDelta', 'f'),
            ('m_carPosition', 'B'), ('m_currentLapNum', 'B'), ('m_pitStatus', 'B'),
            ('m_numPitStops', 'B'), ('m_sector', 'B'), ('m_currentLapInvalid', 'B'),
            ('m_penalties', 'B'), ('m_totalWarnings', 'B'), ('m_cornerCuttingWarnings', 'B'),
            ('m_numUnservedDriveThroughPens', 'B'), ('m_numUnservedStopGoPens', 'B'),
            ('m_gridPosition', 'B'), ('m_driverStatus', 'B'), ('m_resultStatus', 'B'),
            ('m_pitLaneTimerActive', 'B'), ('m_pitLaneTimeInLaneInMS', 'H'),
            ('m_pitStopTimerInMS', 'H'), ('m_pitStopShouldServePen', 'B'),
            ('m_speedTrapFastestSpeed', 'f'), ('m_speedTrapFastestLap', 'B'),
        ]

        try:
            for name, fmt in FIELD_FORMATS:
                size = struct.calcsize(f'<{fmt}')
                value = struct.unpack(f'<{fmt}', data[offset:offset+size])[0]
                values[name] = value
                offset += size
            return cls(**values)
        except struct.error as e:
            # This helps debug if the byte slice is ever wrong
            print(f"Error parsing LapData field-by-field: {e}", file=sys.stderr)
            # Return a default object on failure to satisfy type checker and prevent crashes
            return cls(**{f.name: 0 for f in cls.__dataclass_fields__.values() if f.type in [int, float]})

@dataclass
class PacketLapData:
    m_header: PacketHeader
    m_lapData: List[LapData]
    m_timeTrialPBCarIdx: int
    m_timeTrialRivalCarIdx: int

    PACKET_SIZE = 1285
    HEADER_SIZE = 29
    LAP_DATA_SIZE = 57

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['PacketLapData']:
        if len(data) < cls.PACKET_SIZE:
            return None
        try:
            header = PacketHeader.from_bytes(data)
            if not header:
                return None
            
            lap_data_list = []
            for i in range(22):
                offset = cls.HEADER_SIZE + (i * cls.LAP_DATA_SIZE)
                lap_data_bytes = data[offset:offset + cls.LAP_DATA_SIZE]
                
                lap_data_obj = LapData.from_bytes(lap_data_bytes)
                lap_data_list.append(lap_data_obj)


            final_fields_offset = cls.HEADER_SIZE + (22 * cls.LAP_DATA_SIZE)
            m_timeTrialPBCarIdx, m_timeTrialRivalCarIdx = struct.unpack('<BB', data[final_fields_offset:final_fields_offset + 2])
            
            return cls(
                m_header=header,
                m_lapData=lap_data_list,
                m_timeTrialPBCarIdx=m_timeTrialPBCarIdx,
                m_timeTrialRivalCarIdx=m_timeTrialRivalCarIdx
            )
        except Exception as e:
            print(f"Error parsing PacketLapData: {e}", file=sys.stderr)
            return None 