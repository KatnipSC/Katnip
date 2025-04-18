import main_parser

def translate(code):
    """
    Translates the given Scratch code into a Scratch 3 project

    Args:
      code (dict): Scratch code to be translated
          code["SpriteName"]: Name of the Scratch sprite
              Sprite attributes (list): Code, Costumes, Sounds

    Returns:
      filename (str): Scratch .sb3 file for the generated Scratch code
    """
    project_parser = main_parser.project()
    project_parser.process_scrtxt(code) # Make this be all items not just 0th
    project_parser.write()

    #appUi.open_sb3_TW(project_file) uncomment this line if you are running this locally to open with turbowarp
    return f'program_{project_parser.id}.sb3'

with open("app_static\\scripts\\illegal.knp", "r") as f:
    code = f.read()
    f.close()

    translate({"Stage": ["",[["Default-Blank", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGBgAAAABQABpfZFQAAAAABJRU5ErkJggg=="]]],
               "S1": [code, [["Smile","data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGPgFvwPAAFGARyS/G3DAAAAAElFTkSuQmCC"]]]
               })