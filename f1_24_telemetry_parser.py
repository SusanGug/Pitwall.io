import socket
import struct
import sys
import time

# Add the packets directory to the Python path
sys.path.append('/packets')

from packets.packet_header import PacketHeader
from packets.packet_car_telemetry import PacketCarTelemetryData
from packets.packet_participants import PacketParticipantsData
from packets.packet_lap_data import PacketLapData

# UDP settings
UDP_IP = "0.0.0.0"
UDP_PORT = 20777

# Not All packets are used, but we need to know the size of the packet to slice it correctly
PACKET_TYPES = {
    0: 'Motion',
    1: 'Session',
    2: 'LapData',
    3: 'Event',
    4: 'Participants',
    5: 'CarSetups',
    6: 'CarTelemetry',
    7: 'CarStatus',
    8: 'FinalClassification',
    9: 'LobbyInfo',
    10: 'CarDamage',
    11: 'SessionHistory',
    12: 'TyreSets',
    13: 'MotionEx',
    14: 'TimeTrial'
}

def to_influx(measurement, fields, tags=None):
    if tags is None:
        tags = {}
    
    tag_str = ",".join([f"{k}={v}" for k, v in tags.items()])
    field_str = ",".join([f"{k}={v}" for k, v in fields.items() if v is not None])
    
    if not field_str:
        return None

    return f"{measurement},{tag_str} {field_str}"

def process_car_telemetry(packet: PacketCarTelemetryData):
    """
    Processes the parsed Car Telemetry packet and prints InfluxDB line protocol.
    """
    player_car_index = packet.m_header.m_playerCarIndex
    for i, car_telemetry in enumerate(packet.m_carTelemetryData):
        tags = {'carIndex': str(i)} # FIX: Ensure carIndex is always a string
        
        if i == player_car_index:
            tags['isPlayer'] = "true"

        fields = {
            'speed': car_telemetry.m_speed,
            'throttle': car_telemetry.m_throttle,
            'steer': car_telemetry.m_steer,
            'brake': car_telemetry.m_brake,
            'clutch': car_telemetry.m_clutch,
            'gear': car_telemetry.m_gear,
            'engineRPM': car_telemetry.m_engineRPM,
            'drs': car_telemetry.m_drs,
            'revLightsPercent': car_telemetry.m_revLightsPercent,
            'revLightsBitValue': car_telemetry.m_revLightsBitValue,
            'brakesTemperatureRL': car_telemetry.m_brakesTemperature[0],
            'brakesTemperatureRR': car_telemetry.m_brakesTemperature[1],
            'brakesTemperatureFL': car_telemetry.m_brakesTemperature[2],
            'brakesTemperatureFR': car_telemetry.m_brakesTemperature[3],
            'tyresSurfaceTemperatureRL': car_telemetry.m_tyresSurfaceTemperature[0],
            'tyresSurfaceTemperatureRR': car_telemetry.m_tyresSurfaceTemperature[1],
            'tyresSurfaceTemperatureFL': car_telemetry.m_tyresSurfaceTemperature[2],
            'tyresSurfaceTemperatureFR': car_telemetry.m_tyresSurfaceTemperature[3],
            'tyresInnerTemperatureRL': car_telemetry.m_tyresInnerTemperature[0],
            'tyresInnerTemperatureRR': car_telemetry.m_tyresInnerTemperature[1],
            'tyresInnerTemperatureFL': car_telemetry.m_tyresInnerTemperature[2],
            'tyresInnerTemperatureFR': car_telemetry.m_tyresInnerTemperature[3],
            'engineTemperature': car_telemetry.m_engineTemperature,
            'tyresPressureRL': car_telemetry.m_tyresPressure[0],
            'tyresPressureRR': car_telemetry.m_tyresPressure[1],
            'tyresPressureFL': car_telemetry.m_tyresPressure[2],
            'tyresPressureFR': car_telemetry.m_tyresPressure[3],
            'surfaceTypeRL': car_telemetry.m_surfaceType[0],
            'surfaceTypeRR': car_telemetry.m_surfaceType[1],
            'surfaceTypeFL': car_telemetry.m_surfaceType[2],
            'surfaceTypeFR': car_telemetry.m_surfaceType[3],
        }

        if i == player_car_index:
            fields['mfdPanelIndex'] = packet.m_mfdPanelIndex
            fields['mfdPanelIndexSecondaryPlayer'] = packet.m_mfdPanelIndexSecondaryPlayer
            fields['suggestedGear'] = packet.m_suggestedGear
        
        line = to_influx('CarTelemetry', fields, tags)
        if line:
            print(line)

