import os 
import subprocess

# Function to compress a single PDF file
def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF file using GhostScript based on the specified quality.
    """
    # These are the basic ghostscript commands used and they are the best choice. Do not change. 
    gs_commands = [
        "gs", "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_commands, check=True)
        print(f"Compressed {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compress {input_path}: {e}")


# Function to compress all PDF files in a directory and its subdirectories
def batch_compress_pdfs(input_dir="/", output_dir="vro/static/pdfs", keyword="Ledger"):
    # Input directory and output directory is subject to change based on where project directory is located
    # Having the "/" now means is will traverse through your entire device. 
    # Output directory is the PDFs folder and added a keyword of "Ledger"
    """
    Traverse through the input directory (and its subdirectories) to find and compress PDF files.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Starting directory traversal in '{input_dir}'...")

    # Use os.walk to go through all subdirectories in the input path
    # Basic for loop and if statement that is used to check traverse in the root and all of the files. 
    # Using print statements to show progress and may list any errors. 
    for root, _, files in os.walk(input_dir): # May need "dirs" here, not sure yet. But the script does run properly without. 
        print(f"Checking directory: {root}")
        for filename in files:
            if filename.lower().endswith(".pdf") and keyword in filename.lower():
                input_path = os.path.join(root, filename)
                output_path = os.path.join(output_dir, f"compressed_{filename}")
                
                print(f"Found PDF file: {input_path}")
                compress_pdf(input_path, output_path)
            else:
                print(f"Ignoring non-PDF file: {filename}")

batch_compress_pdfs()