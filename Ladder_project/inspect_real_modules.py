import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\Wajdi TAKTAK\Desktop\DOC\ws_wb\_work\ref\real_clx.L5X')
root = tree.getroot()
ctrl = root.find('Controller')
mods = ctrl.find('Modules')

for m in mods.findall('Module')[:4]:
    print(ET.tostring(m, encoding='unicode'))
