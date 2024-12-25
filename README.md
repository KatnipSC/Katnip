# v2.ScratchText 
![ScratchText](references/title.png)

A text-based language for Scratch programming

## About
This is the second version of ScratchText, a completely re-written version of [the original](https://github.com/B1j2754/scratchtext/).

This project aims to provide a text-based implementation of Scratch programming, to enable faster, clearer, and cleaner development of Scratch projects.

### Links:
- VS Code syntax highlighting extension: [GitHub Repo](https://github.com/B1j2754/syntax-scratchtext)
- Official Forum: [ScratchText Scratch Forum](https://scratch.mit.edu/discuss/topic/769174/)
- Scratch Profile: [B1j2754](https://scratch.mit.edu/users/B1j2754/)
- Github: [B1j2754](https://github.com/B1j2754/)
- Issues?: [GitHub Issues Page](https://github.com/B1j2754/v2.ScratchText/issues)
- Wiki (docs): [GitHub Wiki](https://github.com/B1j2754/v2.ScratchText/wiki)

## Setup:
- Set up offline editor path (should be an .exe file, either turbowarp or scratch). This is done by changing the file path specified in `references/secrets.txt` next to `Program=`
- Edit and make code within a file such as `/scripts/code.scrtxt`. The `.scrtxt` or `.scratchtext` file extension is not necessary, but is required for the [vscode syntax coloring extension](https://github.com/B1j2754/syntax-scratchtext)
- Run using `run.py`, and changing the file path to your script. If everything is set up correctly, it will generate your project in `generated_projects/program.sb3` and open it up.

## Example syntax:
<span style="color:#9966FF">**say(**</span><span style="color:#d60b37">**"Check out the Wiki!"**</span><span style="color:#9966FF">**)**</span>\
<span style="color:#FFAB19">**if(**</span><span style="color:#59C059">**equals(**</span><span style="color:#5CB1D6">**mouse()**</span>, <span style="color:#d60b37">**"true"**</span><span style="color:#59C059">**)**</span><span style="color:#FFAB19">**) {**</span>\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#FF8C1A">**set($mouse_down**</span>, <span style="color:#d60b37">**1**</span><span style="color:#FF8C1A">**)**</span>\
<span style="color:#FFAB19">**}**</span>

## Changelog:
12/13/2024 - Release
12/14/2024 - Completed README.md

## TODO:
- Add custom block support
- Create custom return function for custom blocks (since this is an interpreted language)
- Create packages system to allow others to easily share and use functions from others in their projects
