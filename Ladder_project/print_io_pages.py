with open(r'C:\Users\Wajdi TAKTAK\Desktop\DOC\ws_wb\_work\txt\IO_List_01-MAN-03-06-PDF-C2C_Final.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('===== PAGE 3 =====')
print(text[idx:])
