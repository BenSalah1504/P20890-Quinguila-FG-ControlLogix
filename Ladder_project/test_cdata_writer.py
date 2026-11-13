def write_l5x_with_cdata(tree, output_path):
    import xml.etree.ElementTree as ET
    
    # We can write a custom serializer for L5X that wraps Text, Comment, Description, Line in CDATA
    cdata_tags = {'Text', 'Comment', 'Description', 'Line'}
    
    def serialize_elem(elem, level=0):
        indent = "  " * level
        tag = elem.tag
        attrs = "".join([f' {k}="{v}"' for k, v in elem.attrib.items()])
        
        children = list(elem)
        text = elem.text or ""
        
        if tag in cdata_tags and text.strip():
            # Wrap in CDATA
            val = text.strip()
            # If text doesn't already have CDATA
            if not val.startswith("<![CDATA["):
                cdata_content = f"<![CDATA[{val}]]>"
            else:
                cdata_content = val
            return f"{indent}<{tag}{attrs}>\n{indent}  {cdata_content}\n{indent}</{tag}>\n"
        
        if not children and not text.strip():
            return f"{indent}<{tag}{attrs}/>\n"
        
        s = f"{indent}<{tag}{attrs}>\n"
        if text.strip() and tag not in cdata_tags:
            s = f"{indent}<{tag}{attrs}>{text.strip()}</{tag}>\n"
            return s
            
        for child in children:
            s += serialize_elem(child, level + 1)
        s += f"{indent}</{tag}>\n"
        return s

    root = tree.getroot()
    xml_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    xml_str += serialize_elem(root, 0)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"Wrote {output_path} with CDATA preservation!")

# Test on a small sample
