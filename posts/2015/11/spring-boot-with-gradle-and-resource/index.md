---
title: "Spring Boot with Gradle and resource filtering"
date: 2015-11-28T22:48:00.000+01:00
updated: 2015-11-28T22:48:41.511+01:00
author: "Rafał Borowiec"
tags: ["gradle", "spring boot"]
original_url: https://blog.codeleak.pl/2015/11/spring-boot-with-gradle-and-resource.html
---

# Spring Boot with Gradle and resource filtering

Recently, while working on a rather small Spring Boot web application, I encountered an issue: after the deployment of a WAR file the application did not serve fonts and and other binary files properly. And the issue was with the invalid configuration of resource filtering in Gradle.

I wanted to package the application to a specific profile - **prod**, so when it was deployed to Tomcat **prod** profile was active by default.

During the development I set active profiles via CLI (or run configuration in IntelliJ) but in production I had no such opportunity - I needed to deploy the WAR file and I was able to set active profiles only via `application.properties` and `spring.profiles.active` property. To make things simple, I have done this with resource filtering in `processResources` task in Gradle:

```
processResources {
        filter org.apache.tools.ant.filters.ReplaceTokens, tokens: [
                activeProfiles: project.getProperties().containsKey('activeProfiles') ? project.property('activeProfiles') : ''
        ]
}
```

`activeProfiles` token is included in `application.properties`

```
spring.profiles.active=@activeProfiles@
```

When running the build with `-PactiveProfiles=prod`, `application.properties` is filtered and the token is replaced with a provided value. When property is not set the property is empty which is perfect for the development in my case.

But it did not go fully as expected. After the deployment and the smoke tests 2 big issues appeared.

- The fonts were not properly shown and the Chrome console showed:

```
Failed to decode downloaded font: http:// [...] /fonts/glyphicons-halflings-regular.woff
index.html:1 OTS parsing error: maxp: misaligned table
```

- Generating DOCX reports was failing with the exception:

```
java.util.zip.ZipException: invalid bit length repeat
```

After some time spent on analyzing the issues and looking where I should not have been looking, I found out the issue was with the configuration of `processResources` task in Gradle. The task, as it was originally defined, filtered *all* resources, including binary files and it corrupted those files during the build.

I solved this by filtering only `application.properties`:

```
processResources {
     filesMatching('application.properties') {
        filter org.apache.tools.ant.filters.ReplaceTokens, tokens: [                
                activeProfiles: project.getProperties().containsKey('activeProfiles') ? project.property('activeProfiles') : ''
        ]
     }
}
```

## References

- <http://stackoverflow.com/questions/24783070/gradle-build-spring-boot-app-as-war-with-active-profile>
- <http://jlorenzen.blogspot.com/2013/06/resource-filtering-with-gradle.html>
