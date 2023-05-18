# sandwich

## raspi3b Qemu run
qemu-system-aarch64 -M raspi3b -kernel bin/raspi3b/kernel8.elf -serial null -serial stdio

## VSCode tasks.json
```
{
    "label": "Build",
    "group": "build",
    "type": "shell",
    "command": "ninja",
    "args": ["-C",  "bin/host/"]
}
```

## VSCode launch.json
```
{
    "name": "hello.exe",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/bin/host/hello.exe",
    "externalConsole": false,
    "args": [],
    "stopAtEntry": false,
    "cwd": "${workspaceFolder}",
    "environment": [],
    "MIMode": "gdb",
    "miDebuggerPath": "C:/bin/mingw64/bin/gdb.exe"
}
```

## Build Docker image
```
docker build -t stamerlan/sandwich-build .
```

## Run Docker image in iteractive mode
```
docker run -it --mount src=.,target=/__w,type=bind stamerlan/sandwich-build
```

## Check Docker images
```
docker images
```

## Push Docker image to Dockerhub
```
docker image push stamerlan/sandwich-build
```
