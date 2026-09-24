---
title: "JUnit 5 and Selenium - Setup the project with Gradle, JUnit 5 and Jupiter Selenium"
date: 2019-09-18T23:03:00.002+02:00
updated: 2023-02-09T22:42:56.212+01:00
author: "Rafał Borowiec"
tags: ["junit 5", "selenium"]
original_url: https://blog.codeleak.pl/2019/09/junit-5-and-selenium-setup-project-with.html
---

# JUnit 5 and Selenium - Setup the project with Gradle, JUnit 5 and Jupiter Selenium

Selenium is a set of tools and libraries supporting browser automation and it is mainly used for web applications testing. One of the Selenium's components is a Selenium WebDriver that provides client library, the JSON wire protocol (protocol to communicate with the browser drivers) and browser drivers. One of the main advantages of Selenium WebDriver is that it supported by all major programming languages and it can run on all major operating systems.

In this tutorial I will go through the setup of the test automation project for the popular [TodoMVC](http://todomvc.com) application using Gradle with Java, JUnit 5 and Selenium Jupiter. You will learn about Selenium's PageFactory to implement Page Object pattern. You will also learn about parallel test execution, test execution order, parameterized tests and much more.

## Table of contents

- [About this Tutorial](#about-this-tutorial)
- [Prerequisites](#prerequisites)
- [Setup the project from the ground up](#setup-the-project-from-the-ground-up)
  - [Java and JUnit 5](#java-and-junit-5)
  - [JUnit Jupiter](#junit-jupiter)
  - [Directories and project files](#directories-and-project-files)
  - [Running the test](#running-the-test)
  - [Create Git repository](#create-git-repository)
  - [Importing project to IDE](#importing-project-to-ide)
- [Next steps](#next-steps)

## Changes

- *2023-02* - The project was updated to Gradle 7.2 and Java 17. Dependencies updated to newer versions.

## About this Tutorial

You are reading the first part of the *JUnit 5 with Selenium WebDriver - Tutorial*.

All articles in this tutorial:

- Part 1 - [Setup the project from the ground up - Gradle with JUnit 5 and Jupiter Selenium](../../../2019/09/junit-5-and-selenium-setup-project-with/index.md)
- Part 2 - [Using Selenium built-in `PageFactory` to implement Page Object Pattern](../../../2019/10/junit-5-and-selenium-using-selenium/index.md)
- Part 3 - [Improving the project configuration - executing tests in parallel, tests execution order, parameterized tests, AssertJ and more](../../../2019/12/junit-5-and-selenium-improving-project/index.md)

> The source code for this tutorial can be found on [Github](https://github.com/kolorobot/junit5-selenium-todomvc-demo)

## Prerequisites

First of all, Java JDK is required and it must be installed in your system. I will be using Java 12 and I recommend installing [OpenJDK](https://openjdk.java.net) instead of the Oracle JDK due to licensing changes in Java 11. You will also need [Gradle](https://gradle.org/install/) to init a new project and your favourite Java IDE - I recommend [IntelliJ IDEA](https://www.jetbrains.com/idea/) Community or Professional. Optionally, you can also install [Git](https://git-scm.com) version control system.

For managing (installing, updating, uninstalling) the tools I recommended using the package manager. If you are working on Windows, you can use [Chocolately](https://chocolatey.org), if you are on macOS you should be using [Homebrew](https://brew.sh).

To sum up, make sure you have the following tools installed and available to you while working with the project in this article:

- Java 17+
- Gradle - required *only* for setting up the project, Gradle 7.2+ is recommended
- Your favourite Java IDE - IntelliJ IDEA Community or Professional is recommended
- Chrome browser - for running Selenium tests
- Terminal Emulator - for executing shell commands with at least basic support for Unix commands. In Windows this can be [Cmder](https://cmder.net) (with Git), in macOS I recommend [iTerm2](https://iterm2.com)
- Git - if you want to track your source code history

## Setup the project from the ground up

To create an empty Gradle based project, open you favourite terminal and type:

```
mkdir junit5-selenium-todomvc-demo
cd junit5-selenium-todomvc-demo
gradle init --type basic --dsl groovy
```

The generated project is an empty, *DIY* project - with no plugins and no dependencies. It comes with the redundant `settings.gradle` that can be removed:

```
rm settings.gradle
```

### Java and JUnit 5

For the basic Java project configuration with JUnit 5 add the following content to the `build.gradle`:

```groovy
plugins {
    id 'java'
}

repositories {
  mavenCentral()
}

sourceCompatibility = 17
targetCompatibility = 17

dependencies {
    testImplementation('org.junit.jupiter:junit-jupiter:5.7.1')
}

test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed"
    }
}
```

The above DSL configures Gradle's Java plugin (`plugins`), that provides us capabilities for building Java based projects with Gradle. The project uses Maven repository (`repositories`) to download project dependencies (`dependencies`) that are declared in the project. Test implementation dependency for the project is set to JUnit 5 (`testImplementation`) and the task is adjusted (`test`) to make sure that JUnit 5 is used while executing the tests with Gradle.

Configuration can be verified by executing the Gradle build in the terminal:

```
./gradlew build
```

The build is successful:

```
BUILD SUCCESSFUL in 0s
1 actionable task: 1 executed
```

`./gradlew` command run the Gradle Wrapper instead a global Gradle distribution. The project was generated with the Gradle Wrapper and therefore global Gradle distribution is not needed at all for executing the tasks and working with the project.

> Note: If you are looking for JUnit 5 project templates for Gradle or Maven checkout the official JUnit 5 Samples Github repository: <https://github.com/junit-team/junit5-samples>

### JUnit Jupiter

To simplify the configuration of Selenium WebDriver in the project I am going to use Selenium Jupiter which is the JUnit 5 extension aimed to ease the use of Selenium (WebDriver and Grid) in JUnit 5 tests. It comes as a single dependency that needs to be added to dependencies list in `build.gradle`:

```groovy
dependencies {
    testImplementation('io.github.bonigarcia:selenium-jupiter:4.3.3')
}
```

[Selenium Jupiter](https://bonigarcia.github.io/selenium-jupiter/) library provides integration with Selenium and Appium. Selenium Jupiter supports local and remote browsers, browsers in Docker containers (Docker engine is required) but also [Selenide](https://selenide.org) based browser configuration. It uses [WebDriverManager](https://github.com/bonigarcia/webdrivermanager) internally to manage browser drivers.

> Note: Don't be surprised to see many libraries in your project. Selenium Jupiter has many dependencies. To see all the project dependencies (including transitive dependencies) execute the following command: `./gradlew dependencies`.

### Directories and project files

The project was created with no Java source files. To create the initial directory and the first test the following commands can be executed:

```
mkdir -p src/test/java/pl/codeleak/demos/selenium/todomvc
touch src/test/java/pl/codeleak/demos/selenium/todomvc/SeleniumTest.java
```

The `SeleniumTest.java` file contains very basic test confirming the project is configured properly. The test uses JUnit 5 extension provided by Selenium Jupiter and it has a single test that verifies project is configured properly:

```java
package pl.codeleak.demos.selenium.todomvc;

import io.github.bonigarcia.seljup.SeleniumJupiter;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.chrome.ChromeDriver;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SeleniumJupiter.class)
class SeleniumTest {

    @Test
    void projectIsConfigured(ChromeDriver driver) {
        assertThat(driver).isNotNull();
    }
}
```

### Running the test

Executing the Gradle build should confirm the test is passing:

```
./gradlew build

pl.codeleak.demos.selenium.todomvc.SeleniumTest > projectIsConfigured() PASSED

BUILD SUCCESSFUL in 1s
3 actionable tasks: 2 executed, 1 up-to-date
```

You probably noted that during the execution of the task the Chrome browser was opened and then closed. This only confirms that all the driver configuration was done under the hood by Selenium Jupiter (with the use of WebDriverManager library). You also noticed that there is no setup and cleanup code for this test. Instead, we are *injecting* the instance of the ChromeDriver directly to the test where it is needed. This is how the Selenium Jupiter uses JUnit 5 extension mechanism to inject parameters to test.

### Create Git repository

The initial setup of the project is done. Before the real work starts, the project setup can be now be stored in the Git repository. If you have Git installed, run the following command to create a new repository:

```
git init
```

Edit `.gitignore` file to exclude files and directories you want to skip from the repository:

```
.gradle
.idea
*.iml
build
out
```

Execute the following command to add and commit files to the repository:

```
git add .
git commit -m 'Initial project setup'
```

### Importing project to IDE

Please note that all the job so far was done with no IDE whatsoever (not fully true - the test I created with the help of IDE). In general, this is very important aspect of the project configuration: always make your project IDE independent. Prove you can execute the build with single shell commands. This will pay off - especially when you are going to execute the build using continuous integration tool.

Anyway, with IntelliJ the project will work with no problem. Just lunch it and open a directory with the project and import it as Gradle project.

And now you are all set to start developing the tests and improving the project. But remember, if you are making any configuration changes it is advised that from time to time you test them with the terminal, outside the IDE.

## Next steps

In the next part of this tutorial you will learn some basics about Page Object Pattern and implementing it using Selenium's built-in `PageFactory`: [Using Selenium built-in `PageFactory` to implement Page Object Pattern](../../../2019/10/junit-5-and-selenium-using-selenium/index.md)
