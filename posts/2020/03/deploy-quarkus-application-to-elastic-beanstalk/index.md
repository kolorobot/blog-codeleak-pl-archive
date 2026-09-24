---
title: "Deploy Quarkus application to AWS Elastic Beanstalk"
date: 2020-03-15T21:45:00.000+01:00
updated: 2020-03-15T22:09:46.350+01:00
author: "Rafał Borowiec"
tags: ["aws", "quarkus"]
original_url: https://blog.codeleak.pl/2020/03/deploy-quarkus-application-to-elastic-beanstalk.html
---

# Deploy Quarkus application to AWS Elastic Beanstalk

Elastic Beanstalk allows deploying and managing applications in the AWS Cloud without having to learn about the infrastructure that runs those applications.

With Elastic Beanstalk you can run a website, web application, or web API that serves HTTP requests but you can also run a worker applications for running long tasks. The Elastic Beanstalk supports several preconfigured platforms including `Go`, `.NET` or `Java` (Java 8 only) but also generic `Docker` platform.

You simply upload your application with `AWS CLI`, `AWS EB CLI` or with the `Elastic Beanstack console`, and Elastic Beanstalk automatically handles the rest.

In this blog post you will learn how to launch single container `Docker` environment with Quarkus based application on Elastic Beanstalk.

> Note: This blog does not describe creating the application from scratch. Instead, it is basing on the *Quarkus Pet Clinic REST API application* that I created for [Getting started with Quarkus](../../../2020/02/getting-started-with-quarkus/index.md) blog post. The source code can be found on Github: <https://github.com/kolorobot/quarkus-petclinic-api>

