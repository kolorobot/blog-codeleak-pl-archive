---
title: "Spring MVC: Trgger manual validation of a form object"
date: 2016-04-07T22:44:00.000+02:00
updated: 2016-04-07T22:44:46.829+02:00
author: "Rafał Borowiec"
tags: ["spring mvc"]
original_url: https://blog.codeleak.pl/2016/04/spring-mvc-manual-form-validation.html
---

# Spring MVC: Trgger manual validation of a form object

Sometimes it may be needed to use manual validation in Spring MVC *@Controller.* This is very simple with Spring’s *org.springframework.validation.ValidationUtils* class. Learn how to invoke a validator in two different scenarios.

## Scenario 1 - invoke validation

In this scenario, I have a user form with username field. Username field is validated with custom validator in order to verify the existance in e.g. database.

```java
public class User {

    @UserExists
    private String username;

}
```

In controller class I have a method that handles POST method of that object:

```java
@Autowired
private org.springframework.validation.Validator validator;

@RequestMapping(value = "/user", method = RequestMethod.POST)
public String validate(@ModelAttribute User user, Errors errors) {

    ValidationUtils.invokeValidator(validator, user, errors);

    if (errors.hasErrors()) {
        // error, show errors to the user
    }

    // success, form is valid!
}
```

`org.springframework.validation.ValidationUtils` is a class for invoking a `org.springframework.validation.Validator`.

Please note that user parameter is followed by `org.springframework.validation.Errors` object. Spring initializes this object but it is empty and can be be passed to a `invokeValidator` method.

## Scenario 2 - invoke validation with hints

In this scenario, user form gets a bit more complicated:

```java
@GroupSequence(value = {ValidationOrder.First.class, ValidationOrder.Second.class})
interface ValidationOrder {
    interface First {}
    interface Second {}
}

public class User {

    @UserExists(groups = ValidationOrder.First.class)
    @UserIsEntitledToDiscount(groups = ValidationOrder.Second.class)
    private String username;

}
```

Thanks to `@GroupSequence` I could decide about the order of validation. To trigger validation I need to pass an additional argument to `invokeValidator` method so the groups are correctly used:

```java
ValidationUtils.invokeValidator(validator, user, errors, ValidationOrder.class);
```

## Source code

The source code contains all three approaches, so that you can quickly compare them: <https://github.com/kolorobot/spring-mvc-beanvalidation11-demo>

## Similar articles

In case you find this article interesting, have a look at my other blog posts:

- [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md)
- [Different ways of validating @RequestBody in Spring MVC with @Valid annotation](../../../2013/09/request-body-validation-in-spring-mvc-3.2/index.md)
- [Better Error Messages with Bean Validation 1.1](../../../2014/06/better-error-messages-with-bean/index.md)
- [Spring MVC Integration Testing: Assert the given model attribute(s) have global errors](../../../2014/08/spring-mvc-test-assert-given-model-attribute-global-errors/index.md)
- [Spring 4.1 and Java 8: java.util.Optional as a @RequestParam, @RequestHeader and @MatrixVariable in Spring MVC](../../../2014/07/Spring41-and-Java8-Optional-as-RequestParam-RequestHeader-MatrixVariable/index.md)
