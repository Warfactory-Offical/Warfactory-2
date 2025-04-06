#!/usr/bin/env python3

# if there is a problem with building, please let htmlcsjs or foontinz know
"""build client & server bundles"""

import argparse
import contextlib
import hashlib
import json
import requests
import os
import pathlib
import shutil
import subprocess
import sys
from time import sleep

from deps import ensure_dependencies


def parse_args():
    parser = argparse.ArgumentParser(prog="build", description=__doc__)
    parser.add_argument("--sha", action="store_true",
                        help="append git hash to zips")
    parser.add_argument("--name", type=str, help="append name to zips")
    parser.add_argument("--retries", type=int, default=3,
                        help="download attempts before failure")
    parser.add_argument("--clean", action="store_true",
                        help="clean output dirs")
    parser.add_argument("--dev_build", action="store_true",
                        help="makes a folder with all the files symlinked for development. probably only works on linux")
    parser.add_argument("-c", "--client", action="store_true",
                        help="only builds the client pack")
    return parser.parse_args()

basePath = pathlib.Path(os.path.normpath(os.path.realpath(__file__)[:-7] + ".."))

BUILD_OUT_PATH = basePath / "buildOut"
MODS_PATH = basePath / "mods"
MANIFEST_PATH = basePath / "manifest.json"
README_SERVER_PATH = basePath / "README_SERVER.md"

CACHE_PATH = pathlib.Path(BUILD_OUT_PATH / "modcache")
CLIENT_PATH = BUILD_OUT_PATH / "client"
SERVER_PATH = BUILD_OUT_PATH / "server"

SERVER_MODS_PATH = SERVER_PATH / "mods"
SERVER_VANILLA_MINECRAFT_JAR_PATH = SERVER_PATH / "minecraft_server.1.12.2.jar"

CLIENT_OVERRIDES_PATH = CLIENT_PATH / "overrides"

