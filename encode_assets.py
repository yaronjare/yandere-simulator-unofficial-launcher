import base64
import os

ZIP_NAME = "PoseMod3.zip"
OUTPUT_FILE = "assets.py"

if os.path.exists(ZIP_NAME):
    print("Reading and encoding archive... Please wait, this may take some time.")
    with open(ZIP_NAME, "rb") as f:
        encoded_data = base64.b64encode(f.read()).decode("utf-8")
    
    chunk_size = 120
    chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
    formatted_base64 = "\n".join(chunks)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# Auto-generated file. Do not edit manually.\n')
        f.write('POSEMOD_ZIP_BASE64 = """\\\n')
        f.write(formatted_base64)
        f.write('\n"""\n')
    
    print(f"Success! {OUTPUT_FILE} is optimized for PyInstaller and ready for import.")
else:
    print(f"Error: {ZIP_NAME} not found in the current directory!")
