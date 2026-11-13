import xml.etree.ElementTree as ET

tree = ET.parse('Ladder_project/var.xml')
root = tree.getroot()

matches = []
for v in root.findall('Variable'):
    name = v.findtext('Name', '')
    desc = v.findtext('Description', '')
    addr = v.findtext('IOAddress', '')
    if any(k in name.upper() or k in desc.upper() for k in ['PA_001', 'PROCESS', 'PUMP', 'P2300', 'MURPHY']):
        matches.append((name, addr, desc))

print(f"Total matching variables: {len(matches)}")
for m in matches[:25]:
    print(f"{m[0]:<25} {m[1]:<10} {m[2]}")