def build(args):
    modlist = []
    copyDirs = ["scripts", "resources", "config", "mods", "structures", "groovy"]
    serverCopyDirs = ["scripts", "config", "mods", "structures", "groovy"]

    if args.clean:
        shutil.rmtree(CLIENT_OVERRIDES_PATH, ignore_errors=True)
        shutil.rmtree(SERVER_PATH, ignore_errors=True)
        shutil.rmtree(MODS_PATH, ignore_errors=True)
        sys.exit(0)
    sha = ""
    if args.sha:
        try:
            p = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, cwd=basePath)
            sha = p.stdout.strip().decode("utf-8")
        except Exception as e:
            print("could not determine git sha, skipping")

    with open(MANIFEST_PATH) as file:
        manifest = json.load(file)

    os.makedirs(CLIENT_OVERRIDES_PATH, exist_ok=True)
    os.makedirs(SERVER_PATH, exist_ok=True)
    os.makedirs(MODS_PATH, exist_ok=True)
    os.makedirs(CACHE_PATH, exist_ok=True)

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

    for mod in manifest["externalDeps"]:
        with open(MODS_PATH / mod["url"].split("/")[-1], "w+b") as jar:
            for i in range(args.retries + 1):
                if i == args.retries:
                    raise Exception("Download failed")

                r = requests.get(mod["url"])

                mod_hash = hashlib.sha256(r.content).hexdigest()
                if str(mod_hash) == mod["hash"]:
                    jar.write(r.content)
                    modlist.append(mod["name"])
                    print("hash successful for {}".format(mod["name"]))
                    break
                else:
                    print("hash unsuccessful for {}".format(mod["name"]))
                    print("use", str(mod_hash), "this if it is consistent across runs")

    for directory in copyDirs:
        print(f"copying {basePath / directory} to {CLIENT_OVERRIDES_PATH / directory}")
        with contextlib.suppress(FileNotFoundError):
            shutil.copytree(basePath / directory, CLIENT_OVERRIDES_PATH / directory, dirs_exist_ok=True)
    print(f"directories copied to {CLIENT_PATH}")

    archive =  BUILD_OUT_PATH / "client"
    shutil.copy(MANIFEST_PATH, CLIENT_PATH / "manifest.json")
    shutil.make_archive(f"{archive}-{sha}" if sha else str(archive), "zip", CLIENT_PATH)
    print(f'client zip "{archive}.zip" made')
    print("Finished building client.")

    if args.client:
        print("Exiting. Since argument for only client build was provided")
        return

    mods_to_manually_download = []
    headers = {'Accept': 'application/json'}
    for mod in manifest["files"]:
        curse_forge_mod_url = f"https://api.curseforge.com/v1/mods/{mod['projectID']}"
        download_url = f"{curse_forge_mod_url}/files/{mod['fileID']}/download-url"
        r = requests.get(download_url, headers=headers)
        try:
            metadata = json.loads(r.text)
        except:
            print(download_url)
            mod_response = requests.get(curse_forge_mod_url, headers=headers)
            try:
                data = mod_response.json()["data"]
                mods_to_manually_download.append(f"https://www.curseforge.com/minecraft/mc-mods/{data['slug']}/files/{mod['fileID']}")
            except:
                mods_to_manually_download.append(f"This is the raw mod id and file id, CF api isn`t responding: `{mod['projectID']}`, `{mod['fileID']}`")
            continue

        name = "placeholder"
        if "name" in mod:
            name = mod["name"]
            if name[-4:] != ".jar":
                name += ".jar"
        else:
            name = metadata["data"].split("/")[-1]
        url = metadata["data"]
        clientOnly = False
        try:
            clientOnly = mod["clientOnly"]
        except:
            clientOnly = False

        modlist.append({"name": name, "url": url, "clientOnly": clientOnly})
    print("modlist compiled")

    with open(BUILD_OUT_PATH / "modlist.html", "w") as file:
        data = "<html><body><h1>Modlist</h1><ul>"
        for mod in modlist:
            data += "<li>" + mod["name"].split(".jar")[0] + "</li>"
        data += "</ul></body></html>"
        file.write(data)
    print("modlist.html done")

    shutil.copy(MANIFEST_PATH, SERVER_PATH / "manifest.json")
    shutil.copy(basePath / "LICENSE", SERVER_PATH / "LICENSE")
    shutil.copy(basePath / "launch.sh", SERVER_PATH / "launch.sh")
    for directory in serverCopyDirs:
        print(f"copying {basePath / directory} to {SERVER_PATH / directory}")
        with contextlib.suppress(FileNotFoundError):
            shutil.copytree(basePath / directory, SERVER_PATH / directory)
    print("directories copied to buildOut/server")

    for mod in modlist:
        jarname = mod["url"].split("/")[-1]
        if mod["clientOnly"]:
            continue

        if os.path.exists(CACHE_PATH / jarname):
            shutil.copy2(CACHE_PATH / jarname, SERVER_MODS_PATH / jarname)
            print(f"{mod} loaded from cache")
            continue

        with open(SERVER_MODS_PATH / jarname, "w+b") as jar:
            r = requests.get(mod["url"])
            jar.write(r.content)
            print(f"Downloaded {mod['name']}")
    print("Mods Downloaded")

    with open(SERVER_PATH / "forge-installer.jar", "w+b") as jar:
        forgeVer = manifest["minecraft"]["modLoaders"][0]["id"].split("-")[-1]
        mcVer = manifest["minecraft"]["version"]
        url = (
            "https://maven.minecraftforge.net/net/minecraftforge/forge/"
            + mcVer
            + "-"
            + forgeVer
            + "/forge-"
            + mcVer
            + "-"
            + forgeVer
            + "-installer.jar"
        )
        r = requests.get(url)
        jar.write(r.content)
    print("Forge installer Downloaded")

    # TODO: make a portable version between versions
    if not os.path.isfile(SERVER_VANILLA_MINECRAFT_JAR_PATH):
        with open(SERVER_VANILLA_MINECRAFT_JAR_PATH, "w+b") as jar:
            url = "https://launcher.mojang.com/v1/objects/886945bfb2b978778c3a0288fd7fab09d315b25f/server.jar"
            r = requests.get(url)
            jar.write(r.content)
        print("Vanilla Downloaded")
    subprocess.run(["java", "-jar", "forge-installer.jar", "--installServer"], cwd=SERVER_PATH)
    print("Forge Installed")

    if len(mods_to_manually_download) != 0 or os.path.exists(README_SERVER_PATH):
        with open(SERVER_PATH / "README_SERVER.md", "w") as f:
            if os.path.exists(README_SERVER_PATH):
                with open(README_SERVER_PATH) as g:
                    f.write(g.read())
            if len(mods_to_manually_download) != 0:
                f.write("\n# YOU NEED TO MANUALLY DOWNLOAD THESE MODS\n")
                for i in mods_to_manually_download:
                    f.write(i + "\n")

    try:
        os.remove(SERVER_PATH / "forge-installer.jar")
    except Exception as e:
        print(f"Couldn't delete forge-installer.jar: {e}")
    try:
        os.remove(SERVER_PATH / "forge-installer.jar.log")
    except Exception as e:
        print(f"Couldn't delete forge-installer.jar.log: {e}")

    archive = BUILD_OUT_PATH / "server"
    shutil.make_archive(f"{archive}-{sha}" if sha else str(archive), "zip", SERVER_PATH)
    print(f"server zip '{archive}.zip' made")

    if args.dev_build:
        os.makedirs(BUILD_OUT_PATH / "mmc/minecraft", exist_ok=True)
        shutil.rmtree(BUILD_OUT_PATH / "mmc/minecraft/mods/", ignore_errors=True)
        shutil.copytree(SERVER_MODS_PATH, BUILD_OUT_PATH / "mmc/minecraft/mods/")
        for directory in copyDirs:
            try:
                os.symlink(basePath / directory, BUILD_OUT_PATH / "mmc/minecraft/" / directory)
            except Exception:
                print("Directory exists, skipping")
            print(f"directories copied to {BUILD_OUT_PATH}/mmc/minecraft")

        for mod in modlist:
            jarname = mod["name"].split("/")[-1]
            if not modClientOnly[i]: # todo: this will fail, unresolved ref
                break

            with open(BUILD_OUT_PATH / "mmc/minecraft/mods/" / jarname, "w+b") as jar:
                r = requests.get(mod["url"])
                jar.write(r.content)
                print(f"Downloaded :{mod['name']}")

        shutil.copy(basePath / "mmc-instance-data.json", BUILD_OUT_PATH / "mmc/mmc-pack.json")
        instanceFolder = input("What is your MultiMC instance folder:")
        instanceName = input("What do you want to call the instance:")
        os.symlink(BUILD_OUT_PATH / "mmc/", instanceFolder + "/" + instanceName)
        print("you might need to add an instance.cfg for mmc to reconise it")


REQUIRED_PACKAGES = ["httpx"]
TEMPORARY_DIRECTORY_PATH = "_tempdir_py"

if __name__ == "__main__":
    print("--- Script starting ---")
    ensure_dependencies(REQUIRED_PACKAGES)

    build(parse_args())

    print("--- Script finished ---")