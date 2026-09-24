---
title: "Override Spring Framework version in Spring Boot application built with Gradle"
date: 2015-09-14T22:20:00.001+02:00
updated: 2016-04-07T23:24:37.961+02:00
author: "Rafał Borowiec"
tags: ["spring boot"]
original_url: https://blog.codeleak.pl/2015/09/override-spring-framework-version-in.html
---

# Override Spring Framework version in Spring Boot application built with Gradle

![](logo-spring-io.png)

If you want to use or just check the newest version of Spring with Spring Boot but the current Spring Boot version depends on an older Spring version you need to adjust your Gradle build configuration slightly.

For example, as of time of writing this blog post, Spring 4.2.1 and Spring Boot 1.2.5 were current versions. Spring Boot 1.2.5 depends on Spring 4.1.7. So what to do to in order to use Spring 4.2.1 with Spring Boot 1.2.5? Have a look at two ways of achieving this: with and without Spring IO Platform.

## Spring IO Platform

The idea of [Spring IO Platform](http://docs.spring.io/platform/docs/current/reference/htmlsingle/) is to provide versions of libraries that are known to work together through Maven’s dependency management. The main reason you should consider Spring IO Platform for your project is that you don’t need to care about [dependency versions](http://docs.spring.io/platform/docs/current/reference/htmlsingle/#appendix-dependency-versions) of Spring projects along with their dependencies.

The Platform is also supported by Gradle via [dependency management plugin](https://plugins.gradle.org/plugin/io.spring.dependency-management) - a plugin that provides Maven-like dependency management functionality. To use it you can simply import the Platform’s `BOM` into your application’s `build.gradle` file:

```groovy
dependencyManagement {
    imports {
        mavenBom 'io.spring.platform:platform-bom:1.1.3.RELEASE'
    }
}
```

If you happen to generate projects by [Spring Initializr](http://start.spring.io/) you will notice that Gradle’s dependency management plugin is already included. The remaining thing is to add the dependency management configuration, import the `BOM` as shown above and add dependencies without versions - as versions are provided by `BOM`.

## Overriding dependency versions

Overriding version of a dependency is as easy as changing the value of the dependency version property that can be found in [`BOM`](https://github.com/spring-io/platform/blob/master/platform-bom/pom.xml) and its ancestors [here](https://github.com/spring-projects/spring-boot/blob/master/spring-boot-parent/pom.xml) and [here](https://github.com/spring-projects/spring-boot/blob/master/spring-boot-dependencies/pom.xml).

The properties can be changed in `gradle.properties` file:

```
spring.version = '4.2.1.RELEASE'
```

or in `build.gradle` file:

```
ext['spring.version'] = '4.2.1.RELEASE'
```

The above property defines a version of Spring framework. Overriding it lets you adjust Spring version in the Spring Boot application.

The complete file: <https://gist.github.com/kolorobot/71f0f208ffcd7c5979e7>

Assuming that you have Gradle 2.6 installed, execute `dependencyInsight` task:

```
gradlew dependencyInsight --dependency org.springframework
```

As you can see below, Spring 4.1.7 required by Spring Boot 1.2.5 was resolved to Spring 4.2.1:

```
[...]

org.springframework:spring-webmvc:4.1.7.RELEASE -> 4.2.1.RELEASE
\--- org.springframework.boot:spring-boot-starter-web:1.2.5.RELEASE
     \--- compile                 

org.springframework:spring-webmvc:4.1.7.RELEASE -> 4.2.1.RELEASE
\--- org.springframework.boot:spring-boot-starter-web:1.2.5.RELEASE
     \--- compile                 

[...]
```

## Override Spring Version without Spring IO Platform

In case you are not familiar with the Platform or you are reluctant to use it, you may choose a simple workaround and replace the version of Spring framework with the following configuration:

```groovy
configurations.all {
    resolutionStrategy.eachDependency { DependencyResolveDetails details ->
        if (details.requested.group == 'org.springframework') {
            details.useVersion "4.2.1.RELEASE"
        }
    }
}
```

The complete file: <https://gist.github.com/kolorobot/b5db05f6a5930642e6e3>

You may also find an example in this repository on GitHub: <https://github.com/kolorobot/spring-boot-jersey-demo>
