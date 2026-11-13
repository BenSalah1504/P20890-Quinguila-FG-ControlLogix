import xml.etree.ElementTree as ET
import re

tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
root = tree.getroot()

target_outputs = [
    'EY_6401_001_002', 'SA_7404_001_002', 'P2100_P2200', 'P3600_P3700',
    'PUMP_A', 'PUMP_B_STOP', 'PUMP_B_START', 'PumpShutdown',
    'Pump_A_PulsOut', 'Pump_B_Start_PulsOut', 'Tag_DO_12', 'Tag_DO_13',
    'Tag_DO_14', 'Tag_DO_15', 'PLC_Fault'
]

for r in root.findall('.//Routine'):
    name = r.get('Name')
    for rung in r.findall('.//Rung'):
        t = rung.findtext('Text', '')
        for out in target_outputs:
            if re.search(r'\b(OTE|OTL|OTU)\(' + out + r'\b', t):
                print(f"Routine {name} Rung {rung.get('Number')}: {out} driven by: {t.strip()}")
