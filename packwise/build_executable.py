"""Builds a stand-alone executable for the CURRENT operating system:  python build_executable.py
(PyInstaller cannot cross-compile: run it once on Windows, once on macOS and once on Linux.)"""
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
                       "--name", "PackWise", "run_packwise.py"])
print("Executable written to the dist/ folder.")
