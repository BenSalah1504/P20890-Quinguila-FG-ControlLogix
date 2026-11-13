import xml.etree.ElementTree as ET

def patch_and_rebuild():
    # Load the base file
    tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
    root = tree.getroot()
    ctrl = root.find('Controller')
    prog = ctrl.find('.//Program[@Name="FandG_Angola"]')

    # 1. Fix Init routine: restore original 3 rungs
    r_init = prog.find('.//Routine[@Name="Init"]')
    rll_init = r_init.find('RLLContent')
    for c in list(rll_init):
        rll_init.remove(c)
    
    r0 = ET.SubElement(rll_init, 'Rung', {'Number': '0', 'Type': 'N'})
    c0 = ET.SubElement(r0, 'Comment')
    c0.text = "Initialize pump and system delay timers at first scan"
    t0 = ET.SubElement(r0, 'Text')
    t0.text = "[MOV(0,Pump_Timer1[0]),MOV(0,System_C_E_Delay[0])];"

    r1 = ET.SubElement(rll_init, 'Rung', {'Number': '1', 'Type': 'N'})
    c1 = ET.SubElement(r1, 'Comment')
    c1.text = "Unlatch acoustic alarm commands at initial power up"
    t1 = ET.SubElement(r1, 'Text')
    t1.text = "[OTU(Tag_DO_15_INT),OTU(SA_7404_001_002_INT)];"

    r2 = ET.SubElement(rll_init, 'Rung', {'Number': '2', 'Type': 'N'})
    c2 = ET.SubElement(r2, 'Comment')
    c2.text = "Clear pump timer accumulator"
    t2 = ET.SubElement(r2, 'Text')
    t2.text = "MOV(0,Pump_Timer1[0]);"

    # 2. Fix Logic routine Rung 4: Include physical System_Reset_PB
    r_logic = prog.find('.//Routine[@Name="Logic"]')
    rll_logic = r_logic.find('RLLContent')
    r4 = rll_logic.find('.//Rung[@Number="4"]')
    if r4 is not None:
        t4 = r4.find('Text')
        t4.text = "[XIC(System_Reset_PB),XIC(System_Reset_HMI),XIC(System_Reset_Startup),XIC(S:FS)]OTE(System_Reset);"
        c4 = r4.find('Comment')
        if c4 is not None:
            c4.text = "Master System Reset: Triggered by panel PB E11 (TB-07 21&22), HMI touch button, auto startup reset, or first scan"

    # 3. Fix Sound routine Rung 44: Connect physical Mute_Alm_PB
    r_sound = prog.find('.//Routine[@Name="Sound"]')
    rll_sound = r_sound.find('RLLContent')
    r44 = rll_sound.find('.//Rung[@Number="44"]')
    if r44 is not None:
        t44 = r44.find('Text')
        t44.text = "XIC(Mute_Alm_PB)OTE(System_Mute);"
        c44 = r44.find('Comment')
        if c44 is not None:
            c44.text = "Alarm Mute/Silence: Activated by physical pushbutton E12 on panel door (TB-07 23&24)"

    # 4. Serialize with exact CDATA formatting
    cdata_tags = {'Text', 'Comment', 'Description', 'Line'}
    
    def serialize_node(elem, level=0):
        indent = "  " * level
        tag = elem.tag
        attrs = "".join([f' {k}="{v}"' for k, v in elem.attrib.items()])
        children = list(elem)
        text = elem.text or ""
        
        if tag in cdata_tags:
            val = text.strip()
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
    print("Updated Ladder_project/P20890_Angola_RSLogix5000_V17.L5X")

    # Write Emulate v17 file (Emulator)
    xml_emu = full_xml.replace('ProcessorType="1756-L63"', 'ProcessorType="Emulator"')
    xml_emu = xml_emu.replace('CatalogNumber="1756-L63"', 'CatalogNumber="Emulator"')
    xml_emu = xml_emu.replace('ProductCode="56"', 'ProductCode="53"')
    with open('Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X', 'w', encoding='utf-8') as f:
        f.write(xml_emu)
    print("Updated Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X")

    # Write Studio 5000 v32 file (1756-L82E)
    xml_v32 = full_xml.replace('SoftwareRevision="17.00"', 'SoftwareRevision="32.00"')
    xml_v32 = xml_v32.replace('TargetName="P20890_Angola"', 'TargetName="P20890_Angola_L82E"')
    xml_v32 = xml_v32.replace('Name="P20890_Angola" ProcessorType="1756-L63" MajorRev="17" MinorRev="2"', 'Name="P20890_Angola_L82E" ProcessorType="1756-L82E" MajorRev="32" MinorRev="11"')
    xml_v32 = xml_v32.replace('CatalogNumber="1756-L63" Vendor="1" ProductType="14" ProductCode="56" Major="17" Minor="2"', 'CatalogNumber="1756-L82E" Vendor="1" ProductType="14" ProductCode="167" Major="32" Minor="11"')
    idx_p1 = xml_v32.find('<Bus Size="13"/>\n          </Port>')
    if idx_p1 != -1:
        end_p1 = idx_p1 + len('<Bus Size="13"/>\n          </Port>')
        xml_v32 = xml_v32[:end_p1] + '\n          <Port Id="2" Type="Ethernet" Upstream="false"/>' + xml_v32[end_p1:]
    with open('Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X', 'w', encoding='utf-8') as f:
        f.write(xml_v32)
    print("Updated Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X")

patch_and_rebuild()
