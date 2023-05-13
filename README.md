# sandwich

## raspi3b Qemu run
qemu-system-aarch64 -M raspi3b -kernel bin/hello -serial null -serial stdio

## VSCode tasks.json
```
{
    "label": "Build",
    "group": "build",
    "type": "shell",
    "command": "ninja",
    "args": ["-C",  "bin/"]
}
```

## VSCode launch.json
```
{
    "name": "hello.exe",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/bin/hello.exe",
    "externalConsole": false,
    "args": [],
    "stopAtEntry": false,
    "cwd": "${workspaceFolder}",
    "environment": [],
    "MIMode": "gdb",
    "miDebuggerPath": "C:/bin/mingw64/bin/gdb.exe"
}
```
