---
title: "Get started quickly with Spring 5 using Spring MVC Archetype"
date: 2017-09-28T21:09:00.000+02:00
updated: 2017-09-28T21:09:14.670+02:00
author: "Rafał Borowiec"
tags: ["spring 5", "tools"]
original_url: https://blog.codeleak.pl/2017/09/get-started-quickly-with-spring-5.html
---

# Get started quickly with Spring 5 using Spring MVC Archetype

Spring 5 GA got released so I released the new version of Spring MVC Archetype.

# Create a project

To create a really basic application using the archetype simply run the following command in your shell:

```bash
    mvn archetype:generate \
        -DarchetypeGroupId=pl.codeleak \
        -DarchetypeArtifactId=spring-mvc-quickstart \
        -DarchetypeVersion=5.0.0 \
        -DgroupId=my.groupid \
        -DartifactId=my-artifactId \
        -Dversion=version \
        -DarchetypeRepository=http://kolorobot.github.io/spring-mvc-quickstart-archetype
```

# Changes

## Spring IO Platform

Since I am using the Spring IO Platform (`Brussels-SR5`) in my archetype, I needed to manually override Spring version to 5.0.0.RELEASE:

```
<spring.version>5.0.0.RELEASE</spring.version>
```

## Spring MVC

Spring MVC is built against different version of Jackson, hence Jackson version is overridden as well:

```
<jackson.version>2.9.1</jackson.version>
```

## Thymeleaf

Thymeleaf 3 Support for Spring 5 did not go GA yet, but there is a release candidate in Maven Central that can be used:

```
<dependency>
    <groupId>org.thymeleaf</groupId>
    <artifactId>thymeleaf-spring5</artifactId>
    <version>3.0.7.RC1</version>
</dependency>
```

## Source code

<https://github.com/kolorobot/spring-mvc-quickstart-archetype>
