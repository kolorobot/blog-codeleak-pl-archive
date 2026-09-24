---
title: "HOW-TO: Test dependencies in a Maven project (JUnit, Mocito, Hamcrest, AssertJ)"
date: 2014-03-05T20:08:00.000+01:00
updated: 2014-03-06T00:55:44.916+01:00
author: "Rafał Borowiec"
tags: ["unit testing"]
original_url: https://blog.codeleak.pl/2014/03/how-to-test-dependencies-in-maven.html
---

# HOW-TO: Test dependencies in a Maven project (JUnit, Mocito, Hamcrest, AssertJ)

![](junit.gif)

JUnit itself is not enough for most of today's Java projects. You also need a mocking library, maybe something else. In this mini HOW-TO I present the test dependencies you can start with in a new Java project.

## All starts with JUnit

There are two artifacts in [junit group](http://mvnrepository.com/artifact/junit) in Maven Repository: `junit` and `junit-dep`. Prior to version `4.9` the latter did not contain dependency to Hamcrest inlined. Today, we use `junit` dependency as follows:
The `dependency:tree` produces:

```
[INFO] \- junit:junit:jar:4.11:test
[INFO]    \- org.hamcrest:hamcrest-core:jar:1.3:test
```

## Mockito

The next dependency we usually need is a mocking framework. No doubts that [Mockito](https://code.google.com/p/mockito/) is one of the most popular one. It comes in two favors: `mockito-all` and `mockito-core`. The first is a single jar will all dependencies inlined inside, whereas the latter is just a Mockito. It is recommended to use `mockito-core` with version `4.11` of JUnit. So let's add the dependency:
Now the `dependency:tree` produces:

```
[INFO] +- junit:junit:jar:4.11:test
[INFO] |  \- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] \- org.mockito:mockito-core:jar:1.9.5:test
[INFO]    \- org.objenesis:objenesis:jar:1.0:test
```

## Hamcrest

Knowing that `mockito-core` is better for declarative dependency management, we will override dependencies to both Hamcrest and Objenesis as follows:
Having this we can easily add Hamcrest library, that provides a library of matcher objects, dependency:
And the `dependency:tree` produces:

```
[INFO] +- junit:junit:jar:4.11:test
[INFO] +- org.mockito:mockito-core:jar:1.9.5:test
[INFO] +- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] +- org.hamcrest:hamcrest-library:jar:1.3:test
[INFO] \- org.objenesis:objenesis:jar:1.3:test
```

## AssertJ

[AssertJ](https://github.com/joel-costigliola/assertj-core) - fluent assertions for java - provides a rich and intuitive set of strongly-typed assertions to use for unit testing. AssertJ is a fork of FEST Assert that I wrote about some time ago in this [post](../../../2013/07/test-code-readability-improved-junit/index.md). And what about the dependency? Let's bave a look:
Which result in the following tree:

```
[INFO] +- junit:junit:jar:4.11:test
[INFO] +- org.mockito:mockito-core:jar:1.9.5:test
[INFO] +- org.assertj:assertj-core:jar:1.5.0:test
[INFO] +- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] +- org.hamcrest:hamcrest-library:jar:1.3:test
[INFO] \- org.objenesis:objenesis:jar:1.3:test
```

## The Final Cut

The complete Maven structure looks as follows:
You can find this in [unit-testing-demo](https://github.com/kolorobot/unit-testing-demo) project on GitHub (link to [pom.xml](https://github.com/kolorobot/unit-testing-demo/blob/master/pom.xml)) or you can try out my [spring-mvc-quickstart-archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype) (link to [pom.xml](https://github.com/kolorobot/spring-mvc-quickstart-archetype/blob/master/src/main/resources/archetype-resources/pom.xml)).
