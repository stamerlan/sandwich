from pathlib import Path
import fwbuild
import fwbuild.toolchains
import json

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
            print("Update", conf)
            print("New value:", conf | new_conf)

            found = True
            new_conf_list.append(conf | new_conf)
            continue

        new_conf_list.append(conf)

    if not found:
        new_conf_list.append(new_conf)

    return new_conf_list


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

    launch = {}
    launch_json = vscode_dir / "launch.json"
    if launch_json.is_file():
        with open(launch_json, "r") as f:
            launch = json.load(f, cls=JSONWithCommentsDecoder)

    if "version" not in launch:
        launch["version"] = "0.2.0"
    if "configurations" not in launch:
        launch["configurations"] = []

    for target, build in artifacts.items():
        if isinstance(target, fwbuild.cxx_gtest):
            conf_name = f"{platform.name}: test {target.name}"
        else:
            conf_name = f"{platform.name}: {target.name}"

        launch_conf = {
            "name": conf_name,
            "type":"cppdbg",
            "request": "launch",
            "externalConsole": False,
            "args": [],
            "stopAtEntry": False,
            "cwd": "${workspaceFolder}",
            "environment": []
        }

        program = topout / build.app
        if program.is_relative_to(workspace_folder):
            program = Path("${workspaceFolder}", program.relative_to(workspace_folder))
        launch_conf["program"] = program.as_posix()

        if isinstance(target.toolchain, fwbuild.toolchains.gcc):
            try:
                gdb = fwbuild.tool(target.toolchain.tools.cc.path.parent,
                                   target.toolchain.prefix + "gdb")

                launch_conf["MIMode"] = "gdb"
                launch_conf["miDebuggerPath"] = str(gdb)
            except FileNotFoundError:
                pass

        launch["configurations"] = merge_conf(launch["configurations"],
            launch_conf, name=conf_name)

    launch_json.parent.mkdir(parents=True, exist_ok=True)
    with open(launch_json, "w") as f:
        json.dump(launch, f, indent=4)
