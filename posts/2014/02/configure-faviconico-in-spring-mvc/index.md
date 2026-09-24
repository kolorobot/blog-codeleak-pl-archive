---
title: "Configure favicon.ico in Spring MVC based application"
date: 2014-02-12T00:36:00.000+01:00
updated: 2014-06-06T21:24:45.731+02:00
author: "Rafał Borowiec"
tags: ["java", "practices", "spring mvc"]
original_url: https://blog.codeleak.pl/2014/02/configure-faviconico-in-spring-mvc.html
---

# Configure favicon.ico in Spring MVC based application

Favicon is an icon (favicon.ico) associated with your website. Not every website is using favicon though. But most browsers do not care about it and they make request for it anyways. When favicon is not in place the server will return unnecessary `404 Not Found` error.

In a typical Spring MVC application, we firstly need to configure security filter that it permits all requests to favicon.ico, because Spring Security caches the user's requests, including favicon.ico request. After successful authentication, Spring Security will redirect us to that resource showing the error. To avoid it we configure the security filter the following way:

```xml
<security:http auto-config="true" disable-url-rewriting="true" use-expressions="true">
    <security:form-login login-page="/signin" authentication-failure-url="/signin?error=1" />
    <security:logout logout-url="/logout" invalidate-session="false"/>
    <security:intercept-url pattern="favicon.ico" access="permitAll" />
    <security:intercept-url pattern="/" access="permitAll" />
    <security:intercept-url pattern="/error" access="permitAll" />
    <security:intercept-url pattern="/resources/**" access="permitAll" />
    <security:intercept-url pattern="/signin" access="permitAll" />
    <security:intercept-url pattern="/signup" access="permitAll" />
    <security:intercept-url pattern="/**" access="isAuthenticated()" />
</security:http>
```

The configuration assures that when favicon.ico is requested, no authentication is required. This trick prevents us from seeing `404 Not Found` after logging in to the application.

Usually this is all we need to do to make `404 Not Found` "disappear" in Spring MVC/Spring Security application. But in fact, the client will still look for this resource and the server will return `404 Not Found` error.

The are some ways, in case we don't want to use favicon for our website, to make the server does not return an error upon a request.

Probably the easiest way is to add a "blank" favicon.ico to your static resources and let the server serve this file upon request. In the below configuration, Spring handles static resources from a `/resources/` directory which is mapped to `/resources/**` path:

```java
@Configuration
public class WebMvcConfig extends WebMvcConfigurationSupport {
 

 private static final String RESOURCES_HANDLER = "/resources/";
 private static final String RESOURCES_LOCATION = RESOURCES_HANDLER + "**";

 
 @Override
 public void addResourceHandlers(ResourceHandlerRegistry registry) {
  registry.addResourceHandler(RESOURCES_HANDLER).addResourceLocations(RESOURCES_LOCATION);
 }

}
```

The favicon.ico file can be added to the `resource/images` directory, but then and additional `@Controller` should be created to forward any favicon.ico request to the actual icon. I am doing this with the static class within my configuration:

```java
@Configuration
public class WebMvcConfig extends WebMvcConfigurationSupport {

    @Controller
    static class FaviconController {
        @RequestMapping("favicon.ico")
        String favicon() {
            return "forward:/resources/images/favicon.ico";
        }
    }

}
```

How it works? When a client requests `localhost:8080/favicon.ico`, the controller will forward a request to a static resource. In future, when you need a favicon.ico to be served for your website, just replace the file in `resources/images` directory and you are done.

The other way, I thought of recently, is adding a `@Controller` that has a single method returning an empty `@ResponseBody`:

```java
@Controller
class FaviconController {
    @RequestMapping("favicon.ico")
    @ResponseBody
    void favicon() {}
}
```

It will solve the problem with `404 Not Found` but in future you will need to remember of making a configuration change, in case you will need to add favicon.ico for you website.

The configuration can be found in the [Spring MVC Quickstart Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype) on GitHub.
