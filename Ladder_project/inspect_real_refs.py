import xml.etree.ElementTree as ET

files = [
    r'C:\Users\Wajdi TAKTAK\Desktop\DOC\ws_wb\_work\ref\real_clx.L5X',
    r'C:\Users\Wajdi TAKTAK\Desktop\DOC\ws_wb\_work\ref\ref_v20.L5X',
    r'C:\Users\Wajdi TAKTAK\Downloads\AB_ST_V17.L5X',
    r'C:\Users\Wajdi TAKTAK\Downloads\test_A_v17_skeleton.L5X'
]

for path in files:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        ctrl = root.find('Controller')
        print("="*60)
        print("FILE:", path)
        print("Root attrs:", root.attrib)
        if ctrl is not None:
            print("Controller attrs:", ctrl.attrib)
            mods = ctrl.find('Modules')
            if mods is not None:
                print("Modules count:", len(mods.findall('Module')))
                for m in mods.findall('Module'):
                    ports = [(p.get('Id'), p.get('Type'), p.get('Address')) for p in m.findall('.//Port')]
                    print(f"  Module: {m.get('Name')} | Cat: {m.get('CatalogNumber')} | V: {m.get('Vendor')} | PT: {m.get('ProductType')} | PC: {m.get('ProductCode')} | Rev: {m.get('Major')}.{m.get('Minor')} | Ports: {ports}")
            else:
                print("No Modules element")
    except Exception as e:
        print("Error reading", path, e)
