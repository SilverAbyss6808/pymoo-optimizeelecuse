# DELETE BUILD AND DIST FOLDERS BEFORE RUNNING. THE SCRIPT DOESNT HAVE PERMISSION AND WILL CRASH
import PyInstaller.__main__
PyInstaller.__main__.run([
    'scripts\\optimizer.py',
    '--clean',
    '--contents-directory', 'src',
    '--recursive-copy-metadata', 'imageio'
])