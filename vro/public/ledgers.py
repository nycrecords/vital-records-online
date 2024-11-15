import os 
import subprocess

# Function to compress a single PDF file using Ghostscript Commands
def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF file using Ghostscript based on the specified quality.
    These are the basic Ghostscript commands that are used to compress
    and they offer the best compression while maintaining quality throughout. 
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


# Function to linearize a compressed PDF file using QPDF Commands
def linearize_pdf(input_path, output_path):
    """
    Linearize a PDF file using QPDF. These are the basic QPDF commands
    needed for linearization. And similar to Ghostscript, it takes
    into account the input path and output path. 
    """
    qpdf_commands = ["qpdf", "--linearize", input_path, output_path]

    try:
        print(f"Running command: {' '.join(qpdf_commands)}")
        subprocess.run(qpdf_commands, check=True)
        print(f"Linearized {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to linearize {input_path}: {e.output}")


# Function to generate unique output filenames to avoid the infinite loop of compressing and linearizing
def generate_filename(output_dir, name_beginning, name_ending):
    """
    Generate a unique filename for compressed and linearized files. 
    This is needed in order to differentiate between the files. Previously 
    had an infinite loop that constantly compressed and linearized PDFs that
    were already done. 
    """
    counter = 1
    while True:
        output_path = os.path.join(output_dir, f"{name_beginning}_{counter}{name_ending}")
        if not os.path.exists(output_path):
            return output_path
        counter += 1


# Function to compress and linearize all PDF files in a directory and its subdirectories using Ghostscript and QPDF
def batch_compress_and_linearize_pdfs(input_dir="/", output_dir="vro/static/pdfs", keyword="Ledger"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Starting directory traversal in '{input_dir}'...")

    for root, _, files in os.walk(input_dir):
        print(f"Checking directory: {root}")
        for filename in files:
            print(f"Found file: {filename} (Extension: {os.path.splitext(filename)[1]})")
            
            if os.path.splitext(filename)[1].lower() == ".pdf" and keyword.lower() in filename.lower():
                input_path = os.path.join(root, filename)
                
                # Generate unique filenames for compressed and linearized outputs
                compressed_path = generate_filename(output_dir, "final_compressed", ".pdf")
                linearized_path = generate_filename(output_dir, "final_linearized", ".pdf")

                print(f"Found PDF file: {input_path}")
                
                # Compress PDF
                compress_pdf(input_path, compressed_path)

                # Linearize the compressed PDF bc there's no point in running the linearization command of the raw basic file
                linearize_pdf(compressed_path, linearized_path)
            else:
                print(f"Ignoring non-PDF file: {filename}")


# Run the batch process
batch_compress_and_linearize_pdfs()