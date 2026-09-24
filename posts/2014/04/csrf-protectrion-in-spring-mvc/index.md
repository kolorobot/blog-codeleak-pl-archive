---
title: "CSRF protection in Spring MVC, Thymeleaf, Spring Security application"
date: 2014-04-10T00:43:00.000+02:00
updated: 2014-06-06T21:41:43.036+02:00
author: "Rafał Borowiec"
tags: ["spring", "spring mvc", "spring security", "thymeleaf"]
original_url: https://blog.codeleak.pl/2014/04/csrf-protectrion-in-spring-mvc.html
---

# CSRF protection in Spring MVC, Thymeleaf, Spring Security application

Cross-Site Request Forgery (CSRF) is an attack which forces an end user to execute unwanted actions on a web application in which he/she is currently authenticated. Preventing CSRF attacks in Spring MVC / Thymeleaf application is fairly easy if you use Spring Security 3.2 and above.

## How to test?

To test I created a application with restricted area where I can send a form. The form's source code:

```html
<form class="form-narrow form-horizontal" method="post" th:action="@{/message}" th:object="${messageForm}" action="http://localhost:8080/message">
    <fieldset>
        <legend>Send a classified message</legend>
        <div class="form-group" th:classappend="${#fields.hasErrors('payload')}? 'has-error'">
            <label for="payload" class="col-lg-2 control-label">Payload</label>
            <div class="col-lg-10">
                <input type="text" class="form-control" id="payload" placeholder="Payload" th:field="*{payload}" name="payload"/>
                <span class="help-block" th:if="${#fields.hasErrors('payload')}" th:errors="*{payload}">May not be empty</span>
            </div>
        </div>
        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" class="btn btn-default">Send</button>
            </div>
        </div>
    </fieldset>
</form>
```

Knowing that the action URL was http://localhost:8080/message I created a separate page with a HTTP request referencing that URL (with all parameters):

```html
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
<form action="http://localhost:8080/message" method="post">
    <input type="hidden" name="payload" value="Hacked content!"/>
    <input type="submit" value="Hack!" />
</form>
</body>
</html>
```

I logged on the application and executed the above code. Of course the server allowed me to execute the request because my application is vulnerable to CSRF attacks. To learn more about testing for CSRF visit this link: [Testing for CSRF](https://www.owasp.org/index.php/Testing_for_CSRF_(OWASP-SM-005)).

## How to secure?

If you are using the XML configuration with Spring Security the CSRF protection must be enabled:

```xml
<security:http auto-config="true" disable-url-rewriting="true" use-expressions="true">
    <security:csrf />
    <security:form-login login-page="/signin" authentication-failure-url="/signin?error=1"/>
    <security:logout logout-url="/logout" />
    <security:remember-me services-ref="rememberMeServices" key="remember-me-key"/>

    <!-- Remaining configuration -->

</security:http>
```

In case of Java configruation - it is enabled by default.

As of version Thymeleaf 2.1, CSRF token will be automatically added into forms with hidden input:

```xml
<form class="form-narrow form-horizontal" method="post" action="/message">

    <!-- Fields -->

    <input type="hidden" name="_csrf" value="16e9ae08-76b9-4530-b816-06819983d048" />

</form>
```

Now, when you try to repeat the attack, you will see *Access Denied* error.

One thing to remember, though, is that enabling CSRF protection ensures that log out requires a CSRF token. I used JavaScript to submit a hidden form:

```xml
<a href="/logout" th:href="@{#}" onclick="$('#form').submit();">Logout</a>

<form style="visibility: hidden" id="form" method="post" action="#" th:action="@{/logout}"></form>
```

## Summary

In this short article, I showed how easily you can utilize CSRF protection whilst working with Spring MVC (3.1+), Thymeleaf (2.1+) and Spring Security (3.2+). As of Spring Security 4 CSRF will be enabled by default also when XML configuration will be used. Please note, that HTTP session is used in order to store CSRF token. But this can be easily changed. For more details, see references.

I included CSRF configuration in my [Spring MVC Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype). Please check!

## References

- [Thymeleaf - Integration with RequestDataValueProcessor](http://www.thymeleaf.org/doc/html/Thymeleaf-Spring3.html#integration-with-requestdatavalueprocessor)
- [Spring Security - CSRF Attacks](http://docs.spring.io/spring-security/site/docs/3.2.3.RELEASE/reference/htmlsingle/#csrf)
- [OWASP - Cross-Site Request Forgery (CSRF)](https://www.owasp.org/index.php/CSRF)
