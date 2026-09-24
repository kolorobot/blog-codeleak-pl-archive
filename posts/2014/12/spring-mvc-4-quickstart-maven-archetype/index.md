---
title: "Spring MVC 4 Quickstart Maven Archetype Improved"
date: 2014-12-13T15:51:00.000+01:00
updated: 2016-01-31T22:02:46.497+01:00
author: "Rafał Borowiec"
tags: ["spring 4", "spring mvc", "tools"]
original_url: https://blog.codeleak.pl/2014/12/spring-mvc-4-quickstart-maven-archetype.html
---

# Spring MVC 4 Quickstart Maven Archetype Improved

Spring Boot allows getting started with Spring extremely easy. But there are still people interested in not using Spring Boot and bootstrap the application in a more *classical* way. Several years ago, I created an archetype (long before Spring Boot) that simplifies bootstrapping Spring web applications. Although Spring Boot is already some time on the market, Spring MVC 4 Quickstart Maven Archetype is still quite popular project on [GitHub](https://github.com/kolorobot/spring-mvc-quickstart-archetype). With some recent additions I hope it is even better.

## Java 8

I have decided to switch target platform to Java 8. There is not specific Java 8 code in the generated project yet, but I believe all new Spring projects should be started with Java 8. The adoption of Java 8 is ahead of forecasts. Have a look at: <https://typesafe.com/company/news/survey-of-more-than-3000-developers-reveals-java-8-adoption-ahead-of-previous-forecasts>

Update: More Java 8 features: [http://blog.codeleak.pl/2016/01/spring-mvc-4-quickstart-maven-archetype.html](../../../2016/01/spring-mvc-4-quickstart-maven-archetype/index.md)

## Introducing Spring IO Platform

*Spring IO Platform brings together the core Spring APIs into a cohesive platform for modern applications.*. The main advantage is that it simplifies dependency management by providing versions of Spring projects along with their dependencies that are tested and known to work together.

Previously, all the dependencies were specified manually and solving version conflicts took some time. With Spring IO platform we must change only platform version (and take care of dependencies outside the platform of course):

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.spring.platform</groupId>
            <artifactId>platform-bom</artifactId>
            <version>${io.spring.platform-version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

The dependencies can be now used without specifying the `version` in POM:

```xml
<!-- Spring -->
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-webmvc</artifactId>
</dependency>
<!-- Security -->
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-config</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-web</artifactId>
</dependency>
```

## Java Security configuration

When I firstly created the archetype there was no possibility to configure Spring Security using Java code. But now it is, so I migrated the XML configuration to Java configuration.

The `SecurityConfig` is now extending from `WebSecurityConfigurerAdapter` and it is marked with `@Configuration` and `@EnableWebMvcSecurity` annotations.

### Security configuration details

#### Restrict access to every URL apart from

The XML configuration:

```xml
<security:intercept-url pattern="/" access="permitAll" />
<security:intercept-url pattern="/resources/**" access="permitAll" />
<security:intercept-url pattern="/signup" access="permitAll" />
<security:intercept-url pattern="/**" access="isAuthenticated()" />
```

became:

```java
http
    .authorizeRequests()
        .antMatchers("/", "/resources/**", "/signup").permitAll()
        .anyRequest().authenticated()
```

### Login / Logout

The XML configuration:

```xml
<security:form-login login-page="/signin" authentication-failure-url="/signin?error=1"/>
<security:logout logout-url="/logout" />
```

became:

```java
http
    .formLogin()
        .loginPage("/signin")
        .permitAll()
        .failureUrl("/signin?error=1")
        .loginProcessingUrl("/authenticate")
        .and()
    .logout()
        .logoutUrl("/logout")
        .permitAll()
        .logoutSuccessUrl("/signin?logout");
```

### Remember me

The XML configuration:

```xml
<security:remember-me services-ref="rememberMeServices" key="remember-me-key"/>
```

became:

```java
http
    .rememberMe()
        .rememberMeServices(rememberMeServices())
        .key("remember-me-key");
```

#### CSRF enabled for production and disabled for test

Currently CSRF is by default enabled, so no additional configuration is needed. But in case of integration tests I wanted to be sure that CSRF is disabled. I could not find a good way of doing this. I started with CSRF protection matcher passed to `CsrfConfigurer`, but I ended up with lots of code I did not like to have in `SecurityConfiguration`. I ended up with a `NoCsrfSecurityConfig` that extends from the original `SecurityConfig` and disabled CSRF:

```java
@Configuration
public class NoCsrfSecurityConfig extends SecurityConfig {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        super.configure(http);
        http.csrf().disable();
    }
}
```

## Connection pooling

HikariCP is now used as default connection pool in the generated application. The default configuration is used:

```java
@Bean
public DataSource configureDataSource() {
    HikariConfig config = new HikariConfig();
    config.setDriverClassName(driver);
    config.setJdbcUrl(url);
    config.setUsername(username);
    config.setPassword(password);
    config.addDataSourceProperty("cachePrepStmts", "true");
    config.addDataSourceProperty("prepStmtCacheSize", "250");
    config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
    config.addDataSourceProperty("useServerPrepStmts", "true");

    return new HikariDataSource(config);
}
```

## More to come

Spring MVC 4 Quickstart Maven Archetype is far from finished. As the Spring platform involves the archetype must adjust accordingly. I am looking forward to hear what could be improved to make it a better project. If have an idea or suggestion drop a comment or create an issue on [GitHub](https://github.com/kolorobot/spring-mvc-quickstart-archetype/issues).

## References

[Spring MVC 4 Quickstart Maven Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype)
