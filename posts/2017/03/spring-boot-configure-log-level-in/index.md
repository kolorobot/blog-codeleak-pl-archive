---
title: "Spring Boot - Configure Log Level in runtime using actuator endpoint"
date: 2017-03-06T23:15:00.002+01:00
updated: 2017-03-06T23:15:56.106+01:00
author: "Rafał Borowiec"
tags: ["spring boot"]
original_url: https://blog.codeleak.pl/2017/03/spring-boot-configure-log-level-in.html
---

# Spring Boot - Configure Log Level in runtime using actuator endpoint

As of Spring Boot 1.5 a new `loggers` actuator endpoint allows viewing and changing application logging levels in runtime.

- Add `spring-boot-actuator` to your project

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

- Disable security for `loggers` or for all endpoints

Set either `management.security.enabled` to `false` or `endpoints.loggers.sensitive` to `false` to disable security. Note that the latter changes only `loggers` endpoint.

- Get all loggers details

Execute `/loggers` endpoint in the browser or with `curl`. You will get a detailed view of the loggers configuration, e.g (fragment):

```
{
  "levels": [
    "OFF",
    "ERROR",
    "WARN",
    "INFO",
    "DEBUG",
    "TRACE"
  ],
  "loggers": {
    "ROOT": {
      "configuredLevel": "TRACE",
      "effectiveLevel": "TRACE"
    },
    "org": {
      "configuredLevel": null,
      "effectiveLevel": "TRACE"
    },
    "pl.codeleak.demos.sbt": {
      "configuredLevel": null,
      "effectiveLevel": "TRACE"
    },
    "pl.codeleak.demos.sbt.Application": {
      "configuredLevel": null,
      "effectiveLevel": "TRACE"
    }
  }
}
```

- Get selected logger details

Use the following endpoint to get details of a selected logger:

```
/logger/{logger}
```

Examples:

```
λ curl -i http://localhost:8080/loggers/ROOT

{
"configuredLevel": null,
"effectiveLevel": "TRACE"
}

λ curl -i http://localhost:8080/loggers/pl.codeleak.demos

{
"configuredLevel": null,
"effectiveLevel": "TRACE"
}
```

1. Update selected logger level in runtime

Execute a `POST` request:

```
curl -i -X POST -H 'Content-Type: application/json' -d '{"configuredLevel": "TRACE"}' http://localhost:8080/loggers/ROOT
```

## Source code

The example configuration can be found in <https://github.com/kolorobot/spring-boot-thymeleaf> repository.
