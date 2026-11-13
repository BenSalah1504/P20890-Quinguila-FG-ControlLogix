import xml.etree.ElementTree as ET
tree = ET.parse(r'C:\Users\Wajdi TAKTAK\Desktop\DOC\Ladder_project\P20890_Angola_RSLogix5000_V17.L5X')
r = tree.find('.//Routine[@Name="Init"]')
for rung in r.findall('.//Rung'):
    print(rung.get('Number'), (rung.findtext('Text', '') or '').strip())
