---
title: "Manage multiple Java SDKs with SDKMAN! with ease"
date: 2020-01-05T13:57:00.002+01:00
updated: 2023-02-09T19:40:40.218+01:00
author: "Rafał Borowiec"
tags: ["tools"]
original_url: https://blog.codeleak.pl/2020/01/manage-multiple-java-sdks-with-sdkman.html
---

# Manage multiple Java SDKs with SDKMAN! with ease

*SDKMAN!* is a convenient tool for managing parallel versions of multiple *Software Development Kits*. The tool is especially useful for Java developers as it supports SDKs for the JVM such as Java, Groovy, Scala, Kotlin and Ceylon. Gradle, Maven, Spring Boot and many others are also supported.

- [Manage Java Versions](#manage-java-versions)
- [Install Maven and Gradle](#install-maven-and-gradle)
- [Install Spring Boot CLI](#install-spring-boot-cli)
- [Links](#links)

*SDKMAN!* is supported for all major operating systems including Windows, although it is easiest to be installed on all Unix based systems.

On macOS, open a terminal and run:

```
curl -s "https://get.sdkman.io" | bash
```

Once downloaded restart the terminal session or run:

```
source "$HOME/.sdkman/bin/sdkman-init.sh"
```

> Tip: I am using *iTerm2* terminal as default. Read about tools I use on macOS in this blog post: [macOS: Essential tools for (Java) developer](#)

Once installed, *SDKMAN!* provides a convenient `sdk` command for managing SDKs, called *Candidates*. To list all available *Candidates* use `sdk list` command.

# Manage Java Versions

What I like most about *SDKMAN!* is that managing different Java versions in your operating system is a breeze. You can list, install, uninstall and set selected Java version as default with basic commands.

- To list available Java versions run:

  `sdk list java`

```
$ sdk list java
================================================================================
Available Java Versions
================================================================================
 Vendor        | Use | Version      | Dist    | Status     | Identifier
--------------------------------------------------------------------------------
 AdoptOpenJDK  |     | 13.0.1.j9    | adpt    |            | 13.0.1.j9-adpt
               |     | 13.0.1.hs    | adpt    |            | 13.0.1.hs-adpt
 GraalVM       |     | 19.3.0.r11   | grl     |            | 19.3.0.r11-grl
               |     | 19.3.0.r8    | grl     |            | 19.3.0.r8-grl
               |     | 19.3.0.2.r11 | grl     |            | 19.3.0.2.r11-grl
 Java.net      |     | 15.ea.2      | open    |            | 15.ea.2-open
               |     | 14.ea.28     | open    |            | 14.ea.28-open
               | >>> | 13.0.1       | open    | installed  | 13.0.1-open
               |     | 12.0.2       | open    | installed  | 12.0.2-open
               |     | 11.0.2       | open    |            | 11.0.2-open
               |     | 10.0.2       | open    |            | 10.0.2-open
               |     | 9.0.4        | open    |            | 9.0.4-open
================================================================================
Use the Identifier for installation:

    $ sdk install java 11.0.3.hs-adpt
================================================================================
```

- To install given version use the *Identifier*:

  `sdk install java 12.0.2-open`

The binaries of the installed Java versions can be found in the home *SDKMAN!* directory which defaults to `~/.sdkman/candidates/java`.

```
$ ls -al ~/.sdkman/candidates/java/
drwxr-xr-x  9 rafal.borowiec  staff  288 Jan  4 00:33 12.0.2-open
drwxr-xr-x  9 rafal.borowiec  staff  288 Oct  6 14:05 13.0.1-open
lrwxr-xr-x  1 rafal.borowiec  staff   57 Jan  4 00:20 current -> /Users/rafal.borowiec/.sdkman/candidates/java/13.0.1-open
```

This can be useful if you want to use multiple versions in your projects in IntelliJ, for example.

- To set given version as default run:

  `sdk default java 12.0.2-open`:

We can quickly verify how how easy is to change the version with `sdk default` command:

```
$ java -version
openjdk version "13.0.1" 2019-10-15
OpenJDK Runtime Environment (build 13.0.1+9)
OpenJDK 64-Bit Server VM (build 13.0.1+9, mixed mode, sharing)

$ ls -al ~/.sdkman/candidates/java/
drwxr-xr-x  9 rafal.borowiec  staff  288 Jan  4 00:33 12.0.2-open
drwxr-xr-x  9 rafal.borowiec  staff  288 Oct  6 14:05 13.0.1-open
lrwxr-xr-x  1 rafal.borowiec  staff   57 Jan  4 00:20 current -> /Users/rafal.borowiec/.sdkman/candidates/java/13.0.1-open

$ sdk default java 12.0.2-open
Default java version set to 12.0.2-open

$ java -version
openjdk version "12.0.2" 2019-07-16
OpenJDK Runtime Environment (build 12.0.2+10)
OpenJDK 64-Bit Server VM (build 12.0.2+10, mixed mode, sharing)

$ ls -al ~/.sdkman/candidates/java/
drwxr-xr-x  9 rafal.borowiec  staff  288 Jan  4 00:33 12.0.2-open
drwxr-xr-x  9 rafal.borowiec  staff  288 Oct  6 14:05 13.0.1-open
lrwxr-xr-x  1 rafal.borowiec  staff   57 Jan  5 11:49 current -> /Users/rafal.borowiec/.sdkman/candidates/java/12.0.2-open
```

- To use given version in the current terminal session run:

  `sdk use java 12.0.2-open`

# Install Maven and Gradle

Maven and Gradle are open-source tools for automating the process of building applications and managing their dependencies. Both tools can be managed with *SDKMAN!*.

- Install Maven with the following command:

```
$ sdk install maven

Downloading: maven 3.6.3
In progress... 100.0%
Installing: maven 3.6.3
Done installing!

Setting maven 3.6.3 as default.
```

- Install Gradle with the following command:

```
$ sdk install gradle

Downloading: gradle 6.0.1
In progress... 100.0%
Installing: gradle 6.0.1
Done installing!

Setting gradle 6.0.1 as default.
```

If you need multiple versions of Gradle or Maven you can install them by providing desired version with `sdk install maven 3.6.1` and then switch between them using `sdk set` or `sdk default` commands.

# Install Spring Boot CLI

The Spring Boot CLI is a command line tool that you can use if you want to quickly develop a Spring application.

You can check available Spring Boot versions with `sdk list springboot` command:

```
$ sdk list springboot
================================================================================
Available Springboot Versions
================================================================================
     2.2.2.RELEASE       2.0.1.RELEASE       1.5.1.RELEASE       1.2.3.RELEASE
     2.2.1.RELEASE       2.0.0.RELEASE       1.4.7.RELEASE       1.2.2.RELEASE
     2.2.0.RELEASE       1.5.22.RELEASE      1.4.6.RELEASE       1.2.1.RELEASE
```

Install default version by running `sdk install springboot`.

Once installed, `spring` command will be available:

```
$ spring
usage: spring [--help] [--version]
       <command> [<args>]
```

You can now bootstrap a new Spring Boot project by running:

```
$ spring init --build=gradle --java-version=12 --dependencies=web --packaging=jar my-app.zip
Using service at https://start.spring.io
Content saved to 'my-app.zip'
```

Unpack the zip and from within the application directory run:

```
gradle bootRun
Tomcat started on port(s): 8080 (http) with context path ''
2020-01-04 12:36:59.704  INFO 57156 --- [           main] com.example.myapp.DemoApplication        : Started DemoApplication in 1.251 seconds (JVM running for 1.485)
```

> Note: the above command used global Gradle distribution you installed with *SDKMAN!*, you can run it also with local Gradle installation by invoking `./gradlew` command.

Once the application has started, check if it responds to your requests:

```
$ http localhost:8080
HTTP/1.1 404
Connection: keep-alive
Content-Type: application/json
Date: Sun, 05 Jan 2020 11:38:08 GMT
Keep-Alive: timeout=60
Transfer-Encoding: chunked
Vary: Origin
Vary: Access-Control-Request-Method
Vary: Access-Control-Request-Headers

{
    "error": "Not Found",
    "message": "No message available",
    "path": "/",
    "status": 404,
    "timestamp": "2020-01-05T11:38:08.041+0000"
}
```

> Tip: I am using *httpie* client, not *cURL*. Read about tools I use on macOS in this blog post: [macOS: Essential tools for (Java) developer](../../../2020/01/macos-essential-tools-for-java-developer/index.md)

# Links

- [SDKMAN!](http://sdkman.io)
- [macOS: Essential tools for (Java) developer](../../../2020/01/macos-essential-tools-for-java-developer/index.md)

Do you use ***SDKMAN!***? When do you find it useful? Share your thougths in the comments.
