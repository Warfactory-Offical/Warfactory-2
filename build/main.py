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
    parser.add_argument("--retries", type=int, default=3, help="download attempts before failure")
    parser.add_argument("--clean", action="store_true",help="clean output dirs")
    parser.add_argument(
        "--dev-build", action="store_true", help="makes a folder with all the files symlinked for development. probably only works on linux")
    parser.add_argument("-c", "--client", action="store_true", help="builds only client pack")
    return parser.parse_args()

CF_API_LINK = "https://api.curseforge.com/v1"
HEADERS = {'Accept': 'application/json', 'x-api-key': os.getenv("CFAPIKEY")}

basePath = pathlib.Path(os.path.normpath(os.path.realpath(__file__)[:-7] + ".."))

BUILD_OUT_PATH = basePath / "buildOut"
MODS_PATH = basePath / "mods"
MANIFEST_PATH = basePath / "manifest.json"
README_SERVER_PATH = basePath / "README_SERVER.md"

CACHE_PATH = pathlib.Path(BUILD_OUT_PATH / "modcache")
CLIENT_PATH = BUILD_OUT_PATH / "client"
SERVER_PATH = BUILD_OUT_PATH / "server"
MMC_MINECRAFT_PATH = BUILD_OUT_PATH / "mmc/minecraft"

SERVER_MODS_PATH = SERVER_PATH / "mods"
SERVER_VANILLA_MINECRAFT_JAR_PATH = SERVER_PATH / "minecraft_server.1.12.2.jar"

CLIENT_OVERRIDES_PATH = CLIENT_PATH / "overrides"

def setup_build_out_folders():
    os.makedirs(CLIENT_OVERRIDES_PATH, exist_ok=True)
    os.makedirs(SERVER_PATH, exist_ok=True)
    os.makedirs(MODS_PATH, exist_ok=True)
    os.makedirs(CACHE_PATH, exist_ok=True)

def load_manifest():
    with open(MANIFEST_PATH) as file:
        return json.load(file)

def clear_build():
    shutil.rmtree(MMC_MINECRAFT_PATH / "mods", ignore_errors=True)
    shutil.rmtree(CLIENT_OVERRIDES_PATH, ignore_errors=True)
    shutil.rmtree(SERVER_PATH, ignore_errors=True)
    shutil.rmtree(MODS_PATH, ignore_errors=True)

def compute_commit_hash():
    compute_sha = ["git", "rev-parse", "--short", "HEAD"]
    p = subprocess.run(compute_sha, capture_output=True, cwd=basePath)
    if p.returncode != 0:
        raise ValueError(f"Commit hash could not be computed using `{' '.join(compute_sha)}`")
    return p.stdout.strip().decode("utf-8")

def download_client_dependencies(dependencies, mods_path): # todo: add retries
    downloaded_mods = []
    for mod in dependencies:
        download_url = mod["url"]
        mod_name = mod["name"]
        expected_mod_hash = mod["hash"]
        with open(mods_path / download_url.split("/")[-1], "w+b") as jar:
            response = requests.get(download_url)
            actual_mod_hash = hashlib.sha256(response.content).hexdigest()
            if str(actual_mod_hash) == expected_mod_hash:
                jar.write(response.content)
                downloaded_mods.append(mod_name)
                print(f"Successful checksum for {mod_name}")
            else:
                print(f"Unsuccessful checksum for {mod_name}. \n {actual_mod_hash} != {expected_mod_hash}")
    print("Server mods downloading finished")
    return downloaded_mods

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
            print(f"Could not download forge installer. Error occurred: {e}")
            raise
        jar.write(response.content)
    print("Forge installer Downloaded")

def download_mc_vanilla(path):
    # TODO: make a portable version between versions.
    with open(path, "w+b") as jar:
        url = "https://launcher.mojang.com/v1/objects/886945bfb2b978778c3a0288fd7fab09d315b25f/server.jar"
        response = requests.get(url)
        jar.write(response.content)
    print("Vanilla Downloaded")

def install_forge_server(cwd):
    subprocess.run(
        ["java", "-jar", "forge-installer.jar", "--installServer"], cwd=cwd
    )
    print("Forge Installed")

