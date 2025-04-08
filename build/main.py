#!/usr/bin/env python3
"""build client & server bundles"""

# if there is a problem with building, please let htmlcsjs or foontinz know

import argparse
import contextlib
import hashlib
import json
from json import JSONDecodeError

import requests
import os
import pathlib
import shutil
import subprocess

from requests import HTTPError

from deps import ensure_dependencies

def parse_args():
    parser = argparse.ArgumentParser(prog="build", description=__doc__)

    parser.add_argument("--sha", action="store_true", help="append git hash to zips")
    parser.add_argument("--checksum-externals", default=False, action="store_true", help="whether to checksum external deps using `hash`")
    parser.add_argument("--retries", type=int, default=3, help="download attempts before failure")
    parser.add_argument("--clean", action="store_true",help="clean buildOut before build")
    parser.add_argument(
        "--dev-build", action="store_true", help="makes a folder with all the files symlinked for development. probably only works on linux")
    parser.add_argument("-c", "--client", action="store_true", help="builds only client pack")
    return parser.parse_args()

def setup_build_out_folders():
    os.makedirs(MODS_PATH, exist_ok=True)
    os.makedirs(CACHE_PATH, exist_ok=True)

def load_manifest():
    with open(MANIFEST_PATH) as file:
        return json.load(file)

def compute_commit_hash():
    compute_sha = ["git", "rev-parse", "--short", "HEAD"]
    p = subprocess.run(compute_sha, capture_output=True, cwd=basePath)
    if p.returncode != 0:
        raise ValueError(f"Commit hash could not be computed using `{' '.join(compute_sha)}`")
    return p.stdout.strip().decode("utf-8")

def resolve_curseforge_deps(dependencies):
    unresolved_mods = []
    resolved_mods = []
    for dep in dependencies: # dep is like {"projectID": 1121489, "fileID": 5814089, "required": true}
        mod_project_id, file_id, is_required = dep["projectID"], dep["fileID"], dep["required"]
        curse_forge_mod_url = f"{CF_API_LINK}/mods/{mod_project_id}"
        download_url = f"{curse_forge_mod_url}/files/{file_id}/download-url"
        try:
            print(f"Trying to download metadata from {download_url}", end=" ")
            response = requests.get(download_url, headers=HEADERS)
            response.raise_for_status()
            url = response.json()["data"]
            name = url.split("/")[-1]
            name = name if name.endswith(".jar") else name + ".jar"
            resolved_mods.append({"name": name, "url": url, "clientOnly": dep.get("clientOnly", False)})
            print("Downloaded.")
        except (HTTPError, JSONDecodeError) as e:
            print(f"Failed. With error: `{e}`")
            unresolved_mods.append(dep)
            if is_required:
                print(f"Exiting. {mod_project_id} is required, but cannot be resolved.")
                exit(1)
            continue

    print("Server modlist resolving finished.")
    return resolved_mods, unresolved_mods

def download_external_deps(dependencies, target_location, check_for_hash): # todo: add retries
    downloaded_deps = []
    for mod in dependencies:
        download_url, mod_name, expected_mod_hash = mod["url"], mod["name"], mod["hash"]
        with open(target_location / download_url.split("/")[-1], "w+b") as jar:
            response = requests.get(download_url)
            actual_mod_hash = hashlib.sha256(response.content).hexdigest()
            if (str(actual_mod_hash) != expected_mod_hash) and check_for_hash:
                print(f"Unsuccessful checksum for {mod_name}. \n {actual_mod_hash} != {expected_mod_hash}. Exiting, consider removing `--checksum-externals")
                exit()
            downloaded_deps.append(mod)
            jar.write(response.content)
    print("Client mods downloading finished")
    return downloaded_deps

