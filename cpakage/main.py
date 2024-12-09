import os
import requests
import urllib3
import json
import argparse
import sys
from cpakage import main

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="
DEFAULT_INSTALL_PATH = "local_repo/installed_packages"


def get_package_info(package_name):
    response = requests.get(f"{API_URL}{package_name}", verify=False)
    return response.json()


def update_local_repo(package_name, version, project_page):
    repo_dir = 'local_repo'
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    repo_file = os.path.join(repo_dir, 'installed_packages.json')

    # Example code for updating the local repo
    if os.path.exists(repo_file):
        with open(repo_file, "r") as f:
            installed_packages = json.load(f)
    else:
        installed_packages = []

    # Adding new package to the installed list
    installed_packages.append({"name": package_name, "version": version, "project_page": project_page})

    with open(repo_file, "w") as f:
        json.dump(installed_packages, f, indent=4)


def install_package(package_name, version):
    package_info = get_package_info(package_name)
    download_url = package_info['url'].replace("{version}", version)
    project_page = package_info.get("project_page", "N/A")

    print(f"Downloading {package_name} version {version} from {download_url}...")

    # Downloading package logic (e.g., using requests)
    response = requests.get(download_url, verify=False)

    if response.status_code == 200:
        # Define the file path based on default install path
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

Options (and corresponding environment variables):

-all    : Update All Local Repository Packages
            Examples: cpakage update -All
            
-F      : Install All The Packages Inside The File
            Examples: cpakage install <"File Path">

-S      : CPakage Program Settings
            Some Settings: 
                    0- Show Section Help
                    1- Repository Path For Packages
                    2- Repository Versioning
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
        print(f"Uninstalling {args.package_name} is not yet implemented.")
    else:
        print("Invalid command. Use 'cpakage' for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
