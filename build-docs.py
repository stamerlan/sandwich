from pathlib import Path
import argparse
import subprocess
import sys

topdir = Path(__file__).parent

parser = argparse.ArgumentParser(description="Build sphinx documentation for sandwich")
parser.add_argument("outdir", nargs='?',
                    help="Directory to place documentation to")
args = parser.parse_args()

if args.outdir is None:
    # If output directory is not provided check if the script called from source
    # tree. If so - generate documentation in bin/docs, otherwise - in current
    # working directory.
    if Path.cwd() != topdir:
        args.outdir = Path.cwd()
    else:
        args.outdir = topdir / "bin" / "docs"
else:
    args.outdir = Path(args.outdir).absolute()

# Make Doxyfile from docs/Doxyfile.in
with open(topdir / "docs" / "Doxyfile.in") as f:
    doxyfile = f.read()
doxyfile = doxyfile.replace("@topdir@", topdir.as_posix())
args.outdir.mkdir(parents=True, exist_ok=True)
with open(args.outdir / "Doxyfile", "w") as f:
    f.write(doxyfile)

# Run doxygen
try:
    subprocess.check_call("doxygen", stdout=sys.stdout, stderr=sys.stderr,
                          shell=True, cwd=str(args.outdir))
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)

# Run sphinx
try:
    subprocess.check_call([
        "sphinx-build",
        topdir / "docs",
        "-D", "breathe_projects.sandwich=" + str(args.outdir / "doxy-xml"),
        "-D", "breathe_default_project=sandwich",
        "."],
        stdout=sys.stdout, stderr=sys.stderr,
        shell=True,
        cwd=args.outdir)
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
