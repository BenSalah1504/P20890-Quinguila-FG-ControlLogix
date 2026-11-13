import xml.etree.ElementTree as ET

tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
root = tree.getroot()

for r in root.findall('.//Routine'):
    name = r.get('Name')
    if name in ['Input', 'DI_1', 'Output']:
        print(f"=== Routine: {name} ===")
        for rung in r.findall('.//Rung'):
            num = rung.get('Number')
            text = rung.find('Text')
            print(f"Rung {num}: {text.text if text is not None else ''}")
