import os
import requests
import urllib3
import json
import argparse
import sys
import configparser
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="

BASE_DIR = os.path.expanduser("~/.cpakage")
DEFAULT_INSTALL_PATH = os.path.join(BASE_DIR, "installed_packages")
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")


def _ensure_base_dir():
    os.makedirs(BASE_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config["settings"] = {
            "repository_path": BASE_DIR,
            "repository_versioning": "False",
        }
        with open(CONFIG_FILE, "w") as f:
            config.write(f)


def load_config():
    _ensure_base_dir()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def get_repository_path():
    config = load_config()
    return config.get("settings", "repository_path", fallback=BASE_DIR)


def is_versioning_enabled():
    config = load_config()
    return config.getboolean("settings", "repository_versioning", fallback=False)


def get_package_info(package_name):
    try:
        response = requests.get(f"{API_URL}{package_name}", verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "url" not in data:
            print(f"Error: Package '{package_name}' not found or server returned invalid data.")
            sys.exit(1)
        return data
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage server. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server may be unavailable.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: Server returned an error: {e}")
        sys.exit(1)
    except ValueError:
        print("Error: Received invalid response from server.")
        sys.exit(1)


def update_local_repo(package_name, version, project_page):
    repo_dir = get_repository_path()
    os.makedirs(repo_dir, exist_ok=True)

    repo_file = os.path.join(repo_dir, "installed_packages.json")

    if os.path.exists(repo_file):
        with open(repo_file, "r") as f:
            installed_packages = json.load(f)
    else:
        installed_packages = []

    for pkg in installed_packages:
        if pkg["name"] == package_name and pkg["version"] == version:
            print(f"Package '{package_name}' version '{version}' is already registered in the local repository.")
            return

    installed_packages.append({"name": package_name, "version": version, "project_page": project_page})

    with open(repo_file, "w") as f:
        json.dump(installed_packages, f, indent=4)
    print(f"Updated local repository with package '{package_name}' version '{version}'.")


def is_package_installed(package_name, version):
    repo_file = os.path.join(get_repository_path(), "installed_packages.json")

    if not os.path.exists(repo_file):
        return False

    with open(repo_file, "r") as f:
        installed_packages = json.load(f)

    for pkg in installed_packages:
        if pkg["name"] == package_name and pkg["version"] == version:
            package_file = os.path.join(DEFAULT_INSTALL_PATH, package_name, f"{package_name}-v{version}.tar.gz")
            return os.path.exists(package_file)

    return False


def install_package(package_name, version):
    if is_package_installed(package_name, version):
        print(f"Package '{package_name}' version '{version}' is already installed.")
        return

    package_info = get_package_info(package_name)
    download_url = package_info["url"].replace("{version}", version)
    project_page = package_info.get("project_page", "N/A")

    print(f"Downloading {package_name} version {version} from {download_url}...")

    try:
        response = requests.get(download_url, verify=False, timeout=60)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the download server.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Download timed out.")
        sys.exit(1)

    if response.status_code == 200:
        package_dir = os.path.join(DEFAULT_INSTALL_PATH, package_name)
        os.makedirs(package_dir, exist_ok=True)

        package_file = os.path.join(package_dir, f"{package_name}-v{version}.tar.gz")
        with open(package_file, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded {package_name} version {version} to {package_file}.")
        update_local_repo(package_name, version, project_page)
    else:
        print(f"Failed to download {package_name} version {version}. HTTP {response.status_code}")


def update_package(package_name, version=None):
    if version is None:
        package_info = get_package_info(package_name)
        version = package_info.get("latest_version")
        if not version:
            print(f"Error: Could not determine latest version for '{package_name}'.")
            sys.exit(1)
    install_package(package_name, version)


def uninstall_package(package_name, version=None):
    repo_file = os.path.join(get_repository_path(), "installed_packages.json")

    if not os.path.exists(repo_file):
        print("No packages installed yet.")
        return

    with open(repo_file, "r") as f:
        installed_packages = json.load(f)

    updated_packages = []
    package_found = False

    for package in installed_packages:
        if package["name"].lower() == package_name.lower():
            if version is None or package["version"] == version:
                package_found = True
                pkg_version = package["version"]
                print(f"Uninstalling {package['name']} version {pkg_version}...")

                package_dir = os.path.join(DEFAULT_INSTALL_PATH, package["name"])

                if version is not None:
                    # remove only the specific version file, keep other versions intact
                    package_file = os.path.join(package_dir, f"{package['name']}-v{pkg_version}.tar.gz")
                    if os.path.exists(package_file):
                        try:
                            os.remove(package_file)
                            print(f"Removed {package_file}")
                            if os.path.exists(package_dir) and not os.listdir(package_dir):
                                os.rmdir(package_dir)
                        except Exception as e:
                            print(f"Failed to remove file: {e}")
                    else:
                        print(f"No file found for {package['name']} version {pkg_version}.")
                else:
                    # remove entire package directory when no version specified
                    if os.path.exists(package_dir):
                        try:
                            shutil.rmtree(package_dir)
                            print(f"Removed directory {package_dir}")
                        except Exception as e:
                            print(f"Failed to remove directory: {e}")
                    else:
                        print(f"No files found for {package['name']}.")
            else:
                updated_packages.append(package)
        else:
            updated_packages.append(package)

    if package_found:
        with open(repo_file, "w") as f:
            json.dump(updated_packages, f, indent=4)
        print(f"{package_name} uninstalled successfully.")
    else:
        print(f"No matching package found for {package_name} version {version if version else 'any'}.")


def edit_config(option, value):
    _ensure_base_dir()
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        print(f"Configuration file not found at '{CONFIG_FILE}'.")
        return

    if option.lower() == "path":
        config.set("settings", "repository_path", value)
    elif option.lower() == "versioning":
        if value.lower() in ["true", "false"]:
            config.set("settings", "repository_versioning", value.capitalize())
        else:
            print("Invalid value for versioning. Use 'TRUE' or 'FALSE'.")
            return
    else:
        print(f"Invalid option: {option}")
        return

    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

    print(f"Configuration updated: {option} = {value}")


def handle_settings_command(args):
    if args.path:
        edit_config("path", args.path)
    elif args.versioning:
        edit_config("versioning", args.versioning)
    else:
        print("Invalid settings command. Use '-S -R -P <path>' or '-S -R -V <TRUE/FALSE>'.")


def show_help_message():
    help_message = """
C/C++ Package Manager (CPakage) - Version 0.0.1.1

Usage:
  cpakage install <package_name> [--version <version>]
      Install a package. Installs the latest version if --version is omitted.

  cpakage update <package_name> [--version <version>]
      Update a package. Updates to the latest version if --version is omitted.

  cpakage uninstall <package_name> [--version <version>]
      Uninstall a package. Removes all versions if --version is omitted.

  cpakage -S -R -P <path>
      Set the local repository path.

  cpakage -S -R -V <TRUE|FALSE>
      Enable or disable repository versioning.

Examples:
  cpakage install curl_downloader
  cpakage install curl_downloader --version 7.6.5
  cpakage update  curl_downloader
  cpakage uninstall curl_downloader
  cpakage uninstall curl_downloader --version 7.6.5
  cpakage -S -R -P /custom/path
  cpakage -S -R -V TRUE
"""
    print(help_message)


def main():
    print("cpakage is running!")

    parser = argparse.ArgumentParser(description="C/C++ Package Manager (cpakage)", add_help=False)
    parser.add_argument("command", nargs="?", help="Command to execute (install, update, uninstall)")
    parser.add_argument("package_name", nargs="?", help="Name of the package")
    parser.add_argument("--version", help="Version of the package (optional)")

    parser.add_argument("-S", action="store_true", help="Settings command")
    parser.add_argument("-R", action="store_true", help="Repository option for settings")
    parser.add_argument("-P", dest="path", help="Path for repository")
    parser.add_argument("-V", dest="versioning", help="Enable or disable versioning (TRUE/FALSE)")

    args = parser.parse_args()

    if args.S:
        handle_settings_command(args)
        sys.exit(0)

    if not args.command:
        show_help_message()
        sys.exit(0)

    if args.command == "install":
        if not args.package_name:
            print("Error: Please specify a package name. Usage: cpakage install <package_name>")
            sys.exit(1)
        install_version = args.version if args.version else get_package_info(args.package_name).get("latest_version")
        if not install_version:
            print(f"Error: Could not determine version for '{args.package_name}'.")
            sys.exit(1)
        install_package(args.package_name, install_version)

    elif args.command == "update":
        if not args.package_name:
            print("Error: Please specify a package name. Usage: cpakage update <package_name>")
            sys.exit(1)
        update_package(args.package_name, args.version)

    elif args.command == "uninstall":
        if not args.package_name:
            print("Error: Please specify a package name. Usage: cpakage uninstall <package_name>")
            sys.exit(1)
        uninstall_package(args.package_name, args.version)

    else:
        print(f"Unknown command '{args.command}'. Use 'cpakage' for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
