---
title: "Getting started with Github Actions: Run JUnit 5 tests in a Java project with Maven"
date: 2020-06-17T12:34:00.003+02:00
updated: 2020-06-17T12:35:28.104+02:00
author: "Rafał Borowiec"
tags: ["java", "junit 5", "maven", "testing", "tools"]
original_url: https://blog.codeleak.pl/2020/06/gh-actions-maven-junit5.html
---

# Getting started with Github Actions: Run JUnit 5 tests in a Java project with Maven

Github Actions is a CI/CD service provided by Github and it is free for public repositories. For private repositories, each GitHub account receives a certain amount of free minutes and storage, depending on the product used with the account.

In this blog post, you will learn how to create a simple workflow for running JUnit 5 tests in a Maven based Java project and how to add a build status badge to a README.md file.

> *This is a guest post by [Ewelina Fiedorowicz](https://www.linkedin.com/in/ewelinafiedorowicz), an ambitious beginner Java programmer, open to new technologies, eager to take on new challenges.*

*Table of Contents*

- [Problem](#problem)
- [Solution](#solution)
- [Introducing Workflow Syntax](#introducing-workflow-syntax)
  - [Step 1: Checkout the repository](#step-1-checkout-the-repository)
  - [Step 2: Set up JDK 14](#step-2-set-up-jdk-14)
  - [Step 3: Cache Maven packages](#step-3-cache-maven-packages)
  - [Step 4: Run tests with Maven](#step-4-run-tests-with-maven)
- [Badges](#badges)
- [Summary](#summary)
- [Source code](#source-code)
- [References](#references)

# Problem

On every `push` event, run JUnit 5 tests in a Java project with Maven and cache downloaded dependencies to speed up subsequent runs.

# Solution

TL;DR

The complete workflow, consiting of a single job with four steps, for automating the process of running JUnit tests in a Java project with Maven.

```yml
name: tests
on: push
jobs:
  run_tests:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout the repository
        uses: actions/checkout@v2
      - name: Set up JDK 14
        uses: actions/setup-java@v1
        with:
          java-version: 14
      - name: Cache Maven packages
        uses: actions/cache@v2
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-m2
      - name: Run tests with Maven
        run: mvn -B test --file pom.xml
```

# Introducing Workflow Syntax

Workflow files use *YAML* syntax and should have either `.yml` or `.yaml` extension. All workflow files have to be placed in `.github/workflows` directory in the root of your project.

You can create your fully customized workflow or you can use actions provided by the Github community. You can find them in [Github Marketplace](https://github.com/marketplace?type=actions)).

Workflows consist of the following sections:

- `name` (optional): a workflow name that will be displayed on the actions page of the repository.
- `on` (required): an event that triggers the workflow (`push`, `pull request`, `page build`, etc.). You can specify one or more events and also you can define branch(es) or tag(s) to run on. The workflow can be also scheduled using cron syntax.
- `env` (optional): environment variables. They can be set for the whole workflow, single job, or a step. It is recommended to use *Github Secrets* to pass tokens or secrets to the workfow. Secrets are encrypted environment variables exposed only to selected actions.

> Learn more about storing secrets in [Github Actions Documentation](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets).

- `jobs` (at least one is required): it is an actual list of tasks to be executed on a runner. Each job must have a unique identifier and may include several properties e.g.:
  - `runs-on` (required): you can choose a type of machine to run the job on (Windows, Linux, or macOS) or your own runner.
  - `steps`: a sequence of tasks. Every step can be either a simple shell command or an action consisting of various steps. An action can be defined in your own repository, any other public repository, or a Docker registry. Some actions require inputs that can be passed using `with` keyword.

> The workflow syntax can be found in [Github Actions documentation](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions).

## Step 1: Checkout the repository

The first step is to checkout the repository. In order to do so, use the `checkout` action:

```yml
- name: Checkhout the repository
  uses: actions/checkout@v2
```

## Step 2: Set up JDK 14

To configure Java environment use `setup-java` action. You can choose from various Java versions including major, minor and early access:

```yml
- name: Set up JDK 14
  uses: actions/setup-java@v1
  with:
    java-version: 14
```

## Step 3: Cache Maven packages

To cache downloaded dependencies and build outputs use `cache` action provided by the Github community. Path parameter defines the file path on the runner to cache or restore. Key parameter is used to search for a cache. If there is no match a new cache entry will be created and saved with the provided key in the path directory. Restore-keys parameter is optional and contains a list of alternative keys.

```yml
- name: Cache Maven packages
  uses: actions/cache@v2
  with:
    path: ~/.m2
    key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
    restore-keys: ${{ runner.os }}-m2
```

## Step 4: Run tests with Maven

Finally, to run tests use `mvn` command.

```yml
- name: Test with Maven
  run: mvn -B test --file pom.xml
```

# Badges

Adding a badge to the [README.md](http://README.md) file is a nice way to show to repository visitors that your project builds properly and all tests pass.

To obtain a badge for a workflow simply replace placeholders in the following URL with relevant information. Note that <WORKFLOW_NAME> is a name defined in the first line of .yml file and it not necessarily has to be the file name:

```
https://github.com/<OWNER>/<REPOSITORY>/workflows/<WORKFLOW_NAME>/badge.svg
```

To add a badge to the project wrap the link to the badge in the following manner and paste it at the top of the [README.md](http://README.md) file:

```
![](https://github.com/kolorobot/spring-boot-junit5/workflows/tests/badge.svg)
```

The badge will appear after committing and pushing changes to the repository.

# Summary

After the workflow successfully triggers, you will see logs and results in the actions page in your Github repository. Github Actions uses the exit codes to define whether an action is passing or failing. Any non-zero exit code is considered as a failure.

# Source code

The source code for this article can be found on [Github](https://github.com/kolorobot/spring-boot-junit5)

# References

- [Spring Boot testing with JUnit 5](../../../2019/09/spring-boot-testing-with-junit-5/index.md)
- [Github Actions](https://help.github.com/en/actions)
- [Github Badges](https://help.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#adding-a-workflow-status-badge-to-your-repository)
- [Github Secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets)
