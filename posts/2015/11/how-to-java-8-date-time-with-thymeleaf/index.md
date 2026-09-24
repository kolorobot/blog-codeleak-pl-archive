---
title: "HOW-TO: Java 8 Date & Time with Thymeleaf and Spring Boot"
date: 2015-11-11T15:37:00.000+01:00
updated: 2016-09-24T22:48:45.598+02:00
author: "Rafał Borowiec"
tags: ["java 8", "spring boot", "thymeleaf"]
original_url: https://blog.codeleak.pl/2015/11/how-to-java-8-date-time-with-thymeleaf.html
---

# HOW-TO: Java 8 Date & Time with Thymeleaf and Spring Boot

If you happen to work with Spring Boot and Thymeleaf and you need to format Java 8 Date & Time objects in your views you may utilize `thymeleaf-extras-java8time` - Thymeleaf module for Java 8 Date & Time API.

*Update (24/9/2016):* Configuration updates.

*Update (21/3/2016):* Dependencies got updated: io.spring.platform, bootstrap, jquery, assertj and selenium

Adding `thymeleaf-extras-java8time` to an existing Maven or Gradle based Spring Boot project is as easy as adding a dependency and registering new dialect with a template engine.

For Maven, you add the following dependency to you existing POM:

```xml
<dependency>
    <groupId>org.thymeleaf.extras</groupId>
    <artifactId>thymeleaf-extras-java8time</artifactId>
    <version>2.1.0.RELEASE</version>
</dependency>
```

If you are using Thymeleaf 3 the version is 3.0.0.RELEASE.

Once you have done it, the next step is to add the dialect to the template engine. With Spring Boot you need to define a bean of type `org.thymeleaf.extras.java8time.dialect.Java8TimeDialect` in your appliacation context. All beans of type `org.thymeleaf.dialect.IDialect` are injected into Spring Boot’s [`ThymeleafAutoConfiguration`](https://github.com/spring-projects/spring-boot/blob/master/spring-boot-autoconfigure/src/main/java/org/springframework/boot/autoconfigure/thymeleaf/ThymeleafAutoConfiguration.java) and added to Thymeleaf’s `SpringTemplateEngine` automatically.

*Note (24/9/2016)* Spring Boot introduced org.springframework.boot.autoconfigure.thymeleaf.ThymeleafAutoConfiguration.ThymeleafJava8TimeDialect class that auto-configures the dialect if Java 8 is available and org.thymeleaf.extras.java8time.dialect.Java8TimeDialect is on the classpath. So the below configuration is not needed anymore if you are using newest Spring Boot.

```java
@SpringBootApplication
public class Application {

    @Bean
    public Java8TimeDialect java8TimeDialect() {
        return new Java8TimeDialect();
    }

    public static void main(String[] args) {
        SpringApplication.run(Application.class);
    }
}
```

What `Java8TimeDialect`does, it adds a `temporals`object to the context as utility objects during expression evaluations. This means, that it can be used in OGNL or SpringEL expression evaluations:

```html
The time is: <strong th:text="${#temporals.format(now, 'dd/MMM/yyyy HH:mm')}">31/12/2015 15:00</strong>
```

`temporals` provide many utility method to work with `java.time.Temporal`: formatting, accessing properties and creating new objects. For more information about the extension and `temporals` itself checkout project page on GitHub: [thymeleaf-extras-java8time](https://github.com/thymeleaf/thymeleaf-extras-java8time)

***Note***: The Spring Boot and Thymeleaf project setup is described in greater details in this blog post: [Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md)

The source code used in this blog post: <https://github.com/kolorobot/spring-boot-thymeleaf>
