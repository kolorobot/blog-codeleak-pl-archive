---
title: "HOW-TO: Method-level validation in Spring with @Validated annotation"
date: 2012-03-05T23:27:00.000+01:00
updated: 2016-03-30T22:57:57.107+02:00
author: "Codeleak.pl"
tags: ["java", "spring"]
original_url: https://blog.codeleak.pl/2012/03/how-to-method-level-validation-in.html
---

# HOW-TO: Method-level validation in Spring with @Validated annotation

@Validated is a Spring’s specific variant of JSR-303’s javax.validation.Valid, supporting the specification of validation groups. @Validated can be used with Spring MVC handler methods arguments as well as with method level validation.

In this article, you will learn how to use @Validated annotation with method level validation in Spring.

> Note: This blog post got a solid update (30/03/2016). The source code got migrated to new repository and it is Spring Boot driven. See references. If you still prefer classic Spring MVC application you may use my [spring-mvc-quickstart-archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype)

In order to indicate that a specific class is supposed to be validated at the method level it needs to be annotated with @Validated annotation at type level. Methods applicable for validation must have JSR-303 constraint annotations on their parameters and/or on their return values.

```java
@Service
@Validated
public class SomeService {

    @Length(min = 3, max = 5)
    public String createUser(@NotBlank @Email String email,
                             @NotBlank String username,
                             @NotBlank String password) {
        return username;
    }

}
```

Beans annotated with `@Validated` annotation will be detected by `MethodValidationPostProcessor` and validation functionality is delegated to JSR 303 provider. When the validation fails `ConstraintViolationException`, with a set of constraint violations, is thrown.

To visualize that let’s create a Unit Test.

```java
@ContextConfiguration(classes = {SomeServiceTest.Config.class})
@RunWith(SpringJUnit4ClassRunner.class)
public class SomeServiceTest {

}
```

The context of the test is configured using `MethodValidationPostProcessor`. This is a must-have configuration in order to trigger method-level validation.

```java
@Configuration
public static class Config {
    @Bean
    public MethodValidationPostProcessor methodValidationPostProcessor() {
        return new MethodValidationPostProcessor();
    }

    @Bean
    public SomeService userCreateService() {
        return new SomeService();
    }
}
```

The expected exception is verified with AssertJ.

> Note: If you want to learn how to verify exceptions in JUnit tests with AssertJ have a look at [JUnit: Testing Exceptions with Java 8 and AssertJ](../../../2015/04/junit-testing-exceptions-with-java-8/index.md).

```java
@Test
public void throwsViolationExceptionWhenAllArgumentsInvalid() {
    assertThatExceptionOfType(ConstraintViolationException.class)
        .isThrownBy(() -> service.createUser(null, null, null))
        .matches(e -> e.getConstraintViolations().size() == 3);
}

@Test
public void throwsViolationExceptionWhen2ArgumentsInvalid() {
    assertThatExceptionOfType(ConstraintViolationException.class)
        .isThrownBy(() -> service.createUser(null, null, "valid"))
        .matches(e -> e.getConstraintViolations().size() == 2);

}

@Test
public void throwsViolationExceptionWhenEmailInvalidArgumentsInvalid() {
    assertThatExceptionOfType(ConstraintViolationException.class)
        .isThrownBy(() -> service.createUser("invalid_email", "valid", "valid"))
        .matches(e -> e.getConstraintViolations().size() == 1)
        .matches(e -> e.getConstraintViolations().stream()
                       .allMatch(v -> v.getMessage().equals("not a well-formed email address")));

}

@Test
public void throwsViolationExceptionWhenReturnValueTooLong() {
    assertThatExceptionOfType(ConstraintViolationException.class)
        .isThrownBy(() -> service.createUser("user@domain.com", "too_long_username", "valid"))
        .matches(e -> e.getConstraintViolations().size() == 1)
        .matches(e -> e.getConstraintViolations().stream()
                       .allMatch(v -> v.getMessage().equals("length must be between 3 and 5")));

}

@Test
public void createsUser() {
    service.createUser("user@domain.com", "valid", "valid");
}
```

Of course, I could be more specific with the assertions, but the tests are here only to visualize the validation.

> Note: You may want to learn how to utilize custom assertions with AssertJ: [Spice up your test code with custom assertions](../../../2014/05/spice-up-your-test-code-with-custom-assertions/index.md)

## Summary

With just couple lines of code you may start with method-level validation in Spring. But there is one pending question: “Do we want to utilize method-level validation in production code?”. What’s your opinion?

## Source code

The source code contains not only the examples from this article, but many others. And it gets updated! See all the examples here: <https://github.com/kolorobot/spring-mvc-beanvalidation11-demo>

## Similar articles

In case you find this article interesting, have a look at my other blog posts:

- [Better Error Messages with Bean Validation 1.1](../../../2014/06/better-error-messages-with-bean/index.md)
- [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md)
- [Spring MVC Integration Testing: Assert the given model attribute(s) have global errors](../../../2014/08/spring-mvc-test-assert-given-model-attribute-global-errors/index.md)
- [java.util.Optional as a @RequestParam, @RequestHeader and @MatrixVariable in Spring MVC](../../../2014/07/Spring41-and-Java8-Optional-as-RequestParam-RequestHeader-MatrixVariable/index.md)
