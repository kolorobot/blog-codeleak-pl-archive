---
title: "Spring Boot and Thymeleaf: Reload templates and static resources without restarting the application"
date: 2016-12-06T22:27:00.001+01:00
updated: 2016-12-07T22:35:18.967+01:00
author: "Rafał Borowiec"
tags: ["spring boot", "thymeleaf"]
original_url: https://blog.codeleak.pl/2016/12/thymeleaf-reload-templates-and-static-resources.html
---

# Spring Boot and Thymeleaf: Reload templates and static resources without restarting the application

Thymeleaf was designed around the concept of *Natural Templates* that allows static prototyping: template logic doesn’t affect the template from being used as prototype. Although this is a great technique, you may also want to see the results in a running Spring Boot application and **without** restarting the server each time you change Thymeleaf view. In addition, you may expect that all other static resources like JavaScript and CSS files can be reloaded during development also. How to achieve it with Spring Boot?

# Thymeleaf templates reloading

While working on a Spring Boot application that is utilizing Thymeleaf view engine two properties are needed in order to ensure reloading templates: `spring.thymeleaf.cache` and `spring.thymeleaf.prefix`. Setting `spring.thymeleaf.cache` to `false` disables template caching whereas `spring.thymeleaf.prefix` allows specifying prefix that gets prepended to view names when building a view URL.

Example (Windows):

```
spring.thymeleaf.prefix=file:///C:/Projects/github/spring-boot-thymeleaf/src/main/resources/templates/
```

Assuming the all templates are in the path specified, changing them will require a page refresh but not application / server restart.

Both properties can be used in a development profile (e.g. create `application-dev.properties` and run the application with `dev` profile active).

# Reload static resources (CSS, JavaScript)

With Spring Boot and Thymeleaf reloading templates during development is relatively easy. If you want to achieve reloading of static resources like CSS and JavaScript the approach is very similar: you need to use `spring.resources.static-locations`.

Example (Windows):

```
spring.resources.static-locations=file:///C:/Projects/github/spring-boot-thymeleaf//src/main/resources/static/
```

In the above example there is a single location, but the property accepts multiple locations.

Furthermore, you can configure more settings related to static resources, like for example caching etc. Please refer to Spring Boot documentation and find out about `spring.resources.*` properties (<http://docs.spring.io/spring-boot/docs/current/reference/html/common-application-properties.html>)

# application-dev.properties

The final solution could look like below:

```
#
# Development profile with templates and static resources reloading
#

# Path to project
project.base-dir=file:///C:/Projects/github/spring-boot-thymeleaf

# Templates reloading during development
spring.thymeleaf.prefix=${project.base-dir}/src/main/resources/templates/
spring.thymeleaf.cache=false

# Static resources reloading during development
spring.resources.static-locations=${project.base-dir}/src/main/resources/static/
spring.resources.cache-period=0
```

Note: You will find it in the source code reference in this article: [HOW-TO: Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md)

If you don’t want to create new profile, you can simply provide properties as JVM options (`-D`) while running the application.

# Alternative approach - Spring Boot DevTools

One of the modules of Spring Boot is the DevTools (as of version 1.3). Among many features it enables live reloading Thymeleaf templates and static resources without any further configuration. It has also support for LiveReload protocol.

**Note**: When you change the template / resource rebuild the project (CTRL+F9 on Windows) and then refresh. When you install LiveReload plugin (I tested with LiveReload plugin for Chrome: <https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei>) after rebuild the page gets refreshed automatically.

Find out more here: <https://spring.io/blog/2015/06/17/devtools-in-spring-boot-1-3> and here: <https://t.co/td23nP73mt>

# Summary

You can make frontend development of the Spring Boot application much easier thanks to the techniques described in this article. But possibility of serving Thymeleaf templates and static resources of your Spring Boot application from outside the classpath in production could bring some advantages too. One of the example could be separating backend and frontend deployments.

# See also

- [HOW-TO: Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md)
- [Spring Boot and Thymeleaf with Maven on GitHub](https://github.com/kolorobot/spring-boot-thymeleaf)
