import sys
import os
from cx_Freeze import setup, Executable


copyDependentFiles = True
silent = True
base = None
if sys.platform == "win32":
    base = "Win32GUI"
elif sys.platform == "win64":
    base = "Win64GUI"

includes = ["sys", "os", "time", "BVHCommon"]
excludes = []
excludes = ["IPython", "jupyter", "notebook", "backports", "concurrent", "curses",
            "email", "html", "http", "nose", "multiprocessing", "OpenGL_accelerate",
            "json", "pydoc_data", "pyreadline", "pkg_resources", "xml", "xmlrpc",
            "urllib"]
packages = ["numpy", "PyQt5.Qt", "OpenGL"]
includeFiles = ["IconResource/", "platforms/", "imageformats/", ]

# tcl, tk Directory Path
os.environ['TCL_LIBRARY'] = "C:\\Anaconda3\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Anaconda3\\tcl\\tk8.6"

setup( name = "BVH Player [ver 1.0]",
    version = "1.0",
    options = {"build_exe": {"includes": includes, "excludes": excludes,
               "packages": packages, "include_files": includeFiles}},
    executables = [Executable("BVHPlayerPy.py", base=base)])