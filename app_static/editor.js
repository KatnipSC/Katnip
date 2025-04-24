const clean = function(text) {
    return text
    .replace(/</g, "&lt;") // Replace < with &lt;
    .replace(/>/g, "&gt;") // Replace > with &gt;
    /*
    .replace(/&/g, "&amp;") // Replace & with &amp;
    .replace(/;/g, "&#59;") // Replace ; with &#59;
    .replace(/"/g, "&quot;") // Replace " with &quot;
    .replace(/'/g, "&#39;") // Replace'with &#39;
    .replace(/\//g, "&#47;") // Replace / with &#47;
    */
}

const special_syntax_keys = { // Very specific order of precedence
    "\".*?\"": "string",
    "\\$(\\w+)": "variable",
    "\\@(\\w+)": "list",
    "#.*": "comment",
    "\\ba\\.\\w+": "my_blocks-reporter", // Matches custom reporter blocks starting with "a."
    "\\w+\\[\\w+\\]": "my_blocks-reporter", // Matches custom reporter blocks with open and closing brackets
    "\\bfn\\.(\\w+)": "my_blocks-stack", // Matches stack blocks with "fn."
    "\\bfunc\\:(\\&nbsp\\;)*\\w+": "my_blocks-hat", // Matches hat blocks with "func:"
    "\\w+\\:": "my_blocks-reporter", // [Apply after func: to avoid overlap] Matches passing in values to arguments: argname + ":" + value
    "(?<=[,(]|&nbsp;)-?\\d*\\.?\\d+": "num", // Matches numbers (.5, -.3, 9.3, -3.4, 2, etc.) following a comma, open paren, or &nbsp;
};

const syntax_keys = {
    "motion-stack": "\\b(move|turn|gotoXY|goto|glideXY|glideto|point|pointTo|changeX|setX|changeY|setY|edgeBounce|rotationStyle)\\b",
    "motion-reporter": "\\b(xPos|yPos|direction)\\b",
    "looks-stack": "\\b(timeSay|say|timeThink|think|switchCostume|nextCostume|switchBackdrop|nextBackdrop|changeSize|setSize|changeFx|setFx|clearFx|show|hide|goToLayer|changeLayer)\\b",
    "looks-reporter": "\\b(getCostume|getBackdrop|size)\\b",
    "sound-stack": "\\b(play|playWait|stopSounds|changeSoundFx|setSoundFx|clearSoundFx|changeVolume|setVolume)\\b",
    "sound-reporter": "\\b(volume)\\b",
    "events-hat": "\\b(whenFlag|whenKey|whenSpriteClicked|whenBackdropSwitch|whenGreater|whenBroadcast|whenTouching)\\b",
    "events-stack": "\\b(sendBroadcast|sendBroadcastWait)\\b",
    "control-stack": "\\b(wait|waitUntil|createClone|clearCounter|incrCounter)\\b",
    "control-c": "\\b(repeat|forever|if|ifElse|repeatUntil|while|for|allAtOnce|else)\\b",
    "control-cap": "\\b(stop|deleteClone)\\b",
    "control-hat": "\\b(whenCloneStart)\\b",
    "control-reporter": "\\b(counter)\\b",
    "sensing-reporter": "\\b(touching|touchingClr|clrTouchingClr|distanceto|answer|keypressed|mouse|mouseX|mouseY|loudness|timer|getAttribute|current|dayssince2000|username)\\b",
    "sensing-stack": "\\b(ask|setdragmode|resetTime)\\b",
    "operators-reporter": "\\b(add|subtract|multiply|divide|random|lt|equals|gt|and|or|not|join|getLetter|length|contains|mod|round|mathop)\\b",
    "variables-stack": "\\b(setvar|changevar|showvar|hidevar)\\b",
    "lists-stack": "\\b(listAdd|listDelete|listDeleteAll|listInsert|listReplace|listShow|listHide)\\b",
    "lists-reporter": "\\b(getItem|getItemNum|listLength|listContains)\\b",
    "pen-stack": "\\b(penClear|stamp|penDown|penUp|hexPen|changePen|setPen|changePenSize|setPenSize)\\b"
};

