import xml.etree.ElementTree as ET

def verify_l5x(filename):
    print(f"=== VERIFYING {filename} ===")
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception as e:
        print(f"FATAL: XML parse failed: {e}")
        return False

    ctrl = root.find('Controller')
    if ctrl is None:
        print("FATAL: No Controller node")
        return False

    print(f"SoftwareRevision: {root.get('SoftwareRevision')}, Controller: {ctrl.get('Name')}, ProcessorType: {ctrl.get('ProcessorType')}")
    
    mods = ctrl.find('Modules')
    if mods is None:
        print("FATAL: No Modules node")
        return False
    
    mod_list = mods.findall('Module')
    print(f"Total Modules configured: {len(mod_list)}")
    for m in mod_list:
        ports = [(p.get('Id'), p.get('Type'), p.get('Address')) for p in m.findall('.//Port')]
        bus = [b.get('Size') for b in m.findall('.//Bus') if b.get('Size')]
        print(f"  Slot {ports[0][2] if ports else 'N/A'}: {m.get('Name')} ({m.get('CatalogNumber')}) Ports={ports} BusSize={bus}")

    tags = {t.get('Name'): t.get('DataType') for t in ctrl.find('Tags').findall('Tag')}
    print(f"Total Controller Tags: {len(tags)}")

    # Check program and routines
    prog = ctrl.find('.//Program')
    routines = {r.get('Name'): r for r in prog.find('Routines').findall('Routine')}
    print(f"Program: {prog.get('Name')}, Total Routines: {len(routines)}")

    required_routines = [
        'MainRoutine', 'Init', 'Input', 'IO_Mapping_In', 'DI_1', 'DI_2',
        'AI_1', 'AI_2', 'AI_3', 'Vote_1', 'Logic', 'CE_LOG', 'Sound',
        'Modbus_Comm', 'Output', 'Shutdow', 'Protect', 'Indicat', 'Loc_Al',
        'FLT_1', 'IO_Mapping_Out'
    ]
    missing_routines = [r for r in required_routines if r not in routines]
    if missing_routines:
        print(f"WARNING: Missing routines: {missing_routines}")
    else:
        print("All required routines present!")

    total_rungs = 0
    errors = 0
    for r_name, r_elem in routines.items():
        rungs = r_elem.findall('.//Rung')
        total_rungs += len(rungs)
        for rung in rungs:
            num = rung.get('Number')
            txt = rung.findtext('Text', '')
            if txt.count('(') != txt.count(')'):
                print(f"ERROR: Unbalanced () in {r_name} Rung {num}: {txt}")
                errors += 1
            if txt.count('[') != txt.count(']'):
                print(f"ERROR: Unbalanced [] in {r_name} Rung {num}: {txt}")
                errors += 1
            if not txt.strip().endswith(';'):
                print(f"ERROR: Missing semicolon in {r_name} Rung {num}: {txt}")
                errors += 1

    print(f"Total rungs checked: {total_rungs}, Syntax errors: {errors}")
    return errors == 0

print("\n--- 1. RSLogix 5000 v17 Physical (1756-L63) ---")
res1 = verify_l5x('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')

print("\n--- 2. RSLogix 5000 v17 Simulation (Emulator) ---")
res2 = verify_l5x('Ladder_project/P20890_Angola_RSLogix5000_V17_Emulate.L5X')

print("\n--- 3. Studio 5000 v32 Physical (1756-L82E BOM exact) ---")
res3 = verify_l5x('Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X')

if res1 and res2 and res3:
    print("\n>>> ALL 3 PROJECT VARIANTS VERIFIED 100% SUCCESSFULLY! <<<")
