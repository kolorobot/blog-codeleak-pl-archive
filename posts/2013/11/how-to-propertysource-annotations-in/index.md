---
title: "HOW-TO: Using @PropertySource annotation in Spring 4 with Java 7"
date: 2013-11-11T23:07:00.000+01:00
updated: 2013-11-13T20:57:03.328+01:00
author: "Rafał Borowiec"
tags: ["spring 4", "spring mvc"]
original_url: https://blog.codeleak.pl/2013/11/how-to-propertysource-annotations-in.html
---

# HOW-TO: Using @PropertySource annotation in Spring 4 with Java 7

![](logo-spring-io.png)

Today I migrated one of my projects, that I am currently working on, to Spring 4.0. Since it is a really simple web application I use to learn and demo Spring features, I only needed to update the POM file of my project and change the Spring version. I deployed the project to Tomcat 7 server and apparently the application did not start. I saw this message in IntelliJ console: `Failed to load bean class: pl.codeleak.t.config.RootConfig; nested exception is org.springframework.core.NestedIOException: Unable to collect imports; nested exception is java.lang.ClassNotFoundException: java.lang.annotation.Repeatable`. What the ...?

[java.lang.annotation.Repeatable](http://download.java.net/jdk8/docs/api/java/lang/annotation/Repeatable.html) annotation that is the meta annotation used to mark your annotations for multiple usage in Java 8 (but I am using Java 7 in the project). E.g.:

```java
@Repeatable(Schedules.class)
public @interface Schedule { ... }

@Schedule(dayOfMonth="last")
@Schedule(dayOfWeek="Fri", hour="23")
public void doPeriodicCleanup() { ... }
```

This is well described here: <http://docs.oracle.com/javase/tutorial/java/annotations/repeating.html>.

Spring 4 utilizes this feature in its [@PropertySource](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/PropertySource.html) annotation. To remind you, [@PropertySource](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/PropertySource.html) annotation provides a mechanism for adding a source of name/value property pairs to Spring's [Environment](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/core/env/Environment.html) and it is used in conjunction with [@Configuration](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/Configuration.html) classes. As you probably already know, I am using this feature in my own configuration:

```java
@Configuration
@PropertySource("classpath:/datasource.properties")
public class DefaultDataSourceConfig implements DataSourceConfig {

    @Autowired
    private Environment env;

    @Override
    @Bean
    public DataSource dataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName(env.getRequiredProperty("dataSource.driverClassName"));
        dataSource.setUrl(env.getRequiredProperty("dataSource.url"));
        dataSource.setUsername(env.getRequiredProperty("dataSource.username"));
        dataSource.setPassword(env.getRequiredProperty("dataSource.password"));
        return dataSource;
    }
}
```

The first think I thought, that Spring is not compatible with Java below 8 anymore. Impossible. While doing GitHub lookup I found a brand new [@PropertySources](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/PropertySources.html) annotation that is a container of [@PropertySource](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/PropertySource.html) annotations. And that was my solution for Java compatibility issue: using [@PropertySources](http://docs.spring.io/spring-framework/docs/4.0.x/javadoc-api/org/springframework/context/annotation/PropertySources.html) annotation on my configuration class like this:

```java
@Configuration
@PropertySources(value = {@PropertySource("classpath:/datasource.properties")})
public class DefaultDataSourceConfig implements DataSourceConfig {

    @Autowired
    private Environment env;

}
```

And that's it! After this change my application started and I could see it is working just fine!

**EDIT**: See: <https://jira.springsource.org/browse/SPR-11086>