def save_modlist(modlist, path):
    with open(path, "w") as file:
        data = "<html><body><h1>Modlist</h1><ul>"
        for mod in modlist:
            data += "<li>" + mod["name"].split(".jar")[0] + "</li>"
        data += "</ul></body></html>"
        file.write(data)
    print("modlist.html done")

def resolve_server_mod_dependencies(dependencies):
    guidance_lines = []
    mods_resolved = []
    for mod in dependencies:
        mod_project_id, file_id = mod["projectID"], mod["fileID"]
        curse_forge_mod_url = f"{CF_API_LINK}/mods/{mod_project_id}"
        download_url = f"{curse_forge_mod_url}/files/{file_id}/download-url"

        try:
            print(f"Trying to download metadata from {download_url}", end=" ")
            response = requests.get(download_url, headers=HEADERS)
            response.raise_for_status()
            metadata = json.loads(response.json())
            print()
        except (HTTPError, JSONDecodeError) as e:
            print(f"Failed. With error: `{e}`")
            try:
                print(f"Trying to download metadata from `{curse_forge_mod_url}`.", end=" ")
                response_by_project = requests.get(curse_forge_mod_url, headers=HEADERS)
                response_by_project.raise_for_status()
                data = response_by_project.json()["data"]
                guidance_lines.append( # genuinely not sure if this is correct. Left as it was
                    f"https://www.curseforge.com/minecraft/mc-mods/{data['slug']}/files/{file_id}")
                print()
            except (HTTPError, JSONDecodeError) as e:
                print(f"Failed. With error: `{e}`")
                guidance_lines.append(
                    f"This is the raw data, CF api isn`t responding: mod_id: `{mod_project_id}`, file_id: `{file_id}`"
                )
            continue

        name = mod.get("name", metadata["data"].split("/")[-1])
        name = name if name.endswith(".jar") else name + ".jar"
        url = metadata["data"]
        mods_resolved.append({"name": name, "url": url, "clientOnly": mod.get("clientOnly", False)})
    print("Server modlist resolved")
    return mods_resolved, guidance_lines

def copy_dirs(dirs, from_location, target_location):
    """
    Copied dirs from from_location to target_location.
    Suppresses FileNotFoundError. Raises FileExistsError if target_location has dirs
    """

    for directory in dirs:
        print(f"copying {from_location / directory} to {target_location / directory}")
        with contextlib.suppress(FileNotFoundError):
            shutil.copytree(
                from_location / directory,
                target_location / directory,
                dirs_exist_ok=True
            )
    print(f"Copied directories: `{dirs}`. From `{from_location}` to `{target_location}`")

def build_for_client(dependencies, client_dirs, archive_name):
    modlist = download_client_dependencies(dependencies=dependencies, mods_path=MODS_PATH) # todo: they are not client mods, they are both
    copy_dirs(
        client_dirs,
        from_location=basePath,
        target_location=CLIENT_OVERRIDES_PATH,
    )

    shutil.copy(MANIFEST_PATH, CLIENT_PATH / "manifest.json")
    client_archive_path = BUILD_OUT_PATH / archive_name
    shutil.make_archive(client_archive_path, "zip", CLIENT_PATH)
    print(f"Archived client to zip at: `{client_archive_path}.zip`")
    print("Finished building client")
    return modlist

