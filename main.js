const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const youtubedl = require('youtube-dl-exec');
const fs = require('fs');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 780,
    height: 740,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

let currentProcess = null;

ipcMain.handle('select-folder', async (event, currentPath) => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory'],
    defaultPath: currentPath || app.getPath('downloads')
  });
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

ipcMain.handle('start-download', async (event, data) => {
  const { url, downloadPath, format, resolution, startVideo, endVideo } = data;
  
  let args = {
    noWarnings: true,
    noCallHome: true,
    noCheckCertificate: true,
    youtubeSkipDashManifest: true,
    paths: downloadPath,
    output: '%(playlist_index)s - %(title)s.%(ext)s'
  };

  if (startVideo) args.playlistStart = parseInt(startVideo, 10);
  if (endVideo) args.playlistEnd = parseInt(endVideo, 10);

  if (format === 'MP3') {
    args.extractAudio = true;
    args.audioFormat = 'mp3';
  } else {
    let resStr = 'bestvideo+bestaudio/best';
    if (resolution !== 'Highest') {
        const height = resolution.replace('p', '');
        resStr = `bestvideo[height<=${height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best`;
    }
    args.format = resStr;
    args.mergeOutputFormat = 'mp4';
  }

  currentProcess = youtubedl.exec(url, args);

  currentProcess.stdout.on('data', (d) => {
    event.sender.send('download-progress', d.toString());
  });

  currentProcess.stderr.on('data', (d) => {
     event.sender.send('download-progress', d.toString());
  });

  try {
    await currentProcess;
    return { success: true };
  } catch (error) {
    if (error.message && error.message.includes('SIGKILL') || error.message.includes('SIGTERM')) {
       return { success: false, cancelled: true };
    }
    return { success: false, error: error.message };
  } finally {
    currentProcess = null;
  }
});

ipcMain.handle('cancel-download', async () => {
  if (currentProcess) {
    currentProcess.kill('SIGKILL');
  }
});

ipcMain.handle('get-default-path', () => {
  return app.getPath('downloads');
});
