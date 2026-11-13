import xml.etree.ElementTree as ET

ref_path = r'C:\Users\Wajdi TAKTAK\.workbuddy-ai\workspace\sessions\38c5b29d-e87a-48e7-91d1-eeae5578f803\modify_backup\14.m.1d57d9fc.GNTF_FGCP_7404_001_V17_review.L5X'
tree = ET.parse(ref_path)
root = tree.getroot()

for r in root.findall('.//Routine'):
    if r.get('Name') == 'Modbus_Comm':
        print(f"=== Routine {r.get('Name')} ({len(r.findall('.//Rung'))} rungs) ===")
        for rung in r.findall('.//Rung'):
            t = rung.findtext('Text', '')
            c = rung.findtext('Comment', '')
            print(f"Rung {rung.get('Number')}: {c.strip()} -> {t.strip()}")
