import keyboard

# Iterate through all key names and print them with their scan codes
for key, scan_codes in keyboard._key_table.items():
    print(f'Key: {key}, Scan Codes: {scan_codes}')
