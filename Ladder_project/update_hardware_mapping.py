import xml.etree.ElementTree as ET
import copy

def update_l5x():
    tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
    root = tree.getroot()
    controller = root.find('Controller')

    # 1. Update Controller ProcessorType
    controller.set('ProcessorType', '1756-L63')

    # 2. Update Modules
    modules = controller.find('Modules')
    if modules is not None:
        controller.remove(modules)
    
    new_modules = ET.Element('Modules')
    
    # Slot 0: Local (1756-L63)
    mod_local = ET.SubElement(new_modules, 'Module', {
        'Name': 'Local',
        'CatalogNumber': '1756-L63',
        'Vendor': '1',
        'ProductType': '14',
        'ProductCode': '56',
        'Major': '17',
        'Minor': '2',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'true'
    })
    ET.SubElement(mod_local, 'EKey', {'State': 'ExactMatch'})
    ports_local = ET.SubElement(mod_local, 'Ports')
    port1_local = ET.SubElement(ports_local, 'Port', {
        'Id': '1',
        'Address': '0',
        'Type': 'ICP',
        'Upstream': 'false'
    })
    ET.SubElement(port1_local, 'Bus', {'Size': '13'})

    # Slot 1: EN2T_Slot01 (1756-EN2T)
    mod_en2t = ET.SubElement(new_modules, 'Module', {
        'Name': 'EN2T_Slot01',
        'CatalogNumber': '1756-EN2T',
        'Vendor': '1',
        'ProductType': '12',
        'ProductCode': '166',
        'Major': '11',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_en2t, 'EKey', {'State': 'CompatibleModule'})
    ports_en2t = ET.SubElement(mod_en2t, 'Ports')
    ET.SubElement(ports_en2t, 'Port', {'Id': '1', 'Address': '1', 'Type': 'ICP', 'Upstream': 'true'})
    ET.SubElement(ports_en2t, 'Port', {'Id': '2', 'Type': 'Ethernet', 'Upstream': 'false'})

    # Slot 2: AI_Slot02_IF16 (1756-IF16)
    mod_ai02 = ET.SubElement(new_modules, 'Module', {
        'Name': 'AI_Slot02_IF16',
        'CatalogNumber': '1756-IF16',
        'Vendor': '1',
        'ProductType': '10',
        'ProductCode': '10',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ai02, 'EKey', {'State': 'CompatibleModule'})
    ports_ai02 = ET.SubElement(mod_ai02, 'Ports')
    ET.SubElement(ports_ai02, 'Port', {'Id': '1', 'Address': '2', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 3: AI_Slot03_IF16 (1756-IF16)
    mod_ai03 = ET.SubElement(new_modules, 'Module', {
        'Name': 'AI_Slot03_IF16',
        'CatalogNumber': '1756-IF16',
        'Vendor': '1',
        'ProductType': '10',
        'ProductCode': '10',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ai03, 'EKey', {'State': 'CompatibleModule'})
    ports_ai03 = ET.SubElement(mod_ai03, 'Ports')
    ET.SubElement(ports_ai03, 'Port', {'Id': '1', 'Address': '3', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 4: AI_Slot04_IF16 (1756-IF16)
    mod_ai04 = ET.SubElement(new_modules, 'Module', {
        'Name': 'AI_Slot04_IF16',
        'CatalogNumber': '1756-IF16',
        'Vendor': '1',
        'ProductType': '10',
        'ProductCode': '10',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ai04, 'EKey', {'State': 'CompatibleModule'})
    ports_ai04 = ET.SubElement(mod_ai04, 'Ports')
    ET.SubElement(ports_ai04, 'Port', {'Id': '1', 'Address': '4', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 5: AI_Slot05_IF16 (1756-IF16)
    mod_ai05 = ET.SubElement(new_modules, 'Module', {
        'Name': 'AI_Slot05_IF16',
        'CatalogNumber': '1756-IF16',
        'Vendor': '1',
        'ProductType': '10',
        'ProductCode': '10',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ai05, 'EKey', {'State': 'CompatibleModule'})
    ports_ai05 = ET.SubElement(mod_ai05, 'Ports')
    ET.SubElement(ports_ai05, 'Port', {'Id': '1', 'Address': '5', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 6: AI_Slot06_IF8H (1756-IF8H)
    mod_ai06 = ET.SubElement(new_modules, 'Module', {
        'Name': 'AI_Slot06_IF8H',
        'CatalogNumber': '1756-IF8H',
        'Vendor': '1',
        'ProductType': '10',
        'ProductCode': '68',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ai06, 'EKey', {'State': 'CompatibleModule'})
    ports_ai06 = ET.SubElement(mod_ai06, 'Ports')
    ET.SubElement(ports_ai06, 'Port', {'Id': '1', 'Address': '6', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 7: DI_Slot07_IB32 (1756-IB32)
    mod_di07 = ET.SubElement(new_modules, 'Module', {
        'Name': 'DI_Slot07_IB32',
        'CatalogNumber': '1756-IB32',
        'Vendor': '1',
        'ProductType': '7',
        'ProductCode': '14',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_di07, 'EKey', {'State': 'CompatibleModule'})
    ports_di07 = ET.SubElement(mod_di07, 'Ports')
    ET.SubElement(ports_di07, 'Port', {'Id': '1', 'Address': '7', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 8: DO_Slot08_OB32 (1756-OB32)
    mod_do08 = ET.SubElement(new_modules, 'Module', {
        'Name': 'DO_Slot08_OB32',
        'CatalogNumber': '1756-OB32',
        'Vendor': '1',
        'ProductType': '7',
        'ProductCode': '22',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_do08, 'EKey', {'State': 'CompatibleModule'})
    ports_do08 = ET.SubElement(mod_do08, 'Ports')
    ET.SubElement(ports_do08, 'Port', {'Id': '1', 'Address': '8', 'Type': 'ICP', 'Upstream': 'true'})

    # Insert Modules right after DataTypes or Description
    tags_idx = list(controller).index(controller.find('Tags'))
    controller.insert(tags_idx, new_modules)

    # 3. Add Modbus and HART Enable tags if not present
    tags_elem = controller.find('Tags')
    existing_tags = {t.get('Name') for t in tags_elem.findall('Tag')}
    
    new_tags_def = [
        ('MCM_IN', 'INT', '250', 'MVI56E-MCM Modbus input image (250 words) from Murphy panels'),
        ('MCM_OUT', 'INT', '248', 'MVI56E-MCM Modbus output image (248 words)'),
        ('MB_P2300_ALMCODE', 'INT', None, 'Power oil pump P2300 annunciator shutdown / alarm code'),
        ('MB_P2300_RPM', 'INT', None, 'Power oil pump P2300 annunciator speed'),
        ('P2300_SHUTDOWN', 'BOOL', None, 'Power oil pump P2300 shutdown active'),
        ('MB_P2400_ALMCODE', 'INT', None, 'Power oil pump P2400 annunciator shutdown / alarm code'),
        ('MB_P2400_RPM', 'INT', None, 'Power oil pump P2400 annunciator speed'),
        ('P2400_SHUTDOWN', 'BOOL', None, 'Power oil pump P2400 shutdown active'),
        ('MB_P2500_ALMCODE', 'INT', None, 'Power oil pump P2500 annunciator shutdown / alarm code'),
        ('MB_P2500_RPM', 'INT', None, 'Power oil pump P2500 annunciator speed'),
        ('P2500_SHUTDOWN', 'BOOL', None, 'Power oil pump P2500 shutdown active'),
        ('MB_P2600_ALMCODE', 'INT', None, 'Power oil pump P2600 annunciator shutdown / alarm code'),
        ('MB_P2600_RPM', 'INT', None, 'Power oil pump P2600 annunciator speed'),
        ('P2600_SHUTDOWN', 'BOOL', None, 'Power oil pump P2600 shutdown active'),
        ('MB_P3800_ALMCODE', 'INT', None, 'Water injection pump P3800 annunciator shutdown / alarm code'),
        ('MB_P3800_RPM', 'INT', None, 'Water injection pump P3800 annunciator speed'),
        ('P3800_SHUTDOWN', 'BOOL', None, 'Water injection pump P3800 shutdown active'),
        ('MB_P3900_ALMCODE', 'INT', None, 'Water injection pump P3900 annunciator shutdown / alarm code'),
        ('MB_P3900_RPM', 'INT', None, 'Water injection pump P3900 annunciator speed'),
        ('P3900_SHUTDOWN', 'BOOL', None, 'Water injection pump P3900 shutdown active'),
        ('MB_V710_ALMCODE', 'INT', None, 'Treater V-710 shutdown / alarm code'),
        ('MB_V710_RPM', 'INT', None, 'Treater V-710 speed'),
        ('MB_V810_ALMCODE', 'INT', None, 'Treater V-810 shutdown / alarm code'),
        ('MB_V810_RPM', 'INT', None, 'Treater V-810 speed'),
        ('MB_FT6401_ALMCODE', 'INT', None, 'Flowmeter oil expedition 6401-FT-005 shutdown / alarm code'),
        ('MB_FT6401_RPM', 'INT', None, 'Flowmeter oil expedition 6401-FT-005 flow rate'),
        ('PA_001_Process', 'BOOL', None, 'PA-001 common process alarm from pump annunciators'),
        ('HART_DG011R_Enable', 'BOOL', None, 'Enable reading Open Path Gas Detector 7404-DG-011R from Slot 6 1756-IF8H HART module')
    ]

    for name, dtype, dim, desc in new_tags_def:
        if name not in existing_tags:
            tag_attrs = {'Name': name, 'TagType': 'Base', 'DataType': dtype}
            if dim:
                tag_attrs['Dimensions'] = dim
            t_elem = ET.SubElement(tags_elem, 'Tag', tag_attrs)
            d_elem = ET.SubElement(t_elem, 'Description')
            d_elem.text = desc
            print(f"Added tag: {name}")

    # 4. Create IO_Mapping_In Routine
    prog = controller.find('.//Program[@Name="FandG_Angola"]')
    routines_elem = prog.find('Routines')
    
    # Check if IO_Mapping_In exists
    r_io_in = prog.find('.//Routine[@Name="IO_Mapping_In"]')
    if r_io_in is not None:
        routines_elem.remove(r_io_in)
    
    r_io_in = ET.Element('Routine', {'Name': 'IO_Mapping_In', 'Type': 'RLL'})
    rll_in = ET.SubElement(r_io_in, 'RLLContent')

    # Mapping DI rungs (32 rungs)
    di_mapping = [
        ('Local:7:I.Data.0', 'ZSH_6401_001', '6401-ZSH-001 ESD valve open'),
        ('Local:7:I.Data.1', 'ZSL_6401_001', '6401-ZSL-001 ESD valve closed'),
        ('Local:7:I.Data.2', 'FS_7503_001', '7503-FS-001 Stop foam button'),
        ('Local:7:I.Data.3', 'LS_7503_001', '7503-LS-001 AFFF tank low level'),
        ('Local:7:I.Data.4', 'LS_7503_002', '7503-LS-002 Diesel tank low level'),
        ('Local:7:I.Data.5', 'Pump_A_PulsIn', 'Pump A Out signal pulse feedback'),
        ('Local:7:I.Data.6', 'Pump_B_Start_PulsIn', 'Pump B Start signal pulse feedback'),
        ('Local:7:I.Data.7', 'SpareDI_08', 'SpareDI-08'),
        ('Local:7:I.Data.8', 'Pump_B_Inhibited', 'Standby pump B inhibited'),
        ('Local:7:I.Data.9', 'ESDV_6401_001', '6401-ESDV-001 ESD Fuel Gas Button'),
        ('Local:7:I.Data.10', 'SpareDI_11', 'SpareDI-11'),
        ('Local:7:I.Data.11', 'INHIBIT_FOAM_REL', 'Foam release inhibit switch'),
        ('Local:7:I.Data.12', 'INHIBIT_ALL_OUTPUTS', 'All outputs inhibit switch'),
    ] + [(f'Local:7:I.Data.{i}', f'SpareDI_{i+1:02d}', f'SpareDI-{i+1:02d}') for i in range(13, 32)]

    rung_num = 0
    for src, dst, comment in di_mapping:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"DI Slot 7 ({src}) -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"XIC({src})OTE({dst});"
        rung_num += 1

    # Mapping AI Slot 2 (8 channels)
    ai_slot2 = [
        ('Local:2:I.Ch0Data', 'DG_7404_001', '7404-DG-001 Gas detector pump house'),
        ('Local:2:I.Ch1Data', 'DG_7404_002', '7404-DG-002 Gas detector pump house'),
        ('Local:2:I.Ch2Data', 'DG_7404_003', '7404-DG-003 Gas detector pump house'),
        ('Local:2:I.Ch3Data', 'DG_7404_004', '7404-DG-004 Gas detector pump house'),
        ('Local:2:I.Ch4Data', 'DG_7404_005', '7404-DG-005 Gas detector pump house'),
        ('Local:2:I.Ch5Data', 'DG_7404_006', '7404-DG-006 Gas detector pump house'),
        ('Local:2:I.Ch6Data', 'DG_7404_007', '7404-DG-007 Gas detector pump house'),
        ('Local:2:I.Ch7Data', 'DG_7404_008', '7404-DG-008 Gas detector pump house'),
    ]
    for src, dst, comment in ai_slot2:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"AI Slot 2 ({src}) -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"MOV({src},{dst});"
        rung_num += 1

    # Mapping AI Slot 3 (8 channels)
    ai_slot3 = [
        ('Local:3:I.Ch0Data', 'DG_7404_009', '7404-DG-009 Gas detector pump house'),
        ('Local:3:I.Ch1Data', 'DG_7404_010', '7404-DG-010 Gas detector pump house'),
        ('Local:3:I.Ch2Data', 'SpareAI_11', 'SpareAI-11 (Defective channel - alarms disabled)'),
        ('Local:3:I.Ch3Data', 'DF_7404_001', '7404-DF-001 Flame detector pump house'),
        ('Local:3:I.Ch4Data', 'DF_7404_002', '7404-DF-002 Flame detector pump house'),
        ('Local:3:I.Ch5Data', 'DG_7404_011R', '7404-DG-011R Open path detector (4-20mA channel)'),
        ('Local:3:I.Ch6Data', 'SpareAI_15', 'SpareAI-15'),
        ('Local:3:I.Ch7Data', 'SpareAI_16', 'SpareAI-16'),
    ]
    for src, dst, comment in ai_slot3:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"AI Slot 3 ({src}) -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"MOV({src},{dst});"
        rung_num += 1

    # Mapping AI Slot 4 (8 channels)
    ai_slot4 = [
        ('Local:4:I.Ch0Data', 'PST_7002_001', '7002-PST-001 Air acc. pressure'),
        ('Local:4:I.Ch1Data', 'PST_6401_001', '6401-PST-001 Fuel gas pressure'),
        ('Local:4:I.Ch2Data', 'PST_7503_001', '7503-PST-001 Deluge line pressure'),
        ('Local:4:I.Ch3Data', 'FR_7503_001_002', '7503-FR-001/002 Foam release from field'),
        ('Local:4:I.Ch4Data', 'SpareAI_21', 'SpareAI-21'),
        ('Local:4:I.Ch5Data', 'FR_7503_003', '7503-FR-003 Foam release from panel'),
        ('Local:4:I.Ch6Data', 'SpareAI_23', 'SpareAI-23'),
        ('Local:4:I.Ch7Data', 'SpareAI_24', 'SpareAI-24'),
    ]
    for src, dst, comment in ai_slot4:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"AI Slot 4 ({src}) -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"MOV({src},{dst});"
        rung_num += 1

    # Slot 6 HART Open Path detector
    rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
    c_elem = ET.SubElement(rung, 'Comment')
    c_elem.text = "AI Slot 6 HART (Local:6:I.Ch0Data) -> DG_7404_011R Open Path Detector (Active when HART enabled)"
    t_elem = ET.SubElement(rung, 'Text')
    t_elem.text = "[XIC(HART_DG011R_Enable)MOV(Local:6:I.Ch0Data,DG_7404_011R)];"
    rung_num += 1

    routines_elem.append(r_io_in)
    print("Created IO_Mapping_In routine with", rung_num, "rungs")

    # 5. Create IO_Mapping_Out Routine
    r_io_out = prog.find('.//Routine[@Name="IO_Mapping_Out"]')
    if r_io_out is not None:
        routines_elem.remove(r_io_out)
    
    r_io_out = ET.Element('Routine', {'Name': 'IO_Mapping_Out', 'Type': 'RLL'})
    rll_out = ET.SubElement(r_io_out, 'RLLContent')

    do_mapping = [
        ('EY_6401_001_002', 'Local:8:O.Data.0', '6401-EY-001/002 ESD fuel gas valve shutdown (Fail-safe de-energize)'),
        ('SA_7404_001_002', 'Local:8:O.Data.1', '7404-SA-001/002 Local alarm pump house beacon/siren'),
        ('P2100_P2200', 'Local:8:O.Data.2', 'P2100/P2200 Oil booster pump shutdown (Fail-safe de-energize)'),
        ('P3600_P3700', 'Local:8:O.Data.3', 'P3600/P3700 Water booster pump shutdown (Fail-safe de-energize)'),
        ('PUMP_A', 'Local:8:O.Data.4', 'Deluge pump A Start/Stop contactor'),
        ('PUMP_B_STOP', 'Local:8:O.Data.5', 'Deluge pump B Stop diesel solenoid'),
        ('PUMP_B_START', 'Local:8:O.Data.6', 'Deluge pump B Start diesel solenoid'),
        ('PumpShutdown', 'Local:8:O.Data.7', 'Fire & Gas pump shutdown (Fail-safe de-energize)'),
        ('Pump_A_PulsOut', 'Local:8:O.Data.8', 'Pulsed output for open circuit check on Pump A Out'),
        ('Pump_B_Start_PulsOut', 'Local:8:O.Data.9', 'Pulsed output for open circuit check on Pump B Start'),
        ('SpareDO_11', 'Local:8:O.Data.10', 'SpareDO-11'),
        ('Tag_DO_12', 'Local:8:O.Data.11', 'ESD valve open lamp indication'),
        ('Tag_DO_13', 'Local:8:O.Data.12', 'ESD valve closed lamp indication'),
        ('Tag_DO_14', 'Local:8:O.Data.13', 'ESD valve low air indication'),
        ('Tag_DO_15', 'Local:8:O.Data.14', 'Panel alarm beacon/siren'),
        ('PLC_Fault', 'Local:8:O.Data.15', 'PLC Fault lamp indication'),
    ] + [(f'SpareDO_{i+1:02d}', f'Local:8:O.Data.{i}', f'SpareDO-{i+1:02d}') for i in range(16, 32)]

    rung_num = 0
    for src, dst, comment in do_mapping:
        rung = ET.SubElement(rll_out, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"DO {src} -> Slot 8 ({dst}) : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"XIC({src})OTE({dst});"
        rung_num += 1

    routines_elem.append(r_io_out)
    print("Created IO_Mapping_Out routine with", rung_num, "rungs")

    # 6. Create Modbus_Comm Routine
    r_mb = prog.find('.//Routine[@Name="Modbus_Comm"]')
    if r_mb is not None:
        routines_elem.remove(r_mb)
    
    r_mb = ET.Element('Routine', {'Name': 'Modbus_Comm', 'Type': 'RLL'})
    rll_mb = ET.SubElement(r_mb, 'RLLContent')

    mb_rungs = [
        ("Modbus_Comm - Interface to ProSoft MVI56E-MCM Modbus Module (Slot 9) for Murphy Engine Panels", "NOP();"),
        ("Power oil pump P2300 annunciator : shutdown / alarm code", "MOV(MCM_IN[1],MB_P2300_ALMCODE);"),
        ("Power oil pump P2300 annunciator : engine speed", "MOV(MCM_IN[2],MB_P2300_RPM);"),
        ("Power oil pump P2300 annunciator : non-zero code = fault", "NEQ(MB_P2300_ALMCODE,0)OTE(P2300_SHUTDOWN);"),
        ("Power oil pump P2400 annunciator : shutdown / alarm code", "MOV(MCM_IN[11],MB_P2400_ALMCODE);"),
        ("Power oil pump P2400 annunciator : engine speed", "MOV(MCM_IN[12],MB_P2400_RPM);"),
        ("Power oil pump P2400 annunciator : non-zero code = fault", "NEQ(MB_P2400_ALMCODE,0)OTE(P2400_SHUTDOWN);"),
        ("Power oil pump P2500 annunciator : shutdown / alarm code", "MOV(MCM_IN[21],MB_P2500_ALMCODE);"),
        ("Power oil pump P2500 annunciator : engine speed", "MOV(MCM_IN[22],MB_P2500_RPM);"),
        ("Power oil pump P2500 annunciator : non-zero code = fault", "NEQ(MB_P2500_ALMCODE,0)OTE(P2500_SHUTDOWN);"),
        ("Power oil pump P2600 annunciator (new) : shutdown / alarm code", "MOV(MCM_IN[31],MB_P2600_ALMCODE);"),
        ("Power oil pump P2600 annunciator (new) : engine speed", "MOV(MCM_IN[32],MB_P2600_RPM);"),
        ("Power oil pump P2600 annunciator (new) : non-zero code = fault", "NEQ(MB_P2600_ALMCODE,0)OTE(P2600_SHUTDOWN);"),
        ("Water injection pump P3800 annunciator : shutdown / alarm code", "MOV(MCM_IN[41],MB_P3800_ALMCODE);"),
        ("Water injection pump P3800 annunciator : engine speed", "MOV(MCM_IN[42],MB_P3800_RPM);"),
        ("Water injection pump P3800 annunciator : non-zero code = fault", "NEQ(MB_P3800_ALMCODE,0)OTE(P3800_SHUTDOWN);"),
        ("Water injection pump P3900 annunciator : shutdown / alarm code", "MOV(MCM_IN[51],MB_P3900_ALMCODE);"),
        ("Water injection pump P3900 annunciator : engine speed", "MOV(MCM_IN[52],MB_P3900_RPM);"),
        ("Water injection pump P3900 annunciator : non-zero code = fault", "NEQ(MB_P3900_ALMCODE,0)OTE(P3900_SHUTDOWN);"),
        ("Treater V-710 (phase 2) : shutdown / alarm code", "MOV(MCM_IN[61],MB_V710_ALMCODE);"),
        ("Treater V-710 (phase 2) : engine speed", "MOV(MCM_IN[62],MB_V710_RPM);"),
        ("Treater V-810 (phase 2) : shutdown / alarm code", "MOV(MCM_IN[71],MB_V810_ALMCODE);"),
        ("Treater V-810 (phase 2) : engine speed", "MOV(MCM_IN[72],MB_V810_RPM);"),
        ("Flowmeter oil expedition 6401-FT-005 (0-500 bbl/h) : shutdown / alarm code", "MOV(MCM_IN[81],MB_FT6401_ALMCODE);"),
        ("Flowmeter oil expedition 6401-FT-005 (0-500 bbl/h) : engine speed", "MOV(MCM_IN[82],MB_FT6401_RPM);"),
        ("PA-001 common process alarm from the pump annunciators", "[XIC(P2300_SHUTDOWN),XIC(P2400_SHUTDOWN),XIC(P2500_SHUTDOWN),XIC(P2600_SHUTDOWN),XIC(P3800_SHUTDOWN),XIC(P3900_SHUTDOWN)]OTE(PA_001_Process);")
    ]

    for idx, (comm, txt) in enumerate(mb_rungs):
        rung = ET.SubElement(rll_mb, 'Rung', {'Number': str(idx), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = comm
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = txt

    routines_elem.append(r_mb)
    print("Created Modbus_Comm routine with", len(mb_rungs), "rungs")

    # 7. Update Routine Input: add JSR(IO_Mapping_In,0) as Rung 0
    r_input = prog.find('.//Routine[@Name="Input"]')
    rll_inp = r_input.find('RLLContent')
    rungs_inp = rll_inp.findall('Rung')
    # Check if IO_Mapping_In is already called
    has_io_in = any('IO_Mapping_In' in (r.findtext('Text') or '') for r in rungs_inp)
    if not has_io_in:
        new_rung = ET.Element('Rung', {'Number': '0', 'Type': 'N'})
        c_elem = ET.SubElement(new_rung, 'Comment')
        c_elem.text = "Map physical input modules (Slot 7 DI, Slots 2-4 AI, Slot 6 HART) into program tags"
        t_elem = ET.SubElement(new_rung, 'Text')
        t_elem.text = "JSR(IO_Mapping_In,0);"
        rll_inp.insert(0, new_rung)
        # renumber rungs
        for i, r in enumerate(rll_inp.findall('Rung')):
            r.set('Number', str(i))
        print("Updated Input routine with JSR(IO_Mapping_In,0)")

    # 8. Update Routine Output: add JSR(IO_Mapping_Out,0) as last rung
    r_output = prog.find('.//Routine[@Name="Output"]')
    rll_outp = r_output.find('RLLContent')
    rungs_outp = rll_outp.findall('Rung')
    has_io_out = any('IO_Mapping_Out' in (r.findtext('Text') or '') for r in rungs_outp)
    if not has_io_out:
        num = len(rungs_outp)
        new_rung = ET.SubElement(rll_outp, 'Rung', {'Number': str(num), 'Type': 'N'})
        c_elem = ET.SubElement(new_rung, 'Comment')
        c_elem.text = "Map program output tags to physical digital output module (Slot 8 DO)"
        t_elem = ET.SubElement(new_rung, 'Text')
        t_elem.text = "JSR(IO_Mapping_Out,0);"
        print("Updated Output routine with JSR(IO_Mapping_Out,0)")

    # 9. Update Routine MainRoutine: add JSR(Modbus_Comm,0) before Output
    r_main = prog.find('.//Routine[@Name="MainRoutine"]')
    rll_main = r_main.find('RLLContent')
    rungs_main = rll_main.findall('Rung')
    has_mb = any('Modbus_Comm' in (r.findtext('Text') or '') for r in rungs_main)
    if not has_mb:
        # insert before JSR(Output,0)
        idx_out = 3
        for i, r in enumerate(rungs_main):
            if 'Output' in (r.findtext('Text') or ''):
                idx_out = i
                break
        new_rung = ET.Element('Rung', {'Number': str(idx_out), 'Type': 'N'})
        c_elem = ET.SubElement(new_rung, 'Comment')
        c_elem.text = "Poll Modbus communication from Murphy engine panels via MVI56E-MCM module"
        t_elem = ET.SubElement(new_rung, 'Text')
        t_elem.text = "XIO(S:FS)JSR(Modbus_Comm,0);"
        rll_main.insert(idx_out, new_rung)
        # renumber rungs
        for i, r in enumerate(rll_main.findall('Rung')):
            r.set('Number', str(i))
        print("Updated MainRoutine with JSR(Modbus_Comm,0)")

    # Write output to P20890_Angola_RSLogix5000_V17.L5X
    tree.write('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X', encoding='utf-8', xml_declaration=True)
    print("Successfully updated Ladder_project/P20890_Angola_RSLogix5000_V17.L5X")

    # Also create Emulator companion file
    tree_emu = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
    root_emu = tree_emu.getroot()
    ctrl_emu = root_emu.find('Controller')
    ctrl_emu.set('ProcessorType', 'Emulator')
    loc_mod = root_emu.find('.//Module[@Name="Local"]')
    loc_mod.set('CatalogNumber', 'Emulator')
    loc_mod.set('ProductCode', '53')
    tree_emu.write('Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X', encoding='utf-8', xml_declaration=True)
    print("Successfully created Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X")

update_l5x()
