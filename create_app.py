#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

def ensure_executable(file_path):
    if not os.access(file_path, os.X_OK):
        os.chmod(file_path, 0o755)
        print(f"Set {file_path} to be executable.")

def add_alias(script_name):
    alias_name = script_name.rsplit('.', 1)[0]
    alias_command = f'alias {alias_name}=~/Projects/apps/{script_name}\n'
    
    zshrc_path = os.path.expanduser('~/.zshrc')
    with open(zshrc_path, 'r') as file:
        content = file.read()
        
    if alias_command not in content:
        with open(zshrc_path, 'a') as file:
            file.write(alias_command)
        print(f"Added alias for {script_name}.")
    
    subprocess.run(['zsh', '-c', f'source {zshrc_path}'])
    print("Sourced .zshrc to apply changes.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    home_dir = os.path.expanduser('~/Projects/apps')
    
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)
    
    full_path = os.path.join(home_dir, filename)
    
    shutil.move(filename, full_path)
    ensure_executable(full_path)
    
    # Check if the file is a Python script and add the shebang line if necessary
    if filename.endswith('.py'):
        with open(full_path, 'r+') as file:
            content = file.read()
            file.seek(0, 0)
            if not content.startswith('#!/usr/bin/env python3'):
                file.write('#!/usr/bin/env python3\n' + content)
    
    add_alias(os.path.basename(full_path))

if __name__ == "__main__":
    main()
