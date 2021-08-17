import os
import subprocess

for root, subdirs, files in os.walk('ui', ):
    for filename in files:
        if filename.endswith('.ui'):
            ui_path = os.path.join(root, filename)
            py_path = os.path.join(root, filename[:-3] + '.py')
#            print(['pyuic5', ui_path, '-o', py_path])
            subprocess.run(['pyuic5', ui_path, '-o', py_path])
