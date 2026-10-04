import sys
import struct

HEADER_MAGIC = bytes([0xAC, 0x11, 0xD3, 0x03])
FOOTER_MAGIC = bytes([0xAA, 0xA1, 0xDA, 0xAA])

def convert_ms_to_tg_with_name(ms_bin_path: str, tg_template_path: str, output_bin_path: str):
    print(f"Reading Model:Samples file: {ms_bin_path}")
    with open(ms_bin_path, "rb") as f:
        ms_data = bytearray(f.read())

    print(f"Reading Model-TG Template file: {tg_template_path}")
    with open(tg_template_path, "rb") as f:
        tg_data = bytearray(f.read())

    print("Migrating pattern trigs, note data, and microtiming arrays...")
    SEQ_START = 556
    SEQ_LEN = (len(ms_data) - 12) - SEQ_START
    
    # 1. Transfer the full project performance data block
    tg_data[SEQ_START:SEQ_START+SEQ_LEN] = ms_data[SEQ_START:SEQ_START+SEQ_LEN]

    # 2. Update Header Metadata for Model-TG Configuration
    tg_data[0:4] = HEADER_MAGIC
    tg_data[6:8] = b'\x07\x00'  # Force Model:Cycles/TG Device profile

    # 3. FIX: Surgically migrate the original Project Name string from the M:S file
    # This copies the name text (e.g., 'E2rmx') so it shows up correctly on the screen!
    print("Surgically restoring the original project name tags...")
    tg_data[36:48] = ms_data[36:48]

    # 4. Recalculate CRC-32 Validation Checksums for the Footer
    print("Recalculating file integrity hashes...")
    from dx2_decompress import firmware_crc32
    
    tg_body = tg_data[31:-12]
    tg_crc = firmware_crc32(tg_body, 0xFFFFFFFF)
    
    # Pack the new checksum back into the official 12-byte footer layout
    tg_footer = struct.pack(">I", tg_crc) + b'\x04\x04\x21\x00' + FOOTER_MAGIC
    
    final_tg_bin = bytes(tg_data[:-12] + tg_footer)

    with open(output_bin_path, "wb") as f:
        f.write(final_tg_bin)
    print(f"Successfully generated converted Model-TG binary matrix layout with native name flags.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python ms_to_tg_converter.py <MS_Project_Flat.bin> <TG_Empty_Flat.bin> <Output_TG.bin>")
        sys.exit(1)
    convert_ms_to_tg_with_name(sys.argv[1], sys.argv[2], sys.argv[3])