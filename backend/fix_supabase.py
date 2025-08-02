import subprocess
import sys
import os

os.chdir(r"D:\genAI\line-agent-langchain\backend")

# Uninstall current supabase
print("Uninstalling current supabase...")
subprocess.run([sys.executable, "-m", "pip", "uninstall", "supabase", "-y"])

# Install specific version
print("Installing supabase==2.0.2...")
subprocess.run([sys.executable, "-m", "pip", "install", "supabase==2.0.2"])

print("Done!")
