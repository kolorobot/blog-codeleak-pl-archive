---
title: "Manage multiple Java SDKs with asdf with ease"
date: 2023-01-01T23:58:00.004+01:00
updated: 2023-09-21T21:42:27.097+02:00
author: "Rafał Borowiec"
tags: ["javascript", "tools", "typescript"]
original_url: https://blog.codeleak.pl/2023/01/manage-multiple-java-sdks-with-asdf.html
---

# Manage multiple Java SDKs with asdf with ease

`asdf` is a helpful command-line tool that allows you to manage and switch between different versions of programming language runtimes including `Java`, `Kotlin`, `Node.js`, `Python` and their associated packages and libraries including `Gradle`, `Maven`, `Yarn`, `Spring Boot CLI`.

`asdf` is supported for all major operating systems including Windows via [Windows Subsystem for Linux 2 (WSL2)](https://asdf-vm.com/more/faq.html).

Depending on your setup (OS, shell and installation method) you need to perform several steps in order to make sure `asdf` works correctly. Consult the documentation for more details: <https://asdf-vm.com/guide/getting-started.html>.

I work on macOS with `Iterm2` and `oh-my-zsh`, so the setup was to install `asdf` with `Homebrew` (`brew install asdf`) and then to install `asdf` for `oh-my-zsh` (<https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/asdf>)

# Install and manage Java versions

Once you have `asdf` installed, you can use the following steps to install and manage `Java` versions:

- Add the `Java` plugin to `asdf` by running: `asdf plugin add java`.
- List all available `Java` versions by running: `asdf list all java`. *Tip:* Pipe the command with `grep` if you are looking for specific runtime.
- Use the `asdf install` command to install a specific `Java` version. For example, to install `GraalVM` with `Java 19` support, you would run `asdf install java graalvm-22.3.0+java19`:

```
➜  ~ asdf install java graalvm-22.3.0+java19
###################### 100.0%
graalvm-ce-java19-darwin-amd64-22.3.0.tar.gz
graalvm-ce-java19-darwin-amd64-22.3.0.tar.gz: OK
```

- Use the `asdf global` command to set the default version of `Java` to use on your machine. For example, to set previously installed version as the default version, you would run `asdf global graalvm-22.3.0+java19`:

```
➜  ~ asdf global java graalvm-22.3.0+java19
➜  ~ java -version
openjdk version "19.0.1" 2022-10-18
OpenJDK Runtime Environment GraalVM CE 22.3.0 (build 19.0.1+10-jvmci-22.3-b08)
OpenJDK 64-Bit Server VM GraalVM CE 22.3.0 (build 19.0.1+10-jvmci-22.3-b08, mixed mode, sharing)
```

Global defaults are managed in `$HOME/.tool-versions` file:

```
➜  ~ tail $HOME/.tool-versions
java graalvm-22.3.0+java19
```

In contrary, when you want to use version specific to a directory you would use `asdf local` command which creates `$PWD/.tool-versions` file. Now, each you navigate to that directory, `asdf` picks the versions and set them properly for this directory only.

> Note: To set `JAVA_HOME` environment variable during shell initialization you need to add `. ~/.asdf/plugins/java/set-java-home.zsh` to your shell configuration file (e.g. `~/.zshrc`).

# Install other tools

There are many language runtimes and tools you can manage with `asdf`. The process is as follows:

- You look for the plugin (e.g. `asdf plugin list all | grep gradle`)
- You add the plugin (e.g. `asdf plugin add gradle`)
- You find the version you want to manage (e.g. `asdf list all gradle`)
- You install the selected version of langugate runtime or tool (e.g. `asdf install gradle 7.6`)

# Alternative: SDKMAN!

Before I discovered `asdf`, I used `SDKMAN!`. `SDKMAN!` is a tool for managing parallel versions of multiple SDKs and once installed, it provides a convenient `sdk` command for installing, switching, removing and listing installed SDKs. Learn more about it from my blog post: [Manage multiple Java SDKs with SDKMAN! with ease](../../../2020/01/manage-multiple-java-sdks-with-sdkman/index.md)

# Links

- [asdf](https://asdf-vm.com)
- [macOS: Essential tools for (Java) developer](../../../2020/01/macos-essential-tools-for-java-developer/index.md)
