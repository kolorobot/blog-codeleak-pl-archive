---
title: "5 reasons why you should consider upgrading your applications to Spring 4"
date: 2015-12-09T20:58:00.000+01:00
updated: 2016-01-31T22:11:47.639+01:00
author: "Rafał Borowiec"
tags: ["spring 4"]
original_url: https://blog.codeleak.pl/2015/12/5-reasons-why-you-should-consider.html
---

# 5 reasons why you should consider upgrading your applications to Spring 4

Firstly released in 2004, Spring Framework is among top Java frameworks. Spring 4 has been released in December 2013 and it is the first version of framework to support Java 8. Learn why you should consider upgrading your applications to Spring 4.

*Note: I orginally wrote this blog post on my company’s blog at <http://blog.goyello.com>. You may find the original article here: <http://blog.goyello.com/2015/11/30/5-reasons-to-upgrade-to-spring-4/>.*

*Update*: Check Spring MVC Quickstart Maven Archetype (no-xml Spring MVC 4 web application): [Spring MVC Quickstart Maven Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype) to get started with Spring MVC 4 and Java 8 quickly. The project is actively maintained and just got updated!

## #1 Faster development with Java 8

Java 8, released in 2014, was the biggest update since Java 1.5. There are no doubts you should consider upgrading to Java 8 because:

- Java 8 is faster
- Java 8 has Lambda Expressions
- Java 8 has Streams API
- Java 8 has new Date & Time API

Learn more in the following article: <https://dzone.com/articles/why-java-8-1> and remember that Java 7 is now end of life: <https://www.java.com/en/download/faq/java_7.xml>

Spring 4 was the first version of the framework that fully supports Java 8 and if you want to use Spring with Java 8 you definitely need to upgrade.

Creating more compact and cleaner code is easy with Spring 4 and Java 8. For example, many of the Spring’s existing and new interfaces are functional interfaces which can be used in lambda expressions. New Date & Time API is supported in core framework but you can also utilize it in Thymeleaf views or with Spring Data JPA. Another example is the support of `java.util.Optional` in the framework. For example, you can inject it using`@RequestParam`, `@RequestHeader` and `@MatrixVariable`. Spring also provides out-of-the-box converters for `Stream`, `Charset`, `Currency`, and `TimeZone`.

## #2 Productivity improved

Each subsequent Spring release comes with a bunch of improvements that simplify the development. More and more tasks that needed custom solutions are now a part of the framework. For example, in Spring, injection of Java generics types is finally possible. Spring will automatically consider generics as a form of `@Qualifier`. Introduction of `@EventListener` and generic events simplify event handling in Spring applications. Spring not only introduced support for JCache (JSR-107) but also improved its own caching abstraction over time. If you happen to work with JMS, you may expect improvements here too, mainly with regards to the configuration (`@EnableJms`) and registering endpoints (`@JmsListener`).

There are many changes in testing infrastructure that allow creating integration tests much faster. New `TestTransaction` API to manage transactions programatically, SQL script execution per-class or per-method, executing tests with JUnit rules instead of JUnit test runner are only few examples of the changes.

## #3 Up to date

Spring framework coexists and integrates with many framework and 3rd party libraries. The dependencies are updated so you can work with the most recent ones. Spring integrates well with JEE APIs like JMS 2.1, JPA 2.1, Bean Validation 1.1 or already mentioned JCache. Spring also brought support for binding and conversion of types of `javax.money` package, from Money and Currency API. It integrates with Gson - an alternative to Jackson - and Google Protocol Buffers data protocol too.

It is also worth mentioning that Spring supports standards like WebSockets, SockJS and HTTP Streaming and Server-Sent Events - which is supported by the framework.

## #4 No more JAR hell

Introducing the Spring IO Platform project has a significant impact on the way the dependencies are managed in Spring applications that use Maven or Gradle.

> The Spring IO platform provides versions of the various Spring projects and their dependencies. With the configuration shown above added to your build script, you’re ready to declare your dependencies without having to worry about version numbers.

As a result of some problems with upgrading dependency versions developers were afraid to do so. With the platform the fear is gone. In many cases upgrading all dependency versions supported by the platform may require a change of the platform version only.

## #5 Happy developers

Developers love to work with the newest technologies. Upgrading the framework to its newest releases gives them an opportunity to boost their productivity, learn something new and improve their skills. This may also be a way to keep them motivated and prevent them from thinking about stepping out of the legacy project.

## References

Spring 4 and Java 8:   
- <http://www.baeldung.com/java-8-spring-4-and-spring-boot-adoption>   
- <https://spring.io/blog/2015/06/02/spring-4-and-java-8-adoption>   
- <https://dzone.com/guides/the-java-ecosystem-2015-edition>

Migrating:   
- <https://spring.io/blog/2014/01/30/migrating-from-spring-framework-3-2-to-4-0-1>   
- <https://github.com/spring-projects/spring-framework/wiki/Migrating-from-earlier-versions-of-the-spring-framework>

Spring IO Platform:   
- <http://docs.spring.io/platform/docs/current/reference/htmlsingle/#platform-documentation>
