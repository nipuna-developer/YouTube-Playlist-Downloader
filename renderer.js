const { ipcRenderer } = require('electron');

const urlInput = document.getElementById('url');
const pathInput = document.getElementById('path');
const browseBtn = document.getElementById('browse-btn');
const formatSelect = document.getElementById('format');
const resolutionSelect = document.getElementById('resolution');
const startVideoInput = document.getElementById('start-video');
const endVideoInput = document.getElementById('end-video');
const statusText = document.getElementById('status-text');
const progressBar = document.getElementById('progress-bar');
const downloadBtn = document.getElementById('download-btn');
const cancelBtn = document.getElementById('cancel-btn');

// Initialize path
ipcRenderer.invoke('get-default-path').then(defaultPath => {
    pathInput.value = defaultPath;
});

browseBtn.addEventListener('click', async () => {
    const selectedPath = await ipcRenderer.invoke('select-folder', pathInput.value);
    if (selectedPath) {
        pathInput.value = selectedPath;
    }
});

formatSelect.addEventListener('change', () => {
    if (formatSelect.value === 'MP3') {
        resolutionSelect.disabled = true;
        resolutionSelect.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        resolutionSelect.disabled = false;
        resolutionSelect.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});

downloadBtn.addEventListener('click', async () => {
    if (!urlInput.value) {
        alert('Please enter a YouTube Playlist URL.');
        return;
    }

    statusText.innerText = 'Starting download...';
    progressBar.style.width = '0%';

    downloadBtn.disabled = true;
    downloadBtn.classList.add('opacity-50', 'cursor-not-allowed');

    cancelBtn.disabled = false;
    cancelBtn.classList.remove('opacity-50', 'cursor-not-allowed');

    const data = {
        url: urlInput.value,
        downloadPath: pathInput.value,
        format: formatSelect.value,
        resolution: resolutionSelect.value,
        startVideo: startVideoInput.value,
        endVideo: endVideoInput.value
    };

    const result = await ipcRenderer.invoke('start-download', data);

    downloadBtn.disabled = false;
    downloadBtn.classList.remove('opacity-50', 'cursor-not-allowed');

    cancelBtn.disabled = true;
    cancelBtn.classList.add('opacity-50', 'cursor-not-allowed');

    if (result.success) {
        statusText.innerText = 'Download Completed Successfully!';
        progressBar.style.width = '100%';
        setTimeout(() => { statusText.innerText = 'Ready'; progressBar.style.width = '0%'; }, 5000);
    } else if (result.cancelled) {
        statusText.innerText = 'Download Cancelled by User.';
        progressBar.style.width = '0%';
    } else {
        statusText.innerText = `Error: ${result.error}`;
    }
});

cancelBtn.addEventListener('click', () => {
    statusText.innerText = 'Cancelling...';
    cancelBtn.disabled = true;
    ipcRenderer.invoke('cancel-download');
});

ipcRenderer.on('download-progress', (event, message) => {
    const output = message.trim();
    if (output) {
        statusText.innerText = output.length > 80 ? output.substring(0, 80) + '...' : output;
        const match = output.match(/\[download\]\s+([\d\.]+)\%/);
        if (match && match[1]) {
            progressBar.style.width = `${match[1]}%`;
        }
    }
});
