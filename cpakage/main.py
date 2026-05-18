import os
import requests
import urllib3
import json
import argparse
import sys
import configparser
import shutil
import tarfile
import getpass

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        tomllib = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="
REGISTRY_URL = "https://cpakage.ir/api/v1"

BASE_DIR = os.path.expanduser("~/.cpakage")
DEFAULT_INSTALL_PATH = os.path.join(BASE_DIR, "installed_packages")
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
TOKEN_FILE = os.path.join(BASE_DIR, "token")


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

        extract_dir = os.path.join(package_dir, f"{package_name}-v{version}")
        os.makedirs(extract_dir, exist_ok=True)
        try:
            with tarfile.open(package_file, "r:gz") as tar:
                tar.extractall(extract_dir)
            print(f"Extracted to {extract_dir}")
        except tarfile.TarError as e:
            print(f"Warning: Could not extract package: {e}")

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
                    package_file = os.path.join(package_dir, f"{package['name']}-v{pkg_version}.tar.gz")
                    extract_dir = os.path.join(package_dir, f"{package['name']}-v{pkg_version}")
                    if os.path.exists(package_file):
                        try:
                            os.remove(package_file)
                            print(f"Removed {package_file}")
                        except Exception as e:
                            print(f"Failed to remove file: {e}")
                    if os.path.exists(extract_dir):
                        try:
                            shutil.rmtree(extract_dir)
                            print(f"Removed {extract_dir}")
                        except Exception as e:
                            print(f"Failed to remove directory: {e}")
                    if os.path.exists(package_dir) and not os.listdir(package_dir):
                        os.rmdir(package_dir)
                else:
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


