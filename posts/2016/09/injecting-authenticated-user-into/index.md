---
title: "Injecting authenticated user into Spring MVC @Controllers"
date: 2016-09-14T00:16:00.001+02:00
updated: 2016-09-14T07:53:59.353+02:00
author: "Rafał Borowiec"
tags: ["spring mvc", "spring security"]
original_url: https://blog.codeleak.pl/2016/09/injecting-authenticated-user-into.html
---

# Injecting authenticated user into Spring MVC @Controllers

Injecting injecting authenticated user into Spring MVC handler method can be done with `@AuthenticationPrincipal` annotation and `AuthenticationPrincipalArgumentResolver` that is an implementation of Spring MVS `MethodArgumentResolver`. `AuthenticationPrincipalArgumentResolver` is registered by default with web security configuration (e.g. when you enable security with `@EnableWebSecurity`).

### 1. Custom `UserDetails`

Let’s assume we have our custom `UserDetails` implementation:

```java
import org.springframework.security.core.GrantedAuthority;
import pl.codeleak.surveyapp.entities.Member;

import java.util.Collection;

public class AccountDetails
    extends org.springframework.security.core.userdetails.User {

    private final Account account;

    public AccountDetails(Account account,
                          Collection<? extends GrantedAuthority> authorities) {
        super(account.getMember().getEmail(), account.getPassword(), authorities);
        this.account = account;
    }

    public Account getAccount() {
        return account;
    }

    public Member getMember() {
        return account.getMember();
    }
}
```

`AccountDetails` has two additional methods that allow accessing a related account and member information. `AccountDetails` is then used by our own `UserDetailsService` implementation that is later used by Spring Security DAO Authentication Manager to authenticate users.

Note: Spring Security configuration is out of the scope of this article.

### 2. Injecting `AccountDetails`

The most basic use of `@AuthenticationPrincipal` annotation is to inject UserDetails. In our scenario we want `AccountDetails` to be injected. In order to do so simply put `@AuthenticationPrincipal` annotated argument to Spring MVC handler method:

```java
@RequestMapping(value = {"", "/", "index.html"})
public String index(@AuthenticationPrincipal AccountDetails accountDetails) {
    return "index";
}
```

In case the authenticated user does not exist `accountDetails` will evaluate to `null`. In case user is authenticated - `accountDetails` will evaluate to a valid object.

Note: As of Spring 4.0 you should use `org.springframework.security.core.annotation.AuthenticationPrincipal`

### 3. Using `expression` to inject `AccountDetails` properties

`AccountDetails` has two additional methods the get the `account` and `member` objects. If we want to inject them directly into the handler method we can use `expression` property of `@AuthenticatedPricipal` annotation:

```java
@RequestMapping(value = {"", "/", "index.html"})
public String index(@AuthenticationPrincipal(expression = "account") Account account) {
    return "index";
}
```

```java
@RequestMapping(value = {"", "/", "index.html"})
public String index(@AuthenticationPrincipal(expression = "member") Member member) {
    return "index";
}
```

The expression defines a SpEL expression that will be used when injecting the argument. Pretty handy.

### 4. ‘Extending’ `@AuthenticationPrincipal` annotation

Instead of repeating in handler methods `@AuthenticationPrincipal(expression = "account") Account account` we may create a meta annotation and use it in our `@Controller`s:

```java
@Target({ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@AuthenticationPrincipal(expression = "account")
public @interface LoggedInAccount {

}
```

### 5. `@AuthenticationPrincipal` in Spring Security 3.2 and Spring Security 4+

- Spring Security 3.2 - `org.springframework.security.web.bind.annotation.AuthenticationPrincipal`
- Spring Security 4.0 - `org.springframework.security.core.annotation.AuthenticationPrincipal`
