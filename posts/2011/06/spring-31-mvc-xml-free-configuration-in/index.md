---
title: "Spring 3.1 MVC: xml-free configuration in Servlet 3.0 environment"
date: 2011-06-16T23:55:00.001+02:00
updated: 2016-01-31T22:06:40.484+01:00
author: "Codeleak.pl"
tags: ["spring"]
original_url: https://blog.codeleak.pl/2011/06/spring-31-mvc-xml-free-configuration-in.html
---

# Spring 3.1 MVC: xml-free configuration in Servlet 3.0 environment

Starting from Spring 3.1.0.M2 you can configure Servlet Context programatically in Servlet 3.0 environment (Tomcat 7 for example), with no **web.xm**l and **no xml** at all. This article demonstrate working Hello World example with xml-free web application configuration.

**Update:** See Spring MVC Quickstart Maven Archetype (no-xml Spring MVC 4 web application): <https://github.com/kolorobot/spring-mvc-quickstart-archetype> to get started with Spring MVC. **The project is actively maintained** and just got updated: [http://blog.codeleak.pl/2016/01/spring-mvc-4-quickstart-maven-archetype.html](../../../2016/01/spring-mvc-4-quickstart-maven-archetype/index.md)

To start with the project I used STS and I created new Template Project (`File > New > Spring Template Project > Spring MVC Project`). Once the project was created I made some small modification to the POM file:

- removed Spring Roo dependencies - why they are there - I don't know
- changed Spring version to 3.1.0.M2 - to have new functionality in place
- change maven-war-plugin configuration - so the build will not fail on missing web.xml file:

  ```xml
  <plugin>
   <groupid>org.apache.maven.plugins</groupId>
   <artifactid>maven-war-plugin</artifactId>
   <configuration>
    <warname>spring-mvc-3.1-demo</warName>
    <failonmissingwebxml>false</failOnMissingWebXml>
   </configuration>
  </plugin>
  ```

And to the project structure:

- remove /WEB-INF/web.xml

Note: It is not required to remove web.xml. If you would like to leave it - make sure it looks like this:

```xml
<web-app xmlns="http://java.sun.com/xml/ns/javaee"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_3_0.xsd"
      version="3.0"> 
</web-app>
```

Having project fixed it is time to create configuration files. Let's start with web application initializer that will bootstrap Servlet Context and the Dispatcher Servlet:

```java
public class Initializer implements WebApplicationInitializer {
 public void onStartup(ServletContext servletContext)
   throws ServletException {
  AnnotationConfigWebApplicationContext mvcContext = new AnnotationConfigWebApplicationContext();
  mvcContext.register(MvcConfig.class);

  ServletRegistration.Dynamic dispatcher = servletContext.addServlet(
    "dispatcher", new DispatcherServlet(mvcContext));
  dispatcher.setLoadOnStartup(1);
  dispatcher.addMapping("/app/*");
 }
}
```

Initializer is going to be automatically bootstrapped by any Servlet 3.0 container. I checked that with Tomcat 7 server. While bootstrapping you will find following log entries:  
  
 `INFO : org.springframework.web.SpringServletContainerInitializer - Delegating ServletContext to the following WebApplicationInitializer instances: [pl.codeleak.springmvc31demo.config.Initializer@1b4cd65]`

Next step is to configure Spring MVC. I do that in following class:

```java
@Configuration
@EnableWebMvc
@ComponentScan(basePackages = "pl.codeleak.springmvc31demo.web")
public class MvcConfig {
 @Bean
 public InternalResourceViewResolver configureInternalResourceViewResolver() {
  InternalResourceViewResolver resolver = new InternalResourceViewResolver();
  resolver.setPrefix("/WEB-INF/views/");
  resolver.setSuffix(".jsp");
  return resolver;
 }
}
```

@EnableWebMvc annotation used together with @Configuration enables default Spring MVC configuration, equivalent to  `<mvc:annotation-driven />` . With @ComponentScan annotation we make sure our @Controller will be added to the application context. The configuration class also defines one @Bean: our default view resolver.

The @Controller generated from template I leave with no changes:

```java
@Controller
public class HomeController {
 
 private static final Logger logger = LoggerFactory.getLogger(HomeController.class);

 @RequestMapping(value = "/", method = RequestMethod.GET)
 public String home() {
  logger.info("Welcome home!");
  return "home";
 }
}
```

Now it is time to run our Hello World example on Tomcat 7 server and see immediate result in the browser:  
  
**Hello World!**

I must admit I like recent configuration changes in Spring MVC. It is easy to bootstrap the application with no xml files in place. Of course, this is not everything that Spring MVC 3.1.0 brings to the developers. To see more details checkout this post: [http://blog.springsource.com/2011/06/13/spring-3-1-m2-spring-mvc-enhancements-2](http://blog.springsource.com/2011/06/13/spring-3-1-m2-spring-mvc-enhancements-2/)

You may be also interested in getting started with Spring Boot and Thymeleaf using Maven. Spring Boot is a great piece of software allowing you to bootstrap Spring application within a few seconds. Check this post: [HOW-TO: Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md)
