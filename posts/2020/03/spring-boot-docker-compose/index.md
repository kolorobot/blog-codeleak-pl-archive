---
title: "Docker Compose for Spring Boot application with PostgreSQL"
date: 2020-03-23T20:38:00.000+01:00
updated: 2020-03-30T23:42:31.732+02:00
author: "Rafał Borowiec"
tags: ["docker", "spring boot"]
original_url: https://blog.codeleak.pl/2020/03/spring-boot-docker-compose.html
---

# Docker Compose for Spring Boot application with PostgreSQL

In this blog post you will learn how to configure Spring Boot application with PostgreSQL for running with Docker Compose.

This blog post covers:

- Spring Boot application `Dockerfile` configuration with clean separation between dependencies and resources
- `Docker Compose` configuration for running the application with PostgreSQL

# Prerequisites

- Docker
- Java 13
- Terminal
- httpie (or curl)

# Application

- Generate the Maven based Spring Boot application with `Spring Web`, `Spring Data JPA`, `Spring Data REST`, `PostgreSQL JDBC Driver` dependencies.
- Add Testcontainers to use dockerized database in integration tests. You can read more about using Testcontainers with Spring Boot in this article: [Spring Boot tests with Testcontainers and PostgreSQL, MySQL or MariaDB](../../../2020/03/spring-boot-tests-with-testcontainers/index.md)

> The source code for this article can be found on Github: <https://github.com/kolorobot/spring-boot-tc>

# `Dockerfile`

- Create `Dockerfile`
- Base Docker image uses `Alpine` Linux:

```
FROM openjdk:13-alpine
```

- Do not run the application as `root`:

```
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
```

- Do not deploy the fat-jar into the container, but rather split dependencies and application classes and resources into separate layers:

```
ARG DEPENDENCY=target/dependency
COPY ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY ${DEPENDENCY}/META-INF /app/META-INF
COPY ${DEPENDENCY}/BOOT-INF/classes /app
```

> Note: `ARG` can be used to adjust the directory, in case you you have Gradle based project: `docker build --build-arg DEPENDENCY=build/dependency -t spring-boot-tc .`

- Run the application inside the containers by pointing the main class and the libs in the `java` command:

```
ENTRYPOINT ["java","-cp","app:app/lib/*","pl.codeleak.samples.springboot.tc.SpringBootTestcontainersApplication"]
```

The complete `Dockerfile`:

```
FROM openjdk:13-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
ARG DEPENDENCY=target/dependency
COPY ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY ${DEPENDENCY}/META-INF /app/META-INF
COPY ${DEPENDENCY}/BOOT-INF/classes /app
ENTRYPOINT ["java","-cp","app:app/lib/*","pl.codeleak.samples.springboot.tc.SpringBootTestcontainersApplication"]
```

> New to Docker?  Docker explained in 12 minutes: <https://www.youtube.com/watch?v=YFl2mCHdv24>

# Docker Compose

- Create `docker-compose.yml`
- We will have two `services`: `db` for PostgreSQL database and `app` for the application
  - `db` service will use the `postgres` image from a public repository, it will expose port `5432` to the host and it will pass the environment properties `POSTGRES_*` to the container to setup the database name, user and password.
  - `app` service will use the local build we created earlier, it will expose port `9000` to the host and it will pass the environment properties that will override the datasource configuration of the application (`application.properties`). The `app` service will depend on `db` service. The datasource URL uses the `db` as hostname which reflects the name of the `db` service.

The complete `docker-compose.yml`:

```
version: '3'

services:
  db:
    image: "postgres"
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: tc
      POSTGRES_USER: tc
      POSTGRES_PASSWORD: tc
  app:
    build: .
    ports:
      - "9000:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db/tc
      SPRING_DATASOURCE_USERNAME: tc
      SPRING_DATASOURCE_PASSWORD: tc
    depends_on:
      - db
```

> New to Docker Compose? Docker Compose explained in 12 min: <https://www.youtube.com/watch?v=Qw9zlE3t8Ko>

# Running the application

- Package the application

```
$ ./mvnw clean package
```

> To skip the tests use: `-DskipTests=true`

- Extract libraries from `fat-jar`

```
$ mkdir -p target/dependency && (cd target/dependency; jar -xf ../*.jar)
```

- Run with `docker-compose`

```
$ docker-compose build && docker-compose up
```

- Verify the application is running and responding to requests

```
$ http get :9000/owners

HTTP/1.1 200
Connection: keep-alive

{
    "_embedded": {
        "owners": []
    },
    "_links": {
        "profile": {
            "href": "http://localhost:8080/profile/owners"
        },
        "self": {
            "href": "http://localhost:8080/owners{?page,size,sort}",
            "templated": true
        }
    },
    "page": {
        "number": 0,
        "size": 20,
        "totalElements": 0,
        "totalPages": 0
    }
}
```

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/spring-boot-tc>

# References

- <https://spring.io/guides/gs/spring-boot-docker/>
- <https://openliberty.io/blog/2018/06/29/optimizing-spring-boot-apps-for-docker.html>

# See also

- [Spring Boot tests with Testcontainers and PostgreSQL, MySQL or MariaDB](../../../2020/03/spring-boot-tests-with-testcontainers/index.md)
- [Spring Boot testing with JUnit 5](../../../2019/09/spring-boot-testing-with-junit-5/index.md)
- [macOS: essential tools for (Java) developer](../../../2020/01/macos-essential-tools-for-java-developer/index.md)
