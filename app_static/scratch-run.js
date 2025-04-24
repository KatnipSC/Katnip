function stringToDataURI(STRING, TYPE ) {
    // Convert the string to base64 using the encodeURIComponent function
    const base64String = btoa(unescape(encodeURIComponent(STRING)));
    // Construct and return the data URI
    return `data:${TYPE};base64,${base64String}`;
  }

document.addEventListener('DOMContentLoaded', function () {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@turbowarp/packager@2.0.0/dist/scaffolding/scaffolding-full.min.js';
    script.onload = () => {
        console.log('TurboWarp library loaded');
        // Initialize components
        const scaffolding_instance = new Scaffolding.Scaffolding();
        scaffolding_instance.width = 480; // Custom stage width
        scaffolding_instance.height = 360; // Custom stage height
        scaffolding_instance.resizeMode = 'preserve-ratio'; // or 'dynamic-resize' or 'stretch'
        scaffolding_instance.editableLists = false; // Affects list monitors
        scaffolding_instance.setup();
        var turboMode = false;

        scaffolding_instance.appendTo(document.getElementById('project-display')); // Link instance to div
        scaffolding_instance.renderer.setUseHighQualityRender(true);

        // Send custom event to signal loading finished
        const event = new CustomEvent("loaded", {
            detail: {},
        });
        window.dispatchEvent(event);

        // Create listener to fix audio playback
        document.addEventListener("click", function () {
            const audioContext = scaffolding_instance.audioEngine.audioContext;
            audioContext.resume().then(() => {
                console.log('Audio playback resumed');
            }).catch((error => {
                console.error('Failed to resume audio playback:', error);
            }))
        }, { once: true });

        // Define button functionality
        const sync_btn = document.getElementById('sync-btn');
        const code_textarea = document.getElementById('code_editor_AREA');
        sync_btn.addEventListener('click', function () {
            console.log('sync-btn clicked');
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain' // Indicate the type of content being sent (plaintext)
                },
                body: code_textarea.value, // Send 'code' in 'body' as plaintext
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json(); // Parse the JSON response
                })
                .then(data => {
                    const proj_id = data.proj_id // Get id of generated .sb3 project

                    fetch(`/projects/${proj_id}`)
                        .then(response => {
                            if(!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.arrayBuffer(); // Get file's arrayBuffer
                        })
                        .then(arrayBuffer => {
                            scaffolding_instance.loadProject(arrayBuffer)
                            .then(() => {
                                console.log('Project loaded successfully');
                            })
                        })
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        const start_btn = document.getElementById('start-btn');
        start_btn.addEventListener('click', function () {
            scaffolding_instance.greenFlag();
        });

        const stop_btn = document.getElementById('stop-btn');
        stop_btn.addEventListener('click', function () {
            scaffolding_instance.stopAll();
        });

        const download_btn = document.getElementById('download-btn');
        download_btn.addEventListener('click', function () {
            fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain' // Indicate the type of content being sent (plaintext)
                },
                body: code_textarea.value, // Send 'code' in 'body' as plaintext
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json(); // Parse the JSON response
                })
                .then(data => {
                    const proj_id = data.proj_id // Get id of generated .sb3 project
                    window.location.href = `/download/${proj_id}`; // Redirect to download url
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        const rocket_btn = document.getElementById('rocket-btn');
        rocket_btn.addEventListener('click', function () {
            scaffolding_instance.vm.setTurboMode(!turboMode);
            turboMode = !turboMode
        });
    };
    script.onerror = () => {
        console.error('Failed to load TurboWarp library');
    };
    document.head.appendChild(script);
});

/* 
// Press the green flag (like Scratch's green flag button)
scaffolding.greenFlag();

// Stop all (like Scratch's stop sign button)
scaffolding.stopAll();

// Turbo Mode
scaffolding.vm.setTurboMode(true);

// Framerate
scaffolding.vm.setFramerate(60);

// Interpolation
scaffolding.vm.setInterpolation(true);

// High quality pen
scaffolding.renderer.setUseHighQualityRender(true);

// Turn off the compiler
scaffolding.vm.setRuntimeOptions({enabled: false});

// Infinite clones, Remove miscellaneous limits, Remove fencing
scaffolding.vm.setRuntimeOptions({fencing: false, miscLimits: false, maxClones: Infinity});

// Load custom extension
// Do this before calling loadProject() for best results.
scaffolding.vm.extensionManager.loadExtensionURL('https://extensions.turbowarp.org/fetch.js');

// Do something when the project stops
vm.runtime.on('PROJECT_RUN_STOP', () => {
  // ...
});


// Add project settings with setting for "willReadFrequently" canvas attribute
*/