def process_lap_data(packet: PacketLapData):
    """
    Processes the parsed Lap Data packet and prints InfluxDB line protocol.
    """
    player_car_index = packet.m_header.m_playerCarIndex
    for i, lap_data in enumerate(packet.m_lapData):
        tags = {'carIndex': str(i)}
        if i == player_car_index:
            tags['isPlayer'] = "true"
        
        fields = {
            'lastLapTimeInMS': lap_data.m_lastLapTimeInMS,
            'currentLapTimeInMS': lap_data.m_currentLapTimeInMS,
            'sector1TimeInMS': (lap_data.m_sector1TimeMinutesPart * 60000) + lap_data.m_sector1TimeMSPart,
            'sector2TimeInMS': (lap_data.m_sector2TimeMinutesPart * 60000) + lap_data.m_sector2TimeMSPart,
            'lapDistance': lap_data.m_lapDistance,
            'totalDistance': lap_data.m_totalDistance,
            'safetyCarDelta': lap_data.m_safetyCarDelta,
            'carPosition': lap_data.m_carPosition,
            'currentLapNum': lap_data.m_currentLapNum,
            'pitStatus': lap_data.m_pitStatus,
            'numPitStops': lap_data.m_numPitStops,
            'sector': lap_data.m_sector,
            'currentLapInvalid': lap_data.m_currentLapInvalid,
            'penalties': lap_data.m_penalties,
            'totalWarnings': lap_data.m_totalWarnings,
            'cornerCuttingWarnings': lap_data.m_cornerCuttingWarnings,
            'gridPosition': lap_data.m_gridPosition,
            'driverStatus': lap_data.m_driverStatus,
            'resultStatus': lap_data.m_resultStatus,
        }
        
        line = to_influx('LapData', fields, tags)
        if line:
            print(line)

def process_participants_data(packet: PacketParticipantsData):
    """
    Processes the parsed Participants packet and prints InfluxDB line protocol.
    """
    for i, participant in enumerate(packet.m_participants):
        if i < packet.m_numActiveCars and participant.m_name:
            tags = {'carIndex': str(i)}
            # InfluxDB requires string fields to be surrounded by double quotes.
            # The name might contain spaces, which need to be escaped.
            name = participant.m_name.replace(' ', '\\ ')
            fields = {'name': f'"{name}"'}
            
            line = to_influx('Participants', fields, tags)
            if line:
                print(line)

def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        print("Listening for F1 24 telemetry on port 20777...", file=sys.stderr)

        while True:
            data, addr = sock.recvfrom(2048) # Receive a chunk of data

            while len(data) >= 29: # Minimum packet size (header)
                header = PacketHeader.from_bytes(data)
                if not header:
                    # If header is invalid, we can't trust the rest of the chunk
                    break 

                packet_id = header.m_packetId
                
                # Determine packet size based on ID to slice correctly
                packet_size = 0
                if packet_id == 2:
                    packet_size = PacketLapData.PACKET_SIZE
                elif packet_id == 4:
                    packet_size = PacketParticipantsData.PACKET_SIZE 
                elif packet_id == 6:
                    packet_size = PacketCarTelemetryData.PACKET_SIZE
                
                # Add other packet sizes here as you implement them
                
                if packet_size > 0 and len(data) >= packet_size:
                    # Slice the exact packet from the buffer
                    current_packet_data = data[:packet_size]

                    if packet_id == 2:
                        lap_data_packet = PacketLapData.from_bytes(current_packet_data)
                        if lap_data_packet:
                            process_lap_data(lap_data_packet)
                    elif packet_id == 4:
                        participants_packet = PacketParticipantsData.from_bytes(current_packet_data)
                        if participants_packet:
                            process_participants_data(participants_packet)
                    elif packet_id == 6:
                        telemetry_packet = PacketCarTelemetryData.from_bytes(current_packet_data)
                        if telemetry_packet:
                            process_car_telemetry(telemetry_packet)

                    # Remove the processed packet from the buffer
                    data = data[packet_size:]
                else:
                    # Not enough data for a full packet of this type, or unknown packet.
                    # This could happen with the last packet in a chunk.
                    break
            
            sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL: Unhandled error in main function: {e}", file=sys.stderr)
        sys.stderr.flush()
        # Exit with 0 to prevent Telegraf from logging a scary error,
        # as we have already logged the actual problem to stderr.
        sys.exit(0)

if __name__ == "__main__":
    main() 