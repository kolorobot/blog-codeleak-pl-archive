---
title: "How-To: JSR303 validation groups in Spring MVC 3 wizard-style controllers"
date: 2011-03-19T14:21:00.003+01:00
updated: 2014-08-13T21:29:02.763+02:00
author: "Codeleak.pl"
tags: ["java"]
original_url: https://blog.codeleak.pl/2011/03/how-to-jsr303-validation-groups-in.html
---

# How-To: JSR303 validation groups in Spring MVC 3 wizard-style controllers

*Beginning with Spring 3, Spring MVC has the ability to automatically validate @Controller inputs. To trigger validation of a @Controller input, simply annotate the input argument as javax.validation.Valid*.

Simple. But there is one drawback with **automatic** validation: using JSR303 validation groups is not possible. A group defines a subset of constraints. Instead of validating all constraints for a given object, only a subset is validated. Each constraint declaration defines the list of groups it belongs to. To trigger group validation group class or classes need to be passed to the validator. As mentioned, validation is triggered by with @Valid annotation. and there is no way you say which validation groups should be used in validation of @Controller input parameter. Until Spring 3.1 is ready and solves the problem, to utilize JSR303 validation groups manual validation is needed.

***Note:*** Have a look at the follow up post that describes the automatic validation with Spring's `@Validated` annotation (with the source code on GitHub): [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md).

In this article I will present easy way of utilizing validation groups in Spring MVC with wizard-style controller example.

The example is hypothetical 3-step account registration wizard. The model class is simply a User.

### Model

```java
@Entity
public class User {

 @Id
 @GeneratedValue(strategy = GenerationType.AUTO)
 private Integer id;

 @Column
 @NotNull
 private String name;
 
 @Column
 @NotNull
 private String email;
 
 @Column
 @NotNull
 private String password;

 // getters and setters
}
```

### View

The three mentioned steps are:

- Step 1: Username and Email
- Step 2: Password with confirmation
- Step 3: Summary page

Each step is stored in AccountForm bean:

```java
@SamePasswords(groups = { AccountForm.AccountStepTwo.class })
public class AccountForm implements PasswordAware {
 // group interfaces (don't need to be interfaces) to be used by constraints.      
 public interface AccountStepOne{}
 public interface AccountStepTwo{}

 // validation group assignment
 @NotNull(groups = { AccountStepOne.class })
 private String username;

 @Email(groups = { AccountStepOne.class })
 @NotNull(groups = { AccountStepOne.class })
 private String email;

 @NotNull(groups = { AccountStepTwo.class })
 private String password;

 @NotNull(groups = { AccountStepTwo.class })
 private String confirmedPassword;

 // getters and setters
}
```

For each step the view needs to be created. To each view the same model attribute is passed (accountForm)

In stepOne.jsp only the name and email input is required. And therefore it will be only passed to @Controller on form submission:

```xml
<form:form modelAttribute="accountForm" method="post">
    <form:errors path="" element="p" />
    <table>
        <tr>
            <td>Name</td>
            <td>
                <form:input path="username"></form:input>
                <form:errors path="username"></form:errors>
            </td>
        </tr>
        <tr>
            <td>Email</td>
            <td>
                <form:input path="email"></form:input>
                <form:errors path="email"></form:errors>
            </td>
        </tr>
        <tr>
            <td colspan="2"><input type="submit" value="Next"></input></td>
        </tr>
    </table>
</form:form>
```

In stepTwo.jsp password input is required (with confirmation field).

```xml
<form:form modelAttribute="accountForm" method="post">
    <form:errors path="" element="p" />
    <table>
        <tr>
            <td>Password</td>
            <td>
                <form:password path="password"></form:password> 
                <form:errors path="password"></form:errors>
            </td>
        </tr>
        <tr>
            <td>Confrim password</td>
            <td>
                <form:password path="confirmedPassword"></form:password> 
                <form:errors path="confirmedPassword"></form:errors>
            </td>
        </tr>
        <tr>
            <td colspan="2"><input type="submit" value="Next"></input></td>
        </tr>
    </table>
</form:form>
```

Summary page is skipped, since it contains only the view of input provided.

### @Controller

The wizard functionality is handled by AccountRegistrationWizardController.