const sync = function() {
    // Find elements
    const editorElement = document.getElementById('code_editor_AREA');
    const displayElement = document.getElementById('code_editor_DISPLAY');

    // When the textarea is being edited, update scroll position
    displayElement.scrollTop = editorElement.scrollTop;
    displayElement.scrollLeft = editorElement.scrollLeft;

    // Sync text contents between elements, applying syntax highlighting in the midst
    const inputText = editorElement.value
    
    // Apply syntax highlighting (replace newlines with <br> tags so they are processed correcly)
    coloredText = applySyntax(inputText.replace(/ /g, "&nbsp;")).replace(/\n/g, "<br>");

    // Display the text
    displayElement.innerHTML  = coloredText;
}

String.prototype.replaceAt = function(index, replacement, removal_length) {
    return this.substring(0, index) + replacement + this.substring(index + removal_length);
}

// Function to stylize input text
function applySyntax(inputText) {
    let outputText = inputText;

    let placeholders = []; // keep track of placeholders actual text
    let place_id = 0; // "id" of placeholder

    // First capture names (special syntax)
    for (let [regex, className] of Object.entries(special_syntax_keys)) {
        // Create a regex from the syntax pattern with case-insensitive flag
        const pattern = new RegExp(regex, 'gi');  // 'g' for global, 'i' for case-insensitive

        // Replace matching text with <span> tags and the class name
        outputText = outputText.replace(pattern, (match) => {
            place_id++;
            const placeholder = `__PLACEHOLDER${place_id}__`
            placeholders.push({placeholder, text: match, className: className});
            return placeholder;
        });
    }

    // Loop through all the syntax keys
    for (let [className, regex] of Object.entries(syntax_keys)) {
        // Create a regex from the syntax pattern with case-insensitive flag
        const pattern = new RegExp(regex, 'gi');  // 'g' for global, 'i' for case-insensitive

        // Replace matching text with <span> tags and the class name
        outputText = outputText.replace(pattern, (match) => {
            //outputText = outputText.replaceAt(idx, `<span class="${key}">${match}</span>`, match.length)
            return `<span class="${className}">${match}</span>`;
        });
    }

    // Replace placeholders with actual text
    for (let placeholder of placeholders) {
        const text = `<span class="${placeholder.className}">${placeholder.text}</span>`;
        outputText = outputText.replaceAt(outputText.indexOf(placeholder.placeholder), text, placeholder.placeholder.length);
    }

    // Return the modified text with styled elements
    return outputText;
}

function adjustCanvasHeight() {
    // Get the canvas project display element
    const canvasElement = document.getElementsByClassName('sc-canvas')[0];
    const editor_parent = document.getElementById("editor_PARENT");

    // Set the canvas project display element to match the size of the Editor elements
    editor_parent.style.height = canvasElement.height + 'px';
}

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
            break;
        }
    }
}

function checkParenBalance(text) {
    let depth = 0;
    for (let char of text) {
        if (char === "(") {
            depth++;
        } else if (char === ")") {
            depth--;
            if (depth < 0) {
                return false;
            }
        }
    }
    return depth == 0;
}

String.prototype.nextIndexOf = function(char, index) {
    return this.substring(index).indexOf(char);
}

