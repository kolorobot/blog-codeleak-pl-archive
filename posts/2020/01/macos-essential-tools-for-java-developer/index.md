---
title: "macOS: essential tools for a developer in 2024"
date: 2020-01-05T14:07:00.017+01:00
updated: 2024-07-02T23:09:33.641+02:00
author: "Rafał Borowiec"
tags: ["macOS", "tools"]
original_url: https://blog.codeleak.pl/2020/01/macos-essential-tools-for-java-developer.html
---

# macOS: essential tools for a developer in 2024

Are you considering macOS as your next operating system? Are switching from **Windows** to **macOS**? Do you want to develop in `Java` on **macOS**? Or maybe you are looking for tools to help you to be more productive?

Read about tools that are essential to me (after switching from **Windows** to **macOS**).

> *2023-02* - `Powerlevel10k`, `bat`, `fzf` and zsh syntax highlighting and autosuggestions added. Removed standard tools, tools I don't use anymore or tools that are specific to my workplace. I also reorganized the post a bit.

# Table of contents

- [Table of contents](#table-of-contents)
- [Development](#development)
  - [Homebrew](#homebrew)
  - [iTerm2](#iterm2)
  - [oh-my-zsh](#oh-my-zsh)
  - [Powerlevel10k](#powerlevel10k)
  - [Zsh syntax highlighting and autosuggestions](#zsh-syntax-highlighting-and-autosuggestions)
  - [Fuzzy Finder](#fuzzy-finder)
  - [tldr](#tldr)
  - [asdf](#asdf)
  - [SDKMAN!](#sdkman)
  - [bat](#bat)
  - [Git](#git)
  - [Docker](#docker)
  - [Colima](#colima)
  - [HTTPie](#httpie)
  - [Postman](#postman)
- [Editors and IDEs](#editors-and-ides)
  - [IntelliJ](#intellij)
  - [Visual Studio Code](#visual-studio-code)
- [Utilities](#utilities)
  - [Raycast](#raycast)
  - [Cheatsheet](#cheatsheet)
  - [Magnet](#magnet)
  - [CleanShotX](#cleanshotx)
  - [Macs Fan Control](#macs-fan-control)
  - [SoundSource](#soundsource)
  - [AppCleaner](#appcleaner)
  - [Google Drive](#google-drive)
  - [Cyberduck](#cyberduck)
  - [KeePassXC](#keepassxc)
  - [Choosy](#choosy)

# Development

## Homebrew

For managing the tools on macOS you should use the package manager. The package manager eliminates the need of manual software management and lets you install, configure, update and uninstall the tools you will need for your work. All is done using Command Line Interface and it works for both command line and GUI tools.

The most common package manager for macOS is [*Homebrew*](https://www.google.com/search?client=safari&rls=en&q=homebrew&ie=UTF-8&oe=UTF-8). Once installed, *Homebrew* provides the `brew` command.

*Homebrew* packages ([*Formulae*](https://formulae.brew.sh/formula/)) can be searched with `brew search`, installed with `brew install`, upgraded with `brew upgrade`, removed with `brew uninstall`.

*Homebrew* comes with a *Cask* extension, available with `brew cask` command, that provides the same workflow but for the management of macOS applications with graphical user interface. With *Cask* you can install tools like *IntelliJ*, *Atom*, *Postman* etc. *Casks* can be searched with `brew search` command, installed with `brew cask install`, upgraded with `brew upgrade` and upgraded with `brew uninstall`.

Links:

- <https://brew.sh>

> Note: The Homebrew package manager may be used on Linux and Windows Subsystem for Linux (WSL). See the documentation for more details.

## iTerm2

A terminal emulator, that lets you run commands using the command line interface (CLI), is an indispensable element of the environment on Unix systems. The macOS built-in terminal has too little to offer, so in order to improve your work I recommend replacing it with the open-source *iTerm2*.

*iTerm2* supports features like split panes, window transparency, hotkey window, full-screen mode, and Growl notifications.

It can perform "smart selection" to highlight URLs, email addresses, filenames, and more. It provides advanced ways of working with the text including copy & paste and search.

And what is most important *iTerm2* is fully configurable so it can be adjusted to the needs of more demanding proffessionals.

iTerm2 can be installed with *Homebrew*:

```
brew cask install iterm2
```

Links:

- <https://iterm2.com>

Usefull settings:

- Unmark the following option: `Settings > Profile > Terminal > Shell Integration > Show mark indicators`
- Change key mappings to natural: `Settings > Profile > Keys > Key Mappings` and choose `Natural Text Editing` preset.

## oh-my-zsh

Oh My Zsh is an open source framework for managing your `zsh` configuration. You can install `oh-my-zsh` with the following command:

```
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

> Note: `oh-my-zsh` works fine with iTerm2 as well as default macOS Terminal app (as of macOS 10.15 Catalina `zsh` is a default shell for Terminal app).

Links:

- <https://ohmyz.sh>
- [Plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins)
- [Cheatsheet](https://github.com/ohmyzsh/ohmyzsh/wiki/Cheatsheet)

## Powerlevel10k

[Powerlevel10k](https://github.com/romkatv/powerlevel10k) is a theme for Zsh. It emphasizes speed, flexibility and out-of-the-box experience. If you want your terminal expierience to be as smooth as possible, you should try this theme. It works well with `iterm2`, but also `Visual Studio Code` and `IntelliJ`as well as built-in macOS Terminal app.

Tips for consistent look and feel across different terminals:

- Install `Meslo Nerd Font` font in macOS so it can be used with any app
- Configure `IntelliJ` terminal font to use `Meslo Nerd Font` (`Preferences > Editor > Color Scheme > Console Font`)
- Configure `Visual Studio Code` terminal font to use `Meslo Nerd Font` (`Preferences > Settings > Terminal > Integrated: Font Family`)
- Configure `Terminal` font to use `Meslo Nerd Font` (`Preferences > Profiles > Text > Font`)

> More information: <https://github.com/romkatv/powerlevel10k/blob/master/font.md>

To reconfigure the theme, run `p10k configure` in the terminal.

## Zsh syntax highlighting and autosuggestions

There are two additional plugins I find useful that I use with `oh-my-zsh`:

- `zsh-syntax-highlighting` is a plugin for `zsh` that provides syntax highlighting for your shell.
- `zsh-autosuggestions` provides autocompletion for commands and their options.

Both can be installed with `brew`:

```
brew install zsh-syntax-highlighting    
brew install zsh-autosuggestions
```

Once installed, don't forget to active them in your `~/.zshrc` file:

```
source /usr/local/share/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

> Note: Although both tools can be installed as `oh-my-zsh` plugins, I have found out that they work better when installed with `brew` (the issue was with colors not being displayed correctly).

Links:

- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting)
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)

## Fuzzy Finder

Fuzzy Finder (`fzf`) is a command-line fuzzy finder. It can be used with any list: files, command history, processes, hostnames, bookmarks, git commits, etc. It is a general-purpose command-line tool that helps you find things in files and commands.

`fzf` can be installed with `brew`:

```
brew install fzf
```

My main use cases with `fzf`:

- Search history - `Ctrl + R` - it is just awesome!
- Search files - `Ctrl + T` or `fzf`
- Search in files - `bat <FILE> | fzf`

Follow the documentation to configure `fzf`.

Links:

- [fzf](https://github.com/junegunn/fzf)

## tldr

`tldr` is a small utility that is providing useful examples for particular commands. Instead of using `man` or googling for examples `tldr` can be used:

```bash
➜ tldr find

find

Find files or directories under the given directory tree, recursively.
More information: <https://manned.org/find>.

- Find files by extension:
    find root_path -name '*.ext'

- Find files matching multiple path/name patterns:
    find root_path -path '**/path/**/*.ext' -or -name '*pattern*'

[...]
```

## asdf

*asdf* is a tool for managing parallel versions of language runtimes like `Java`, `Python`, `Node.js` and tools inclduing, `Gradle`, `yarn` and much more. Once installed, it provides a convienient `asdf` command for installing, swiching, removing and listing versions of installed languages and tools.

My must-have runtimes managed with `asdf`:

- Java
- Python
- Node.js
- Bun
- yarn
- Gradle
- Maven

One of the useful features is to have seperate `.tool-versions` file for different projects` directories.

Links:

- [asdf](https://asdf-vm.com)
- [asdf plugins](https://github.com/asdf-vm/asdf-plugins)

> On this blog: [Manage multiple Java SDKs with asdf with ease](../../../2023/01/manage-multiple-java-sdks-with-asdf/index.md)

## SDKMAN!

Before I discovered `asdf`, I used *SDKMAN!* a lot. *SDKMAN!* is a tool for managing parallel versions of multiple Software Development Kits called *Candidates*. Once installed, it provides a convenient `sdk` command for installing, switching, removing and listing SDKs.

The tool is especially useful for Java developers as it supports SDKs for the JVM such as Java, Groovy, Scala, Kotlin and Ceylon. Gradle, Maven, Spring Boot and many others are also supported.

Install *SDKMAN!* with the following command:

```
curl -s "https://get.sdkman.io" | bash
```

> On this blog: [Manage multiple Java SDKs with SDKMAN! with ease](../../../2020/01/manage-multiple-java-sdks-with-sdkman/index.md)

## bat

*bat* is a `cat` clone with syntax highlighting and Git integration. It is a drop-in replacement for `cat` and supports the same flags.

```
brew install bat
```

## Git

*Git* is a distributed version control system, loved because to its high performance, simple structure and strong branching support. In the recent years *Git* was popularized mainly by services such as GitHub, BitBucket or GitLab, where most open source projects can be found today. *Git* is a must-have tool.

*Git* can be installed with *Homebrew*:

```
brew install git
```

Links:

- <https://git-scm.com>

## Docker

Docker is an OS-level virtualization that is build around the idea of containers. Containers allow a developer to package up an application with all the software it needs and ship it as a single package.

Docker is natively supported by macOS and can be installed with *Homebrew*:

```
brew cask install docker
```

> Note: In order to use `docker` command you must start *Docker* app.

Links:

- <https://docs.docker.com/docker-for-mac/>
- <https://docs.docker.com/get-started/>

## Colima

Colima is a container runtimes on macOS supporing Docker hence it can be used as a replacement for Docker Desktop:

```bash
➜ docker ps
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
➜ colima start
INFO[0000] starting colima
INFO[0000] runtime: docker
INFO[0000] preparing network ...                         context=vm
INFO[0000] creating and starting ...                     context=vm
INFO[0065] provisioning ...                              context=docker
INFO[0066] starting ...                                  context=docker
INFO[0071] done
➜ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

```
brew install colima
```

- <https://github.com/abiosoft/colima>

## HTTPie

*HTTPie* is a client-side implementation of the HTTP protocol that is an alternative to *cURL*. Once installed, it provides `http` command that can be used to execute HTTP requests. If *cURL* is to heavy to you you should consider checking *httpie*.

Why I like it?

- Easy to use and rememberable options, expressed more naturally
- Syntax highlighting
- Easy working with JSON inputs

Examples (via `tldr`):

```bash
➜ tldr http

http

HTTPie: HTTP client, aims to be easier to use than cURL.
More information: <https://httpie.org>.

- Download a URL to a file:
    http --download example.org

- Send form-encoded data:
    http --form example.org name='bob' profile_picture@'bob.png'

- Send JSON object:
    http example.org name='bob'

- Specify an HTTP method:
    http HEAD example.org

- Include an extra header:
    http example.org X-MyHeader:123

- Pass a username and password for server authentication:
    http --auth username:password example.org

- Specify raw request body via stdin:
    cat data.txt | http PUT example.org
```

*HTTPie* can be installed with *Homebrew*:

```
brew install httpie
```

Links:

- <https://httpie.org>

## Postman

*Postman* gained a lot of popularity in the past years, starting as an Chrome extension, today it is a powerful app used by many developers. A must have tool in my toolbox.

*Postman* can be installed with *Homebrew*:

```
brew install postman
```

Links:

- <https://www.getpostman.com>

Links:

- <https://yarnpkg.com>

# Editors and IDEs

## IntelliJ

IntelliJ is my default Java IDE. It gives me an extensive editor with syntax highlighting, code analysis and error detection. I like its ergonomic user interface, with advanced search functions and keyboard shortcuts support.

IntelliJ is available in two versions: *Ultimate* (commercial) and *Community* (open-source). The *Community* version is completely sufficient for projects that do not use frameworks and technologies for enterprise-class applications.

You can install *IntelliJ Ultimate* with *Homebrew*:

```
brew install intellij-idea
```

Links:

- <https://www.jetbrains.com/idea/>

> Tip: While switching from Windows I started using IntelliJ with suggested macOS keymap. I recommend doing the same. The shortcuts are optimized for macOS and once you get more productive on macOS itself you will also notice an improvement in IntelliJ.

## Visual Studio Code

For basic source code editing and viewing I use *Visual Studio Code*. *VSC* comes with built-in support for web technologies like HTML, XML, JavaScript and can be easily extended to support many other languages such as Markdown, Python, PHP, Go or even Java.

One of the first extensions I installed was *IntelliJ IDEA Keybindings*. With this extension *VSC* feels a bit like IntelliJ and I don't need to learn all the new shortcuts (I use *VSC* much less than IntelliJ).

*Visual Studio Code* can be installed with *Homebrew*:

```
brew install visual-studio-code
```

Links:

- <https://code.visualstudio.com>

# Utilities

## Raycast

For developers looking to optimize their workflow on macOS, Raycast is an indispensable tool.
Acting as a powerful, extendable launcher, Raycast provides quick access to a plethora of productivity tools directly from your keyboard.

You can manage tasks, run scripts, and integrate seamlessly with popular services like Jira, GitHub, and OpenAI. Raycast’s customizable extensions and commands help automate repetitive tasks, ensuring you never waste a moment.

This makes it an excellent addition to any developer’s toolkit.

Links:

- <https://www.raycast.com>

## Cheatsheet

Cheatsheet is a little utility app to support you in learning essential shortcuts on macOS. When I switched to macOS I needed to quickly learn so many new shortcuts ...:

*"Just hold the ⌘-Key a bit longer to get a list of all active short cuts of the current application. It's as simple as that."*

Cheatsheet can be installed with *Homebrew*:

```
brew install cheatsheet
```

- <https://www.mediaatelier.com/CheatSheet>

## Magnet

Magnet is a commercial window manager for macOS. Activated by dragging or with customizable keyboard shortcuts helps organizing windows. For me personally, this is a must have tool.

Links:

- <https://magnet.crowdcafe.com>

> Note: Alternatively you may consider using a free [*Rectangle* app](https://rectangleapp.com), actively maintained and open source window management app. Install with brew: `brew cask install rectangle`. Documentation of the project can be found on [Github](https://github.com/rxhanson/Rectangle).

> Raycast: If you decided to install Raycast (highly recommended), it provides built-in window management features via `Window Management` extension.

## CleanShotX

CleanShotX (commercial) is a powerfull screen capturing app (screenshots and screen recording) packed with many useful features like quick access to the screenshots, annotate tool, scrolling capture or screen recording. Many features can be accessed quickly with configurable keyboard shortcuts.

- <https://cleanshot.com>

## Macs Fan Control

Especially useful for those with Intel-based MacBooks.

- <https://crystalidea.com/macs-fan-control>

  brew install macs-fan-control

## SoundSource

SoundSource is a commercial utility that serves as great sound control for my Mac. The features I use and love are advanced audio effects and per-application sound control like sound redirection.

- <https://rogueamoeba.com/soundsource/>

## AppCleaner

AppCleaner is a small GUI tool which allows uninstall unwanted apps (i.e. apps installed without *Homebrew*) by removing all the files spread around the system. It is also useful when you want to see what files and directories are created by a selected application.

AppCleaner can be installed with *Homebrew*:

```
brew install appcleaner
```

Links:

- [AppCleaner](https://freemacsoft.net/appcleaner/)

## Google Drive

Install Google Drive to sync with your computer.

```
brew install google-drive
```

Links:

- [Backup and Sync](https://www.google.com/intl/en-GB_ALL/drive/download/backup-and-sync/)

## Cyberduck

*Cyberduck* is open-source GUI client for FTP and SFTP, WebDAV. It also supports cloud storage like Amazon S3 or Google Drive. I investigated several tools but I did not find any supporting so many protocols and cloud storages and still being free.

*Cyberduck* can be installed with *Homebrew*:

```
brew install cyberduck
```

Links:

- <https://cyberduck.io>

## KeePassXC

I use *KeePass* for years and the best client for macOS for me is *KeePassXC*. The tool provides pretty convienient UI and supports keyboard shortcuts I need. If you are looking for *KeePass* client for macOS, you should consider *KeePassXC*.

*KeePassXC* can be installed with *Homebrew*:

```
brew install keepassxc
```

Links:

- <https://keepassxc.org>

## Choosy

Choosy can prompt you to select from the browsers for a particular link. For me this is an essential tool, as I use several browsers on a daily basis (`Safari` - for private browsing, `Chrome` - at my workplace, `Edge` - more and more often and occasionally `Brave`). `Choosy` support all I need in my daily workflow. It works fast and reliably also when using multiple screens. The application is not free, but you can try it with trial version.

```
brew install choosy
```

Links:

- <https://www.choosyosx.com>
