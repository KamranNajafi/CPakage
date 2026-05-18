import os
import subprocess
import sys


def setup_venv():
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

    pip_path = (
        os.path.join("venv", "Scripts", "pip.exe")
        if os.name == "nt"
        else os.path.join("venv", "bin", "pip")
    )

    print("Installing required libraries...")
    subprocess.run([pip_path, "install", "requests"], check=True)

    activate_path = (
        os.path.join("venv", "Scripts", "activate")
        if os.name == "nt"
        else os.path.join("venv", "bin", "activate")
    )

    print("\nSetup complete! To activate the virtual environment, run:")
    if os.name == "nt":
        print(f"  {activate_path}")
    else:
        print(f"  source {activate_path}")


if __name__ == "__main__":
    setup_venv()
