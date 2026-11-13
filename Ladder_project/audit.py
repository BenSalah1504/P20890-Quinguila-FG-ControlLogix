import xml.etree.ElementTree as ET, re, collections
P='Ladder_project/P20890_Angola_RSLogix5000_V17.L5X'
raw=open(P,encoding='utf-8').read()
print("HEADER:", raw[:120].replace('\n',' '))
print("CDATA count:", raw.count('<![CDATA['))
root=ET.parse(P).getroot()
ctrl=root.find('Controller')
# 1. who writes each tag (OTE/OTL/OTU/MOV dest/COP dest)
writers=collections.defaultdict(list)
for r in root.iter('Routine'):
    for rg in r.iter('Rung'):
        t=rg.findtext('Text','') or ''
        for m in re.finditer(r'\b(OTE|OTL|OTU)\(([^)]+)\)',t): writers[m.group(2).strip()].append((r.get('Name'),rg.get('Number'),m.group(1)))
        for m in re.finditer(r'\bMOV\(([^,]+),([^)]+)\)',t): writers[m.group(2).strip()].append((r.get('Name'),rg.get('Number'),'MOV'))
print("\n== Tags written by >1 OTE/MOV (double-coil) ==")
for k,v in writers.items():
    ote=[x for x in v if x[2] in('OTE','MOV')]
    if len(ote)>1: print(k,ote)
# 2. physical-input tags written outside IO_Mapping_In
phys=[ 'ZSH_6401_001','ZSL_6401_001','FS_7503_001','LS_7503_001','LS_7503_002','ESDV_6401_001','INHIBIT_FOAM_REL','INHIBIT_ALL_OUTPUTS','DG_7404_001','DG_7404_011R','PST_7503_001','FR_7503_003']
print("\n== Writers of physical-input tags ==")
for p in phys: print(p, writers.get(p))
# 3. AOI_AI_Channel: how PV is used
for a in root.iter('AddOnInstructionDefinition'):
    print("\n== AOI",a.get('Name'),"==")
    for p in a.iter('Parameter'): print("  param",p.get('Name'),p.get('DataType'),p.get('Usage'))
    for rg in a.iter('Rung'): print("  ",(rg.findtext('Text') or '').strip()[:300])
    for l in a.iter('Line'): print("  ST:",(l.text or '').strip()[:200])
# 4. module elements content
for m in ctrl.find('Modules'):
    print("\nMODULE",m.get('Name'),m.get('CatalogNumber'),'PC',m.get('ProductCode'),'children:',[c.tag for c in m])
