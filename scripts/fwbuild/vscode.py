from pathlib import Path
import contextlib
import fwbuild
import fwbuild.toolchains
import json
import sys

class JSONWithCommentsDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def decode(self, s: str):
        s = '\n'.join(l if not l.lstrip().startswith('//') else '' for l in s.split('\n'))
        return super().decode(s)


def merge_conf(conf_list: list[dict[str, str]], new_conf: dict[str, str],
                **properties) -> list[dict[str, str]]:
    """ Look for item in conf_list which has specific properties set and equal
        to the value. If found merge the conf with new_conf, otherwise add conf
        to the end of conf_list.
    """
    new_conf_list = []
    found = False
    for conf in conf_list:
        for k, v in properties.items():
            if conf.get(k, None) != v:
                break
        else:
            found = True
            new_conf_list.append(conf | new_conf)
            continue

        new_conf_list.append(conf)

    if not found:
        new_conf_list.append(new_conf)

    return new_conf_list


def mk_launch_conf(topout: Path, workspace: Path,
        platform: "fwbuild.platform_base", target: "fwbuild.cxx_app",
        artifacts: "fwbuild.cxx_app.artifacts") -> dict[str, str]:

    launch_conf = {}

    if isinstance(target, fwbuild.cxx_gtest):
        launch_conf = {
            "name": f"{platform.name}: test {target.name}",
            "request": "launch",
            "externalConsole": False,
            "program": topout / artifacts.app,
            "args": [],
            "stopAtEntry": False,
            "cwd": "${workspaceFolder}",
            "environment": []
        }
        with contextlib.suppress(FileNotFoundError):
            if isinstance(target.toolchain, fwbuild.toolchains.gcc):
                gdb = fwbuild.tool(target.toolchain.tools.cc.path.parent,
                                   target.toolchain.prefix + "gdb")
                launch_conf["type"] ="cppdbg"
                launch_conf["MIMode"] = "gdb"
                launch_conf["miDebuggerPath"] = str(gdb)
    else:
        launch_conf = {
            "name": f"{platform.name}: {target.name}",
        }
        conf = platform.vscode_launch(topout, target, artifacts)
        if conf is None:
            return None
        launch_conf |= conf

    if "program" in launch_conf:
        program = Path(launch_conf["program"])
        if program.is_relative_to(workspace):
            program = Path("${workspaceFolder}", program.relative_to(workspace))
        launch_conf["program"] = program.as_posix()

    return launch_conf


def write_launch_json(filename: Path, topout: Path, workspace: Path,
        platform: "fwbuild.platform_base",
        artifacts: dict["fwbuild.cxx_app", "fwbuild.cxx_app.artifacts"]):
    launch = {}
    if filename.is_file():
        with open(filename, "r") as f:
            with contextlib.suppress(json.decoder.JSONDecodeError):
                launch = json.load(f, cls=JSONWithCommentsDecoder)

    if "version" not in launch:
        launch["version"] = "0.2.0"
    if "configurations" not in launch:
        launch["configurations"] = []

    # Add applications to launch.json
    for target, build in artifacts.items():
        if isinstance(target, fwbuild.cxx_gtest):
            continue
        if not isinstance(target, fwbuild.cxx_app):
            raise RuntimeError(f"Unexpected target type {type(target)}")

        launch_conf = mk_launch_conf(topout, workspace, platform, target, build)
        if launch_conf is None:
            continue
        launch["configurations"] = merge_conf(launch["configurations"],
            launch_conf, name=launch_conf["name"])

    # Add tests to launch.json
    for target, build in artifacts.items():
        if not isinstance(target, fwbuild.cxx_gtest):
            continue

        launch_conf = mk_launch_conf(topout, workspace, platform, target, build)
        launch["configurations"] = merge_conf(launch["configurations"],
            launch_conf, name=launch_conf["name"])

    # Write updated file
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(launch, f, indent=4)


