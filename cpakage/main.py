import os
import requests
import urllib3
import json
import argparse
import sys
import configparser
from cpakage import main


config = configparser.ConfigParser()
config.read('config.ini')
repository_path = config.get('settings', 'repository_path')
repository_versioning = config.get('settings', 'repository_versioning')


# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="
DEFAULT_INSTALL_PATH = "local_repo/installed_packages"


def get_package_info(package_name):
    response = requests.get(f"{API_URL}{package_name}", verify=False)
    return response.json()


def update_local_repo(package_name, version, project_page):
    """Update the local repository file with new package information."""
    repo_dir = 'local_repo'
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    repo_file = os.path.join(repo_dir, 'installed_packages.json')

    # Load existing packages
    if os.path.exists(repo_file):
        with open(repo_file, "r") as f:
            installed_packages = json.load(f)
    else:
        installed_packages = []

    # Check if the package with the same version already exists
    for pkg in installed_packages:
        if pkg["name"] == package_name and pkg["version"] == version:
            print(f"Package '{package_name}' version '{version}' is already registered in the local repository.")
            return  # Do nothing if it's already registered

    # Add the new package information
    installed_packages.append({"name": package_name, "version": version, "project_page": project_page})

    # Write updated list back to the file
    with open(repo_file, "w") as f:
        json.dump(installed_packages, f, indent=4)
    print(f"Updated local repository with package '{package_name}' version '{version}'.")


def is_package_installed(package_name, version):
    """Check if the package with a specific version is already installed."""
    repo_file = os.path.join('local_repo', 'installed_packages.json')

    if not os.path.exists(repo_file):
        return False  # If the repo file doesn't exist, package isn't installed.

    with open(repo_file, "r") as f:
        installed_packages = json.load(f)

    for pkg in installed_packages:
        if pkg["name"] == package_name and pkg["version"] == version:
            # Check if the physical file exists
            package_dir = os.path.join(DEFAULT_INSTALL_PATH, package_name)
            package_file = os.path.join(package_dir, f"{package_name}-v{version}.tar.gz")
            return os.path.exists(package_file)  # Return True only if the file exists.

    return False  # Package not found in the repo.


def install_package(package_name, version):
    """Install a package if not already installed or its file is missing."""
    if is_package_installed(package_name, version):
        print(f"Package '{package_name}' version '{version}' is already installed.")
        return

    package_info = get_package_info(package_name)
    download_url = package_info['url'].replace("{version}", version)
    project_page = package_info.get("project_page", "N/A")

    print(f"Downloading {package_name} version {version} from {download_url}...")

    # Download the package
    response = requests.get(download_url, verify=False)

    if response.status_code == 200:
        # Save the package to the local repository
        package_dir = os.path.join(DEFAULT_INSTALL_PATH, package_name)
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)

        package_file = os.path.join(package_dir, f"{package_name}-v{version}.tar.gz")
        with open(package_file, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded {package_name} version {version} to {package_file}.")
        update_local_repo(package_name, version, project_page)
    else:
        print(f"Failed to download {package_name} version {version}.")


def update_package(package_name, version):
    install_package(package_name, version)

def uninstall_package(package_name, version=None):
    """
    Uninstall a specific package by name and optionally by version.

    Args:
        package_name (str): Name of the package to uninstall.
        version (str, optional): Specific version to uninstall. If not provided, all versions of the package are removed.
    """
    repo_file = os.path.join('local_repo', 'installed_packages.json')

    if not os.path.exists(repo_file):
        print("No packages installed yet.")
        return

    with open(repo_file, "r") as f:
        installed_packages = json.load(f)

    # Find and remove the specified package
    updated_packages = []
    package_found = False

    for package in installed_packages:
        if package["name"].lower() == package_name.lower():
            if version is None or package["version"] == version:
                package_found = True
                print(f"Uninstalling {package['name']} version {package['version']}...")
                # Remove the package files from the local directory
                package_dir = os.path.join(DEFAULT_INSTALL_PATH, package["name"])
                if os.path.exists(package_dir):
                    try:
                        import shutil
                        shutil.rmtree(package_dir)
                        print(f"Removed files from {package_dir}")
                    except Exception as e:
                        print(f"Failed to remove files from {package_dir}: {e}")
                else:
                    print(f"No files found for {package['name']} version {package['version']}.")
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

def show_help_message():

    help_message = """
C/C++ Package Manager (CPakage)
C/C++ Package Manager New version V=0.0.1.1
Usage:
  cpakage install <package_name> [--version <version>]
      Install a package with the specified name and version.
      If no version is specified, the latest version is installed.

  cpakage update <package_name> [-Options]
      Update the specified package to the latest version.

  cpakage uninstall <package_name>
      Uninstall the specified package.

****Uppercase or lowercase letters do not matter****
Options (and corresponding environment variables):

-all    : Update All Local Repository Packages
            Examples: cpakage update -All
            
-f      : Install All The Packages Inside The File
            Examples: cpakage install -F <"File Path">

-s      : CPakage Program Settings
            Some Settings: 
                    0- Show Section Help
                    1- Repository Path For Packages <"Default:FALSE">
                    2- Repository Versioning <"Default:FALSE">
            Examples 0: CPakage -S
            Examples 1: CPakage -S -R -P <"Folder Path">
            Examples 2: CPakage -S -R -V <"TRUE OR FALSE">



Examples:
  cpakage install <package_name>
  cpakage install <package_name> --version 7.6.5
  cpakage update  <package_name>
  
"""
    print(help_message)


def main():
    print("cpakage is running!")

    parser = argparse.ArgumentParser(description="C++ Package Manager (cpakage)", add_help=False)
    parser.add_argument("command", nargs="?", help="Command to execute (install, update, uninstall)")
    parser.add_argument("package_name", nargs="?", help="Name of the package")
    parser.add_argument("--version", help="Version of the package (optional)")

    # Parse arguments
    args = parser.parse_args()


    if not args.command:
        show_help_message()
        sys.exit(0)


    if args.command == "install":
        install_version = args.version if args.version else get_package_info(args.package_name)["latest_version"]
        install_package(args.package_name, install_version)
    elif args.command == "update":
        update_package(args.package_name, args.version)
    elif args.command == "uninstall":
        if not args.package_name:
            print("Please specify a package name to uninstall.")
        else:
            uninstall_package(args.package_name, args.version)

    else:
        print("Invalid command. Use 'cpakage' for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
