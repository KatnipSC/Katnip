// Features:
// 1. Create folders
// 2. Create files within folders
// 3. Delete folders
// 4. Delete files
// 5. Toggle folder visibility (single click name or folder icon)
// 6. Double click on a folder name to rename it
const foldersDiv = document.getElementById('folders');
const createFolderBtn = document.getElementById('createFolderBtn');
var root = {name: "root",
            files: [],
            subfolders: []
        };

// Folder functions
createFolderBtn.addEventListener('click', () => {
    const folderName = prompt('Enter folder name:');
    if (folderName) {
        const folder = {
            displayName: "📂 " + folderName,
            name: folderName,
            path: String(root.subfolders.length), // This is only talking about the folders in root
            type: "folder",
            collapsed: false,
            justClicked: false,
            files: [],
            subfolders: []
        };
        root.subfolders.push(folder);
        renderFolders();
    }
});

function deleteFolder(folderPath) {
    const folder = getFolderByPath(folderPath);
    if (folder && confirm('Are you sure you want to delete this folder?')) {
        const parentFolder = getParentFolder(folderPath);
        if (parentFolder) { // Check if parentFolder is defined
            const index = parentFolder.subfolders.indexOf(folder);
            if (index !== -1) { // Ensure the folder exists in the parent's subfolders
                parentFolder.subfolders.splice(index, 1);
                renderFolders();
            }
        } else {
            console.error('Parent folder not found for path:', folderPath);
        }
    }
}

function toggleFolder(folderPath) {
    const folder = getFolderByPath(folderPath);
    if (folder) {
        folder.collapsed = !folder.collapsed;
        folder.displayName = folder.collapsed ? "📁 " + folder.name : "📂 " + folder.name;
        renderFolders();
    }
}

function folderClickHandler(folderPath) {
    const folder = getFolderByPath(folderPath);
    if (folder) {
        if (folder.justClicked) {
            folder.justClicked = false;
            const newFolderName = prompt('Enter new folder name:');
            if (newFolderName) {
                folder.name = newFolderName;
                folder.displayName = "📂 " + newFolderName;
                renderFolders();
            }
            return;
        } else {
            folder.justClicked = true;
            setTimeout(() => {
                if (folder.justClicked) {
                    folder.justClicked = false;
                    toggleFolder(folderPath);
                }
            }, 200);
        }
    }
}

