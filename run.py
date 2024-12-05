import parser
import appUi

import shutil
import os

with open("code.txt", "r") as f:
    code = f.read()
    f.close()

project_file = os.path.normpath('projects/program.sb3')

shutil.copyfile('static/start.sb3', 'projects/program.sb3')
project_parser = parser.project(project_file)

project_parser.add_sprite_scripts("S1", code)
project_parser.write(project_file)

appUi.open_sb3_TW(project_file)