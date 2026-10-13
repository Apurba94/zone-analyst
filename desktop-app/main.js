// Zone Analyst for Windows: opens the bundled website/ folder in its own window.
// The site has no server code and already works from disk, so nothing runs
// here except the window itself. Links to other sites open in the browser.

const { app, BrowserWindow, nativeTheme, shell } = require("electron");
const path = require("node:path");

// Packaged: website/ is copied next to the app (see "extraResources" in
// package.json). Development (`npm start`): read it straight from the repo.
const SITE = app.isPackaged
  ? path.join(process.resourcesPath, "website")
  : path.join(__dirname, "..", "website");

function openOutside(url) {
  if (/^https?:\/\//i.test(url)) shell.openExternal(url);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 380,
    minHeight: 520,
    title: "Zone Analyst",
    icon: path.join(__dirname, "build", "icon.png"),
    // Page colours from site.css, so the window doesn't flash before it paints.
    backgroundColor: nativeTheme.shouldUseDarkColors ? "#0E1A22" : "#E9E0CC",
    autoHideMenuBar: true,
    show: false,
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false },
  });

  // The home page hides its "Get the app" section when it sees this marker.
  const wc = win.webContents;
  wc.setUserAgent(`${wc.getUserAgent()} ZoneAnalystApp/${app.getVersion()}`);

  wc.setWindowOpenHandler(({ url }) => {
    openOutside(url);
    return { action: "deny" };
  });
  wc.on("will-navigate", (event, url) => {
    if (!url.startsWith("file:")) {
      event.preventDefault();
      openOutside(url);
    }
  });

  win.once("ready-to-show", () => win.show());
  win.loadFile(path.join(SITE, "index.html"));
}

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", () => {
    const [win] = BrowserWindow.getAllWindows();
    if (win) {
      if (win.isMinimized()) win.restore();
      win.focus();
    }
  });
  app.whenReady().then(createWindow);
  app.on("window-all-closed", () => app.quit());
}
