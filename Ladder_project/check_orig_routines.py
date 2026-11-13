import xml.etree.ElementTree as ET

tree = ET.parse(r'C:\Users\Wajdi TAKTAK\Desktop\DOC\Ladder_project\P20890_Angola_RSLogix5000_V17.L5X')
root = tree.getroot()

for r in root.findall('.//Routine'):
    print(r.get('Name'), len(r.findall('.//Rung')))
