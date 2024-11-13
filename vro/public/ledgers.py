import os 
import subprocess

# Function to compress a single PDF file
def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF file using GhostScript based on the specified quality.
    """
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
        print(f"Running command: {' '.join(gs_commands)}")
        subprocess.run(gs_commands, check=True)
        print(f"Compressed {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compress {input_path}: {e.output}")

# Function to compress all PDF files in a directory and its subdirectories
def batch_compress_pdfs(input_dir="/", output_dir="vro/static/pdfs", keyword="Ledger"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Starting directory traversal in '{input_dir}'...")

    for root, _, files in os.walk(input_dir):
        print(f"Checking directory: {root}")
        for filename in files:
            print(f"Found file: {filename} (Extension: {os.path.splitext(filename)[1]})")
            
            if os.path.splitext(filename)[1].lower() == ".pdf" and keyword.lower() in filename.lower():
                input_path = os.path.join(root, filename)
                output_path = os.path.join(output_dir, f"compressed_{filename}")
                
                print(f"Found PDF file: {input_path}")
                compress_pdf(input_path, output_path)
            else:
                print(f"Ignoring non-PDF file: {filename}")

batch_compress_pdfs()