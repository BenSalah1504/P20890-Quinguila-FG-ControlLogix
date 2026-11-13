import xml.etree.ElementTree as ET

tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
root = tree.getroot()

for r in root.findall('.//Routine'):
    if r.get('Name') == 'MainRoutine':
        for rung in r.findall('.//Rung'):
            t = rung.find('Text')
            print(f"Rung {rung.get('Number')}: {t.text if t is not None else ''}")
