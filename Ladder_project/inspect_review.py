import xml.etree.ElementTree as ET

ref_path = r'C:\Users\Wajdi TAKTAK\.workbuddy-ai\workspace\sessions\38c5b29d-e87a-48e7-91d1-eeae5578f803\modify_backup\14.m.1d57d9fc.GNTF_FGCP_7404_001_V17_review.L5X'
tree = ET.parse(ref_path)
root = tree.getroot()

for r in root.findall('.//Routine'):
    name = r.get('Name')
    if name in ['Output', 'DI_1']:
        print(f"=== Routine {name} ===")
        for rung in r.findall('.//Rung'):
            t = rung.find('Text')
            print(f"Rung {rung.get('Number')}: {t.text if t is not None else ''}")
