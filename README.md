# Elektron Model:Samples to Model-TG Project Converter

A Python-based utility pipeline designed to automatically batch-convert **Model:Samples (`.msprj`)** project files into stable, loadable **Model:Cycles / Model-TG (`.mcprj`)** project files.
This tool allows you to safely migrate your extensive library of patterns, step grids, microtiming vectors, velocities, and sound design parameter settings from a stock Model:Samples setup straight onto hardware running the custom **Model-TG custom firmware**.

## No automatic sample assignments
While the TG sample engine has the parameters of the Model Samples, the sample assignments are store in the main file, not in a Sample folder with hash mapping in the JSON found in the .msprj file.
So the mappings are lost no matter what. :(
You must add the files to the device (Ive found setting the Device mode to SMP and dragging in the .msprj file, preserving the original file structure to work well. It will load the samples first then fail on the project).
Then once you import the converted .mcprj file you must assign each track to sample engine and assign the desired sample. I have an additional M:S so side by side makes this easy, ymmv.
However once mapped the patterns are restored and faithful to running natively on the M:S.

## How It Works
Because the Model:Samples and Model:Cycles share an identical 6-track array framework, their underlying sequencing data layout aligns perfectly. However, the machines utilize different internal tracking architectures and sizes to handle sound engine properties. 

This utility solves the data-drift constraint by executing a **Full-Scale Data Payload Copy**. It preserves the stable, working machine profile and engine allocations of a Model-TG baseline template file, while seamlessly injecting your complete Model:Samples sequencing performances over all 16 banks and patterns.

*Note: This compiler framework builds directly upon the reverse-engineering breakthroughs of the Elektron community's Digitakt II / Digitone II continuous LZ4 packing tools.*

## Repository Structure
Ensure the following files remain grouped in your working directory:
*   `dx2_decompress.py`     - Unpacks the continuous LZ4 chunk compression layer inside Elektron packages.
*   `dx2_compress.py`       - Repacks flat binaries back into validation-signed container files.
*   `ms_to_tg_converter.py` - Handles device header identification swaps, project name string restoral, and layout block integration.
*   `batch_convert.py`      - The automated main script that runs the entire pipeline end-to-end.

## Prerequisites
1. **Python 3.10+** installed on your system.
2. The **`lz4`** python library. Install it via terminal:
   ```bash
   pip install lz4
   ```

## Setup & Preparation
Before running a conversion loop, you must capture a stable memory map baseline template file directly from your Model-TG hardware unit:
1. Boot up your Model-TG / Cycles box. Create a brand-new, initialized empty project. Name it **`TstTG`**.
2. Export this project from your machine using **Elektron Transfer** (`TstTG.mcprj`).
3. Decompress the template archive to raw binary using the decompression tool:
   ```bash
   python dx2_decompress.py TstTG.mcprj TstTG_Flat.bin
   ```
4. Ensure the resulting **`TstTG_Flat.bin`** file sits inside your main converter directory workspace.

## Usage

### Batch Conversion (Recommended)
1. Copy all of the `.msprj` files you wish to convert directly into the script directory.
2. Execute the batch coordinator tool:
   ```bash
   python batch_convert.py
   ```
3. The script will automatically clone the packages to background temporary files, handle file translation blocks, clear the cache files, and populate your assets inside a clean subfolder called `/Converted_Projects`.

### Manual Conversion (Single File)
If you prefer to step through the pipeline stages manually for tracking purposes, run these three consecutive terminal commands:
```bash
# 1. Clone extension layout and unpack the source
cp MyProject.msprj temp_archive.zip
python dx2_decompress.py temp_archive.zip MS_Flat.bin

# 2. Forge the structural translation bridge profile
python ms_to_tg_converter.py MS_Flat.bin TstTG_Flat.bin TG_Bridged.bin

# 3. Compile the container with the Model:Cycles hardware ID marker (45)
python dx2_compress.py TG_Bridged.bin MyProject.mcprj MyProject 45
```

## Post-Conversion Hardware Routing
Because the Model-TG custom firmware targets a shared global sample directory on your unit's flash drive instead of baking audio files explicitly inside individual archive files:
1. Use **Elektron Transfer** to upload your required audio sample paths onto your Model-TG box natively.
2. Load your newly converted `.mcprj` project file onto your device using Elektron Transfer.
3. Open the pattern grid. Your 4-bar performance step patterns, velocities, and custom knobs shaping metrics will load completely and safely.
4. Navigate through your machine's track menu, pick the **Sample engine**, and quickly link the tracks back to your uploaded audio files.

## Disclaimer
This is an experimental community utility. Always ensure your original pattern files are backed up safely on your computer storage before processing them through conversion pipelines.
