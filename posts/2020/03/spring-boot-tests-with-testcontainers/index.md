---
title: "Spring Boot tests with Testcontainers and PostgreSQL, MySQL or MariaDB"
date: 2020-03-30T23:40:00.000+02:00
updated: 2020-03-30T23:40:18.296+02:00
author: "Rafał Borowiec"
tags: ["docker", "spring boot"]
original_url: https://blog.codeleak.pl/2020/03/spring-boot-tests-with-testcontainers.html
---

# Spring Boot tests with Testcontainers and PostgreSQL, MySQL or MariaDB

[Testcontainers](https://www.testcontainers.org) is a Java library that allows integrating Docker containers in JUnit tests with ease. In a *Containerized World*, there is little sense to complicate the tests configuration with embedded databases and services. Instead, use run your services in Docker and let the Testcontainers manage this for you.

In this blog post you will learn how to configure [Testcontainers](https://www.testcontainers.org) to run PostgreSQL, MySQL and MariaDB in Spring Boot 2 integration tests.

This blog post covers:

- Testcontainers configuration (via **JDBC URL Scheme**) for Spring Boot 2 tests with *PostgreSQL*, *MySQL* and *MariaDB*
- Testcontainers in `@DataJpaTest`

*Table of Contents*

- [Dependencies](#dependencies)
- [Test datasource configuration](#test-datasource-configuration)
  - [PostgreSQL configuration:](#postgresql-configuration)
  - [MySQL configuration:](#mysql-configuration)
  - [MariaDB configuration:](#mariadb-configuration)
- [Initializing test database with Testcontainers](#initializing-test-database-with-testcontainers)
- [@DataJpaTest](#datajpatest)
- [@SpringBootTest](#springboottest)
- [Summary](#summary)
- [Source code](#source-code)
- [See also](#see-also)

## Dependencies

In order to use Testcontainers add the following dependencies to the `pom.xml` (assuming Maven based project):

```xml
<properties>
    <org.testcontainers.version>1.12.5</org.testcontainers.version>
</properties>

<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>${org.testcontainers.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>DATABASE</artifactId>
    <version>${org.testcontainers.version}</version>
    <scope>test</scope>
</dependency>
```

where the `DATABASE` is one of `postgresql`, `mysql`, `mariadb`.

> Note: Testcontainers provides JUnit 5 (Jupiter) plugin, but in the scenario presented in this pluging won’t be needed.

## Test datasource configuration

Steps to configure Testcontainers for Spring Boot tests:

- Set the driver to `org.testcontainers.jdbc.ContainerDatabaseDriver` which is a Testcontainers JDBC proxy driver. This driver makes will be responsible for starting the required Docker container when the datasource is initialized.
- Set the dialect explicitly to implementation of the dialect for your database otherwise you get the exception while starting the application. This step is required when you use *JPA* in your application (via *Spring Data JPA*)
- Set the JDBC URL to `jdbc:tc:<database-image>:<version>:///` so that Testcontainers knows which database image to use.

### PostgreSQL configuration:

The complete configuration:

```
spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver
spring.datasource.url=jdbc:tc:postgresql:9.6:///
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQL9Dialect
```

### MySQL configuration:

```
spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver
spring.datasource.url=jdbc:tc:mysql:8:///
spring.jpa.database-platform=org.hibernate.dialect.MySQL8Dialect
```

### MariaDB configuration:

```
spring.datasource.driver-class-name=org.testcontainers.jdbc.ContainerDatabaseDriver
spring.datasource.url=jdbc:tc:mariadb:10.3:///
spring.jpa.database-platform=org.hibernate.dialect.MariaDB103Dialect
```

> See more on database configuration in the official documentation here: <https://www.testcontainers.org/modules/databases/>

## Initializing test database with Testcontainers

You may initialize the database with the script loaded by Testcontainers. The file can be loaded either directly from the classpath or from any location. The only thing to do is to change the JDBC URL:

```
spring.datasource.url=jdbc:tc:postgresql:9.6:///?TC_INITSCRIPT=file:src/main/resources/init_db.sql
```

or

```
spring.datasource.url=jdbc:tc:postgresql:9.6:///?TC_INITSCRIPT=classpath:init_db.sql
```

## @DataJpaTest

In order to use TC in `@DataJpaTest` you need to make sure that the application defined (auto-configured) datasource is used. You can do it easily by annotating your test with `@AutoConfigureTestDatabase` as shown below:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class OwnerRepositoryTests {

    @Autowired
    private OwnerRepository ownerRepository;

    @Test
    void findAllReturnsJohnDoe() { // as defined in tc-initscript.sql
        var owners = ownerRepository.findAll();
        assertThat(owners.size()).isOne();
        assertThat(owners.get(0).getFirstName()).isEqualTo("John");
        assertThat(owners.get(0).getLastName()).isEqualTo("Doe");
    }
}
```

## @SpringBootTest

`@SpringBootTest` will use application defined datasource, so no additional changes are needed.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
public class OwnerResourceTests {

    @Autowired
    WebApplicationContext wac;

    @Test
    void findAllReturnsJohnDoe() throws Exception {
        given()
                .webAppContextSetup(wac)
        .when()
                .get("/owners")
        .then()
                .status(HttpStatus.OK)
                .body(
                        "_embedded.owners.firstName", containsInAnyOrder("John"),
                        "_embedded.owners.lastName", containsInAnyOrder("Doe")
                );
    }
}
```

## Summary

You have just learned the easiest way to configure PostgreSQL, MySQL and MariaDB with Testcontainers in Spring Boot integration tests. This solution is well suited for rather simple setup. If you need more control over the Docker images, please consult official [Testcontainers](https://www.testcontainers.org) documentation.

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/spring-boot-tc>

## See also

- [Spring Boot testing with JUnit 5](../../../2019/09/spring-boot-testing-with-junit-5/index.md)
- [Docker Compose for Spring Boot application with PostgreSQL](../../../2020/03/spring-boot-docker-compose/index.md)
