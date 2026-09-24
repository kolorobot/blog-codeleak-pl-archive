---
title: "macOS: sync files between two volumes using launchd and rsync"
date: 2020-05-06T23:54:00.002+02:00
updated: 2020-05-07T07:43:56.002+02:00
author: "Rafał Borowiec"
tags: ["macOS", "tools"]
original_url: https://blog.codeleak.pl/2020/05/macos-sync-files-between-two-volumes.html
---

# macOS: sync files between two volumes using launchd and rsync

Backing up and syncing files and directories between drives is pretty common use case for many users. In this quick tutorial you will learn how to use *launchd* and *rsync* to synchronize files between different volumnes in macOS.

# Problem

Synchronize a (KeePass) file between two drives in macOS in both directions.

# Solution

- Watch for file changes in both locations
- Synchronize the file between locations and update only if the source file is newer than the destination file

# Implementation

## Watch for file changes with `launchd`

The easiest way to watch for a file or directory for a change is by using *launchd*. *launchd* is a macOS service for starting, stopping and managing daemons, applications, processes, and scripts. *launchd* uses property list (*plist*) files to configure how the program is to be run. In this scenario we want to run the program whenever the file or directory changes.

The configuration is as follows:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>file.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/kolorobot/.scripts/file.sync.sh</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Volumes/Kolorodisk/My Files/KeePass/my-db.kdbx</string>
        <string>/Users/kolorobot/KeePass/my-db.kdbx</string>
    </array>
    <key>StandardErrorPath</key>
    <string>/tmp/file.sync.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/file.sync.out</string>
</dict>
</plist>
```

The above configuration can be read as follows:

- The name of the of the job is `file.sync`
- The program to be run is `/Users/kolorobot/.scripts/file.sync.sh`
- The program is to be run when there are changes to two files:
  - `/Volumes/Kolorodisk/My Files/KeePass/my-db.kdbx`
  - `/Users/kolorobot/KeePass/my-db.kdbx`
- Standard output is redirected to `/tmp/file.sync.out`
- Standard error is redirected to `/tmp/file.sync.err`

> Note no escape character is used in path with `spacebar`

## Executed the job on behalf of the currently logged in user

*launchd* can execute jobs as a system user or a currently logged in user. We will use the second scenario and for that:

- Store the file in `~/Library/LaunchAgents/file.sync.plist`
- In terminal, execute `launchctl load -w ~/Library/LaunchAgents/file.sync.plist` to load the definition.

> To unload the definition run: `launchctl unload -w ~/Library/LaunchAgents/file.sync.plist`

## Syncing the files

To sync the files we will use `rsync` but it will be launched via previously mentioned `file.sync.sh`

The contents of this file:

```bash
#!/bin/sh
SRC="/Volumes/Kolorodisk/My Files/KeePass/my-db.kdbx"
DST="/Users/kolorobot/KeePass/my-db.kdbx"

if [ -d  /Volumes/Kolorodisk ]
then
    echo "---- Sync ----"
    rsync -rtuv "$SRC" "$DST"
    rsync -rtuv "$DST" "$SRC"
    /usr/bin/osascript -e 'display notification "File sync complete!" with title "Sync"'
fi
```

- In `~/.scripts` create `file.sync.sh` and make it executable
- Paste the above contents and verify the script is working by executing it

What does the script do?

- It checks if the external drive is mounted
- It synchronizes the file in **both directions** using *rsync*. The file is only copied if the *source* is newer than *destination*
- It displays the system notification

## Full Disk Access for `bin/sh`

With macOS Catalina launch daemons and launch agents introduce new user privacy protections (<https://developer.apple.com/documentation/macos_release_notes/macos_catalina_10_15_release_notes>) and to keep it short, programs run by *launchd* need to be granted access to the external drive. If not done properly, you may see the following error:

```
sync: send_files failed to open "/Volumes/Kolorodisk/My Files/KeePass/my-db.kdbx": Operation not permitted (1)
rsync error: some files could not be transferred (code 23) at /BuildRoot/Library/Caches/com.apple.xbs/Sources/rsync/rsync-54/rsync/main.c(996) [sender=2.6.9]
```

The easiest way to fix this is by giving `bin/sh` **Full Disk Access** in `System Preferences > Security & Privacy > Privacy > Full Disk Access`.

## Test the solution

When all is setup, you can test the solution by making changes to the synchronized files.

# See also

- [macOS: essential tools for (Java) developer](../../../2020/01/macos-essential-tools-for-java-developer/index.md)
