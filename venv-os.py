import os
import subprocess


def setup_venv():
    # ایجاد محیط مجازی
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        os.system("python -m venv venv")

    # فعال‌سازی محیط مجازی
    activate_script = "venv\\Scripts\\activate" if os.name == "nt" else "source venv/bin/activate"
    print(f"Activating virtual environment...")
    os.system(activate_script)

    # نصب کتابخانه‌ها
    print("Installing required libraries...")
    os.system("pip install requests")

    print("Setup complete! Virtual environment is ready.")


if __name__ == "__main__":
    setup_venv()
