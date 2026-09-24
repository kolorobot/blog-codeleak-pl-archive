---
title: "Spring MVC 4 Quickstart Maven Archetype Improved - More Java 8 Features"
date: 2016-01-31T22:01:00.000+01:00
updated: 2016-01-31T22:01:05.627+01:00
author: "Rafał Borowiec"
tags: ["maven", "spring 4", "spring mvc", "tools"]
original_url: https://blog.codeleak.pl/2016/01/spring-mvc-4-quickstart-maven-archetype.html
---

# Spring MVC 4 Quickstart Maven Archetype Improved - More Java 8 Features

For all those developers interested in bootstrapping Spring 4 application quickly without Spring Boot, please check my Spring MVC 4 Quickstart Maven Archetype that just got updated. Archetype uses Java 8 as target platform for some time already but no specific Java 8 features were supported. Recent changes bring (apart from some bug fixing) support for Java 8 Data & Time API in Thymeleaf, Jackson and JPA.

## Thymeleaf JSR 310 (Java 8 Date & Time) support

If you happen to work with Spring MVC and Thymeleaf and you need to format Java 8 Date & Time objects in your views you may now utilize *thymeleaf-extras-java8time* - Thymeleaf module for Java 8 Date & Time API.

The POM was modified and the new dependency was added:

```xml
<dependency>
    <groupId>org.thymeleaf.extras</groupId>
    <artifactId>thymeleaf-extras-java8time</artifactId>
    <version>2.1.0.RELEASE</version>
</dependency>
```

Additionally, `Java8TimeDialect` was added to the `TemplateEngine`:

```java
@Bean
public SpringTemplateEngine templateEngine() {
    SpringTemplateEngine templateEngine = new SpringTemplateEngine();
    templateEngine.setTemplateResolver(templateResolver());
    templateEngine.addDialect(new SpringSecurityDialect());
    templateEngine.addDialect(new Java8TimeDialect());
    return templateEngine;
}
```

What `Java8TimeDialect` does, it adds a `temporals` object to the context as utility objects during expression evaluations. This means, that it can be used in OGNL or SpringEL expression evaluations:

```html
<div th:fragment="footer" th:align="center">
    &copy; <span th:text="${#temporals.format(#temporals.createNow(), 'yyyy')}">2016</span>,
    <span th:text="${@environment.getProperty('app.version')}"></span>
</div>
```

## Jackson JSR 310 (Java 8 Date & Time) support

To be able to serialize or deserialize *java.time* types with Jackson an external datatype module must be used. This module is *jackson-datatype-jsr310*.

The POM was modified and the new dependency was added:

```xml
<dependency>
    <groupId>com.fasterxml.jackson.datatype</groupId>
    <artifactId>jackson-datatype-jsr310</artifactId>
</dependency>
```

We don’t need to provide the version, as Spring IO platform is utilized in the project. And if you don’t know, the main advantage of Spring IO Platform is that it simplifies dependency management by providing versions of Spring projects along with their dependencies that are tested and known to work together.

No other configuration is needed at the moment, as the module will be registered by Spring automatically. This is done by `org.springframework.http.converter.json.Jackson2ObjectMapperBuilder`.

An example?

```json
{
    "id": 2,
    "email": "admin",
    "role": "ROLE_ADMIN",
    "created": 1454017095.878
}
```

where `created` is an `Instant` that got serialized to a decimal (default).

Learn more about this module here: <https://github.com/FasterXML/jackson-datatype-jsr310>

## JPA JSR 310 (Java 8 Date & Time) support

JPA 2.1 does not support mapping *java.time* types into a SQL valid date or timestamp types. Fortunatelly, it brings a new `AttributeConverter` interface and *“a class that implements this interface can be used to convert entity attribute state into database column representation and back again.”*.

Such converters are part of Spring Data JPA project and are available in `Jsr310JpaConverters` class. This class converts new *java.time* types into the old `Date` types.

Activating converters is possible by making `org.springframework.data.jpa.convert.threeten` package to be scanned by `LocalContainerEntityManagerFactoryBean`:

```java
@Bean
public LocalContainerEntityManagerFactoryBean emf(DataSource dataSource) {

    [...]

    String entities = ClassUtils.getPackageName(Application.class);
    String converters = ClassUtils.getPackageName(Jsr310JpaConverters.class);
    entityManagerFactoryBean.setPackagesToScan(entities, converters);        

    [...]

    return entityManagerFactoryBean;
}
```

If you are working with PostgreSQL, the `java.time.Instant` type will be now stored as `TIMESTAMP` in PostgreSQL instead of `BYTEA` (as without the converters).

Learn more JPA 2.1 and JSR 310 support here: <http://www.thoughts-on-java.org/persist-localdate-localdatetime-jpa/>

## Where to find it?

Find the update archetype on GitHub: <https://github.com/kolorobot/spring-mvc-quickstart-archetype>

I am looking forward to hear what could be improved to make it a better project. If you have an idea or suggestion drop a comment or create an issue.
