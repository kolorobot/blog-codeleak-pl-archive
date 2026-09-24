---
title: "HOW-TO: Spring Boot and Thymeleaf with Maven"
date: 2014-04-13T21:18:00.000+02:00
updated: 2016-12-06T22:30:49.419+01:00
author: "Rafał Borowiec"
tags: ["intellij", "spring", "spring boot", "thymeleaf"]
original_url: https://blog.codeleak.pl/2014/04/how-to-spring-boot-and-thymeleaf-with-maven.html
---

# HOW-TO: Spring Boot and Thymeleaf with Maven

Spring Boot is a great piece of software allowing you to bootstrap Spring application within a few seconds. And it really works. As little configuration as possible to get started. And still possible to change the defaults. Let's see how easily is to bootstrap Spring MVC with Thymeleaf and Maven and work with it in IntelliJ.

*Update (06/12/2016):* Source code updated for this article: [Spring Boot and Thymeleaf: Reload templates and static resources without restarting the application](../../../2016/12/thymeleaf-reload-templates-and-static-resources/index.md)

*Update (24/9/2016):* Source code and article updated. Minor fixes, configuration changes, adjusting to Spring 4.3

*Update (25/4/2016):* Source code updated: Maven 3 Wrapper included and basic documentation updated

*Update (21/3/2016):* Dependencies got updated: io.spring.platform, bootstrap, jquery, assertj and selenium

## Basic setup Spring MVC + Thymeleaf with Maven

Make sure you have Maven 3 installed with the following command: `mvn --version`. Navigate to the directory you want to create your project in and execute Maven archtetype:

```
mvn archetype:generate -DarchetypeArtifactId=maven-archetype-quickstart -DgroupId=pl.codeleak.demos.sbt -DartifactId=spring-boot-thymeleaf -interactiveMode=false
```

The above command will create a new directory `spring-boot-thymeleaf`. Now you can import it to your IDE. In my case this is IntelliJ.  
The next step is to configure the application. Open `pom.xml` and add a parent project:
Values from the parent project will be the default for this project if they are left unspecified.  
The next step is to add web dependencies. In order to do so, I firstly removed all previous dependencies (junit 3.8.1 actually) and added the below dependencies:

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-thymeleaf</artifactId>
    </dependency>
</dependencies>
```

Now, wait a second until Maven downloads the dependencies and run `mvn dependency:tree` to see what dependencies are included.  
The next thing is a packaging configuration. Let's add Spring Boot Maven Plugin:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

With the above steps, the basic configuration is ready. Now we can run the application. Spring Boot Maven Plugin offers two goals `run` and `repackage`. So let's run the application by using `mvn spring-boot:run`. The command should produce `Hello World!`. Please note, that the `App` class has `main` method. So in fact, you can run this class in IntellJ (or any other IDE).

```
Hello World!
```

But wait a moment. This is not the web application. So let's modify the `App` class so it is the entry point to the Spring Boot application:

```java
package pl.codeleak.demos.sbt;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class);
    }
}
```

In addition to the above, I would remove the `AppTest` as it sucks (it was created by the maven-archetype-quickstart)! Now we can run the application again to see what happens:

```
java.lang.IllegalStateException: Cannot find template location: class path resource [templates/] (please add some templates or check your Thymeleaf configuration)
```

Clear. Let's add some Thymeleaf templates then.

## Where to put Thymeleaf templates?

The default place for templates is ... `templates` available in classpath. So we need to put at least one template into `src/main/resources/templates` directory. Let's create a simple one:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello Spring Boot!</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
<p>Hello Spring Boot!</p>
</body>
</html>
```

Running the application again will start embedded Tomcat with our application on port 8080:

```
Tomcat started on port(s): 8080/http
```

Ok. But something is missing. When we navigate to `localhost:8080` we will see `404` page. Of course! There are no controllers yet. So let's create one:

```java
package pl.codeleak.demos.sbt.home;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
class HomeController {

    @GetMapping("/")
    String index() {
        return "index";
    }
}
```

After running the application again you should be able to see `Hello Spring Boot!` page!

## Adding static resources

Similarly to Thymeleaf templates, static resources are served from classpath by default. We may put CSS files to `src/main/resources/static/css`, JavaScript files to `src/main/resources/static/js` etc.   
In Thymeleaf template we reference them like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello Spring Boot!</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link href="../static/css/core.css"
          th:href="@{/css/core.css}"
          rel="stylesheet" media="screen" />
</head>
<body>
<p>Hello Spring Boot!</p>
</body>
</html>
```

### Using WebJars

The above approach works perfectly fine. But in case you are interested in better client side libraries management, you can use WebJars. *WebJars are client side web libraries (e.g. jQuery & Bootstrap) packaged into JAR (Java Archive) files.*

Spring Boot suppors WebJars out of the box. You don't need to worry about the configuration, you just need to add Maven dependencies to pom.xml:

```xml
<dependency>
    <groupId>org.webjars</groupId>
    <artifactId>bootstrap</artifactId>
    <version>3.2.0</version>
</dependency>
<dependency>
    <groupId>org.webjars</groupId>
    <artifactId>jquery</artifactId>
    <version>2.1.1</version>
