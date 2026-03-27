Here's the refactored version, ready to paste:

---

**File Storage & Sync — Mental Models**

---

**The fundamental question: where do files actually live?**

```
Cloud only    → need internet, browser to access
Local only    → works offline, no backup
Both          → works offline + backed up ✅
```

---

**Google Drive — manual sync**

```
→ You explicitly open app and tap upload every time
→ Nothing happens automatically
→ You are in full control, nothing is magic
```

---

**Google Photos — cloud only, auto backup**

```
Takes photo on iPhone
    ↓
Google Photos app running in background
    ↓
Auto uploads to Google Cloud ✅ (this part is automatic)
    ↓
To access on laptop:
→ Open browser → photos.google.com
→ Photos live in cloud ONLY
→ NOT on laptop's local storage
→ Need internet to access them

Key insight: automatic UPLOAD but manual ACCESS
```

---

**Dropbox — local folder + cloud backup, fully automatic**

```
→ Installs a real folder on your machine
   e.g. /Users/yourname/Dropbox/

→ You save ANY file inside this folder
→ Background watcher detects change automatically
→ Uploads to cloud silently
→ Appears on all other devices automatically

To access files:
→ Just open Dropbox folder in Finder/File Explorer
→ Like any normal folder on your disk
→ No app, no browser needed
→ Works completely offline ✅

Key insight: automatic UPLOAD and automatic ACCESS
            cloud is just a silent backup
```

---

**iCloud Photos — two modes, you choose behavior**

```
Mode 1: "Optimize Storage" (default)
→ Full resolution photo lives in iCloud
→ Only small thumbnail stored on device
→ Looks like it's there but it's not fully downloaded
→ Click photo → downloads from iCloud at that moment
→ Needs internet to see full photo
→ Saves local storage space
→ Behaves like: Google Photos + thumbnail preview

Mode 2: "Download Originals"
→ Full photo stored BOTH on device AND in iCloud
→ Works completely offline ✅
→ Takes up local storage space
→ Behaves like: Dropbox
```

---

**Comparison table:**

|Product|Auto upload?|Where files live|Need internet to access?|Feels like|
|---|---|---|---|---|
|Google Drive|❌ Manual|Cloud only|Yes|Web app|
|Google Photos|✅ Yes|Cloud only|Yes|Cloud viewer|
|iCloud (Optimize)|✅ Yes|Cloud + thumbnail|Yes for full file|Hybrid|
|iCloud (Originals)|✅ Yes|Both|No|Dropbox|
|Dropbox|✅ Yes|Both always|No|Local folder + backup|

---

**One line summary per product:**

```
Google Drive   → you do everything manually
Google Photos  → uploads automatically, access via browser
iCloud         → your choice: save space or work offline
Dropbox        → magic local folder that silently backs up everything
```

---

**Key concept for Dropbox system design:**

The background service that watches for file changes is called a **File System Watcher.** It is the core component that makes automatic sync possible. Without it, Dropbox is just Google Drive.