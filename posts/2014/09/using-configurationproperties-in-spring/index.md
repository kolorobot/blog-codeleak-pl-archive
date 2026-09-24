---
title: "Using @ConfigurationProperties in Spring Boot"
date: 2014-09-17T22:57:00.002+02:00
updated: 2017-03-06T22:36:00.037+01:00
author: "Rafał Borowiec"
tags: ["spring boot"]
original_url: https://blog.codeleak.pl/2014/09/using-configurationproperties-in-spring.html
---

# Using @ConfigurationProperties in Spring Boot

In my latest blog post I described shortly how one can [configure mail in Spring Boot application](../../../2014/09/testing-mail-code-in-spring-boot/index.md). To inject properties into the configuration I used Spring’s `@Value` annotation. But *Spring Boot provides an alternative method of working with properties that allows strongly typed beans to govern and validate the configuration of your application.* In this post I will demonstrate how to utilize `@ConfigurationProperties` while configuring the application.

*Update 6/03/2017:* As of Spring Boot 1.5, if you have `@ConfigurationProperties` classes that use JSR-303 constraint annotations, you should now additionally annotate them with `@Validated`.

*Update 20/05/2016:* The code was updated to reflect the newest Spring Boot.

So we want to use the mail configuration as an example. The configuration file is placed in a separate file, called `mail.properties`. The properties must be named using a proper convention, so they can be bind properly. Let’s see some examples:

- `protocol` and `PROTOCOL` will be bind to `protocol` field of a bean
- `smtp-auth`, `smtp_auth`, `smtpAuth` will be bind to `smtpAuth` field of a bean
- `smtp.auth` will be bind to … hmm to `smtp.auth` field of a bean!

Spring Boot uses some relaxed rules for binding properties to `@ConfigurationProperties` beans and supports hierarchical structure.

So let’s create a `@ConfigurationProperties` bean:

Note: As of Spring Boot 1.2 (December 2014) there is `org.springframework.boot.autoconfigure.mail.MailProperties` class similar to the below.

```java
@ConfigurationProperties(locations = "classpath:mail.properties", ignoreUnknownFields = false, prefix = "mail")
public class MailProperties {

    public static class Smtp {

        private boolean auth;
        private boolean starttlsEnable;

        // ... getters and setters
    }

    @NotBlank
    private String host;
    private int port;  
    private String from;
    private String username;
    private String password;
    @NotNull
    private Smtp smtp;

    // ... getters and setters

}
```

… that should be created from the following properties (`mail.properties`):

```
mail.host=localhost
mail.port=25
mail.smtp.auth=false
mail.smtp.starttls-enable=false
mail.from=me@localhost
mail.username=
mail.password=
```

In the above example, we annotated a bean with `@ConfigurationProperties`so that Spring Boot can bind properties to it. `ignoreUnknownFields = false` tells Spring Boot to throw an exception when there are properties that do not match a declared field in the bean. This is pretty handy during the development! `prefix` let you select the name prefix of the properties to bind.

Please note that setters and getters should be created in `@ConfigurationProperties` bean! And opposite to `@Value` annotation it may bring some extra noise to the code (especially in simple cases, in my opinion).

Ok, but we want to use the properties to configure our application. There are at least two ways of creating `@ConfigurationProperties`. We can either use it together with `@Configuration` that provides `@Bean`s or we can use it separately and inject into `@Configuration` bean.

The first scenario:

```java
@Configuration
@ConfigurationProperties(locations = "classpath:mail.properties", prefix = "mail")
public class MailConfiguration {

    public static class Smtp {

        private boolean auth;
        private boolean starttlsEnable;

        // ... getters and setters
    }

    @NotBlank
    private String host;
    private int port;  
    private String from;
    private String username;
    private String password;
    @NotNull
    private Smtp smtp;

    // ... getters and setters   

    @Bean
    public JavaMailSender javaMailSender() {
        // omitted for readability
    }
}
```

In the second scenario, we simply annotate the properties bean (as above) and use Spring’s`@Autowire`to inject it into mail configuration bean:

```java
@Configuration
public class MailConfiguration {

    @Autowired
    private MailProperties mailProperties;

    @Bean
    public JavaMailSender javaMailSender() {
        // omitted for readability
    }
}
```

Note: The below is no more valid in Spring Boot. `@ConfigurationProperties` are enabled by default.

~~Please note `@EnableConfigurationProperties`annotation. This annotation tells Spring Boot to enable support for `@ConfigurationProperties` of a specified type. If not specified, you may otherwise see the `org.springframework.beans.factory.NoSuchBeanDefinitionException` exception.~~

To sum up, `@ConfigurationProperties` beans are pretty handy. Is it better than using `@Value` annotation? In certain scenarios probably yes, but this is just the choice you need to make.

Have a look at Spring Boot’s documentation to read more about typesafe configuration properties: <http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#boot-features-external-config-typesafe-configuration-properties>

*See also:*  [${… } placeholders support in @Value annotations in Spring](../../../2015/09/placeholders-support-in-value/index.md)
