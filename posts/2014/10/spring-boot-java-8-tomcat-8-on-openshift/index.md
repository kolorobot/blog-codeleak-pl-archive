---
title: "Spring Boot / Java 8 / Tomcat 8 on Openshift with DIY"
date: 2014-10-17T23:59:00.002+02:00
updated: 2016-07-20T22:20:08.088+02:00
author: "Rafał Borowiec"
tags: ["openshift", "spring boot"]
original_url: https://blog.codeleak.pl/2014/10/spring-boot-java-8-tomcat-8-on-openshift.html
---

# Spring Boot / Java 8 / Tomcat 8 on Openshift with DIY

DIY cartridge is an experimental cartridge that provides a way to test unsupported languages on OpenShift. It *provides a minimal, free-form scaffolding which leaves all details of the cartridge to the application developer*. This blog post illustrates the use of Spring Boot / Java 8 / Tomcat 8 application with PostgreSQL service bound to it.

## Change Log

- 20/07/2016 - Spring Boot 1.3.6. Fixed loading initial data. Several other fixed to the source code.

# Creating new application

## Prerequisite

Before we can start building the application, we need to have an OpenShift free account and client tools installed.

## Step 1: Create DIY application

To create an application using client tools, type the following command:

```
rhc app create boot diy-0.1
```

This command creates an application *boot* using *DIY* cartridge and clones the repository to *boot* directory.

## Step 2: Add PostgreSQL cartridge to application

The application we are creating will use PostgreSQL database, hence we need to add appropriate cartridge to the application:

```
rhc cartridge add postgresql-9.2 --app boot
```

After creating the cartridge, it is possible to check its status with the following command:

```
rhc cartridge status postgresql-9.2 --app boot
```

## Step 3: Delete Template Application Source code

OpenShift creates a template project that can be freely removed:

```
git rm -rf .openshift README.md diy misc
```

Commit the changes:

```
git commit -am "Removed template application source code"
```

## Step 4: Pull Source code from GitHub

```
git remote add upstream https://github.com/kolorobot/openshift-diy-spring-boot-sample.git
git pull -s recursive -X theirs upstream master
```

## Step 5: Push changes

The basic template is ready to be pushed:

```
git push
```

The initial deployment (build and application startup) will take some time (up to several minutes). Subsequent deployments are a bit faster, although starting Spring Boot application may take even more than 2 minutes on small Gear:

```
Tomcat started on port(s): 8080/http
Started Application in 125.511 seconds
```

You can now browse to: <http://boot-yournamespace.rhcloud.com/manage/health> and you should see:

```
{
    "status": "UP",
    "database": "PostgreSQL",
    "hello": 1
}
```

You can also browser the API. To find out what options you have, navigate to the root of the application. You should see the resource root with links to available resources:

```json
{
  "_links" : {
    "person" : {
      "href" : "http://boot-yournamespace.rhcloud.com/people{?page,size,sort}",
      "templated" : true
    }
  }
}
```

Navigating to <http://boot-yournamespace.rhcloud.com/people> should return all people from the database.

## Step 6: Adding Jenkins

Using Jenkins has some advantages. One of them is that the build takes place in it’s own Gear. To build with Jenkins, OpenShift needs a server and a Jenkins client cartridge attached to the application. Creating Jenkins application:

```
rhc app create ci jenkins
```

And attaching Jenkins client to the application:

```
rhc cartridge add jenkins-client --app boot
```

You can now browse to: <http://ci->.rhcloud.com and login with the credentials provided. When you make next changes and push them, the build will be triggered by Jenkins:

```
remote: Executing Jenkins build.
remote:
remote: You can track your build at https://ci-<namespace>.rhcloud.com/job/boot-build
remote:
remote: Waiting for build to schedule.........
```

And when you observe the build result, the application starts a bit faster on Jenkins.

# Under the hood

## Why DIY?

Spring Boot application can be deployed to Tomcat cartridge on OpenShift. But at this moment no Tomcat 8 and Java 8 support exists, therefore DIY was selected. DIY has limitations: it cannot be scaled for example. But it is perfect for trying and playing with new things.

## Application structure

The application is a regular Spring Boot application, that one can bootstrapped with <http://start.spring.io>. Build system used is Maven, packaging type is Jar. Tomcat 8 with Java 8 used. Spring Boot uses Tomcat 7 by default, to change it the following property was added:

```xml
<properties>
    <tomcat.version>8.0.9</tomcat.version>
</properties>
```