</dependency>
```

And reference the libraries in templates like below:

```html
<link href="http://cdn.jsdelivr.net/webjars/bootstrap/3.2.0/css/bootstrap.min.css"
      th:href="@{/webjars/bootstrap/3.2.0/css/bootstrap.min.css}"
      rel="stylesheet" media="screen" />

<script src="http://cdn.jsdelivr.net/webjars/jquery/2.1.1/jquery.min.js"
        th:src="@{/webjars/jquery/2.1.1/jquery.min.js}"></script>
```

As you can see, for static prototyping libraries are downloaded from CDN.

## Converting packaging from jar to war

But what if we want to run the application as plain web app and provide it as a war package? It is fairly easy with Spring Boot. Firstly, we need to convert type of packaging in `pom.xml` from `jar` to `war` (packaging element). Secondly - make that Tomcat is a provided dependency:

```xml
<packaging>war</packaging>

[...]

<!DOCTYPE html>
<html>
<head>
    <title>Hello Spring Boot!</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
<p>Hello Spring Boot!</p>
</body>
</html>
```

The last step is to bootstrap a servlet configuration. Create `Init` class and inherit from `SpringBootServletInitializer`:

```java
package pl.codeleak.demos.sbt;

import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.web.SpringBootServletInitializer;

public class ServletInitializer extends SpringBootServletInitializer {
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(App.class);
    }
}
```

We can check if the configuration works with Maven: `mvn clean package`. The war file should be created:

```
Building war: C:\Projects\demos\spring-boot-thymeleaf\target\spring-boot-thymeleaf-1.0-SNAPSHOT.war
```

Use Maven to start the application from war file directly: `java -jar target\spring-boot-thymeleaf-1.0-SNAPSHOT.war`   
Having a war project we can run the application in IntelliJ. After we changed the packaging, IntellJ should detect the changes in the project and add a web facet to it. The next step is to configure Tomcat server and run it. Navigate to `Edit Configurations` and add Tomcat server with exploded war artifact. Now you can run the application as any other web application.

## Reloading Thymeleaf templates

Since the application running on local Tomcat server in IntelliJ we may reload static resources (e.g. css files) without restarting the server. But by default, Thymeleaf caches the templates, so in order to update Thymeleaf templates we need to change this behaviour. To do this, add `application.properties` to `src/main/resources` directory with the following property: `spring.thymeleaf.cache=false`. Restart the server and from now on you can reload Thymeleaf templates without restarting the server.

## Changing the other configuration defaults

Cache configuration is not the only available configuration we can adjust. Please look at the `ThymeleafAutoConfiguration` class to see what other things you can change. To mention a few: `spring.thymeleaf.mode`, `spring.thymeleaf.encoding`.

## Final thoughts

Spring Boot simplifies bootstrapping web application. With just couple of steps you have fully working web application that can be self-contained or can run in any servlet environment. Instead of learning Spring configuration you may focus on development. To learn further about Spring Boot read the manual and check Spring guides that provide many useful getting started tutorials. Enjoy!

## *[Update]* Using Spring Initializr

With Spring Initializr located at [http://start.spring.io](http://start.spring.io/) you can bootstrap the application much faster! Just select appropriate options in the form and download the project. That's a matter of seconds to have either Maven or Gradle, Web or Jar, Java 6, 7 or 8 in your new Spring Boot project.

## *[Update]* Introducing Spring IO Platform

*Spring IO Platform brings together the core Spring APIs into a cohesive platform for modern applications.* The main advantage is that it simplifies dependency management by providing versions of Spring projects along with their dependencies that are tested and known to work together.

*Note (24/09/2016):* The disadvantage is the Spring IO Platform waits longer for updates thnt e.g. Spring Boot. So for me to test newest version is easier to stick to spring-boot-starter-parent. The below code can be found in the repository, but is it commented out.

```xml
    <!-- Spring IO Platform for dependency management -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>io.spring.platform</groupId>
                <artifactId>platform-bom</artifactId>
                <version>1.1.1.RELEASE</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
```

The code in GitHub was updated.

## *[Update]* Integration testing with Selenium

Web integration tests allow integration testing of Spring Boot application without any mocking. By using @WebIntegrationTest and @SpringApplicationConfiguration we can create tests that loads the application and listen on normal ports. This small addition to Spring Boot makes much easier to create integration tests with Selenium WebDriver. The full article: [http://blog.codeleak.pl/2015/03/spring-boot-integration-testing-with.html](../../../2015/03/spring-boot-integration-testing-with/index.md)

## *[Update]* Java 8 Date & Time support

If you want to work with Java 8 Date & Time objects in your views you may want to utilize thymeleaf-extras-java8time - Thymeleaf module for Java 8 Date & Time API. Read this article to see how to do it: [http://blog.codeleak.pl/2015/11/how-to-java-8-date-time-with-thymeleaf.html](../../../2015/11/how-to-java-8-date-time-with-thymeleaf/index.md)

## References

- [Spring Boot Thymeleaf project sources](https://github.com/kolorobot/spring-boot-thymeleaf)
- [Spring Boot reference materials and articles](../../../p/spring-boot/index.md)
- [Spring Boot Reference Guide](http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring guides](http://spring.io/guides)
- [Thymeleaf project](http://www.thymeleaf.org/)