def login_command():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        response = requests.post(
            f"{REGISTRY_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token", "")
            _ensure_base_dir()
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            print(f"Login successful! Welcome, {username}.")
        else:
            data = response.json()
            print(f"Login failed: {data.get('error', 'Unknown error')}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage registry.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)


def register_command():
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Error: Passwords do not match.")
        sys.exit(1)

    try:
        response = requests.post(
            f"{REGISTRY_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10,
        )
        if response.status_code == 201:
            data = response.json()
            token = data.get("access_token", "")
            _ensure_base_dir()
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            print(f"Registration successful! Logged in as {username}.")
        else:
            data = response.json()
            print(f"Registration failed: {data.get('error', 'Unknown error')}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage registry.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)


def publish_command():
    manifest_file = "cpakage.toml"
    if not os.path.exists(manifest_file):
        print("Error: cpakage.toml not found in current directory.")
        sys.exit(1)

    if not os.path.exists(TOKEN_FILE):
        print("Error: Not logged in. Run 'cpakage login' first.")
        sys.exit(1)

    with open(TOKEN_FILE) as f:
        token = f.read().strip()

    if not token:
        print("Error: Invalid token. Run 'cpakage login' first.")
        sys.exit(1)

    if tomllib is None:
        print("Error: TOML parser not available. Install 'tomli': pip install tomli")
        sys.exit(1)

    try:
        with open(manifest_file, "rb") as f:
            manifest = tomllib.load(f)
    except Exception as e:
        print(f"Error: Could not parse cpakage.toml: {e}")
        sys.exit(1)

    pkg_info = manifest.get("package", {})
    name = pkg_info.get("name", "").strip()
    version = pkg_info.get("version", "").strip()

    if not name or not version:
        print("Error: cpakage.toml must have [package] section with 'name' and 'version'.")
        sys.exit(1)

    archive_name = f"{name}-{version}.tar.gz"
    print(f"Creating {archive_name}...")

    include_paths = manifest.get("publish", {}).get("include", ["."])

    def _tar_filter(info):
        if ".git" in info.name.split(os.sep):
            return None
        if info.name.endswith(".tar.gz"):
            return None
        return info

    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            for path in include_paths:
                if os.path.exists(path):
                    tar.add(path, filter=_tar_filter)
                else:
                    print(f"Warning: Path '{path}' not found, skipping.")
    except Exception as e:
        print(f"Error: Could not create archive: {e}")
        sys.exit(1)

    print(f"Publishing {name} v{version} to registry...")

    try:
        with open(archive_name, "rb") as f:
            response = requests.post(
                f"{REGISTRY_URL}/packages/upload",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (archive_name, f, "application/gzip")},
                data={"manifest": json.dumps(manifest)},
                timeout=120,
            )

        if response.status_code == 201:
            data = response.json()
            print(f"Successfully published {name} v{version}!")
            print(f"Checksum: {data.get('checksum', 'N/A')}")
        else:
            data = response.json()
            print(f"Publish failed: {data.get('error', 'Unknown error')}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage registry.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Upload timed out.")
        sys.exit(1)
    finally:
        if os.path.exists(archive_name):
            os.remove(archive_name)


def list_command():
    repo_file = os.path.join(get_repository_path(), "installed_packages.json")

    if not os.path.exists(repo_file):
        print("No packages installed.")
        return

    with open(repo_file) as f:
        packages = json.load(f)

    if not packages:
        print("No packages installed.")
        return

    print(f"\n{'Name':<30} {'Version':<15} {'Project Page'}")
    print("-" * 80)
    for pkg in packages:
        print(f"{pkg['name']:<30} {pkg['version']:<15} {pkg.get('project_page', 'N/A')}")
    print(f"\nTotal: {len(packages)} package(s)")


def info_command(package_name):
    try:
        response = requests.get(
            f"{REGISTRY_URL}/packages/{package_name}",
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            keywords = data.get("keywords") or []
            print(f"\nPackage:     {data.get('name', 'N/A')}")
            print(f"Description: {data.get('description', 'N/A')}")
            print(f"License:     {data.get('license', 'N/A')}")
            print(f"Homepage:    {data.get('homepage', 'N/A')}")
            print(f"Latest:      {data.get('latest_version', 'N/A')}")
            if keywords:
                print(f"Keywords:    {', '.join(keywords)}")
            versions = data.get("versions", [])
            if versions:
                print(f"Versions:    {', '.join(v['version'] for v in versions[:10])}")
        elif response.status_code == 404:
            print(f"Package '{package_name}' not found in registry.")
            sys.exit(1)
        else:
            data = response.json()
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage registry.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)


def search_command(query):
    try:
        response = requests.get(
            f"{REGISTRY_URL}/search",
            params={"q": query},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            total = data.get("total", 0)

            if not results:
                print(f"No results found for '{query}'.")
                return

            print(f"\nFound {total} package(s) matching '{query}':\n")
            print(f"{'Name':<25} {'Latest':<12} {'Downloads':<12} Description")
            print("-" * 80)
            for pkg in results:
                desc = (pkg.get("description") or "")[:30]
                print(f"{pkg['name']:<25} {str(pkg.get('latest_version', 'N/A')):<12} {str(pkg.get('total_downloads', 0)):<12} {desc}")
        else:
            data = response.json()
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the CPakage registry.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)


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
C/C++ Package Manager (CPakage) — Version 0.0.2.0

Usage:
  cpakage install <pkg> [--version <ver>]   Install a package
  cpakage update  <pkg> [--version <ver>]   Update a package
  cpakage uninstall <pkg> [--version <ver>] Uninstall a package
  cpakage list                              List installed packages
  cpakage info <pkg>                        Show package info from registry
  cpakage search <query>                    Search packages in registry
  cpakage login                             Log in to the registry
  cpakage register                          Create a registry account
  cpakage publish                           Publish package (needs cpakage.toml)
  cpakage -S -R -P <path>                   Set local repository path
  cpakage -S -R -V <TRUE|FALSE>             Enable/disable versioning

Examples:
  cpakage install nlohmann-json
  cpakage install nlohmann-json --version 3.11.2
  cpakage search json
  cpakage info nlohmann-json
  cpakage list
  cpakage login
  cpakage publish
"""
    print(help_message)


def main():
    print("cpakage is running!")

    parser = argparse.ArgumentParser(description="C/C++ Package Manager (cpakage)", add_help=False)
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("package_name", nargs="?", help="Package name or search query")
    parser.add_argument("--version", help="Package version")

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

    elif args.command == "list":
        list_command()

    elif args.command == "info":
        if not args.package_name:
            print("Error: Please specify a package name. Usage: cpakage info <package_name>")
            sys.exit(1)
        info_command(args.package_name)

    elif args.command == "search":
        if not args.package_name:
            print("Error: Please specify a search query. Usage: cpakage search <query>")
            sys.exit(1)
        search_command(args.package_name)

    elif args.command == "login":
        login_command()

    elif args.command == "register":
        register_command()

    elif args.command == "publish":
        publish_command()

    else:
        print(f"Unknown command '{args.command}'. Run 'cpakage' for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
