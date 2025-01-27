import os
from collections import defaultdict
import google.generativeai as genai 
import argparse

from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY =  os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(headers, payload):
    response = model.generate_content([headers, payload])
    return response.text

def extract_code(file_path):
    """Read the given file"""
    with open(file_path, 'r') as file:
        return file.read()
    
def generate_documentation(source_code, file_name):
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt" : f"Generate documentation for the file '{file_name}' with the following code:\n\n{source_code}",
        "language" : "python",
        "output-format" : "markdown"
    }
    
    return get_gemini_response(headers, payload)

def fetch_existing_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r") as file:
            return file.read()
    
    return ""

def update_readme_file(readme_content, new_sections):
    updated_content = readme_content.split('\n')
    updated_content.append('\n## Updated Documentation\n')
    
    for section_title, section_content in new_sections.items():
        updated_content.append(f"### {section_title}")
        updated_content.append(section_content)
        updated_content.append('\n')
    return "\n".join(updated_content)

def main(chnaged_file_path):
    with open(chnaged_file_path, 'r') as file:
        changed_files = [line.strip() for line in file if line.strip().endswith('.py')]
        
    if not changed_files:
        print("No Python file is modified. Skipping Readme Update")
        return 
    
    # Generate documentation for changed files
    new_sections = defaultdict(str)
    for file in changed_files:
        try:
            print(f"Processing {file}...")
            code = extract_code(file)
            documentation = generate_documentation(code, file)
            new_sections[file] = documentation
            print(f"Documentation generated for {file}.")
        except Exception as e:
            print(f"Error processing {file}: {e}")
            
    # Read the existing Readme
    existing_readme = fetch_existing_readme()
    
    updated_readme = update_readme_file(existing_readme, new_sections)
    
    with open("README.md", 'w') as file:
        file.write(updated_readme)
        
    print("README.md updated successfully!")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update README.md with new documentation.")
    parser.add_argument("--changed-files", required=True, help="Path to the file containing the list of changed files.")
    args = parser.parse_args()

    main(args.changed_files)