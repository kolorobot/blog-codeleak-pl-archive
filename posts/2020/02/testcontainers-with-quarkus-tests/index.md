---
title: "Quarkus tests with Testcontainers and PostgreSQL"
date: 2020-02-27T22:10:00.001+01:00
updated: 2020-03-15T22:09:25.992+01:00
author: "Rafał Borowiec"
tags: ["docker", "quarkus", "testing"]
original_url: https://blog.codeleak.pl/2020/02/testcontainers-with-quarkus-tests.html
---

# Quarkus tests with Testcontainers and PostgreSQL

[Testcontainers](https://www.testcontainers.org) is a Java library that allows integrating Docker containers in JUnit tests with ease. In a *Containerized World*, there is little sense to complicate the tests configuration with embedded databases and services. Instead, use run your services in Docker and let the Testcontainers manage this for you. So if you are need Redis, MongoDB or PostgreSQL in your tests - Testcontainers may become your good friend.

In this blog post you will learn how to configure Testcontainers to manage PostgreSQL instance in Quarkus integration tests.

*Table of Contents*

- [Dependencies](#dependencies)
- [Test datasource configuration](#test-datasource-configuration)
- [Initializing test database](#initializing-test-database)
  - [Using Flyway to initialize test database](#using-flyway-to-initialize-test-database)
  - [Using Testcontainers to initialize test database](#using-testcontainers-to-initialize-test-database)
- [Source code](#source-code)
- [See also](#see-also)

## Dependencies

In order to use Testcontainers with PostgreSQL you need to add the following dependencies to the `pom.xml`:

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.12.5</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <version>1.12.5</version>
    <scope>test</scope>
</dependency>
```

> Note: Testcontainers provides JUnit 5 plugin, but in the scenario presented in this article it is not needed.

## Test datasource configuration

The default PostgreSQL configuration in Quarkus application may look like below:

```
quarkus.datasource.url=jdbc:postgresql://localhost:5432/some-db
quarkus.datasource.driver=org.postgresql.Driver
quarkus.datasource.username=user
quarkus.datasource.password=password
```

By default, this configuration will be used in any active profile. The built-in profiles in Quarkus are: `dev`, `prod` and `test`. The `test` profile will be used every time you run the `@QuarkusTest`.

You can adjust `test` profile by providing the `%test.` prefix to the configuration properties in `src/main/application.properties` file. This allows to configure (and launch) PostgreSQL database container via **JDBC URL scheme**. To achieve this make sure to:

- set the driver to `org.testcontainers.jdbc.ContainerDatabaseDriver`. This *special* driver makes sure Docker container is created and run once we need a datasource in the application,
- set the dialect explicitly to `org.hibernate.dialect.PostgreSQL9Dialect` otherwise you get the exception while starting the application:

```
org.junit.jupiter.api.extension.TestInstantiationException: TestInstanceFactory [io.quarkus.test.junit.QuarkusTestExtension] failed to instantiate test class [pl.codeleak.samples.OwnerResourceTest]: io.quarkus.builder.BuildException: Build failure: Build failed due to errors
 [error]: Build step io.quarkus.hibernate.orm.deployment.HibernateOrmProcessor#build threw an exception: io.quarkus.deployment.configuration.ConfigurationError: Hibernate extension could not guess the dialect from the driver 'org.testcontainers.jdbc.ContainerDatabaseDriver'. Add an explicit 'quarkus.hibernate-orm.dialect' property.
 at io.quarkus.hibernate.orm.deployment.HibernateOrmProcessor.guessDialect(HibernateOrmProcessor.java:715)
```

- set the JDBC URL to `jdbc:tc:postgresql:latest:///dbname` so that Testcontainers knows which PostgreSQL version to use while running the container.

The complete configuration:

```
# initializes container for driver initialization
%test.quarkus.datasource.driver=org.testcontainers.jdbc.ContainerDatabaseDriver

# dialect must be set explicitly
%test.quarkus.hibernate-orm.dialect=org.hibernate.dialect.PostgreSQL9Dialect

# Testcontainers JDBC URL
%test.quarkus.datasource.url=jdbc:tc:postgresql:latest:///dbname
```

With the configuration in place, you can run the tests and observe that the test container is created for the test:

```
$ ./mvnw clean test

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running pl.codeleak.samples.OwnerResourceTest
2020-02-27 21:09:21,096 INFO  [io.qua.fly.FlywayProcessor] (build-8) Adding application migrations in path '/Users/rafal.borowiec/Projects/quarkus/quarkus-postgres-sample/target/classes/db/migration' using protocol 'file'
2020-02-27 21:09:23,084 INFO  [org.fly.cor.int.lic.VersionPrinter] (main) Flyway Community Edition 6.1.4 by Redgate
2020-02-27 21:09:23,176 INFO  [org.tes.doc.DockerClientProviderStrategy] (Agroal_1012722761) Loaded org.testcontainers.dockerclient.UnixSocketClientProviderStrategy from ~/.testcontainers.properties, will try it first
2020-02-27 21:09:23,658 INFO  [org.tes.doc.UnixSocketClientProviderStrategy] (Agroal_1012722761) Accessing docker with local Unix socket
2020-02-27 21:09:23,659 INFO  [org.tes.doc.DockerClientProviderStrategy] (Agroal_1012722761) Found Docker environment with local Unix socket (unix:///var/run/docker.sock)
2020-02-27 21:09:23,780 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) Docker host IP address is localhost
2020-02-27 21:09:23,815 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) Connected to docker:
  Server Version: 19.03.2
  API Version: 1.40
  Operating System: Docker Desktop
  Total Memory: 1998 MB
2020-02-27 21:09:23,957 INFO  [org.tes.uti.RegistryAuthLocator] (Agroal_1012722761) Credential helper/store (docker-credential-desktop) does not have credentials for quay.io
2020-02-27 21:09:24,857 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) Ryuk started - will monitor and terminate Testcontainers containers on JVM exit
2020-02-27 21:09:24,857 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) Checking the system...
2020-02-27 21:09:24,858 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) ✔︎ Docker server version should be at least 1.6.0
2020-02-27 21:09:25,040 INFO  [org.tes.DockerClientFactory] (Agroal_1012722761) ✔︎ Docker environment should have more than 2GB free disk space
2020-02-27 21:09:25,078 INFO  [🐳 [postgres:latest]] (Agroal_1012722761) Creating container for image: postgres:latest
2020-02-27 21:09:25,135 INFO  [org.tes.uti.RegistryAuthLocator] (Agroal_1012722761) Credential helper/store (docker-credential-desktop) does not have credentials for index.docker.io
2020-02-27 21:09:25,247 INFO  [🐳 [postgres:latest]] (Agroal_1012722761) Starting container with ID: b436fdabccbe51ba3e6d778d4429505473995d4185a200aef35c4c30b2159369
2020-02-27 21:09:25,779 INFO  [🐳 [postgres:latest]] (Agroal_1012722761) Container postgres:latest is starting: b436fdabccbe51ba3e6d778d4429505473995d4185a200aef35c4c30b2159369
2020-02-27 21:09:26,896 INFO  [🐳 [postgres:latest]] (Agroal_1012722761) Container postgres:latest started in PT3.731519S
2020-02-27 21:09:27,107 INFO  [org.fly.cor.int.dat.DatabaseFactory] (main) Database: jdbc:postgresql://localhost:32830/test (PostgreSQL 12.2)
2020-02-27 21:09:27,146 INFO  [org.fly.cor.int.sch.JdbcTableSchemaHistory] (main) Creating Schema History table "public"."flyway_schema_history" ...
2020-02-27 21:09:27,188 INFO  [org.fly.cor.int.com.DbMigrate] (main) Current version of schema "public": << Empty Schema >>
2020-02-27 21:09:27,193 INFO  [org.fly.cor.int.com.DbMigrate] (main) Migrating schema "public" to version 1.0.0 - Init
2020-02-27 21:09:27,201 INFO  [org.fly.cor.int.sql.DefaultSqlScriptExecutor] (main) DB: table "owners" does not exist, skipping
2020-02-27 21:09:27,226 INFO  [org.fly.cor.int.com.DbMigrate] (main) Successfully applied 1 migration to schema "public" (execution time 00:00.050s)
2020-02-27 21:09:27,726 INFO  [io.quarkus] (main) Quarkus 1.2.1.Final started in 5.761s. Listening on: http://0.0.0.0:8081
2020-02-27 21:09:27,727 INFO  [io.quarkus] (main) Profile test activated.
2020-02-27 21:09:27,727 INFO  [io.quarkus] (main) Installed features: [agroal, cdi, flyway, hibernate-orm, hibernate-orm-panache, hibernate-validator, jdbc-postgresql, narayana-jta, resteasy, resteasy-jackson]
[INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 10.091 s - in pl.codeleak.samples.OwnerResourceTest
2020-02-27 21:09:29,975 INFO  [io.quarkus] (main) Quarkus stopped in 0.689s
[INFO]
[INFO] Results:
[INFO]
[INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  15.375 s
[INFO] Finished at: 2020-02-27T21:09:30+01:00
[INFO] ------------------------------------------------------------------------
```

> See more on database configuration in the official documentation here: <https://www.testcontainers.org/modules/databases/>

## Initializing test database

You have several options to initialize the databse. You can initialize the database with `Flyway`, but you can also use Testcontainers to run the init script after database is started but before the connection is returned to the code.

### Using Flyway to initialize test database

With Flyway, the migration scripts can be adjusted only for the test profile the same way we adjusted the datasource - by adding the `%test.` prefix to the configuration properties. This way you can setup different migration files locations and/or you can configure different prefix for the migration files:

```
%test.quarkus.flyway.locations=test_db/migration
%test.quarkus.flyway.sql-migration-prefix=test_
```

With the above configuration you may need to create `test/src/resources/test_db/migration` and put in it for example `test_1.0.0_schema.sql` file (the name pattern is `test_version_description.sql`).

> Tip: Don’t forget to add Flyway Quarkus extension to the `pom.xml`.

### Using Testcontainers to initialize test database

If you don’t want to use Flyway in tests, you may initialize the database with the script loaded by Testcontainers. The file can be loaded either directly from the classpath or from any location. The only thing to do is to change the JDBC URL:

```
%test.quarkus.datasource.url=jdbc:tc:postgresql:latest:///dbname?TC_INITSCRIPT=file:src/main/resources/init_pg.sql
```

or

```
%test.quarkus.datasource.url=jdbc:tc:postgresql:latest:///dbname?TC_INITSCRIPT=classpath:init_pg.sql
```

## Source code

The source code for this article can be found on Github: [https://github.com/kolorobot/quarkus-postgres-sample](https://github.com/kolorobot/quarkus-postgres-sample/tree/testcontainers) (`testcontainers` branch)

## See also

- [Testcontainers](https://www.testcontainers.org)
- [Getting started with Quarkus - build PetClinic REST API](../../../2020/02/getting-started-with-quarkus/index.md)
- [Deploy Quarkus application to AWS Elastic Beanstalk](../../../2020/03/deploy-quarkus-application-to-elastic-beanstalk/index.md)
