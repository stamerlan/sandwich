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
        conf_name = f"{platform.name}-{target.name}"
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

        found = False
        configurations = []
        for conf in launch["configurations"]:
            if conf.get("name", None) == conf_name:
                conf |= launch_conf
                found = True
            configurations.append(conf)
        if not found:
            configurations.append(launch_conf)

        launch["configurations"] = configurations

    launch_json.parent.mkdir(parents=True, exist_ok=True)
    with open(launch_json, "w") as f:
        json.dump(launch, f, indent=4)
