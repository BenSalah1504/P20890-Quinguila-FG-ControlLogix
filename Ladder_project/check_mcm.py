import xml.etree.ElementTree as ET

ref_path = r'C:\Users\Wajdi TAKTAK\.workbuddy-ai\workspace\sessions\38c5b29d-e87a-48e7-91d1-eeae5578f803\modify_backup\14.m.1d57d9fc.GNTF_FGCP_7404_001_V17_review.L5X'
tree = ET.parse(ref_path)
root = tree.getroot()

tags = root.find('.//Tags')
for t in tags.findall('Tag'):
    if t.get('Name') in ['MCM_IN', 'MCM_OUT', 'MB_P2300_ALMCODE', 'MB_P2300_RPM']:
        print(ET.tostring(t, encoding='unicode'))
