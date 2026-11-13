import xml.etree.ElementTree as ET
import os
import sys

sys.path.append('Ladder_project')
import comments_library

ROUTINE_MAP = {
    'AOI_AI_Channel': comments_library.AOI_COMMENTS,
    'MainRoutine': comments_library.MAIN_COMMENTS,
    'Init': comments_library.INIT_COMMENTS,
    'Input': comments_library.INPUT_COMMENTS,
    'DI_1': comments_library.DI1_COMMENTS,
    'DI_2': comments_library.DI2_COMMENTS,
    'AI_1': comments_library.AI1_COMMENTS,
    'AI_2': comments_library.AI2_COMMENTS,
    'AI_3': comments_library.AI3_COMMENTS,
    'Vote_1': comments_library.VOTE1_COMMENTS,
    'Logic': comments_library.LOGIC_COMMENTS,
    'CE_LOG': comments_library.CELOG_COMMENTS,
    'Sound': comments_library.SOUND_COMMENTS,
    'Output': comments_library.OUTPUT_COMMENTS,
    'Shutdow': comments_library.SHUTDOW_COMMENTS,
    'Protect': comments_library.PROTECT_COMMENTS,
    'Indicat': comments_library.INDICAT_COMMENTS,
    'Loc_Al': comments_library.LOCAL_COMMENTS,
    'FLT_1': comments_library.FLT1_COMMENTS,
    'Modbus_Comm': comments_library.MODBUS_COMMENTS,
    'IO_Mapping_In': comments_library.IOMAP_IN_COMMENTS,
    'IO_Mapping_Out': comments_library.IOMAP_OUT_COMMENTS,
}

def serialize_node(elem, level=0):
    indent = "  " * level
    tag = elem.tag
    
    # Elements that require CDATA wrapping
    if tag in ['Text', 'Comment', 'Description']:
        text = elem.text or ''
        return f"{indent}<{tag}>\n<![CDATA[{text}]]>\n{indent}</{tag}>\n"
        
    attr_str = ""
    if elem.attrib:
        attrs = [f'{k}="{v}"' for k, v in elem.attrib.items()]
        attr_str = " " + " ".join(attrs)
        
    children = list(elem)
    text = (elem.text or '').strip()
    
    if not children and not text:
        return f"{indent}<{tag}{attr_str}/>\n"
    elif not children and text:
        return f"{indent}<{tag}{attr_str}>{text}</{tag}>\n"
    else:
        out = f"{indent}<{tag}{attr_str}>\n"
        for child in children:
            out += serialize_node(child, level + 1)
        out += f"{indent}</{tag}>\n"
        return out

def update_file(filepath):
    print(f"Processing {filepath}...")
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # 1. Update AOI Routine (AOI_AI_Channel -> Logic)
    for aoi in root.iter('AddOnInstructionDefinition'):
        if aoi.get('Name') == 'AOI_AI_Channel':
            desc = aoi.find('Description')
            if desc is None:
                desc = ET.Element('Description')
                aoi.insert(0, desc)
            desc.text = comments_library.ROUTINE_DESCRIPTIONS.get('AOI_AI_Channel', '')
            
            rll = aoi.find('.//RLLContent')
            if rll is not None:
                for rung in rll.findall('Rung'):
                    num = int(rung.get('Number'))
                    if num in comments_library.AOI_COMMENTS:
                        c = rung.find('Comment')
                        if c is None:
                            c = ET.Element('Comment')
                            rung.insert(0, c)
                        c.text = comments_library.AOI_COMMENTS[num]
    
    # 2. Update Program Routines
    prog = root.find('.//Program[@Name="FandG_Angola"]')
    if prog is not None:
        routines = prog.find('Routines')
        if routines is not None:
            for r in routines.findall('Routine'):
                rname = r.get('Name')
                # Routine Description
                if rname in comments_library.ROUTINE_DESCRIPTIONS:
                    rdesc = r.find('Description')
                    if rdesc is None:
                        rdesc = ET.Element('Description')
                        r.insert(0, rdesc)
                    rdesc.text = comments_library.ROUTINE_DESCRIPTIONS[rname]
                
                # Rung Comments
                cmts = ROUTINE_MAP.get(rname, {})
                rll = r.find('RLLContent')
                if rll is not None:
                    for rung in rll.findall('Rung'):
                        num = int(rung.get('Number'))
                        if num in cmts:
                            c = rung.find('Comment')
                            if c is None:
                                c = ET.Element('Comment')
                                rung.insert(0, c)
                            c.text = cmts[num]

    # 3. Serialize and write
    xml_header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    xml_body = serialize_node(root, 0)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_header)
        f.write(xml_body)
        
    print(f"Successfully updated {filepath}!")

if __name__ == '__main__':
    targets = [
        'Ladder_project/P20890_Angola_RSLogix5000_V17.L5X',
        'Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X',
        'Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X'
    ]
    for target in targets:
        update_file(target)