def write_tasks_json(filename: Path, topout: Path, workspace: Path,
        platform: "fwbuild.platform_base",
        artifacts: dict["fwbuild.cxx_app", "fwbuild.cxx_app.artifacts"]):
    tasks = {}

    if filename.is_file():
        with open(filename, "r") as f:
            with contextlib.suppress(json.decoder.JSONDecodeError):
                tasks = json.load(f, cls=JSONWithCommentsDecoder)

    if "version" not in tasks:
        tasks["version"] = "2.0.0"
    if "tasks" not in tasks:
        tasks["tasks"] = []

    # configure task
    conf_task = {
        "label": f"{platform.name}: configure",
        "type": "shell",
        "command": sys.executable,
        "args": sys.argv,
        "options": {
            "cwd": Path.cwd().as_posix()
        }
    }
    tasks["tasks"] = merge_conf(tasks["tasks"], conf_task,
                                label=conf_task["label"])

    # build task
    build_task = {
        "label": f"{platform.name}: build",
        "group": "build",
        "command": "ninja",
        "args": ["-C", topout.as_posix()],
        "dependsOn": [conf_task["label"]]
    }
    tasks["tasks"] = merge_conf(tasks["tasks"], build_task,
                                label=build_task["label"])


    test_exe = []
    for target, target_artifacts in artifacts.items():
        if isinstance(target, fwbuild.cxx_gtest):
            test_exe.append(target_artifacts.app.as_posix())

    if test_exe:
        # build test task
        build_test_task = {
            "label": f"{platform.name}: build test",
            "group": "build",
            "command": "ninja",
            "args": ["-C", topout.as_posix()] + test_exe,
            "dependsOn": [conf_task["label"]]
        }
        tasks["tasks"] = merge_conf(tasks["tasks"], build_test_task,
                                    label=build_test_task["label"])

        # test task
        test_task = {
            "label": f"{platform.name}: test",
            "group": "test",
            "command": "ninja",
            "args": ["-C", topout.as_posix(), "test"],
            "dependsOn": [build_test_task["label"]]
        }
        tasks["tasks"] = merge_conf(tasks["tasks"], test_task,
                                    label=test_task["label"])

    # Write updated file
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=4)


def write_settings_json(filename: Path, topout: Path, workspace: Path,
        platform: "fwbuild.platform_base",
        artifacts: dict["fwbuild.cxx_app", "fwbuild.cxx_app.artifacts"]):
    # check if any task target present
    test_targets = []
    for target, build in artifacts.items():
        if isinstance(target, fwbuild.cxx_gtest):
            test_targets.append(target)

    if not test_targets:
        return

    settings = {}
    if filename.is_file():
        with open(filename, "r") as f:
            with contextlib.suppress(json.decoder.JSONDecodeError):
                settings = json.load(f, cls=JSONWithCommentsDecoder)

    if "gtest-adapter.debugConfig" not in settings:
        settings["gtest-adapter.debugConfig"] = []

    for target in test_targets:
        conf_name = f"{platform.name}: test {target.name}"
        if conf_name not in settings["gtest-adapter.debugConfig"]:
            settings["gtest-adapter.debugConfig"].append(conf_name)

    # Write updated file
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(settings, f, indent=4)


def vscode(platform: "fwbuild.platform_base",
           artifacts: dict["fwbuild.cxx_app", "fwbuild.cxx_app.artifacts"],
           topout: str | Path, vscode_dir: str | Path = ".vscode"):
    topout = Path(topout)
    if not topout.is_absolute():
        topout = Path.cwd() / topout

    vscode_dir = Path(vscode_dir)
    if not vscode_dir.is_absolute():
        vscode_dir = fwbuild.topdir / vscode_dir

    workspace_folder = vscode_dir.parent

    write_launch_json(vscode_dir / "launch.json", topout, workspace_folder,
                      platform, artifacts)
    write_tasks_json(vscode_dir / "tasks.json", topout, workspace_folder,
                     platform, artifacts)
    write_settings_json(vscode_dir / "settings.json", topout, workspace_folder,
                        platform, artifacts)
