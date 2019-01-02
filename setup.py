# This is the build conf file. to make the exe 
# jus run : python setup.py build ...
from cx_Freeze import setup, Executable
# import os

base = None    

executables = [Executable("gui.py", base=base)]

packages = [
	"idna", "os", "tkinter", "time", 
	"re", "pandas", "numpy", "datetime", 
	"apiclient", "httplib2", "oauth2client", "googleapiclient"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

# build_exe_options= {""}

# print(os.path.abspath( os.path.join( '..', 'AppData','Local','Continuum','Miniconda3','envs','patrick_ford','tcl','tcl8.6' )))

# os.environ['TCL_LIBRARY'] = os.path.join(r"c:\Users\aivanov\AppData\Local\Continuum\Miniconda3\envs\patrick_ford\tcl\tcl8.6\";
# os.environ['TCL_LIBRARY'] = r'c:\Users\aivanov\AppData\Local\Continuum\Miniconda3\envs\patrick_ford\tcl\tk8.6\';

setup(
    name = "Patrick_Ford_Pandas",
    options = options,
    version = "0.1",
    description = 'The First Release',
    executables = executables
)
