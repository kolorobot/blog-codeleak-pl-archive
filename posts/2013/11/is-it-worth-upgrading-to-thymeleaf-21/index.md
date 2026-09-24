---
title: "Is it worth upgrading to Thymeleaf 2.1?"
date: 2013-11-06T23:56:00.000+01:00
updated: 2014-06-06T21:56:06.196+02:00
author: "Rafał Borowiec"
tags: ["spring mvc", "thymeleaf"]
original_url: https://blog.codeleak.pl/2013/11/is-it-worth-upgrading-to-thymeleaf-21.html
---

# Is it worth upgrading to Thymeleaf 2.1?

Thymeleaf 2.1 release arrived. The new version brings plenty of new features in its core as well as in Spring Integration module like improvements of fragments inclusions, rendering view fragments directly from @Controller, improved form validation error reporting to name a few. But is it worth upgrading to Thymeleaf 2.1? Let's see.

### Get started with 2.1

To get started with Thymeleaf 2.1 we need to upgrade our project. If you have no project and you want to start quickly, check the Summary section. I work with Maven so we will upgrade Maven dependencies in pom.xml:

```xml
        <properties>
            <org.thymeleaf-version>2.1.0.RELEASE</org.thymeleaf-version>
        </properties>

        <!-- View -->
        <dependency>
            <groupId>org.thymeleaf</groupId>
            <artifactId>thymeleaf</artifactId>
            <version>${org.thymeleaf-version}</version>
        </dependency>
        <dependency>
            <groupId>org.thymeleaf</groupId>
            <artifactId>thymeleaf-spring3</artifactId>
            <version>${org.thymeleaf-version}</version>
        </dependency>
        <dependency>
            <groupId>org.thymeleaf.extras</groupId>
            <artifactId>thymeleaf-extras-springsecurity3</artifactId>
            <version>2.1.0.RELEASE</version>
        </dependency>
```

Spring Security 3 module is using its own versioning, so I did not use the same variable, as you noticed. And remember to upgrade this module. Otherwise you may expect an runtime exceptions like the below:

```
org.thymeleaf.spring3.expression.SpelVariableExpressionEvaluator.computeContextVariables(Lorg/thymeleaf/Configuration;Lorg/thymeleaf/context/IProcessingContext;)Ljava/util/Map;
```

### Improved form validation error reporting

For the following form:

```html
<form class="form-narrow form-horizontal" method="post" th:action="@{/signup}" th:object="${signupForm}">
    <fieldset>
        <legend>Please Sign Up</legend>
        <div class="form-group" th:classappend="${#fields.hasErrors('email')}? 'has-error'">
            <label for="email" class="col-lg-2 control-label">Email</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="email" placeholder="Email address" th:field="*{email}" />
                <span class="help-block" th:if="${#fields.hasErrors('email')}" th:errors="*{email}">Incorrect email</span>
            </div>
        </div>
        <div class="form-group" th:classappend="${#fields.hasErrors('password')}? 'has-error'">
            <label for="password" class="col-lg-2 control-label">Password</label>
            <div class="col-lg-10">
                <input type="password" class="form-control" id="password" placeholder="Password" th:field="*{password}"/>
                <span class="help-block" th:if="${#fields.hasErrors('password')}" th:errors="*{password}">Incorrect password</span>
            </div>
        </div>
        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" class="btn btn-default">Sign up</button>
            </div>
        </div>
        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <p>Already have an account? <a href="signin" th:href="@{/signin}">Sign In</a></p>
            </div>
        </div>
    </fieldset>
</form>
```

We are able to show a general error message outside the `form` element like this:

```html
<div class="alert alert-dismissable alert-danger" th:if="${#fields.hasErrors('${signupForm.*}')}">
    <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
    <span>Please correct the form and try again!</span>
</div>

<form class="form-narrow form-horizontal" method="post" th:action="@{/signup}" th:object="${signupForm}">
   ...
</form>
```

If you want to know more about form error handling see [New th:errorclass for adding CSS class to form fields in error](http://www.thymeleaf.org/whatsnew21.html#errcl) and [Additional form validation error reporting options](http://www.thymeleaf.org/whatsnew21.html#sperr)

### Fragments inclusions improvements

As of Thymeleaf 2.1 we can pass parameters to template fragments which improves reusability and readability of the templates. With the combination of newly introduced `th:block` we can do the following:

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">
<body>
    <div th:fragment="alert (type, message)" class="alert alert-dismissable" th:classappend="'alert-' + ${type}">
        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
        <span th:text="${message}">Test</span>
    </div>
</body>
</html>
```

This is standard template fragment that is placed in `fragments/alert.html` template. The fragment accepts two named parameters: `type` and `messagea`. These parameters are used to generate the content of the alert we want to include. To include the fragment we will do the following:

```html
<th:block th:if="${#fields.hasErrors('${signupForm.*}')}">
    <div th:replace="fragments/alert :: alert (type='danger', message='Form contains errors. Please try again.')">Alert</div>
</th:block>
```

Please notice the usage of `th:block` that is an attribute container of whichever attributes. Thymeleaf will execute these attributes and then simply make the block disapear without a trace. So the above code works as follows: if there are errors in the form, include the alert fragment with type and message parameters. Pretty nice.

Having parametrized fragment we are able to reuse it in more templates, e.g. to display flash messages from the @Controller:

```html
    <!-- /* Handling the flash message */-->
    <th:block th:if="${message != null}">
        <div th:replace="fragments/alert :: alert (type=${#strings.toLowerCase(message.type)}, message=${message.message})">&nbsp;</div>
    </th:block>
```

### Summary

Thymeleaf 2.1 brings many improvements. In this post we saw couple of them only and I think **it is worth upgrading to Thymeleaf 2.1**. No doubt about it. If you want to learn more, visit [What's new in Thymeleaf 2.1](http://www.thymeleaf.org/whatsnew21.html) page.

To get started quickly with Spring and Thymeleaf use [Spring MVC Quickstart Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype). You will find the above improvements in [Thymeleaf](https://github.com/kolorobot/spring-mvc-quickstart-archetype/tree/thymeleaf) branch.

EDIT. Inspired by one of the comments I wrote a post regarding template layouts in Thymeleaf. I hope you will find it interesting: [Thymeleaf template layouts in Spring MVC application with no extensions](../../../2013/11/thymeleaf-template-layouts-in-spring/index.md)
