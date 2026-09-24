---
title: "Spring Boot - spring.config.name - Case Study"
date: 2017-10-03T23:31:00.000+02:00
updated: 2017-10-03T23:31:23.774+02:00
author: "Rafał Borowiec"
tags: ["spring boot"]
original_url: https://blog.codeleak.pl/2017/10/spring-boot-springconfigname-case-study.html
---

# Spring Boot - spring.config.name - Case Study

Externalizing Spring Boot application properties is useful when the same application code must be used with different configuration. If the configuration is to be kept away from the source code (which is considered a best practice anyways)`spring.config.location` environment property *can* be used to point the directory location with properties files for example. On the other hand, `spring.config.name` can be used to change the base name of the properties file which defaults to `application`. The documentation reads: *if you **don’t like** application.properties as the configuration file name you can switch to another*. But in what scenario `spring.config.name` could be used?

## (Potential) problem

One of the ways of providing `spring.config.location` is by using environment variable: `SPRING_CONFIG_LOCATION`. This can be considered useful when deploying Spring Boot application to Tomcat server. And when Spring Boot application starts it picks up `application.properties` (with profile specific properties files) from `SPRING_CONFIG_LOCATION` directory.

But what would happen when multiple Spring Boot applications are to be deployed to the same Tomcat server?

In such case we may expect some *unexpected* behavior as other applications will also pick app the `application.properties` from `SPRING_CONFIG_LOCATION` directory - and in case these are different app we may run into troubles.

## (Potential) solution

One of the ways to solve the issue is to change the configuration base name in each application.

It can be done programatically in servlet initializer with `spring.config.name` property:

```
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.support.SpringBootServletInitializer;

public class ServletInitializer extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application
            .properties("spring.config.name:my-app-1")
            .sources(MyApiApplication.class);
    }

}
```

When starting the application, Spring Boot will expect that `my-app-1.properties` exists (with profile specific variants e.g. `my-app-1-test.properties`) . This way we may multiple applications deployed easily to the same Tomcat server with externalized configuration:

```
/data/config/my-app-1.properties
/data/config/my-app-1-test.properties
/data/config/my-app-2.properties
/data/config/my-app-2-test.properties
```

## Final thoughts

Hardcoding configuration is not the best solution, but in some scenarios there may be no better way than doing so.