```java
@Controller
@SessionAttributes("accountForm")
@RequestMapping("account")
public class AccountRegistrationWizardController {

}
```

Class is annotated with @Controller annotation. It will be autodetected through classpath scanning. @SessionAttributes defines our form attribute to be stored in session between requests

```java
@Autowired(required = true)
private javax.validation.Validator validator;
```

Spring injects javax.validation.Validator to our controller. We use validator to validate input parameters manually

```java
@RequestMapping("stepOne")
public AccountForm stepOneAccountRegistration() {
 return new AccountForm();
}
```

Upong entering "account/stepOne" empty AccountForm is populated to the view

```java
@RequestMapping(value = "stepOne", method = RequestMethod.POST)
public String stepOneAccountRegistration(@ModelAttribute AccountForm accountForm, BindingResult bindingResult, Model model) {
 if (isNotValid(accountForm, bindingResult, AccountStepOne.class)) {
  return "account/stepOne";
 }
 return "redirect:stepTwo";
}
```

Above method takes a account form bound from the requests - step one form (see stepOne.jsp). It is followed by binding result parameter that is used to register validation errors. Please note that account form parameter is not preceded by @Valid annotation and therefore the automatic validation won't happen. Instead, we provide manual validation by calling isNotValid method. This method takes 3 parameters: object to be validated, binding result to store errors and validation group (AccountStepOne.class) to applied during validation.

The validation method below is created based on the code from org.springframework.validation.beanvalidation.SpringValidatorAdapter.validate(Object target, Errors errors). The main change according to original code is that we need to call javax.validation.Validator.validate by passing additional arguments: **groups** and that is the whole trick.

```java
Set<ConstraintViolation<Object>> result = validator.validate(target, groups);
for (ConstraintViolation<Object> violation : result) {
    // method logic
}
```

Same steps are performed for the next wizard step. This time constraints in AccountStepTwo.class group are going to be validated:

```java
@RequestMapping(value = "stepTwo", method = RequestMethod.POST)
public String stepTwoAccountRegistration(@ModelAttribute AccountForm accountForm, BindingResult bindingResult) {
 if (isNotValid(accountForm, bindingResult, AccountStepTwo.class)) {
  return "account/stepTwo";
 }

 return "redirect:summary";
}
```

In the final step we may want to validate the complete AccountForm object. To do so, we call the validator as following:

```java
@Transactional
@RequestMapping("finish")
public String finishAccountRegistration(@ModelAttribute AccountForm accountForm, BindingResult bindingResult, SessionStatus sessionStatus) {
 if (isNotValid(accountForm, bindingResult, AccountStepOne.class, AccountStepTwo.class)) {
  return "redirect:stepOne";
 }
 User user = createUser(accountForm);
 sessionStatus.setComplete();
 FlashMap.setInfoMessage("Account'" + user.getName() + "' created!");
 return "redirect:../user/list";
}
```

This time we passed both groups to the validator to make sure all fields are going to be validated. If the object is valid, we store it in database and finish the wizard by calling org.springframework.web.bind.support.SessionStatus.setComplete(). Please note that form object is not passed from the form but it is retrieved from the session for us (see complete code)

### Summary

In above steps I presented how easy we may utilize JSR303 validation groups functionality in Spring MVC 3 wizard-style controllers. Hopefully, in Spring 3.1 this workaround will not be needed anymore.

### Update

Have a look at the follow up post that describes the automatic validation with Spring's `@Validated` annotation (with the source code on GitHub): [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md).

### References

- [JSR303 Specification](http://people.redhat.com/~ebernard/validation/)
- [Hibernate Validator documentation](http://docs.jboss.org/hibernate/stable/validator/reference/en-US/html)
- [Spring 3.x reference - Validation, Data Binding, and Type Conversion](http://static.springsource.org/spring/docs/3.0.x/spring-framework-reference/html/validation.html)

### Downloads

Project created with Maven2 and Eclipse and was tested with Tomcat 7.

Download: [bean-validation-springmvc-demo.zip](https://sites.google.com/a/codeleak.pl/blogfiles/home/bean-validation-springmvc-demo.zip?attredirects=0&d=1)

### Follow up

Have a look at the follow up post that describes the automatic validation with Spring's `@Validated` annotation: [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md).
