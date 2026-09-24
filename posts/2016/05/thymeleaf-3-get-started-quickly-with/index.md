---
title: "Thymeleaf 3 - Get Started Quickly with Thymeleaf 3 and Spring MVC"
date: 2016-05-14T00:03:00.000+02:00
updated: 2016-05-14T00:03:37.382+02:00
author: "Rafał Borowiec"
tags: ["spring 4", "thymeleaf"]
original_url: https://blog.codeleak.pl/2016/05/thymeleaf-3-get-started-quickly-with.html
---

# Thymeleaf 3 - Get Started Quickly with Thymeleaf 3 and Spring MVC

Thymeleaf 3 release arrived. The new version brings plenty of new features like HTML5 support as well as Text templates support with no markup - `[# th:utext="${thymeleaf.version}" /]` , improved inline capabilities - `<p>Thymeleaf [[${thymeleaf.version}]] is great!</p>`, performence improvements and much more.

The easiest way the get starter with Thymeleaf 3 and Spring MVC is by using [Spring MVC 4 Quickstart Maven Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype). The archetype was updated to support Thymeleaf 3. The changes that are made to the archetype are described below.

### Dependencies

The project uses Spring Platform BOM for dependencies management, but it does not yet (as time of writing this post) declare dependency on Thymeleaf 3, so I needed to declare the versions manually.

- Thymeleaf:

```xml
<dependency>
    <groupId>org.thymeleaf</groupId>
    <artifactId>thymeleaf</artifactId>
    <version>3.0.0.RELEASE</version>
</dependency>
```

- Thymeleaf Spring 4:

```xml
<dependency>
    <groupId>org.thymeleaf</groupId>
    <artifactId>thymeleaf-spring4</artifactId>
    <version>3.0.0.RELEASE</version>
</dependency>
```

- Thymeleaf Spring Security 4:

```xml
<dependency>
    <groupId>org.thymeleaf.extras</groupId>
    <artifactId>thymeleaf-extras-springsecurity4</artifactId>
    <version>3.0.0.RELEASE</version>
</dependency>
```

The application generated with the archetype uses Java 8 Time Dialect and since Thymeleaf API changed, the dialect dependency must be updated too. Before it is available in Maven Central, we must add snapshot repository to POM:

```xml
<repository>
    <id>sonatype-nexus-snapshots</id>
    <name>Sonatype Nexus Snapshots</name>
    <url>https://oss.sonatype.org/content/repositories/snapshots</url>
    <snapshots>
        <enabled>true</enabled>
    </snapshots>
</repository>
```

And then declare the dependency:

```xml
<dependency>
    <groupId>org.thymeleaf.extras</groupId>
    <artifactId>thymeleaf-extras-java8time</artifactId>
    <version>3.0.0-SNAPSHOT</version>
</dependency>
```

### Configuration changes

- Template resolver

*Template resolver before:*

```java
@Bean
public TemplateResolver templateResolver() {
   TemplateResolver resolver = new ServletContextTemplateResolver();
   resolver.setPrefix(VIEWS);
   resolver.setSuffix(".html");
   resolver.setTemplateMode("HTML5");
   resolver.setCacheable(false);
   return resolver;
}
```

*Template resolver after:*

```java
@Bean
public ITemplateResolver templateResolver() {
    SpringResourceTemplateResolver resolver = new SpringResourceTemplateResolver();
    resolver.setPrefix(VIEWS);
    resolver.setSuffix(".html");
    resolver.setTemplateMode(TemplateMode.HTML);
    resolver.setCacheable(false);
    return resolver;
}
```

- Template Engine

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

- View Resolver:

```java
@Bean
public ViewResolver viewResolver() {
    ThymeleafViewResolver thymeleafViewResolver = new ThymeleafViewResolver();
    thymeleafViewResolver.setTemplateEngine(templateEngine());
    thymeleafViewResolver.setCharacterEncoding("UTF-8");
    return thymeleafViewResolver;
}
```

### Templates

The templates did not change in this project. But if you are migrating a *real* project, you may be interested in reading [migration guide.](http://www.thymeleaf.org/doc/articles/thymeleaf3migration.html)

## References

- [Thymeleaf 3 release info](http://forum.thymeleaf.org/Thymeleaf-3-0-is-here-td4029676.html)
- [Thymeleaf 3 Migration guide](http://www.thymeleaf.org/doc/articles/thymeleaf3migration.html)
- [Spring MVC 4 Quickstart Maven Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype)

## You may be also interested in

- [Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md)
- [Spring MVC and Thymeleaf: how to acess data from templates](../../../2014/05/spring-mvc-and-thymeleaf-how-to-acess-data-from-templates/index.md)
- [Thymeleaf Page Layouts](../../../2014/01/thymeleaf-page-layouts/index.md)