function renderFolders(parentDiv = foldersDiv, folderList = folders, depth = 0) {
    if (parentDiv) parentDiv.innerHTML = '';
    folderList.forEach((folder, folderIndex) => {
        const folderDiv = document.createElement('div');
        folderDiv.className = 'folder';
        folderDiv.draggable = true;
        folderDiv.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span class="folder-name" onclick="folderClickHandler('${folder.path}')">${folder.displayName}</span>
                <div class="folder-tool-bar">
                    <span title="Create a new file within the folder" class="create-file-icon" onclick="createFile('${folder.path}')">➕</span>
                    <span title="Delete folder" class="delete-folder-icon" onclick="deleteFolder('${folder.path}')">🗑️</span>
                </div>
            </div>
            <div class="files" style="display: ${folder.collapsed ? 'none' : 'block'};" ondragover="handleDragOver(event)" ondrop="handleDrop(event, '${folder.path}')">
                ${renderFiles(folder.files, folder.path)}
            </div>
        `;
        folderDiv.addEventListener('dragstart', (event) => handleDragStart(event, "folder", folder.path));
        if (parentDiv) parentDiv.appendChild(folderDiv);
        if (folder.subfolders.length > 0 && !folder.collapsed) {
            const subfolderDiv = document.createElement('div');
            subfolderDiv.className = 'subfolders';
            renderFolders(subfolderDiv, folder.subfolders, depth + 1);
            folderDiv.appendChild(subfolderDiv);
        }
    });
}

function renderFiles(files, folderPath) {
    return files.map((file, fileIndex) => `
        <div class="file" draggable="true" ondragstart="handleDragStart(event, 'file', '${folderPath}', ${fileIndex})">
            <span class="file-name">${file.name}</span>
            <span title="Delete file" class="delete-file-icon" onclick="deleteFile('${folderPath}', ${fileIndex})">🗑️</span>
        </div>
    `).join('') || '<div>. . .</div>';
}

function createFile(folderPath) {
    const folder = getFolderByPath(folderPath);
    const fileName = prompt('Enter file name:');
    if (fileName) {
        folder.files.push({ name: fileName, type: "file" });
        renderFolders();
    }
}

function deleteFile(folderPath, fileIndex) {
    const folder = getFolderByPath(folderPath);
    if (folder && confirm('Are you sure you want to delete this file?')) {
        folder.files.splice(fileIndex, 1);
        renderFolders();
    }
}

// Drag & Drop functions
let draggedItem = null;
let draggedType = null; // "file" or "folder"
let draggedFolderPath = null;
let draggedFileIndex = null;

function handleDragStart(event, type, folderPath, fileIndex = null) {
    event.stopPropagation(); // Stop parent elements from receiving the event (i.e. folder div)
    draggedItem = type === "folder" ? getFolderByPath(folderPath) : getFolderByPath(folderPath).files[fileIndex];
    draggedType = type;
    draggedFolderPath = folderPath;
    draggedFileIndex = fileIndex;
    event.dataTransfer.effectAllowed = "move";
}

function handleDragOver(event) {
    event.preventDefault(); // Required to allow dropping
}

function handleDrop(event, targetFolderPath) {
    event.preventDefault();
    if (!draggedItem || draggedFolderPath === targetFolderPath) return; // Prevent dropping on itself
    const targetFolder = getFolderByPath(targetFolderPath);
    if (targetFolder) {
        if (draggedType === "file") {
            const sourceFolder = getFolderByPath(draggedFolderPath);
            const file = sourceFolder.files.splice(draggedFileIndex, 1)[0];
            targetFolder.files.push(file);
        } else if (draggedType === "folder") {
            const sourceFolder = getParentFolder(draggedFolderPath);
            const folderIndex = Number(draggedFolderPath.split('.').pop());
            const folder = sourceFolder?.subfolders ? sourceFolder.subfolders.splice(folderIndex, 1)[0] : sourceFolder.splice(folderIndex, 1)[0]; // If its the root directory, pull directly from it
            if (folder && !isDescendant(folder, targetFolder)) {
                targetFolder.subfolders.push(folder);
                updateFolderPaths(folder, targetFolder.path);
            } else {
                alert("Cannot move a folder into itself or its child.");
            }
        }
    } else {
        console.error('Target folder not found:', targetFolderPath);
    }
    renderFolders();
}

function updateFolderPaths(folder, parentPath) {
    folder.path = parentPath + '.' + folder.subfolders.length // If appended path is 0, to become the first child, you need to update the other children's path recursively to update their position 
    folder.subfolders.forEach((subfolder, index) => {
        updateFolderPaths(subfolder, folder.path + '.' + index);
    });
}

function isDescendant(folder, target) {
    if (!target.subfolders) return false;
    if (target.subfolders.includes(folder)) return true;
    return target.subfolders.some(sub => isDescendant(folder, sub));
}

function getFolderByPath(path) {
    const pathArray = path.split('.').map(Number);
    let currentFolder = folders[pathArray.splice(0, 1)[0]]; // First element is the root folder

    if (!currentFolder?.subfolders) return { subfolders: currentFolder}; // If the root folder is the target folder, return it directly

    for (const index of pathArray) {
        currentFolder = currentFolder.subfolders[index];
        if (!currentFolder) return undefined; // Added check for undefined
    }
    return currentFolder;
}

function getParentFolder(path) {
    const pathArray = path.split('.').map(Number);
    pathArray.pop(); // This removes the last element (the current folder)
    let currentFolder = folders;
    for (const index of pathArray) {
        currentFolder = currentFolder[index];
        if (!currentFolder) return undefined; // Added check for undefined
    }
    return currentFolder;
}

// Upload file/folder functions
const fileInput = document.getElementById('fileInput');
const fileBtn = document.getElementById('uploadFileBtn');
const folderInput = document.getElementById('folderInput');
const folderBtn = document.getElementById('uploadFolderBtn');
fileBtn.addEventListener('click', () => fileInput.click());
folderBtn.addEventListener('click', () => folderInput.click());