import os
import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="


def get_package_info(package_name):
    response = requests.get(f"{API_URL}{package_name}", verify=False)
    return response.json()


def update_local_repo(package_name, version):
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
    installed_packages.append({"name": package_name, "version": version})

    with open(repo_file, "w") as f:
        json.dump(installed_packages, f, indent=4)


def install_package(package_name, version):
    package_info = get_package_info(package_name)
    download_url = package_info['url']
    print(f"Downloading {package_name} version {version} from {download_url}...")

    # Downloading package logic (e.g., using requests)
    response = requests.get(download_url, verify=False)

    if response.status_code == 200:
        # Extract and install the package
        print(f"Successfully downloaded {package_name} version {version}.")
        update_local_repo(package_name, version)
    else:
        print(f"Failed to download {package_name} version {version}.")


def update_package(package_name, version):
    install_package(package_name, version)


if __name__ == "__main__":
    package_name = 'curl_downloader'
    install_version = '7.6.5'
    update_package(package_name, install_version)
