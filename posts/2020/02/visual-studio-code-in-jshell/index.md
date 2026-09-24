---
title: "Set Visual Studio Code as default editor in jshell"
date: 2020-02-03T21:45:00.001+01:00
updated: 2020-02-03T21:45:46.001+01:00
author: "Rafał Borowiec"
tags: ["java", "tools"]
original_url: https://blog.codeleak.pl/2020/02/visual-studio-code-in-jshell.html
---

# Set Visual Studio Code as default editor in jshell

Java Shell (*jshell*) is an interactive tool for learning and prototyping in Java. It was introduced with Java 9 and since then I use it ocassionally either for some quick prototyping, during presentations or simply to verify new features in the Java language. Since *jshell* is a command line tool (with basic intellisense) editing files in *jshell* is not the best expierience. Fortunatelly, *jshell* allows changing the default editor and set it to the one of your choice, including *Visual Studio Code*, *Atom* or *Sublime*.

My primary and favorite IDE is IntelliJ it is pretty havy for some really basic source code editing and its built-in support for *jshell* is far from perfect. So why not to set *Visual Studio Code* as a default *jshell* editor?

### Set editor for the current *jshell* session

Open jshell in the terminal

```
$ jshell
```

Run *jshell* command

```
jshell> /set editor /usr/local/bin/code -w
|  Editor set to: /usr/local/bin/code -w
```

The `-w` option sets waiting for the file to be closed before returning.

Now you can edit the current session by running the `edit` command:

```
jshell> /edit
```

This will open *Visual Studio Code* (it opens new tab if you have *VSC* opened). You can edit the file and once you are done with editing save and close the file.

### Set editor and retain the setting between *jshell* sessions

If you want to retain the setting between *jshell* sessions you need to add `retain` flag while setting the editor:

```
jshell> /set editor -retain /usr/local/bin/code -w
|  Editor set to: /usr/local/bin/code -w
|  Editor setting retained: /usr/local/bin/code -w
```

> Learn about the tools I use on macOS in this post: [macOS: essential tools for (Java) developer]](../../../2020/01/macos-essential-tools-for-java-developer/index.md)

The solution presented here will also work for *Atom* or any other editor with the option to wait for the opened file to be closed before returning.

## See also

Do you want to switch Java SDKs easily so that you can play with new Java features in *jshell*? Use SDKMAN! Check this blog post and learn how to get started with SDKMAN!: [Manage multiple Java SDKs with SDKMAN! with ease](../../../2020/01/manage-multiple-java-sdks-with-sdkman/index.md)
