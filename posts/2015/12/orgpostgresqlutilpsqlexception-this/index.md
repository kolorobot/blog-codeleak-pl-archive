---
title: "org.postgresql.util.PSQLException: This connection has been closed in Spring Boot"
date: 2015-12-09T23:13:00.002+01:00
updated: 2015-12-09T23:13:53.314+01:00
author: "Rafał Borowiec"
tags: ["spring boot"]
original_url: https://blog.codeleak.pl/2015/12/orgpostgresqlutilpsqlexception-this.html
---

# org.postgresql.util.PSQLException: This connection has been closed in Spring Boot

In Spring Boot data source connection pooling is auto-configured if a proper JDBC Driver is used (e.g. `org.postgresql.Driver`) and by default Tomcat pooling is used - although it can be easily changed). But the default configuration may not be enough in the production environment. One of the issues I had was `org.postgresql.util.PSQLException: This connection has been closed` exception after Postgres database was restarted while the application was running. In order to restore the connection application restart is needed.

Quickly digging into the Spring Boot documentation and several properties can be found that improve the data source configuration and the pooling in particular. Setting the below properties solve the problem:

```
spring.datasource.test-on-borrow=true
spring.datasource.remove-abandoned=true
# Validation query must be set in order to test connections
spring.datasource.validation-query=SELECT 1;
```

If you want to even further customize the pooling (e.g. on production), please refer to [Spring Boot documentation](http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#common-application-properties) and browse `spring.datasource.*` properties
