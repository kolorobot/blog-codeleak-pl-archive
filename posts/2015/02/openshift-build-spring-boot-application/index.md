---
title: "Openshift: Build Spring Boot application on Wildfly 8.2.0 with Java 8"
date: 2015-02-20T00:00:00.000+01:00
updated: 2016-09-28T00:19:36.093+02:00
author: "Rafał Borowiec"
tags: ["openshift", "spring boot"]
original_url: https://blog.codeleak.pl/2015/02/openshift-build-spring-boot-application.html
---

# Openshift: Build Spring Boot application on Wildfly 8.2.0 with Java 8

![](boot.png)

OpenShift DIY cartridge is a great way to test unsupported languages on OpenShift. But it is not scalable (you can vote for Scalable DIY cartridge [here](https://openshift.uservoice.com/forums/258655-ideas/suggestions/6291504-scalable-diy-cartridge)) which makes it hard to use with production grade Spring Boot applications. But what if we deployed Spring Boot application to WildFly Application Server? Spring Boot can run with embedded servlet container like Tomcat or much faster Undertow, but it also can be deployed to a standalone application server. This would mean that it can be also deployed to WildFly application server that is supported by OpenShift. Let’s see how easy is to get started with creating a Spring Boot application from scratch and deploy it to WildFly 8.2 on OpenShift.

**Note**: While browsing OpenShift [documentation](https://developers.openshift.com/en/wildfly-overview.html) one can think that on WildFly 8.1 and Java 7 is supported (as of time of writing this blog post). But this is fortunately not true anymore: WildFly 8.2 and Java 8 will work fine and it is default in fact!. This was the first time when I was happy about documentation being outdated.

**Update**: If you are looking for a quick start, without the step by step walkthrough have a look here: [Quick Start: Spring Boot and WildfFly 8.2 on OpenShift](../../../2015/02/quick-start-spring-boot-and-wildffly-82/index.md)

## Prerequisite

Before you can start building the application, you need to have an OpenShift free account and client tools (`rhc`) installed.

## Create WildFly application

To create a WildFly application using client tools, type the following command:

```
rhc create-app boot jboss-wildfly-8 --scaling
```

`jboss-wildfly-8` cartridge is described as WildFly Application Server 8.2.0.Final. Scaling option is used as it will be impossible to set it later (vote [here](https://openshift.uservoice.com/forums/258655-ideas/suggestions/6521350-ability-to-scale-existing-applications-without-i))

When the application is created you should see username and password for an administration user created for you. Please store these credentials to be able to login to the WildFly administration console.

## Template Application Source code

OpenShift creates a template project. The project is a standard Maven project. You can browse through `pom.xml` and see that Java 8 is used by default for this project. In addition, there are two non standard folders created: `deployments`, that is used to put the resulting archive into, and `.openshift` with OpenShift specific files. Please note `.opensift/config`. This is the place where WildFly configuration is stored.

## Spring Boot dependencies

As the dependency management Spring IO Platform will be used. The main advantage of using Spring IO Platform is that it simplifies dependency management by providing versions of Spring projects along with their dependencies that are tested and known to work together. Modify the `pom.xml` by adding:

```xml
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

Now, Spring Boot dependencies can be added. Please note that since the application will be deployed to WildFly, we need to explicitly remove dependency on Tomcat.:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
```

## Configure the application

### Initialize Spring Boot Application

Having all dependencies, we can add application code. Create `Application.java` in `demo` package. The `Application` class’s work is to initiate Spring Boot application, so it must extend from `SpringBootServletInitializer` and be annotated with `@SpringBootApplication`

```java
package demo;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.web.SpringBootServletInitializer;

@SpringBootApplication
public class Application extends SpringBootServletInitializer {

}
```

### @Entity, @Repository, @Controller

Spring Data JPA, part of the larger Spring Data family, makes it easy to easily implement JPA based repositories. For those who are not familiar with the project please visit: <http://projects.spring.io/spring-data-jpa/>.

Domain model for this sample project is just a `Person` with some basic fields:

```java
@Entity
@Table(name = "people")
public class Person {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    protected Integer id;

    @Column(name = "first_name")
    @NotEmpty
    protected String firstName;

    @Column(name = "last_name")
    @NotEmpty
    protected String lastName;

    @Column(name = "address")
    @NotEmpty
    private String address;

    @Column(name = "city")
    @NotEmpty
    private String city;

    @Column(name = "telephone")
    @NotEmpty
    @Digits(fraction = 0, integer = 10)
    private String telephone;

}
```

The `Person` needs a `@Repository`, so we can createa basic one using Spring’s Data repository. Spring Data repositories reduce much of the boilerplate code thanks to a simple interface definition:

```java
@Repository
public interface PeopleRepository extends PagingAndSortingRepository<Person, Integer> {
    List<Person> findByLastName(@Param("lastName") String lastName);
}
```

With the domain model in place some test data can be handy. The easiest way is to provide a `data.sql` file with the SQL script to be executed on the application start-up.

Create `src/main/resources/data.sql` containing initial data for the `people` table (see below). Spring Boot will pick this file and run against configured Data Source. Since the Data Source used is connecting to H2 database, the proper SQL syntax must be used:

```sql
INSERT INTO people VALUES (1, 'George', 'Franklin', '110 W. Liberty St.', 'Madison', '6085551023');
```

Having Spring Data JPA repository in place, we can create a simple controller that exposes data over REST:

```java
@RestController
@RequestMapping("people")
public class PeopleController {

    private final PeopleRepository peopleRepository;

    @Inject
    public PeopleController(PeopleRepository peopleRepository) {
        this.peopleRepository = peopleRepository;
    }

    @RequestMapping
    public Iterable<Person> findAll(@RequestParam Optional<String> lastName) {
        if (lastName.isPresent()) {
            return peopleRepository.findByLastName(lastName.get());
        }
        return peopleRepository.findAll();
    }
}
```

`findAll` method accepts optional `lastName` parameter that is bound to Java’s 8 `java.util.Optional`.

### Start page

The project generated by OpenShift during project setup contain `webapp` folder with some static files. These files can be removed and `index.html` can be modified:

```html
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>OpenShift</title>
</head>
<body>
<form role="form" action="people">
    <fieldset>
        <legend>People search</legend>
        <label for="lastName">Last name:</label>
        <input id="lastName" type="text" name="lastName" value="McFarland"/>
        <input type="submit" value="Search"/>
    </fieldset>
</form>
<p>
    ... or: <a href="people">Find all ...</a>
</p>
</body>
</html>
```

It is just a static page, but I noticed that application will not start if there is not default mapping (`/`) or if returns code different than `200`. Normally, there will be always a default mapping.

### Configuration

Create `src/main/resources/application.properties` and put the following values:

- `management.context-path=/manage`: actuator default management context path is `/`. This is changed to `/manage`, because OpenShift exposes `/health` endpoint itself that covers Actuator’s `/health` endpoint .
- `spring.datasource.jndi-name=java:jboss/datasources/ExampleDS`: since the application uses Spring Data JPA, we want to bind to the server’s Data Source via JNDI. Please look at `.openshift/config/standalone.xml` for other datasources. This is important if you wish to configure MySql or PostgreSQL to be used with your application. Read more about connecting to JNDI Data Source in Spring Boot here: <http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#boot-features-connecting-to-a-jndi-datasource>
- `spring.jpa.hibernate.ddl-auto=create-drop`: create structure of the database based on the provided entities.

## Deploying to OpenShift

The application is ready to be pushed to the repository. Commit your local changes and then push it to remote:

```
git push
```

The initial deployment (build and application startup) will take some time (up to several minutes). Subsequent deployments are a bit faster. You can now browse to: <http://appname-yournamespace.rhcloud.com/> and you should see the form:

Clicking search with default value will get record with id = 3:

```
[
    {
        "id": 3,
        "firstName": "2693 Commerce St.",
        "lastName": "McFarland",
        "address": "Eduardo",
        "city": "Rodriquez",
        "telephone": "6085558763"
    }
]
```

Navigating to <http://appname-yournamespace.rhcloud.com/people> will return all records from the database.

## Going Java 7

If you want to use Java 7 in your project, instead of default Java 8, rename `.openshift/markers/java8` to `.openshift/markers/java7` and changte `pom.xml` accordingly:

```xml
<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.7</maven.compiler.source>
    <maven.compiler.target>1.7</maven.compiler.target>
    <maven.compiler.fork>true</maven.compiler.fork>
</properties>
```

Please note `maven.compiler.executable` was removed. Don’t forget to change the `@Controller`’s code and make it Java 7 compatible.

## Summary

In this blog post you learned how to configure basic Spring Boot application and run it on OpenShift with WildfFly 8.2 and Java 8. OpenShift scales the application with the web proxy HAProxy. OpenShift takes care of automatically adding or removing copies of the application to serve requests as needed.

## Resources

- <https://github.com/kolorobot/openshift-wildfly-spring-boot> - source code for this blog post.