The Maven was selected, since currently only Gradle 1.6 can be used on OpenShift. This is due to a bug in [Gradle](https://issues.gradle.org/browse/GRADLE-2871). Gradle 2.2 fixes this issue.

## Maven settings.xml

The `settings.xml` file is pretty important, as it contains the location of Maven repository: `${OPENSHIFT_DATA_DIR}/m2/repository`.

On OpenShift, write permissions are only in $OPENSHIFT_DATA_DIR.

## Data source configuration

The application uses Spring Data REST to export repositories over REST. The required dependencies are:

- spring-boot-starter-data-jpa - repositories configuration
- spring-boot-starter-data-rest - exposing repositoties over REST
- hsqldb - for embedded database support
- postgresql - for PostgreSQL support. Since currently OpenShift uses PostgreSQL 9.2, the appropriate driver’s version is used

### Common properties - application.properties

By default (default profile, `src/main/resources/application.properties`), the application will use embedded HSQLDB and populate it with the `src/main/resources/data.sql`. The data file will work on both HSQLDB and PostrgeSQL, so we don’t need to provide platform specific files (which is possible with Spring Boot)

- `spring.jpa.hibernate.ddl-auto = create-drop` makes sure that the schema will be exported.

### OpenShift properties - application-openshift.properties

OpenShift specific configuration (`src/main/resources/application-openshift.properties`) allows the use of PostgreSQL service. The configuration uses OpenShift env variables to setup the connection properties:

- $OPENSHIFT_POSTGRESQL_DB_HOST - for the database host
- $OPENSHIFT_POSTGRESQL_DB_PORT - for the database port
- $OPENSHIFT_APP_NAME - for the database name
- $OPENSHIFT_POSTGRESQL_DB_USERNAME - for the database username
- $OPENSHIFT_POSTGRESQL_DB_PASSWORD - for the database password

Spring allows to use env variables directly in properties with `${}` syntax, e.g.:

```
spring.datasource.username = ${OPENSHIFT_POSTGRESQL_DB_USERNAME}
```

To let Spring Boot activate OpenShift profile, the `spring.profiles.active` property is passed to the application at startup: `java -jar <name>.jar --spring.profiles.active=openshift`

## Logging on OpenShift

The logging file will be stored in $OPENSHIFT_DATA_DIR:

```
logging.file=${OPENSHIFT_DATA_DIR}/logs/app.log
```

## Actuator

Actuator default management context path is `/`. This is changed to `/manage`, because OpenShift exposes `/health` endpoint itself that covers Actuator’s `/health` endpoint .

```
management.context-path=/manage
```

## OpenShift action_hooks

OpenShift executes action hooks script files at specific points during the deployment process. All hooks are placed in the `.openshift/action_hooks` directory in the application repository. Files must have be executable. In Windows, in Git Bash, the following command can be used:

```
git update-index --chmod=+x .openshift/action_hooks/*
```

### Deploying the application

The `deploy` script downloads Java and Maven, creates some directories and exports couple of environment variables required to properly run Java 8 / Maven build.

The final command of the deployment is to run Maven goals:

```
mvn -s settings.xml clean install
```

### Starting the application

When `deploy` script finishes successfully, the `target` directory will contain a single jar with the Spring Boot application assembled. The application is started and bound to the server address and port provided by OpenShift. In addition, the profile name is provided, so a valid data source will be created. The final command that runs the application:

```
nohup java -Xms384m -Xmx412m -jar target/*.jar --server.port=${OPENSHIFT_DIY_PORT} --server.address=${OPENSHIFT_DIY_IP} --spring.profiles.active=openshift &
```

### Stopping the application

The `stop` script is looking for a Java process and when it finds it… you know what happens.

# Summary

I am pretty happy with the evaluation of OpenShift with Do It Yourself cartridge. Not everything went smooth as I expected, mostly due to memory limitations on small Gear. I spent some time to figure it out and have proper configuration. But still, OpenShift with DIY is worth trying and playing with for a short while. Especially, that to get started is completely for free.

# References

- The project source code, used throughout this article, can be found on GitHub: <https://github.com/kolorobot/openshift-diy-spring-boot-sample>.
- Spring Boot documentation: <http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#cloud-deployment-openshift>
- Some OpenShift references used while creating this article:   
  <https://blog.openshift.com/run-gradle-builds-on-openshift>   
  <https://blog.openshift.com/tips-for-creating-openshift-apps-with-windows>