def download_forge_installer(path, forge_version, mc_version):
    with open(path / "forge-installer.jar", "w+b") as jar:
        url = (
            "https://maven.minecraftforge.net/net/minecraftforge/forge/"
            + mc_version
            + "-"
            + forge_version
            + "/forge-"
            + mc_version
            + "-"
            + forge_version
            + "-installer.jar"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as e:
            print(f"Could not download forge installer.")
            raise
        jar.write(response.content)
    print("Forge installer Downloaded")

def clean_forge_installer(path):
    with contextlib.suppress(FileNotFoundError):
        os.remove(path / "forge-installer.jar")
        os.remove(path / "forge-installer.jar.log")

def download_mc_vanilla(path):
    # TODO: make a portable version between versions.
    with open(path / "minecraft_server.1.12.2.jar", "w+b") as jar:
        url = "https://launcher.mojang.com/v1/objects/886945bfb2b978778c3a0288fd7fab09d315b25f/server.jar"
        try:
            response = requests.get(url)
            jar.write(response.content)
        except HTTPError:
            print(f"Could not download Minecraft vanilla.")
            raise
    print("Vanilla Downloaded")

def install_forge_server(cwd):
    subprocess.run(
        ["java", "-jar", "forge-installer.jar", "--installServer"], cwd=cwd
    )
    print("Forge Installed")

def save_modlist(modlist, path):
    with open(path / "modlist.html", "w") as file:
        data = "<html><body><h1>Modlist</h1><ul>"
        for mod in modlist:
            data += "<li>" + mod["name"].split(".jar")[0] + "</li>"
        data += "</ul></body></html>"
        file.write(data)
    print(f"Saved modlist.html to {path}")

def copy_dirs_filling_tree(dirs, from_location, target_location):
    """
    Copied dirs from from_location to target_location.
    Suppresses FileNotFoundError. Raises FileExistsError if target_location has dirs
    """

    for directory in dirs:
        print(f"copying {from_location / directory} to {target_location / directory}")
        shutil.copytree(
            from_location / directory,
            target_location / directory,
            dirs_exist_ok=True
        )
    print(f"Copied directories: `{dirs}`. From `{from_location}` to `{target_location}`")

def copy_files(files, from_location, target_location):
    """ Copies files from from_location to target_location. Raises FileExistsError/FileNotFoundError"""
    for file in files:
        print(f"copying {file} to {target_location / file}")
        shutil.copyfile(from_location / file, target_location / file)

def build_for_client(client_dirs):
    """ Copies files&folders for client."""

    os.makedirs(CLIENT_OVERRIDES_PATH, exist_ok=True)
    copy_dirs_filling_tree(
        client_dirs,
        from_location=basePath,
        target_location=CLIENT_OVERRIDES_PATH,
    )
    shutil.copy(MANIFEST_PATH, CLIENT_PATH)

def download_cf_dependencies(dependencies, target_location, download_client_mods):
    failed_deps = []
    for dep in dependencies:
        mod_url, mod_name = dep["url"], dep["name"]
        mod_filename = mod_url.split("/")[-1]
        if not download_client_mods:
            if dep["clientOnly"]:
                continue
        if copy_from_cache(mod_filename, target_location):
            continue

        with open(target_location / mod_filename, "w+b") as jar:
            try:
                print(f"Trying to download {mod_name}. From `{mod_url}` to `{target_location}`", end=" ")
                response = requests.get(mod_url)
                response.raise_for_status()
                jar.write(response.content)
                copy_to_cache(target_location / mod_filename)
                print()
            except HTTPError:
                print(f"Failed to download `{mod_name}`")
                failed_deps.append(dep)
    print("Curseforge dependencies downloading finished")
    if failed_deps:
        raise ValueError(f"Failed to download dependencies from CF: {failed_deps}. Exiting")

def build_for_server(manifest, server_dirs):
    """ Copies files&folders for server. Downloads mods from modlist"""
    os.makedirs(SERVER_PATH, exist_ok=True)
    copy_files(
        files=[LICENSE_FILE_NAME, MANIFEST_FILE_NAME, LAUNCH_SCRIPT_FILENAME],
        from_location=basePath,
        target_location=SERVER_PATH,
    )
    copy_dirs_filling_tree(dirs=server_dirs, from_location=basePath, target_location=SERVER_PATH)

    forge_version = manifest["minecraft"]["modLoaders"][0]["id"].split("-")[-1]
    mc_version = manifest["minecraft"]["version"]
    download_forge_installer(SERVER_PATH, forge_version, mc_version)
    download_mc_vanilla(SERVER_PATH)
    install_forge_server(SERVER_PATH)
    clean_forge_installer(SERVER_PATH)

def copy_from_cache(filename, target_location):
    if os.path.exists(CACHE_PATH / filename):
        shutil.copy2(CACHE_PATH / filename, target_location / filename)
        print(f"{filename} loaded from cache to {target_location}")
        return True
    return False

def copy_to_cache(from_location):
    if pathlib.Path(from_location).exists():
        shutil.copy(from_location, CACHE_PATH)
        print(f"{from_location} copied to cache to {CACHE_PATH}")

def create_server_readme(lines):
    shutil.copy(README_SERVER_PATH, SERVER_PATH)
    with open(SERVER_PATH / "README_SERVER.MD", "a") as f:
        f.write("\n# YOU NEED TO MANUALLY DOWNLOAD THESE MODS, THEY COULD NOT BE RESOLVED VIA CFAPI\n")
        for l in lines:
            f.write(f"Following mod info: {l}\n")

def build(args):
    cf_and_external_mods = [] # [{"name":"", "url":""}, ...]
    client_dirs_to_copy = ["scripts", "resources", "config", "mods", "structures", "groovy"]
    server_dirs_to_copy = ["scripts", "config", "mods", "structures", "groovy"]

    # args satisfying
    if args.clean:
        shutil.rmtree(BUILD_OUT_PATH)
    archive_suffix = f"-{compute_commit_hash()}" if args.sha else ""

    manifest = load_manifest()
    setup_build_out_folders()

    cf_and_external_mods.extend(download_external_deps(
        dependencies=manifest["externalDeps"], target_location=MODS_PATH, check_for_hash=args.checksum_externals))
    print("External dependencies downloading finished")

    build_for_client(client_dirs=client_dirs_to_copy)

    if not args.client: # build for server
        resolved_cf_deps, unresolved_cf_deps = resolve_curseforge_deps(manifest["files"])
        cf_and_external_mods.extend(resolved_cf_deps)
        build_for_server(manifest=manifest, server_dirs=server_dirs_to_copy)
        download_cf_dependencies(dependencies=resolved_cf_deps, target_location=SERVER_MODS_PATH, download_client_mods=False)
        save_modlist(cf_and_external_mods, SERVER_PATH)
        create_server_readme(unresolved_cf_deps)

        server_archive_path = BUILD_OUT_PATH / f"server{archive_suffix}"
        shutil.make_archive(str(server_archive_path), "zip", SERVER_PATH)
        print(f"Server archive saved at `{server_archive_path}.zip`")
        print("Finished building server")
    else:
        print("Exiting. Since argument for only client build was provided")

    client_archive_path = BUILD_OUT_PATH / f"client{archive_suffix}"
    shutil.make_archive(str(client_archive_path), "zip", CLIENT_PATH)
    save_modlist(cf_and_external_mods, CLIENT_PATH)
    print(f"Archived client to zip at: `{client_archive_path}.zip`")
    print("Finished building client")

    if args.dev_build: # I`m not sure about this. What we expect to have in buildOut/mmc/ folder ?
        os.makedirs(MMC_MINECRAFT_PATH, exist_ok=True)
        shutil.copytree(SERVER_MODS_PATH, MMC_MINECRAFT_PATH / "mods")

        for directory in client_dirs_to_copy:
            with contextlib.suppress(FileExistsError):
                os.symlink(basePath / directory, MMC_MINECRAFT_PATH / directory)
            print(f"Directories copied to {MMC_MINECRAFT_PATH}")

        for mod in cf_and_external_mods:
            jar_name = mod["name"]
            if not mod["clientOnly"]:
                continue
            with open(MMC_MINECRAFT_PATH / "mods" / jar_name, "w+b") as jar:
                response = requests.get(mod["url"])
                jar.write(response.content)
                print(f"Downloaded :{jar_name}")

        shutil.copy(basePath / "mmc-instance-data.json", MMC_PATH / "mmc-pack.json")
        instance_dir = pathlib.Path(input("What is your MultiMC instance folder:"))
        instance_name = input("What do you want to call the instance:")
        os.symlink(MMC_PATH, instance_dir / instance_name)
        print("You might need to add an instance.cfg for mmc to recognize it")


REQUIRED_PACKAGES = ["requests"]
CF_API_LINK = "https://api.curseforge.com/v1"
HEADERS = {'Accept': 'application/json', 'x-api-key': os.getenv("CFAPIKEY")}

basePath = pathlib.Path(os.path.normpath(os.path.realpath(__file__)[:-7] + ".."))

# filenames
LICENSE_FILE_NAME = "LICENSE"
MANIFEST_FILE_NAME = "manifest.json"
LAUNCH_SCRIPT_FILENAME = "launch.sh"

# filepaths
BUILD_OUT_PATH = basePath / "buildOut"
MODS_PATH = basePath / "mods"
MANIFEST_PATH = basePath / MANIFEST_FILE_NAME
README_SERVER_PATH = basePath / "README_SERVER.md"

CACHE_PATH = pathlib.Path(BUILD_OUT_PATH / "modcache")
CLIENT_PATH = BUILD_OUT_PATH / "client"
SERVER_PATH = BUILD_OUT_PATH / "server"
MMC_PATH = BUILD_OUT_PATH / "mmc"
MMC_MINECRAFT_PATH = MMC_PATH / "minecraft"

SERVER_MODS_PATH = SERVER_PATH / "mods"
CLIENT_OVERRIDES_PATH = CLIENT_PATH / "overrides"

if __name__ == "__main__":
    print("--- BUILD starting ---")
    ensure_dependencies(REQUIRED_PACKAGES)
    assert os.getenv("CFAPIKEY"), "You have to provide a CFAPI key as environment variable"
    build(parse_args())
    print("--- BUILD finished ---")