def build(args):
    modlist = []
    client_dirs_to_copy = ["scripts", "resources", "config", "mods", "structures", "groovy"]
    server_dirs_to_copy = ["scripts", "config", "mods", "structures", "groovy"]

    if args.clean:
        return clear_build()
    archive_identifier = compute_commit_hash() if getattr(args, "sha", False) else ""
    setup_build_out_folders()

    # if we downloaded mods before, add them to the cache
    cached = 0
    if os.path.isdir(SERVER_MODS_PATH):
        for mod in os.listdir(SERVER_MODS_PATH):
            # don't waste time copying mods to the cache that are already there
            if os.path.exists(CACHE_PATH / mod):
                continue
            cached += 1
            shutil.copy2(SERVER_MODS_PATH / mod, CACHE_PATH / mod)
    if cached > 0:
        print(f"cached {cached} mod downloads in {CACHE_PATH}")

    manifest = load_manifest()
    client_modlist = build_for_client(
        manifest["externalDeps"],
        client_dirs_to_copy,
        f"client-{archive_identifier}")
    modlist.extend(client_modlist)

    if args.client:
        print("Exiting. Since argument for only client build was provided")
        return

    save_modlist(modlist, BUILD_OUT_PATH / "modlist.html")

    shutil.copy(MANIFEST_PATH, SERVER_PATH / "manifest.json")
    shutil.copy(basePath / "LICENSE", SERVER_PATH / "LICENSE")
    shutil.copy(basePath / "launch.sh", SERVER_PATH / "launch.sh")
    copy_dirs(server_dirs_to_copy, from_location=basePath, target_location=SERVER_PATH)

    for mod in modlist:
        mod_url, mod_name = mod["url"], mod["name"]
        jar_name = mod_url.split("/")[-1]
        if mod["clientOnly"]:
            continue

        if os.path.exists(CACHE_PATH / jar_name): # todo decompose
            shutil.copy2(CACHE_PATH / jar_name, SERVER_MODS_PATH / jar_name)
            print(f"{mod} loaded from cache")
            continue

        with open(SERVER_MODS_PATH / jar_name, "w+b") as jar:
            try:
                print(f"Trying to download {mod_name}")
                response = requests.get(mod_url)
                response.raise_for_status()
                jar.write(response.content)
            except HTTPError:
                print(f"Failed to download {mod_name}")
    print("Server mods downloading finished")

    forge_version = manifest["minecraft"]["modLoaders"][0]["id"].split("-")[-1]
    mc_version = manifest["minecraft"]["version"]
    download_forge_installer(SERVER_PATH, forge_version, mc_version)
    download_mc_vanilla(SERVER_VANILLA_MINECRAFT_JAR_PATH)
    install_forge_server(SERVER_PATH)

    resolved_mods, guidance_for_server_readme_lines = resolve_server_mod_dependencies(manifest["files"])
    modlist.extend(resolved_mods)

    shutil.copy(README_SERVER_PATH, SERVER_PATH)
    if guidance_for_server_readme_lines:
        with open(SERVER_PATH / "README_SERVER.md", "w") as f:
            f.write("\n# YOU NEED TO MANUALLY DOWNLOAD THESE MODS\n")
            for line in guidance_for_server_readme_lines:
                f.write(line + "\n")

    with contextlib.suppress(FileNotFoundError):
        os.remove(SERVER_PATH / "forge-installer.jar")
        os.remove(SERVER_PATH / "forge-installer.jar.log")

    server_archive_path = f"{BUILD_OUT_PATH / 'server'}{f'-{archive_identifier}' if archive_identifier else ''}"
    shutil.make_archive(server_archive_path, "zip", SERVER_PATH)
    print(f"Server archive saved at `{server_archive_path}.zip`")

    if args.dev_build: # I`m not sure about this.
        os.makedirs(MMC_MINECRAFT_PATH, exist_ok=True)
        shutil.copytree(SERVER_MODS_PATH, MMC_MINECRAFT_PATH / "mods")

        for directory in client_dirs_to_copy:
            with contextlib.suppress(FileExistsError):
                os.symlink(basePath / directory, MMC_MINECRAFT_PATH / directory)
            print(f"Directories copied to {MMC_MINECRAFT_PATH}")

        for mod in modlist:
            jar_name = mod["name"].split("/")[-1]
            if not mod["clientOnly"]:
                continue

            with open(MMC_MINECRAFT_PATH / "mods" / jar_name, "w+b") as jar:
                response = requests.get(mod["url"])
                jar.write(response.content)
                print(f"Downloaded :{mod['name']}")

        shutil.copy(basePath / "mmc-instance-data.json", BUILD_OUT_PATH / "mmc/mmc-pack.json")
        instanceFolder = input("What is your MultiMC instance folder:")
        instanceName = input("What do you want to call the instance:")
        os.symlink(BUILD_OUT_PATH / "mmc/", instanceFolder + "/" + instanceName)
        print("you might need to add an instance.cfg for mmc to recognize it")


REQUIRED_PACKAGES = ["httpx"]

if __name__ == "__main__":
    print("--- BUILD starting ---")
    ensure_dependencies(REQUIRED_PACKAGES)

    assert os.getenv("CFAPIKEY"), "You have to provide a CFAPI key as environment variable"
    build(parse_args())

    print("--- BUILD finished ---")