import os
import zipfile
from pathlib import Path

def create_submission_zip():
    base_dir = Path(__file__).parent.parent
    zip_filename = base_dir.parent / "AI_Panel_Submission.zip"
    
    # Files and folders to exclude
    excludes = {
        'node_modules', 
        '.git', 
        '__pycache__', 
        '.pytest_cache',
        '.venv',
        'venv',
        'env'
    }
    
    print(f"Creating submission zip: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Modify dirs in-place to exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                # Do not zip the zip file itself if it happens to be inside
                if file.endswith('.zip'):
                    continue
                
                # Never include environment files containing secrets
                if file == '.env' or file.startswith('.env.'):
                    continue
                    
                file_path = Path(root) / file
                # The archive name should be relative to base_dir
                arcname = file_path.relative_to(base_dir)
                
                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)
                
    print("\nSuccessfully packaged the project!")
    print(f"Zip file is ready at: {zip_filename.resolve()}")
    print("NOTE: 'node_modules' and '.git' are deliberately excluded because this is the industry standard. Your 'package.json' represents the complete source code for dependencies.")

if __name__ == "__main__":
    create_submission_zip()
