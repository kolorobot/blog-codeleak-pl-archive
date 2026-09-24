---
title: "Spring Security 3.1: Enhanced security namespace configuration"
date: 2011-04-28T22:58:00.002+02:00
updated: 2014-06-06T22:04:22.903+02:00
author: "Codeleak.pl"
tags: ["spring", "spring security"]
original_url: https://blog.codeleak.pl/2011/04/spring-security-31-enhanced-security.html
---

# Spring Security 3.1: Enhanced security namespace configuration

Security namespace configuration in Spring Security 3.1 improved. The change that made my life easier is the possibility of using multiple `<http>` to configure security in web application. Each `<http>` can now configure separate filter chain for different request pattern. This is very useful when you have a web application that consist of standard web application and the API and you want API to be accessible only with basic authentication.
To achieve that in Spring Security 3.1 you need to define security configuration as following:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:sec="http://www.springframework.org/schema/security"
    xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
  http://www.springframework.org/schema/security http://www.springframework.org/schema/security/spring-security-3.1.xsd">

    <sec:global-method-security secured-annotations="enabled" pre-post-annotations="enabled" />

    <sec:authentication-manager>
        <sec:authentication-provider>
            <sec:user-service>
                <sec:user name="user" password="user" authorities="ROLE_USER" />
                <sec:user name="api" password="api" authorities="ROLE_APIUSER" />
            </sec:user-service>
        </sec:authentication-provider>
    </sec:authentication-manager>
    
    <sec:http pattern="/app/login" security="none"/>
    
    <sec:http pattern="/app/api/**" create-session="stateless" realm="My application API" >
        <sec:intercept-url pattern="/**" access="ROLE_APIUSER" />
        <sec:http-basic />
    </sec:http>
    
    <sec:http create-session="ifRequired">
        <sec:intercept-url pattern="/app/**" access="ROLE_USER"/>
        <sec:form-login login-page="/app/login" always-use-default-target="false" default-target-url="/app/"
            authentication-failure-url="/app/login?login_error=true" password-parameter="password" username-parameter="username" />
        <sec:logout invalidate-session="true" />
    </sec:http>

</beans>
```

Each time user accesses `/app/api/**` url in browser he sees basic authentication login dialog. In case he accesses `/app/**` he is redirected to the login form.

### What is new

Except for multiple `<http>` elements there some additional changes in above configuration

```xml
<sec:http pattern="/app/login" security="none" />
```

**pattern** attribute that represents the request URL pattern which will be mapped to the filter chain created by http element and **security** attribute that when set to 'none', requests matching the pattern attribute will be ignored by Spring Security.

```xml
<sec:http pattern="/app/api/**" create-session="stateless" />
```

**create-session** attribute has new possible value: **stateless** which implies that the application guarantees that it will not create a session.

```xml
<sec:form-login login-page="/app/login" always-use-default-target="false" default-target-url="/app/" authentication-failure-url="/app/login?login_error=true" password-parameter="password" username-parameter="username" />
```

**password-parameter** that is the name of the request parameter which contains the password and **username-parameter** - the name of username parameter.

### References

<http://static.springsource.org/spring-security/site/docs/3.1.x/reference/ns-config.html>
<http://static.springsource.org/spring-security/site/docs/3.1.x/reference/security-filter-chain.html#filter-chains-with-ns>
