import xml.etree.ElementTree as ET
import re

def build_perfect_l5x():
    # 1. Load the file
    tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
    root = tree.getroot()
    ctrl = root.find('Controller')

    # Ensure schema attributes on Root
    root.set('SchemaRevision', '1.0')
    root.set('SoftwareRevision', '17.00')
    root.set('TargetName', 'P20890_Angola')
    root.set('TargetType', 'Controller')
    root.set('ContainsContext', 'false')
    root.set('Owner', 'EPPM Angola')
    root.set('ExportOptions', 'NoRawData L5KData')

    # Ensure Controller attributes
    ctrl.set('Use', 'Target')
    ctrl.set('Name', 'P20890_Angola')
    ctrl.set('ProcessorType', '1756-L63')
    ctrl.set('MajorRev', '17')
    ctrl.set('MinorRev', '2')

    # 2. Re-order Controller children strictly per Rockwell XSD:
    # Description -> DataTypes -> Modules -> AddOnInstructionDefinitions -> Tags -> Programs -> Tasks -> CST -> WallClockTime
    child_map = {}
    for c in list(ctrl):
        child_map[c.tag] = c
        ctrl.remove(c)

    # Re-build Modules properly
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
    port1_local = ET.SubElement(ports_local, 'Port', {'Id': '1', 'Address': '0', 'Type': 'ICP', 'Upstream': 'false'})
    ET.SubElement(port1_local, 'Bus', {'Size': '13'})

    # Slot 1: 1756-EN2T
    mod_en2t = ET.SubElement(new_modules, 'Module', {
        'Name': 'EN2T_Slot01',
        'CatalogNumber': '1756-EN2T',
        'Vendor': '1',
        'ProductType': '12',
        'ProductCode': '166',
        'Major': '11',
        'Minor': '2',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_en2t, 'EKey', {'State': 'CompatibleModule'})
    ports_en2t = ET.SubElement(mod_en2t, 'Ports')
    ET.SubElement(ports_en2t, 'Port', {'Id': '1', 'Address': '1', 'Type': 'ICP', 'Upstream': 'true'})
    p2 = ET.SubElement(ports_en2t, 'Port', {'Id': '2', 'Type': 'Ethernet', 'Upstream': 'false'})
    ET.SubElement(p2, 'Bus')

    # Slots 2, 3, 4, 5: 1756-IF16/B
    for slot, s_name in [(2, 'AI_Slot02_IF16'), (3, 'AI_Slot03_IF16'), (4, 'AI_Slot04_IF16'), (5, 'AI_Slot05_IF16')]:
        mod = ET.SubElement(new_modules, 'Module', {
            'Name': s_name,
            'CatalogNumber': '1756-IF16/B',
            'Vendor': '1',
            'ProductType': '10',
            'ProductCode': '6',
            'Major': '2',
            'Minor': '1',
            'ParentModule': 'Local',
            'ParentModPortId': '1',
            'Inhibited': 'false',
            'MajorFault': 'false'
        })
        ET.SubElement(mod, 'EKey', {'State': 'CompatibleModule'})
        ports = ET.SubElement(mod, 'Ports')
        ET.SubElement(ports, 'Port', {'Id': '1', 'Address': str(slot), 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 6: 1756-IF8H
    mod_if8h = ET.SubElement(new_modules, 'Module', {
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
    ET.SubElement(mod_if8h, 'EKey', {'State': 'CompatibleModule'})
    ports_if8h = ET.SubElement(mod_if8h, 'Ports')
    ET.SubElement(ports_if8h, 'Port', {'Id': '1', 'Address': '6', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 7: 1756-IB32/B
    mod_ib32 = ET.SubElement(new_modules, 'Module', {
        'Name': 'DI_Slot07_IB32',
        'CatalogNumber': '1756-IB32/B',
        'Vendor': '1',
        'ProductType': '7',
        'ProductCode': '12',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ib32, 'EKey', {'State': 'CompatibleModule'})
    ports_ib32 = ET.SubElement(mod_ib32, 'Ports')
    ET.SubElement(ports_ib32, 'Port', {'Id': '1', 'Address': '7', 'Type': 'ICP', 'Upstream': 'true'})

    # Slot 8: 1756-OB32
    mod_ob32 = ET.SubElement(new_modules, 'Module', {
        'Name': 'DO_Slot08_OB32',
        'CatalogNumber': '1756-OB32',
        'Vendor': '1',
        'ProductType': '7',
        'ProductCode': '17',
        'Major': '3',
        'Minor': '1',
        'ParentModule': 'Local',
        'ParentModPortId': '1',
        'Inhibited': 'false',
        'MajorFault': 'false'
    })
    ET.SubElement(mod_ob32, 'EKey', {'State': 'CompatibleModule'})
    ports_ob32 = ET.SubElement(mod_ob32, 'Ports')
    ET.SubElement(ports_ob32, 'Port', {'Id': '1', 'Address': '8', 'Type': 'ICP', 'Upstream': 'true'})

    child_map['Modules'] = new_modules

    # Attach in strict order:
    ordered_keys = [
        'Description', 'DataTypes', 'Modules', 'AddOnInstructionDefinitions',
        'Tags', 'Programs', 'Tasks', 'CST', 'WallClockTime'
    ]
    for k in ordered_keys:
        if k in child_map:
            ctrl.append(child_map[k])

    # 3. Add any missing tags
    tags_elem = child_map['Tags']
    existing_tags = {t.get('Name'): t for t in tags_elem.findall('Tag')}
    
    needed_tags = [
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
        ('HART_DG011R_Enable', 'BOOL', None, 'Enable reading Open Path Gas Detector 7404-DG-011R from Slot 6 1756-IF8H HART module'),
        ('System_Reset_PB', 'BOOL', None, 'System reset pushbutton on panel door E11 (TB-07 21&22)'),
        ('Mute_Alm_PB', 'BOOL', None, 'Alarm mute/silence pushbutton on panel door E12 (TB-07 23&24)'),
        ('SD_GAS_GENERATORS', 'BOOL', None, 'Shutdown of all gas generators command'),
        ('ALM_H2S', 'BOOL', None, 'Common H2S alarm indication'),
        ('ALM_SMOKE', 'BOOL', None, 'Common smoke alarm indication'),
        ('LAMP_CR1', 'BOOL', None, 'Relay CR1 for LED L2 & L8'),
        ('LAMP_CR2', 'BOOL', None, 'Relay CR2 for LED L3 & L9'),
        ('LAMP_CR3', 'BOOL', None, 'Relay CR3 for LED L4 & L10'),
        ('LAMP_CR4', 'BOOL', None, 'Relay CR4 for LED L5 & L11'),
        ('LAMP_CR5', 'BOOL', None, 'Relay CR5 for LED L6 & L12'),
        ('LAMP_CR6', 'BOOL', None, 'Relay CR6 for LED L7 & L13')
    ]

    for name, dtype, dim, desc in needed_tags:
        if name not in existing_tags:
            t_elem = ET.SubElement(tags_elem, 'Tag', {'Name': name, 'TagType': 'Base', 'DataType': dtype})
            if dim:
                t_elem.set('Dimensions', dim)
            d_elem = ET.SubElement(t_elem, 'Description')
            d_elem.text = desc

    # 4. Update IO_Mapping_In according to 01-MAN-03-06-PDF-C2C Final
    prog = ctrl.find('.//Program[@Name="FandG_Angola"]')
    routines_elem = prog.find('Routines')
    
    r_io_in = prog.find('.//Routine[@Name="IO_Mapping_In"]')
    if r_io_in is not None:
        routines_elem.remove(r_io_in)
        
    r_io_in = ET.Element('Routine', {'Name': 'IO_Mapping_In', 'Type': 'RLL'})
    rll_in = ET.SubElement(r_io_in, 'RLLContent')

    # Slot 7 DI mapping per 01-MAN-03-06-PDF-C2C Final
    di_c2c = [
        ('Local:7:I.Data.0', 'ZSH_6401_001', '6401-ZSH-001 ESD valve open (TB-07: 1&2)'),
        ('Local:7:I.Data.1', 'ZSL_6401_001', '6401-ZSL-001 ESD valve closed (TB-07: 3&4)'),
        ('Local:7:I.Data.2', 'SpareDI_02', 'Spare DI Ch 2 (TB-07: 5&6)'),
        ('Local:7:I.Data.3', 'LS_7503_002', '7503-LS-002 Diesel day tank low level switch (TB-07: 7&8)'),
        ('Local:7:I.Data.4', 'FS_7503_001', '7503-FS-001 Foam stop button (TB-07: 9&10)'),
        ('Local:7:I.Data.5', 'LS_7503_001', '7503-LS-001 AFFF Foam tank low level switch (TB-07: 11&12)'),
        ('Local:7:I.Data.6', 'Pump_A_PulsIn', '75-C-01A Deluge Pump A pulse counter feedback (TB-07: 13&14)'),
        ('Local:7:I.Data.7', 'Pump_B_Start_PulsIn', '75-C-01B Deluge Pump B pulse counter feedback (TB-07: 15&16)'),
        ('Local:7:I.Data.8', 'Pump_B_Inhibited', '75-SB-01B Standby Pump B keyswitch: 1=Auto, 0=Inhibited (TB-07: 17&18)'),
        ('Local:7:I.Data.9', 'SpareDI_09', 'Spare DI Ch 9 (TB-07: 19&20)'),
        ('Local:7:I.Data.10', 'System_Reset_PB', 'FGCP-7404-001 RESET Alarm Button E11 (TB-07: 21&22)'),
        ('Local:7:I.Data.11', 'Mute_Alm_PB', 'FGCP-7404-001 MUTE Alarm Button E12 (TB-07: 23&24)'),
        ('Local:7:I.Data.12', 'ESDV_6401_001', '6401-ESDV-001 ESD Fuel Gas Button E9 (TB-07: 25&26)'),
        ('Local:7:I.Data.13', 'INHIBIT_FOAM_REL', 'FGCP-7404-001 Inhibit Foam Release Keyswitch S2 (TB-07: 27&28)'),
        ('Local:7:I.Data.14', 'INHIBIT_ALL_OUTPUTS', 'FGCP-7404-001 Inhibit All Outputs Keyswitch S3 (TB-07: 29&30)'),
    ] + [(f'Local:7:I.Data.{i}', f'SpareDI_{i:02d}', f'Spare DI Ch {i} (TB-07: {2*i+1}&{2*i+2})') for i in range(15, 32)]

    rung_num = 0
    for src, dst, comment in di_c2c:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"DI Slot 7 ({src}) -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"XIC({src})OTE({dst});"
        rung_num += 1

    # Analog Inputs Slot 2 & Slot 3 per 01-MAN-03-06-PDF-C2C Final
    ai_mappings = [
        ('Local:2:I.Ch0Data', 'DG_7404_001', '7404-DG-001 Gas detector pump house (TB-02: 1-3)'),
        ('Local:2:I.Ch1Data', 'DG_7404_002', '7404-DG-002 Gas detector pump house (TB-02: 4-6)'),
        ('Local:2:I.Ch2Data', 'DG_7404_003', '7404-DG-003 Gas detector pump house (TB-02: 7-9)'),
        ('Local:2:I.Ch3Data', 'DG_7404_004', '7404-DG-004 Gas detector pump house (TB-02: 10-12)'),
        ('Local:2:I.Ch4Data', 'DG_7404_005', '7404-DG-005 Gas detector pump house (TB-02: 13-15)'),
        ('Local:2:I.Ch5Data', 'DG_7404_006', '7404-DG-006 Gas detector pump house (TB-02: 16-18)'),
        ('Local:2:I.Ch6Data', 'DG_7404_007', '7404-DG-007 Gas detector pump house (TB-02: 19-21)'),
        ('Local:2:I.Ch7Data', 'DG_7404_008', '7404-DG-008 Gas detector pump house (TB-02: 22-24)'),
        ('Local:2:I.Ch8Data', 'DG_7404_009', '7404-DG-009 Gas detector pump house (TB-02: 25-27)'),
        ('Local:2:I.Ch9Data', 'DG_7404_010', '7404-DG-010 Gas detector pump house (TB-02: 28-30)'),
        ('Local:3:I.Ch3Data', 'PST_7503_001', '7503-PST-001 Deluge line pressure (TB-03: 10&11)'),
        ('Local:3:I.Ch4Data', 'PST_7002_001', '7002-PST-001 Air accumulator pressure ESDV (TB-03: 13&14)'),
        ('Local:3:I.Ch5Data', 'PST_6401_001', '6401-PST-001 Fuel gas pressure (TB-03: 16&17)'),
        ('Local:3:I.Ch6Data', 'FR_7503_003', '7503-FR-003 Foam release inside Local CP (TB-03: 19)'),
        ('Local:3:I.Ch7Data', 'FR_7503_001_002', '7503-FR-001/002 Foam release outside (TB-03: 20)')
    ]
    for src, dst, comment in ai_mappings:
        rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"AI {src} -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"MOV({src},{dst});"
        rung_num += 1

    # Single Rung for Open Path Gas Detector 7404-DG-011R (Mutually Exclusive: Slot 6 HART or Slot 2 Ch12 4-20mA)
    rung = ET.SubElement(rll_in, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
    c_elem = ET.SubElement(rung, 'Comment')
    c_elem.text = "7404-DG-011R Open Path Detector: Slot 6 Ch0 (HART) when enabled, else Slot 2 Ch12 (4-20mA)"
    t_elem = ET.SubElement(rung, 'Text')
    t_elem.text = "[XIC(HART_DG011R_Enable)MOV(Local:6:I.Ch0Data,DG_7404_011R),XIO(HART_DG011R_Enable)MOV(Local:2:I.Ch12Data,DG_7404_011R)];"
    rung_num += 1

    routines_elem.append(r_io_in)

    # 5. Update IO_Mapping_Out according to 01-MAN-03-06-PDF-C2C Final
    r_io_out = prog.find('.//Routine[@Name="IO_Mapping_Out"]')
    if r_io_out is not None:
        routines_elem.remove(r_io_out)
        
    r_io_out = ET.Element('Routine', {'Name': 'IO_Mapping_Out', 'Type': 'RLL'})
    rll_out = ET.SubElement(r_io_out, 'RLLContent')

    do_c2c = [
        ('PumpShutdown', 'Local:8:O.Data.0', 'ESD_TRIP: Pump Shutdown (TB-08: 1&2) - Fail Safe Active Low'),
        ('EY_6401_001_002', 'Local:8:O.Data.1', '6401-EY-001/002: SDV Fuel Gas Valve (TB-08: 3&4) - Fail Safe Active Low'),
        ('SA_7404_001_002', 'Local:8:O.Data.2', '7404-SA-001/002: Pump House Alarm Siren/Beacon (TB-08: 5&6)'),
        ('Pump_A_PulsOut', 'Local:8:O.Data.3', '7503-PUMP-A: Pump A Pulsed Output (TB-08: 7)'),
        ('PUMP_A', 'Local:8:O.Data.4', '7503-PUMP-A: Deluge pump A Start/Stop contactor (TB-08: 9)'),
        ('Pump_B_Start_PulsOut', 'Local:8:O.Data.5', '7503-PUMP-B: Pump B Pulsed Output (TB-08: 11)'),
        ('PUMP_B_START', 'Local:8:O.Data.6', '7503-PUMP-B: Deluge pump B Start solenoid (TB-08: 13)'),
        ('PUMP_B_STOP', 'Local:8:O.Data.7', '7503-PUMP-B: Deluge pump B Stop solenoid (TB-08: 15&16)'),
        ('P2100_P2200', 'Local:8:O.Data.8', 'EDB1: Oil booster pump trip relay (TB-08: 17&18) - Fail Safe Active Low'),
        ('P3600_P3700', 'Local:8:O.Data.9', 'EDB1: Water booster pump trip relay (TB-08: 19&20) - Fail Safe Active Low'),
        ('PLC_Fault', 'Local:8:O.Data.10', 'Spare Ch 10: PLC Fault Indication Relay (TB-08: 21&22)'),
        ('Tag_DO_13', 'Local:8:O.Data.11', 'ESDV closed led L14 (TB-08: 23&24)'),
        ('Tag_DO_12', 'Local:8:O.Data.12', 'ESDV open led L15 (TB-08: 25&26)'),
        ('Tag_DO_14', 'Local:8:O.Data.13', 'ESDV low air indication L16 (TB-08: 27&28)'),
        ('Tag_DO_11', 'Local:8:O.Data.14', 'Low fuel gas pressure led L17 (TB-08: 29&30)'),
        ('LAMP_CR1', 'Local:8:O.Data.15', 'Relay CR1 for Led L2 & L8 (TB-08: 31-34)'),
        ('LAMP_CR2', 'Local:8:O.Data.16', 'Relay CR2 for Led L3 & L9 (TB-08: 35-38)'),
        ('LAMP_CR3', 'Local:8:O.Data.17', 'Relay CR3 for Led L4 & L10 (TB-08: 39-42)'),
        ('LAMP_CR4', 'Local:8:O.Data.18', 'Relay CR4 for Led L5 & L11 (TB-08: 43-46)'),
        ('LAMP_CR5', 'Local:8:O.Data.19', 'Relay CR5 for Led L6 & L12 (TB-08: 47-50)'),
        ('LAMP_CR6', 'Local:8:O.Data.20', 'Relay CR6 for Led L7 & L13 (TB-08: 51-54)'),
        ('SD_GAS_GENERATORS', 'Local:8:O.Data.21', 'SD-GE: Shut down of all gas generators (TB-08: 55&56)'),
        ('Tag_DO_15', 'Local:8:O.Data.22', 'Z1: Production Control Room Alarm (TB-08: 57&58)'),
        ('PA_001_Process', 'Local:8:O.Data.23', 'PA-001: Common Process Alarm (TB-08: 59&60)'),
    ] + [(f'SpareDO_{i:02d}', f'Local:8:O.Data.{i}', f'Spare DO Ch {i} (TB-08: {2*i+1}&{2*i+2})') for i in range(24, 30)] + [
        ('ALM_H2S', 'Local:8:O.Data.30', 'H2SA-001/002: H2S Alarm (TB-08: 73&74)'),
        ('ALM_SMOKE', 'Local:8:O.Data.31', 'SDA-001: Smoke Alarm (TB-08: 75&76)')
    ]

    rung_num = 0
    for src, dst, comment in do_c2c:
        rung = ET.SubElement(rll_out, 'Rung', {'Number': str(rung_num), 'Type': 'N'})
        c_elem = ET.SubElement(rung, 'Comment')
        c_elem.text = f"DO {src} -> {dst} : {comment}"
        t_elem = ET.SubElement(rung, 'Text')
        t_elem.text = f"XIC({src})OTE({dst});"
        rung_num += 1

    routines_elem.append(r_io_out)

    # 6. Update Init routine Rung 0 to include physical System_Reset_PB
    r_init = prog.find('.//Routine[@Name="Init"]')
    rll_init = r_init.find('RLLContent')
    r0 = rll_init.find('.//Rung[@Number="0"]')
    if r0 is not None:
        t0 = r0.find('Text')
        t0.text = "[XIC(System_Reset_PB),XIC(System_Reset_HMI),XIC(S:FS)]OTE(System_Reset);"
        c0 = r0.find('Comment')
        if c0 is not None:
            c0.text = "Master System Reset triggered by physical pushbutton E11 (TB-07: 21&22), HMI button, or First Scan"

    # 7. Serialize XML with exact CDATA formatting
    cdata_tags = {'Text', 'Comment', 'Description', 'Line'}
    
    def serialize_node(elem, level=0):
        indent = "  " * level
        tag = elem.tag
        attrs = "".join([f' {k}="{v}"' for k, v in elem.attrib.items()])
        children = list(elem)
        text = elem.text or ""
        
        if tag in cdata_tags:
            val = text.strip()
            # Wrap in CDATA
            return f"{indent}<{tag}{attrs}>\n{indent}  <![CDATA[{val}]]>\n{indent}</{tag}>\n"
        
        if not children and not text.strip():
            return f"{indent}<{tag}{attrs}/>\n"
        
        s = f"{indent}<{tag}{attrs}>\n"
        if text.strip() and not children:
            s = f"{indent}<{tag}{attrs}>{text.strip()}</{tag}>\n"
            return s
            
        for child in children:
            s += serialize_node(child, level + 1)
        s += f"{indent}</{tag}>\n"
        return s

    xml_header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    full_xml = xml_header + serialize_node(root, 0)

    # Write Physical v17 file (1756-L63)
    with open('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X', 'w', encoding='utf-8') as f:
        f.write(full_xml)
    print("Successfully generated Ladder_project/P20890_Angola_RSLogix5000_V17.L5X with CDATA and C2C mapping!")

    # Write Emulate v17 file (Emulator)
    xml_emu = full_xml.replace('ProcessorType="1756-L63"', 'ProcessorType="Emulator"')
    xml_emu = xml_emu.replace('CatalogNumber="1756-L63"', 'CatalogNumber="Emulator"')
    xml_emu = xml_emu.replace('ProductCode="56"', 'ProductCode="53"')
    with open('Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X', 'w', encoding='utf-8') as f:
        f.write(xml_emu)
    print("Successfully generated Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X!")

    # Write Studio 5000 v32 file (1756-L82E)
    xml_v32 = full_xml.replace('SoftwareRevision="17.00"', 'SoftwareRevision="32.00"')
    xml_v32 = xml_v32.replace('TargetName="P20890_Angola"', 'TargetName="P20890_Angola_L82E"')
    xml_v32 = xml_v32.replace('Name="P20890_Angola" ProcessorType="1756-L63" MajorRev="17" MinorRev="2"', 'Name="P20890_Angola_L82E" ProcessorType="1756-L82E" MajorRev="32" MinorRev="11"')
    xml_v32 = xml_v32.replace('CatalogNumber="1756-L63" Vendor="1" ProductType="14" ProductCode="56" Major="17" Minor="2"', 'CatalogNumber="1756-L82E" Vendor="1" ProductType="14" ProductCode="167" Major="32" Minor="11"')
    # Add port 2 Ethernet for L82E
    idx_p1 = xml_v32.find('<Bus Size="13"/>\n          </Port>')
    if idx_p1 != -1:
        end_p1 = idx_p1 + len('<Bus Size="13"/>\n          </Port>')
        xml_v32 = xml_v32[:end_p1] + '\n          <Port Id="2" Type="Ethernet" Upstream="false"/>' + xml_v32[end_p1:]
    with open('Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X', 'w', encoding='utf-8') as f:
        f.write(xml_v32)
    print("Successfully generated Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X!")

build_perfect_l5x()