window.addEventListener("loaded", () => {
    // Adjust the height of the Canvas project display element to match the Editor elements
    adjustCanvasHeight(); // Update

    // Create function to sync sizes of Editor elements to the Canvas project display
    document.getElementsByTagName("body")[0].onresize = function() {
        setTimeout(adjustCanvasHeight, 100);
    }
    document.getElementsByClassName('sc-canvas')[0].onresize = function() {
        setTimeout(adjustCanvasHeight, 500);
    }
    document.addEventListener('fullscreenchange', function() {
        setTimeout(adjustCanvasHeight, 100);
    });
    // Listen for vendor-prefixed fullscreen changes for cross-browser support
    document.addEventListener('webkitfullscreenchange', function() {
        setTimeout(adjustCanvasHeight, 100);
    });

    // Select the textarea using the class "code_editor"
    const editorElement = document.getElementById('code_editor_AREA');
    const displayElement = document.getElementById('code_editor_DISPLAY');

    // Marker for autocompletion
    let autocompletionMarker = false;
    let autoCompletionChar = "";
    let autocompletionReset = false;

    if (editorElement && displayElement) {
        // Sync scroll positions of the <textarea> with the <pre> element
        editorElement.addEventListener("scroll", function() {
            displayElement.scrollTop = editorElement.scrollTop;
            displayElement.scrollLeft = editorElement.scrollLeft;
        })

        // Auto-complete: () {} "" 
        editorElement.addEventListener('keydown', (event) => {
            // Update reset marker
            if (autocompletionMarker) {
                autocompletionReset = true;
            }
            if (event.key === '(') {
                const start = editorElement.selectionStart;
                const end = editorElement.selectionEnd;
                const text = editorElement.value;
          
                editorElement.value = text.substring(0, start) + '()' + text.substring(end);
          
                // Set the cursor position between the parentheses
                editorElement.selectionStart = start + 1;
                editorElement.selectionEnd = start + 1;
          
                // Prevent the default behavior of inserting a single parenthesis
                event.preventDefault();

                // Set "auto-fill" to true to mark that if a closing parenthesis is pressed, ignore it
                autocompletionMarker = true;
                autocompletionReset = false;
                autoCompletionChar = "(";
            }
            if (event.key === ')') {
                if (autocompletionMarker && autoCompletionChar == "(") {
                    // Prevent the default behavior of inserting a single parenthesis
                    event.preventDefault();

                    // Move cursor
                    const start = editorElement.selectionStart;
                    editorElement.selectionStart = start + 1;
                    editorElement.selectionEnd = start + 1;
                }
                const currentLineIndex = editorElement.value.lastIndexOf('\n', editorElement.selectionStart - 1) + 1;
                let currentEndLine = editorElement.value.length;
                if (editorElement.value.nextIndexOf('\n', editorElement.selectionStart) !== -1) {
                    currentEndLine = editorElement.value.nextIndexOf('\n', editorElement.selectionStart) - 1;
                }
                const currentLine = editorElement.value.substring(currentLineIndex, currentEndLine);
                if (editorElement.value.charAt(editorElement.selectionStart) === ")" && checkParenBalance(currentLine)) { // If next character is a ")" and parens are balanced:
                    // Prevent the default behavior of inserting a single parenthesis
                    event.preventDefault();

                    // Move cursor
                    const start = editorElement.selectionStart;
                    editorElement.selectionStart = start + 1;
                    editorElement.selectionEnd = start + 1;
                }
            }
            if (event.key === '"') {
                if (autocompletionMarker && autoCompletionChar == '"') {
                    // Prevent the default behavior of inserting a single parenthesis
                    event.preventDefault();

                    // Move cursor
                    const start = editorElement.selectionStart;
                    editorElement.selectionStart = start + 1;
                    editorElement.selectionEnd = start + 1;
                } else {
                    const start = editorElement.selectionStart;
                    const end = editorElement.selectionEnd;
                    const text = editorElement.value;
                
                    editorElement.value = text.substring(0, start) + '""' + text.substring(end);
                
                    // Set the cursor position between the parentheses
                    editorElement.selectionStart = start + 1;
                    editorElement.selectionEnd = start + 1;
                
                    // Prevent the default behavior of inserting a single parenthesis
                    event.preventDefault();

                    // Set "auto-fill" to true to mark that if a closing parenthesis is pressed, ignore it
                    autocompletionMarker = true;
                    autocompletionReset = false;
                    autoCompletionChar = '"';
                }
            }
            if (event.key === '{') {
                const start = editorElement.selectionStart;
                const end = editorElement.selectionEnd;
                const text = editorElement.value;
            
                editorElement.value = text.substring(0, start) + '{}' + text.substring(end);
            
                // Set the cursor position between the parentheses
                editorElement.selectionStart = start + 1;
                editorElement.selectionEnd = start + 1;
            
                // Prevent the default behavior of inserting a single parenthesis
                event.preventDefault();

                // Set "auto-fill" to true to mark that if a closing parenthesis is pressed, ignore it
                autocompletionMarker = true;
                autocompletionReset = false;
                autoCompletionChar = '{';
            }
            if (event.key === 'Tab') {
                const start = editorElement.selectionStart;
                const text = editorElement.value;
            
                const spaces = "    ";
                editorElement.value = text.substring(0, start) + spaces + text.substring(editorElement.selectionEnd);
            
                editorElement.selectionStart = start + 4;
                editorElement.selectionEnd = start + 4;
            
                event.preventDefault();
            }
            if (event.key === 'Enter') {
                if (autocompletionMarker && autoCompletionChar == "{") {
                    // Get current line
                    const start = editorElement.selectionStart;
                    const currentLineIndex = editorElement.value.lastIndexOf('\n', editorElement.selectionStart - 1) + 1;
                    const currentLine = editorElement.value.substring(currentLineIndex, editorElement.selectionStart);
                    const text = editorElement.value;

                    // Capture previous indentation
                    let spaces = ""; // Preset (a.k.a. default indentation being nothing so it doesn't add "null")
                    if (currentLine.match(/^\s+/)) {
                        spaces = currentLine.match(/^\s+/)[0];
                    }
                    
                    // Edit content
                    editorElement.value = 
                        text.substring(0, start) + // Previous text
                        "\r\n" + // newline after openning "{"
                        spaces + "    \r\n" + // current indentation + extra indent + newline
                        spaces + // Current index + ending "}" character that already exists
                        text.substring(editorElement.selectionEnd); // Succeeding text

                    // Move cursor to the line with only indentation
                    // +1 for going to the next line, +spaces.length for currend indentation, +4 for 1 more indent
                    editorElement.selectionStart = start + spaces.length + 5;
                    editorElement.selectionEnd = start + spaces.length + 5;
                    
                    // Stop default even
                    event.preventDefault();
                } else {
                    // Insert current indent depth
                    const start = editorElement.selectionStart;
                    const currentLineIndex = editorElement.value.lastIndexOf('\n', editorElement.selectionStart - 1) + 1;
                    const currentLine = editorElement.value.substring(currentLineIndex, editorElement.selectionStart);
                    const text = editorElement.value;

                    // Capture previous indentation
                    let spaces = ""; // Preset (a.k.a. default indentation being nothing so it doesn't add "null")
                    if (currentLine.match(/^\s+/)) {
                        spaces = currentLine.match(/^\s+/)[0];
                    }

                    // Check to see if current line is top of a function (add 1 more indent if it is)
                    if (editorElement.value.charAt(editorElement.selectionStart - 1) == "{") {
                        spaces += "    ";
                    }

                    console.log(spaces.length)
                    // Add new line + current indentation
                    editorElement.value = 
                        text.substring(0, start) + // Previous text
                        "\r\n" + // newline after current line
                        spaces + // Current indentation
                        text.substring(editorElement.selectionEnd); // Succeeding text

                    // Update cursor position
                    // +1 for going to the next line, +spaces.length for currend indentation
                    editorElement.selectionStart = start + spaces.length + 1;
                    editorElement.selectionEnd = start + spaces.length + 1;

                    // Prevent the default behavior of inserting a new line
                    event.preventDefault();
                }
            }
            sync();
            if (autocompletionReset) {
                autocompletionReset = false;
                autocompletionMarker = false;
            }
        });

        // Display the updated text in the display area
        editorElement.addEventListener("input", function() {
            sync();
        })
    } else {
        console.error('Could not find elements with the specified IDs');
    }
});
