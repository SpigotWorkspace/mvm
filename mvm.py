import argparse
import http.client
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Final, Any
from zipfile import ZipFile

import import_config
import mvn

_SERVERS: Final = {
    "https://archive.apache.org/dist/maven/maven-4/": True,
    "https://archive.apache.org/dist/maven/maven-3/": True,
    "https://archive.apache.org/dist/maven/binaries/": False
}
_config: Final = import_config.get_config()
_MAVEN_PATH: Final = _config.MAVEN_PATH
if not os.path.exists(_MAVEN_PATH):
    print(f"Maven path '{_MAVEN_PATH}' does not exist")
    sys.exit(1)

def scan_versions() -> dict[str, str]:
    versions: dict[str, str] = dict()
    with os.scandir(_MAVEN_PATH) as it:
        for folder in it:
            mvn_path = os.path.join(folder.path, "bin", "mvn")
            is_executable = os.path.exists(mvn_path)

            if not is_executable: continue
            match: re.Match[str] = re.search(r"apache-maven-(.+)", folder.name)
            if match:
                version = match.group(1)
            else:
                command_output = mvn.execute(mvn_path, ["-v"])
                version_line = command_output.splitlines()[0]
                version = re.search(r"(\d+\.\d+\.\d+)", version_line).group(1)
            versions[version] = folder.path
    return versions

def is_version_installed(version: str) -> bool:
    installed_versions = scan_versions()
    return version in installed_versions

def list_command(_):
    versions = scan_versions()
    for version, folder_path in versions.items():
        string = f"- {version}"
        if folder_path == _config.VERSION_TO_USE:
            string += " (default)"

        print(string)

def install_command(version):
    if is_version_installed(version):
        print(f"Version '{version}' is already installed.")
        return None

    error = None
    for url, folders in _SERVERS.items():
        filename = f"apache-maven-{version}-bin.zip"
        if folders:
            url += f"{version}/binaries/"
        url += filename

        try:
            response: http.client.HTTPResponse
            out_file: Any
            zip_path = Path(import_config.BASE_DIR / filename)
            with urllib.request.urlopen(url) as response, open(zip_path, "wb") as out_file:
                if response.status == http.HTTPStatus.OK:
                    print(f"Installing version '{version}'.")
                    shutil.copyfileobj(response, out_file)
                    out_file.close()
                    with ZipFile(zip_path) as zipfile:
                        zipfile.extractall(_config.MAVEN_PATH)
                    os.remove(zip_path)
                    print(f"Successfully installed version '{version}'.")
                    return None
        except Exception as ex:
            error = ex

    print(f"Error installing version '{version}'.")
    print(error)
    sys.exit(1)

def remove_command(version):
    installed_versions = scan_versions()
    if not version in installed_versions:
        print(f"Version '{version}' is not installed.")
        return None
    folder_path = installed_versions.get(version)
    shutil.rmtree(folder_path)

    print(f"Successfully removed version '{version}'.")

def use_command(version):
    installed_versions = scan_versions()
    if not version in installed_versions:
        print(f"Version '{version}' is not installed. Will be installed.")
        print("---------------------")
        install_command(version)
        installed_versions = scan_versions()
        print("---------------------")
    folder_path = installed_versions.get(version)
    _config.VERSION_TO_USE = folder_path
    import_config.save_config(_config)

    print(f"Version {version} will now be used.")

parser = argparse.ArgumentParser("mvm")
subparsers = parser.add_subparsers()

parser_list = subparsers.add_parser("list", help="Lists all installed versions under config.MAVEN_PATH")
parser_list.set_defaults(func=list_command)

parser_install = subparsers.add_parser("install", help="Installs the provided maven version to the config.MAVEN_PATH directory")
parser_install.add_argument("version", help="Version to install")
parser_install.set_defaults(func=install_command)

parser_remove = subparsers.add_parser("remove", help="Removes the provided maven version from the config.MAVEN_PATH directory")
parser_remove.add_argument("version", help="Version to remove")
parser_remove.set_defaults(func=remove_command)

parser_use = subparsers.add_parser("use", help="Sets the maven version to use")
parser_use.add_argument("version", help="Version to use")
parser_use.set_defaults(func=use_command)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

parser_args = parser.parse_args()
if hasattr(parser_args, "func"):
    version_arg = None
    if hasattr(parser_args, "version"):
        version_arg = parser_args.version
    parser_args.func(version_arg)