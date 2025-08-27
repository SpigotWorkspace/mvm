import argparse
import http.client
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from typing import Final, Any
from zipfile import ZipFile

import import_config
import mvn

SERVERS: Final = {
    "https://archive.apache.org/dist/maven/maven-4/": True,
    "https://archive.apache.org/dist/maven/maven-3/": True,
    "https://archive.apache.org/dist/maven/binaries/": False
}
config = import_config.get_config()
MAVEN_PATH = config.MAVEN_PATH
if not os.path.exists(MAVEN_PATH):
    print(f"Maven path '{MAVEN_PATH}' does not exist")
    sys.exit(1)

def scan_versions() -> dict[str, str]:
    versions: dict[str, str] = dict()
    with os.scandir(MAVEN_PATH) as it:
        for folder in it:
            mvn_path = os.path.join(folder.path, "bin", "mvn")
            is_executable = os.path.exists(mvn_path)

            if not is_executable: continue
            match = re.search(r"apache-maven-(.+)", folder.name)
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
    for version in versions:
        print(f"- {version}")

def install_command(args):
    version = args.version
    if is_version_installed(version):
        print(f"version '{version}' is already installed")
        return None

    error = None
    for url, folders in SERVERS.items():
        filename = f"apache-maven-{version}-bin.zip"
        if folders:
            url += f"{version}/binaries/"
        url += filename

        try:
            response: http.client.HTTPResponse
            out_file: Any
            with urllib.request.urlopen(url) as response, open(filename, "wb") as out_file:
                if response.status == http.HTTPStatus.OK:
                    print(f"installing version '{version}'")
                    shutil.copyfileobj(response, out_file)
                    with ZipFile(filename) as zipfile:
                        zipfile.extractall(config.MAVEN_PATH)
                    out_file.close()
                    os.remove(filename)
                    print(f"successfully installed version '{version}'")
                    return None
        except Exception as ex:
            error = ex

    print(f"error installing version {version}")
    print(error)

def remove_command(args):
    version = args.version
    installed_versions = scan_versions()
    if not version in installed_versions:
        print(f"version '{version}' is not installed")
        return None
    folder_path = installed_versions.get(version)
    shutil.rmtree(folder_path)

    print(f"successfully removed version '{version}'")

parser = argparse.ArgumentParser("mvm")
subparsers = parser.add_subparsers()

parser_list = subparsers.add_parser("list", help="lists all installed versions under config.MAVEN_PATH")
parser_list.set_defaults(func=list_command)

parser_install = subparsers.add_parser("install", help="installs the provided maven version to the config.MAVEN_PATH directory")
parser_install.add_argument("version", help="version to install")
parser_install.set_defaults(func=install_command)

parser_remove = subparsers.add_parser("remove", help="removes the provided maven version from the config.MAVEN_PATH directory")
parser_remove.add_argument("version", help="version to remove")
parser_remove.set_defaults(func=remove_command)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

parser_args = parser.parse_args()
if hasattr(parser_args, "func"):
    parser_args.func(parser_args)