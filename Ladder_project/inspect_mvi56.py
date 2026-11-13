import xml.etree.ElementTree as ET

path = r'C:\Users\Wajdi TAKTAK\Downloads\MVI56E_MCMR SAMPLE LADDERS\MVI56(E)MCMR_AddOn_Rung_v1_5.L5X'
tree = ET.parse(path)
root = tree.getroot()

for r in root.findall('.//Rung'):
    print("Rung:", r.get('Number'), r.findtext('Text', ''))
for d in root.findall('.//DataType'):
    print("DataType:", d.get('Name'))
for a in root.findall('.//AddOnInstructionDefinition'):
    print("AOI:", a.get('Name'))
