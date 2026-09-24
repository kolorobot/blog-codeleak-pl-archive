---
title: "Validation groups in Spring MVC"
date: 2014-08-12T23:26:00.000+02:00
updated: 2014-09-08T21:34:29.344+02:00
author: "Rafał Borowiec"
tags: ["spring mvc"]
original_url: https://blog.codeleak.pl/2014/08/validation-groups-in-spring-mvc.html
---

# Validation groups in Spring MVC

![](logo-spring-io.png)

All constraints in Bean Validation may be added to one or more groups via `groups` attribute. This allows you to restrict the set of constraints applied during validation. It can be handy in cases where some groups should be validated before others like e.g. in wizards. As of Spring MVC 3.1, automatic validation utilizing validation groups is possible with `org.springframework.validation.annotation.Validated` annotation. In this article I will use simple Spring MVC application to demonstrate how easily you can use validation groups to validate Spring’s MVC model attributes.

## Form

Let’s start with the form class that will be validated in steps. Firstly, we define interfaces that represents constraint groups:

```java
public class Account implements PasswordAware {

    interface ValidationStepOne {
        // validation group marker interface
    }

    interface ValidationStepTwo {
        // validation group marker interface
    }
}
```

## Validation contraints

Next we assign constraint to groups. Remember, if you don’t provide groups the default one will be used. Please also note `@SamePasswords`, `@StrongPassword` - custom constraints, that must define `groups` attribute:

```java
@SamePasswords(groups = {Account.ValidationStepTwo.class})
public class Account implements PasswordAware {

    @NotBlank(groups = {ValidationStepOne.class})
    private String username;

    @Email(groups = {ValidationStepOne.class})
    @NotBlank(groups = {ValidationStepOne.class})
    private String email;

    @NotBlank(groups = {ValidationStepTwo.class})
    @StrongPassword(groups = {ValidationStepTwo.class})
    private String password;

    @NotBlank(groups = {ValidationStepTwo.class})
    private String confirmedPassword;

    // getters and setters
}
```

## Wizard

Having the `Account`, we can create a 3-step wizard `@Controller` that will let users create an account. In first step we will let Spring validate constraint in `ValidationStepOne` group:

```java
@Controller
@RequestMapping("validationgroups")
@SessionAttributes("account")
public class AccountController {

    @RequestMapping(value = "stepOne")
    public String stepOne(Model model) {
        model.addAttribute("account", new Account());
        return VIEW_STEP_ONE;
    }

    @RequestMapping(value = "stepOne", method = RequestMethod.POST)
    public String stepOne(@Validated(Account.ValidationStepOne.class) Account account, Errors errors) {
        if (errors.hasErrors()) {
            return VIEW_STEP_ONE;
        }
        return "redirect:stepTwo";
    }
}
```

To trigger validation with groups I used `@Validated` annotation. This annotation takes var-arg argument with groups’ types. The code `@Validated(ValidationStepOne.class)` triggers validation of constraint in `ValidationStepOne` group.

In the next step we will let Spring validate constraint in `ValidationStepTwo` group:

```java
@Controller
@RequestMapping("validationgroups")
@SessionAttributes("account")
public class AccountController {

    @RequestMapping(value = "stepTwo")
    public String stepTwo() {
        return VIEW_STEP_TWO;
    }

    @RequestMapping(value = "stepTwo", method = RequestMethod.POST)
    public String stepTwo(@Validated(Account.ValidationStepTwo.class) Account account, Errors errors) {
        if (errors.hasErrors()) {
            return VIEW_STEP_TWO;
        }
        return "redirect:summary";
    }
}
```

In the summary step we will confirm entered data and we will let Spring validate constraint of both groups:

```java
@Controller
@RequestMapping("validationgroups")
@SessionAttributes("account")
public class AccountController {

    @RequestMapping(value = "summary")
    public String summary() {
        return VIEW_SUMMARY;
    }

    @RequestMapping(value = "confirm")
    public String confirm(@Validated({Account.ValidationStepOne.class, Account.ValidationStepTwo.class}) Account account, Errors errors, SessionStatus status) {
        status.setComplete();
        if (errors.hasErrors()) {
            // did not pass full validation
        }
        return "redirect:start";
    }
}
```

Prior to Spring 3.1 you could trigger the validation manually. I described this in one of my previous posts: [http://blog.codeleak.pl/2011/03/how-to-jsr303-validation-groups-in.html](../../../2011/03/how-to-jsr303-validation-groups-in/index.md)

Note: If you want to use validation groups without Spring, you need to pass groups to `javax.validation.Validator#validate()`:

## Validation groups without Spring

```java
Validator validator = Validation
        .buildDefaultValidatorFactory().getValidator();
Account account = new Account();

// validate with first group
Set<ConstraintViolation<Account>> constraintViolations =
        validator.validate(account, Account.ValidationStepOne.class);
assertThat(constraintViolations).hasSize(2);

// validate with both groups
Set<ConstraintViolation<Account>> constraintViolations =
        validator.validate(account, Account.ValidationStepOne.class, Account.ValidationStepTwo.class);
assertThat(constraintViolations).hasSize(4);
```

This is also the easiest way to test validations:

```java
public class AccountValidationTest {

    private Validator validator = Validation.buildDefaultValidatorFactory().getValidator();

    @Test
    public void shouldHaveFourConstraintViolationsWhileValidatingBothGroups() {
        Account account = new Account();
        Set<ConstraintViolation<Account>> constraintViolations = validator.validate(
                account, Account.ValidationStepOne.class, Account.ValidationStepTwo.class
        );
        assertThat(constraintViolations).hasSize(4);
    }

    @Test
    public void shouldHaveTwoConstraintViolationsWhileStepOne() {
        Account account = new Account();
        Set<ConstraintViolation<Account>> constraintViolations = validator.validate(
                account, Account.ValidationStepOne.class
        );
        assertThat(constraintViolations).hasSize(2);

    }
}
```

## Testing validation with Spring Test

Testing validation with Spring Test offers more sophisticated way of testing if validation/binding failed. For the examples, have a look at my other blog post: [Spring MVC Integration Testing: Assert the given model attribute(s) have global errors](../../../2014/08/spring-mvc-test-assert-given-model-attribute-global-errors/index.md)

The source code for this article can be found here: <https://github.com/kolorobot/spring-mvc-beanvalidation11-demo>
