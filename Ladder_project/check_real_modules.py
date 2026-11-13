import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\Wajdi TAKTAK\Desktop\DOC\ws_wb\_work\ref\real_clx.L5X')
for m in tree.findall('.//Module'):
    cat = m.get('CatalogNumber') or ''
    name = m.get('Name') or ''
    v = m.get('Vendor') or ''
    pt = m.get('ProductType') or ''
    pc = m.get('ProductCode') or ''
    maj = m.get('Major') or ''
    minr = m.get('Minor') or ''
    ports = [(p.get('Id'), p.get('Type'), p.get('Address')) for p in m.findall('.//Port')]
    print(f"Catalog={cat:<15} Name={name:<12} Vendor={v} ProductType={pt} ProductCode={pc} Rev={maj}.{minr} Ports={ports}")
