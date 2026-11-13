import xml.etree.ElementTree as ET

tree = ET.parse('Ladder_project/var.xml')
root = tree.getroot()

dis = []
dos = []
ais = []

for v in root.findall('Variable'):
    name = v.findtext('Name', '')
    addr = v.findtext('IOAddress', '')
    desc = v.findtext('Description', '')
    dtype = v.findtext('DataType', '')
    if addr.startswith('%I'):
        dis.append((addr, name, dtype, desc))
    elif addr.startswith('%Q'):
        dos.append((addr, name, dtype, desc))
    elif addr.startswith('%AI'):
        ais.append((addr, name, dtype, desc))

dis.sort(key=lambda x: int(x[0][2:]) if x[0][2:].isdigit() else 999)
dos.sort(key=lambda x: int(x[0][2:]) if x[0][2:].isdigit() else 999)
ais.sort(key=lambda x: int(x[0][3:]) if x[0][3:].isdigit() else 999)

print(f"=== DISCRETE INPUTS (%I) Total: {len(dis)} ===")
for d in dis:
    print(f"{d[0]:<8} {d[1]:<25} {d[3]}")

print(f"\n=== DISCRETE OUTPUTS (%Q) Total: {len(dos)} ===")
for d in dos:
    print(f"{d[0]:<8} {d[1]:<25} {d[3]}")

print(f"\n=== ANALOG INPUTS (%AI) Total: {len(ais)} ===")
for d in ais:
    print(f"{d[0]:<8} {d[1]:<25} {d[3]}")
