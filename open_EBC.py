import gzip
import pandas as pd



def ebc_gz_to_csv(gz_path, csv_path, codepage="cp037", record_length=100, skip_bytes=240):
    with gzip.open(gz_path, "rb") as f:
        raw = f.read()
    
    # 1. Skip Header Labels (IBM Standard Labels = 80 bytes each)
    # Vol1 (80) + HDR1 (80) + HDR2 (80) = 240 bytes. Correct.
    raw = raw[skip_bytes:]
    
    records = []
    # 2. Process record by record in BYTE format first
    for i in range(0, len(raw) - record_length + 1, record_length):
        rec = raw[i : i + record_length]
        
        # 3. Decode each field (This handles potential non-text chars better)
        # Note: If OIL/GOR are COMP-3 (packed), you cannot .decode() the whole string.
        # But assuming they are Zoned Decimal (standard EBCDIC text numbers):
        try:
            row = [
                rec[0:3].decode(codepage).strip(),    # DW-DST (1-3)
                rec[3:11].decode(codepage).strip(),   # DW-FIELD (4-11)
                rec[11:17].decode(codepage).strip(),  # DW-OPERATOR (12-17)
                rec[17:22].decode(codepage).strip(),  # DW-LSE (18-22)
                rec[22:23].decode(codepage).strip(),  # DW-RECNO (23)
                rec[23:29].decode(codepage).strip(),  # DW-WELLNO (24-29)
                rec[29:32].decode(codepage).strip(),  # DW-CO (30-32)
                rec[32:33].decode(codepage).strip(),  # DW-TYPEW (33)
                rec[33:34].decode(codepage).strip(),  # DW-EX14B-CD (34)
                rec[34:40].decode(codepage).strip(),  # DW-14B-DATE (35-40)
                rec[40:41].decode(codepage).strip(),  # DW-EXC-TST (41)
                rec[41:42].decode(codepage).strip(),  # DW-TST-EFF (42)
                
                # --- TEST 1 (Pos 43-58) ---
                rec[42:50].decode(codepage).strip(),  # TST-DT1 (43-50)
                rec[50:55].decode(codepage).strip(),  # OIL1 (51-55) - PIC 9(4)V9
                rec[55:56].decode(codepage).strip(),  # METHOD1 (56)
                rec[56:60].decode(codepage).strip(),  # WATER1 (57-60)
                rec[60:65].decode(codepage).strip(),  # GOR1 (61-65)

                # --- TEST 2 (Pos 66-81) ---
                rec[65:73].decode(codepage).strip(),  # TST-DT2 (66-73)
                rec[73:78].decode(codepage).strip(),  # OIL2 (74-78)
                rec[78:79].decode(codepage).strip(),  # METHOD2 (79)
                rec[79:83].decode(codepage).strip(),  # WATER2 (80-83)
                rec[83:88].decode(codepage).strip(),  # GOR2 (84-88)

                # --- END INFO (Pos 89+) ---
                rec[88:89].decode(codepage).strip(),  # OFF-SHORE (89)
                rec[89:90].decode(codepage).strip(),  # FRM-LCK (90)
                rec[90:91].decode(codepage).strip(),  # SUB-WELL (91)
                rec[91:92].decode(codepage).strip(),  # DELQ-FORM (92)
                rec[92:98].decode(codepage).strip(),  # DT-LST-UTL (93-98)
            ]
            records.append(row)
        except UnicodeDecodeError:
            continue # Skip corrupted/inter-block noise
            
    columns = [
        "DST","FIELD","OPERATOR","LEASE","RECNO","WELL","CO","TYPE",
        "EX14B_CD","DATE14B","EXC_TST","TST_EFF",
        "TST_DT1","OIL1","MET1","WAT1","GOR1",
        "TST_DT2","OIL2","MET2","WAT2","GOR2",
        "OFFSHORE","FRM_LCK","SUB_WELL","DELQ","LAST_UTIL"
    ]
    
    df = pd.DataFrame(records, columns=columns)
    df.to_csv(csv_path, index=False)



ebc_gz_to_csv(r'C:\Users\txjam\Documents\homework\design\records\oltdw.ebc.gz',
               r'C:\Users\txjam\Documents\homework\design\records\oltdw.csv')