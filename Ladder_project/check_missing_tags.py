import xml.etree.ElementTree as ET

tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
root = tree.getroot()
tags = {t.get('Name'): t.get('DataType') for t in root.findall('.//Tag')}

di_expected = [
    'ZSH_6401_001', 'ZSL_6401_001', 'FS_7503_001', 'LS_7503_001', 'LS_7503_002',
    'Pump_A_PulsIn', 'Pump_B_Start_PulsIn', 'SpareDI_08', 'Pump_B_Inhibited',
    'ESDV_6401_001', 'SpareDI_11', 'INHIBIT_FOAM_REL', 'INHIBIT_ALL_OUTPUTS'
] + [f'SpareDI_{i:02d}' for i in range(14, 33)]

do_expected = [
    'EY_6401_001_002', 'SA_7404_001_002', 'P2100_P2200', 'P3600_P3700',
    'PUMP_A', 'PUMP_B_STOP', 'PUMP_B_START', 'PumpShutdown',
    'Pump_A_PulsOut', 'Pump_B_Start_PulsOut', 'SpareDO_11',
    'Tag_DO_12', 'Tag_DO_13', 'Tag_DO_14', 'Tag_DO_15', 'PLC_Fault'
] + [f'SpareDO_{i:02d}' for i in range(17, 33)]

ai_expected = [
    f'DG_7404_{i:03d}' for i in range(1, 11)
] + ['SpareAI_11', 'DF_7404_001', 'DF_7404_002', 'DG_7404_011R', 'SpareAI_15', 'SpareAI_16',
     'PST_7002_001', 'PST_6401_001', 'PST_7503_001', 'FR_7503_001_002', 'SpareAI_21',
     'FR_7503_003', 'SpareAI_23', 'SpareAI_24']

missing_di = [t for t in di_expected if t not in tags]
missing_do = [t for t in do_expected if t not in tags]
missing_ai = [t for t in ai_expected if t not in tags]

print('Missing DI tags:', missing_di)
print('Missing DO tags:', missing_do)
print('Missing AI tags:', missing_ai)
