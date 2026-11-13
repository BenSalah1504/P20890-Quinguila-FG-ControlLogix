import xml.etree.ElementTree as ET

def generate_v32_l82e():
    tree = ET.parse('Ladder_project/P20890_Angola_RSLogix5000_V17.L5X')
    root = tree.getroot()

    root.set('SoftwareRevision', '32.00')
    root.set('TargetName', 'P20890_Angola_L82E')

    ctrl = root.find('Controller')
    ctrl.set('Name', 'P20890_Angola_L82E')
    ctrl.set('ProcessorType', '1756-L82E')
    ctrl.set('MajorRev', '32')
    ctrl.set('MinorRev', '11')

    # Update Local Module
    loc = ctrl.find('.//Module[@Name="Local"]')
    loc.set('CatalogNumber', '1756-L82E')
    loc.set('ProductCode', '167')
    loc.set('Major', '32')
    loc.set('Minor', '11')
    
    ports = loc.find('Ports')
    # Add Ethernet port if not present
    eth_port = ports.find('.//Port[@Type="Ethernet"]')
    if eth_port is None:
        ET.SubElement(ports, 'Port', {'Id': '2', 'Type': 'Ethernet', 'Upstream': 'false'})

    tree.write('Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X', encoding='utf-8', xml_declaration=True)
    print("Successfully generated Ladder_project/P20890_Angola_Studio5000_V32_L82E.L5X")

generate_v32_l82e()
