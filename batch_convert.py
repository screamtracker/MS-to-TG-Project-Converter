import os
import glob
import subprocess
import sys
import shutil

# Configuration - adjust these filenames if yours are named differently
DECOMPRESS_SCRIPT = "dx2_decompress.py"
CONVERTER_SCRIPT = "ms_to_tg_converter.py"
COMPRESS_SCRIPT = "dx2_compress.py"
TG_TEMPLATE = "TG_Empty_Flat.bin"

def run_batch_conversion(input_dir=".", output_dir="Converted_Projects"):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Verify that the required templates and scripts are present
    required_files = [DECOMPRESS_SCRIPT, CONVERTER_SCRIPT, COMPRESS_SCRIPT, TG_TEMPLATE]
    for f in required_files:
        if not os.path.exists(f):
            print(f"❌ Error: Missing required file '{f}' in the current folder.")
            return

    # Find all Model:Samples project files
    ms_files = glob.glob(os.path.join(input_dir, "*.msprj"))
    
    if not ms_files:
        print("ℹ️ No `.msprj` files found in the current directory to convert.")
        return

    print(f"=== Found {len(ms_files)} projects to convert ===")

    for ms_file_path in ms_files:
        # Extract base names
        base_filename = os.path.basename(ms_file_path)
        project_name = os.path.splitext(base_filename)[0]
        
        print(f"\nProcessing project: {project_name}...")

        # Define temporary paths including the explicit .zip clone
        temp_zip_clone = f"temp_{project_name}_clone.zip"
        temp_ms_flat = f"temp_{project_name}_ms.bin"
        temp_tg_flat = f"temp_{project_name}_tg.bin"
        final_package = os.path.join(output_dir, f"{project_name}.mcprj")

        try:
            # Step 0: Clone the original .msprj file directly into a temp .zip file
            print(f"  -> Creating temporary archive clone...")
            shutil.copy2(ms_file_path, temp_zip_clone)

            # Step 1: Decompress MS package using the freshly renamed zip asset
            print(f"  -> Unpacking source zip layout...")
            subprocess.run([sys.executable, DECOMPRESS_SCRIPT, temp_zip_clone, temp_ms_flat], check=True, stdout=subprocess.DEVNULL)

            # Step 2: Convert flat binary and fix hardware configuration headers
            print(f"  -> Merging structure layout...")
            subprocess.run([sys.executable, CONVERTER_SCRIPT, temp_ms_flat, TG_TEMPLATE, temp_tg_flat], check=True, stdout=subprocess.DEVNULL)

            # Step 3: Recompress into Model-TG / Cycles format (ProductType 45)
            print(f"  -> Repacking container...")
            subprocess.run([sys.executable, COMPRESS_SCRIPT, temp_tg_flat, final_package, project_name, "45"], check=True, stdout=subprocess.DEVNULL)

            print(f"  ✅ Success! Generated: {final_package}")

        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to convert {project_name}. Component tool returned an error.")
        except Exception as err:
            print(f"  ❌ System Error during execution loop: {err}")
        finally:
            # Clean up all temporary flat files and the zip clone so your workspace stays pristine
            for temp_file in (temp_zip_clone, temp_ms_flat, temp_tg_flat):
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    print("\n==================================================")
    print(f"🎉 Batch conversion complete! Check the '{output_dir}' folder.")
    print("==================================================")

if __name__ == "__main__":
    run_batch_conversion()