- [TL;DR: Create the package and upload to Elastic Beanstalk](#tldr-create-the-package-and-upload-to-elastic-beanstalk)
  - [Create new application in Elastic Beanstalk console](#create-new-application-in-elastic-beanstalk-console)
  - [Preapare application package](#preapare-application-package)
  - [Upload application to Elastic Beanstalk](#upload-application-to-elastic-beanstalk)
- [Step by step: Configure the application for Elastic Beanstalk](#step-by-step-configure-the-application-for-elastic-beanstalk)
  - [Runtime configuration](#runtime-configuration)
  - [`Dockerfile`](#dockerfile)
  - [Create application package with Maven](#create-application-package-with-maven)
    - [Prepare files for the assembly](#prepare-files-for-the-assembly)
    - [Configure assembly plugin](#configure-assembly-plugin)
    - [Test the package locally](#test-the-package-locally)
- [Source code](#source-code)
- [References](#references)
- [See also](#see-also)

# TL;DR: Create the package and upload to Elastic Beanstalk

## Create new application in Elastic Beanstalk console

> If you’re not already an AWS customer, you need to create an AWS account. Signing up enables you to access Elastic Beanstalk and other AWS services that you need.

- Open the Elastic Beanstalk console using this link: [https://us-west-2.console.aws.amazon.com/elasticbeanstalk/home?region=us-west-2#/gettingStarted?applicationName=Pet Clinic API](https://us-west-2.console.aws.amazon.com/elasticbeanstalk/home?region=us-west-2#/gettingStarted?applicationName=Pet%20Clinic%20API)
- For the `Platform` choose `Docker`
- For the `Application Code` choose `Sample Application`
- Select `Configure more options`
  - Find `Database` on the list and click `Modify`
  - For `Engine` choose `postgres`
  - For `Engine version` choose `11.6`
  - Set `username` and `password` of your choice
  - For `Retention` choose `Delete` if you don’t snaphost to be created.
  - Click `Save`.
- Click `Create app`

Elastic Beanstalk will create the sample application for you with all required resources (including RDS).

The link to the application will be visible to you once the application is created.

> Note: The above steps are based on the official documentation: <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/GettingStarted.CreateApp.html>

## Preapare application package

- Clone the repository

```
git clone https://github.com/kolorobot/quarkus-petclinic-api
```

- Navigate to the application directory and execute:

```
./mvnw clean package assembly:single -Dquarkus.package.uber-jar=true
```

The above command creates the package with the following contents:

```
$ unzip -l target/quarkus-petclinic-api-1.0.1-eb.zip

Archive:  target/quarkus-petclinic-api-1.0.1-eb.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  03-15-2020 13:35   config/
     2059  03-15-2020 13:34   Dockerfile
      369  03-15-2020 13:34   config/application.properties
 38604205  03-15-2020 13:35   quarkus-petclinic-api-1.0.1-runner.jar
---------                     -------
 38606633                     4 files
```

## Upload application to Elastic Beanstalk

- Upload the package using Elastic Beanstalk console
  - Navigate to <https://console.aws.amazon.com/elasticbeanstalk>
  - Navigate to the application dashboard
  - Click `Upload and Deploy`
  - Select the package create in the previous step and click `Deploy`
  - Wait for the application to be deployed

That’s it. In the next paragraph you will learn how to prepare the package using Maven.

# Step by step: Configure the application for Elastic Beanstalk

## Runtime configuration

Let’s start with the application configuration specific for Elastic Beanstalk environment.

Quarkus offers a several options to override properties at runtime. I decided to utilize the approach with configuration file placed in `config/application.properties` file. This file will be automatically read by Quarkus and all properties from this file take precendence over defaults.

Create `src/main/resources/application-eb.properties` file and set `quarkus.http.port` to `5000` as this is the default port for Elastic Beanstalk web application.

The next properties are related to the datasource configuration as the application will be connecting to the RDS (PostgreSQL). The RDS instance’s connection information are available to application running on Elastic Beanstalk through `RDS_*` environment properties which are available to running container. To use this set the following properties:

```
quarkus.datasource.url=jdbc:postgresql://${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}
quarkus.datasource.username=${RDS_USERNAME}
quarkus.datasource.password=${RDS_PASSWORD}
```

> Read more on connecting your application to RDS: <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.managing.db.html>

## `Dockerfile`

Elastic Beanstalk uses `Dockerfile` to build and run the image. The file must be located in the `root` of the application’s directory. I used the original `src/main/docker/Dockerfile.jvm` and made following adjustments:

- Copy `config/application.properties` to the container
- Expose port `5000` instead of `8080`

The complete `src/main/docker/Dockerfile.eb`:

```
FROM registry.access.redhat.com/ubi8/ubi-minimal:8.1

ARG JAVA_PACKAGE=java-11-openjdk-headless
ARG RUN_JAVA_VERSION=1.3.5

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en'

# Install java and the run-java script
# Also set up permissions for user `1001`
RUN microdnf install openssl curl ca-certificates ${JAVA_PACKAGE} \
    && microdnf update \
    && microdnf clean all \
    && mkdir /deployments \
    && chown 1001 /deployments \
    && chmod "g+rwX" /deployments \
    && chown 1001:root /deployments \
    && curl https://repo1.maven.org/maven2/io/fabric8/run-java-sh/${RUN_JAVA_VERSION}/run-java-sh-${RUN_JAVA_VERSION}-sh.sh -o /deployments/run-java.sh \
    && chown 1001 /deployments/run-java.sh \
    && chmod 540 /deployments/run-java.sh \
    && echo "securerandom.source=file:/dev/urandom" >> /etc/alternatives/jre/lib/security/java.security

ENV JAVA_OPTIONS="-Djava.util.logging.manager=org.jboss.logmanager.LogManager"

COPY *-runner.jar /deployments/app.jar
COPY config /deployments/config

EXPOSE 5000
USER 1001

ENTRYPOINT [ "/deployments/run-java.sh" ]
```

## Create application package with Maven

Until now, the following two files were created:

- `src/main/resources/application-eb.properties` with properties specific to Elastic Beanstalk environment
- `src/main/docker/Dockerfile.eb` with container configuration for Elastic Beanstack environment.

To finish the configuration and configure package assembly, we will use `Copy Rename Maven Plugin` and `Maven Assembly Plugin`.

### Prepare files for the assembly

Modify `pom.xml` and add the goal to copy and rename the files that will be stored in the final application package `zip` file:

```xml
<build>
    <plugin>
        <groupId>com.coderplus.maven.plugins</groupId>
        <artifactId>copy-rename-maven-plugin</artifactId>
        <version>1.0</version>
        <executions>
            <execution>
                <id>copy-file</id>
                <phase>package</phase>
                <goals>
                    <goal>copy</goal>
                </goals>
                <configuration>
                    <fileSets>
                        <fileSet>
                            <sourceFile>src/main/resources/application-eb.properties</sourceFile>
                            <destinationFile>target/eb/application.properties</destinationFile>
                        </fileSet>
                        <fileSet>
                            <sourceFile>src/main/docker/Dockerfile.eb</sourceFile>
                            <destinationFile>target/eb/Dockerfile</destinationFile>
                        </fileSet>
                    </fileSets>
                </configuration>
            </execution>
        </executions>
    </plugin>
</build>
```

The `copy-file` goal will run during `package` phase and will copy previously created files to `target/eb` with their names adjusted.

### Configure assembly plugin

`Maven Assembly Plugin` will be used to create the application package. Add the below configuration to the `pom.xml`:

```xml
<build>
    <plugin>
        <artifactId>maven-assembly-plugin</artifactId>
        <version>3.2.0</version>
        <configuration>
            <descriptors>
                <descriptor>src/assembly/eb.xml</descriptor>
            </descriptors>
        </configuration>
    </plugin>
</build>
```

Now, create `src/assembly/eb.xml` descriptor that instructs the assembly plugin to create a `zip` containing `Dockerfile`, `config/application.properties` and the Quarkus `uber-jar`. All three files will be located in the `root` of the archive:

```xml
<assembly>
    <id>eb</id>
    <formats>
        <format>zip</format>
    </formats>
    <includeBaseDirectory>false</includeBaseDirectory>
    <files>
        <file>
            <source>target/eb/Dockerfile</source>
            <outputDirectory></outputDirectory>
            <filtered>false</filtered>
        </file>
        <file>
            <source>target/eb/application.properties</source>
            <outputDirectory>config</outputDirectory>
            <filtered>false</filtered>
        </file>
        <file>
            <source>target/${project.build.finalName}-runner.jar</source>
            <outputDirectory></outputDirectory>
            <filtered>false</filtered>
        </file>
    </files>
</assembly>
```

This concludes the configuration. You can now create the package (assembly) by running:

With all the above changes, we can create the package:

```
./mvnw clean package assembly:single -Dquarkus.package.uber-jar=true
```

### Test the package locally

To test the package locally run:

```
unzip target/quarkus-petclinic-api-1.0.1-eb.zip -d target/eb-dist && cd target/eb-dist
docker build -t quarkus/petclinic-api-jvm-eb .
```

Before running the container, start the database:

```
docker run -it --name petclinic-db -p 5432:5432 -e POSTGRES_DB=petclinic -e POSTGRES_USER=petclinic -e POSTGRES_PASSWORD=petclinic -d postgres:11.6-alpine
```

Run the application passing RDS environment variables and link to the database container:

```
docker run -i --rm -p 8080:5000 --link petclinic-db -e RDS_HOSTNAME=petclinic-db -e RDS_PORT=5432 -e RDS_DB_NAME=petclinic -e RDS_USERNAME=petclinic -e RDS_PASSWORD=petclinic quarkus/petclinic-api-jvm-eb
```

Open `http://localhost:8080` in your browser and you should see the home page.

# Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/quarkus-petclinic-api>

# References

- <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/single-container-docker.html>
- <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.managing.db.html>
- <https://quarkus.io/guides/config#package-and-run-the-application>

# See also

- [Getting started with Quarkus](../../../2020/02/getting-started-with-quarkus/index.md)
- [Quarkus tests with Testcontainers and PostgreSQL](../../../2020/02/testcontainers-with-quarkus-tests/index.md)
