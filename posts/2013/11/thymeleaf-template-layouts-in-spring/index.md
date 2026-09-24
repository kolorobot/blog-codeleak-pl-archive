---
title: "Thymeleaf template layouts in Spring MVC application with no extensions"
date: 2013-11-09T17:10:00.002+01:00
updated: 2017-01-17T22:02:36.290+01:00
author: "Rafał Borowiec"
tags: ["java", "spring mvc", "thymeleaf"]
original_url: https://blog.codeleak.pl/2013/11/thymeleaf-template-layouts-in-spring.html
---

# Thymeleaf template layouts in Spring MVC application with no extensions

After some years with JSP/JSTL and Apache Tiles I started discovering Thymeleaf for my Spring MVC applications. Thymeleaf is a really great view engine and it simplifies and speeds up the development despite that lack of good IntelliJ (vote here: <http://youtrack.jetbrains.com/issue/IDEABKL-6713>) support at the moment (there is an [Eclipse plugin](https://github.com/thymeleaf/thymeleaf-extras-eclipse-plugin) though). While learning how to use Thymeleaf I investigated different possibilities of working with layouts.

Apart from the native [fragment inclusion mechanism](http://www.thymeleaf.org/doc/html/Using-Thymeleaf.html#template-layout) there are at least two options to work with layouts: [Thymeleaf integration with Apache Tile](https://github.com/thymeleaf/thymeleaf-extras-tiles2) and [Thymeleaf Layout Dialect](https://github.com/ultraq/thymeleaf-layout-dialect). Both seem to work fine, but inspired by this [comment](../../../2013/11/is-it-worth-upgrading-to-thymeleaf-21/index.md#c5722173744814267184) about a simple and custom option, I gave it a try. In this post I will show I created the solution.

### *Change Log*

- 17/01/2017 - Source code updated. Fixed bug with casting in the interceptor. Library upgrade.
- 04/12/2016 - Source code updated. Thymeleaf 3.0.2
- 26/07/2016 - Source code updated. No Layout option introduced (@Layout(Layout.NONE)), integration tests, POM improvements and updates.

### Create a Spring MVC project with Thymeleaf support

To get started quickly I used my [Spring MVC Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype/tree/thymeleaf) with Thymeleaf 2.1 support. I created a project by simply invoking the archetype and then imported it to IntellJ.

### Creating the layout file

In WEB-INF/views directory I created a layouts folder where I placed the my first layout file called default.html:

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">

<head>...</head>
<body>
<div th:raplace="fragments/header :: header">
    Header
</div>
<div th:replace="${view} :: content">
    Content
</div>
<div th:replace="fragments/footer :: footer">
    Footer
</div>
</body>
</html>
```

The ${view} variable will contain the view name returned by the @Controller and the content fragment from ${view} file will be placed here.

### Creating the view file

I edited WEB-INF/views/homeNotSignedIn.html and I defined the content fragment like this:

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">

<head>...</head>
<body>
<div class="container" th:fragment="content">
    <!-- /* Handle the flash message */-->
    <th:block th:if="${message != null}">
        <div th:replace="fragments/alert :: alert (type=${#strings.toLowerCase(message.type)}, message=${message.message})">&nbsp;</div>
    </th:block>
    <p>
        Hello <span th:text="${#authentication.name}">User</span>!
        Welcome to the Spring MVC Quickstart application!
    </p>
</div>
</body>
</html>
```

So the only change was defining the fragment named content and removing duplicated fragment inclusions. No additional changes are required. The @Controller returns the original view name, as it was before:

```java
@Controller
class HomeController {
 
 @RequestMapping(value = "/", method = RequestMethod.GET)
 String index(Principal principal) {
  return principal != null ? "home/homeSignedIn" : "home/homeNotSignedIn";
 }
}
```

I changed other views accordingly.

### Creating the interceptor and integrating with Spring MVC

To finish the "new layout framework" I created a handler interceptor that will do the work:

```java
public class ThymeleafLayoutInterceptor extends HandlerInterceptorAdapter {

    private static final String DEFAULT_LAYOUT = "layouts/default";
    private static final String DEFAULT_VIEW_ATTRIBUTE_NAME = "view";

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        if (modelAndView == null || !modelAndView.hasView()) {
            return;
        }
        String originalViewName = modelAndView.getViewName();
        modelAndView.setViewName(DEFAULT_LAYOUT);
        modelAndView.addObject(DEFAULT_VIEW_ATTRIBUTE_NAME, originalViewName);
    }    
}
```

ThymeleafLayoutInterceptor gets the original view name returned from the handler's method and replaces it with the layout name (that is defined in WEB-INF/views/layouts/default.html). The original view is placed in the model as a view variable, so it can be used in the layout file. I overrode the postHandle method, as it is executed just before rendering the view.   
Adding the interceptor is easy:

```java
@Configuration
public class WebMvcConfig extends WebMvcConfigurationSupport {
    @Override
    protected void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new ThymeleafLayoutInterceptor());
    }
}
```

And that's it for the basic configuration. Not a rocket since. The result after going to localhost:8080. This is what I expected. Works like a charm. So I try to signup for an account and what I see after submitting a form:

```
500 returned for /signup with message Error resolving template "redirect:/", template might not exist or might not be accessible by any of the configured Template Resolvers
```

Of course, **redirect:/** after the form submission. I needed to modify the interceptor like this:

```java
public class ThymeleafLayoutInterceptor extends HandlerInterceptorAdapter {

    private static final String DEFAULT_LAYOUT = "layouts/default";
    private static final String DEFAULT_VIEW_ATTRIBUTE_NAME = "view";

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        if (modelAndView == null || !modelAndView.hasView()) {
            return;
        }
        String originalViewName = modelAndView.getViewName();
        if (isRedirectOrForward(originalViewName)) {
            return;
        }
        modelAndView.setViewName(DEFAULT_LAYOUT);
        modelAndView.addObject(DEFAULT_VIEW_ATTRIBUTE_NAME, originalViewName);
    } 
    private boolean isRedirectOrForward(String viewName) {
        return viewName.startsWith("redirect:") || viewName.startsWith("forward:");
    }   
}
```

And it worked as expected. But I realized that I need to define and additional layout because Signup and Signin used this before, but not after applying the above changes.

### Creating additional layouts

I created a new layout called blank.html and placed it to WEB-INF/views/layouts folder. But how to use select the layout? Probably there are many ways to do this. One of the easiest I though is to return the layout name from the @Controller by simply adding a model attribute named layout. If no layout is given, default one is used, otherwise the given one. Simple. But I wanted a more robust solution. So I thought maybe an annotation that I could use like this:

```java
@Controller
class SigninController {

    @Layout(value = "layouts/blank")
    @RequestMapping(value = "signin")
    String signin() {
        return "signin/signin";
    }
}
```

To me it sounded like a good solution. So I implemented it.

### Selecting the layout

I created a method level @Layout annotation that I placed in org.thymeleaf.spring.support package (together with ThymeleafLayoutInterceptor):

```java
package org.thymeleaf.spring.support;

import java.lang.annotation.*;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Layout {
    String value() default "";
}
```

I changed the interceptor as follows:

```java
public class ThymeleafLayoutInterceptor extends HandlerInterceptorAdapter {

    private static final String DEFAULT_LAYOUT = "layouts/default";
    private static final String DEFAULT_VIEW_ATTRIBUTE_NAME = "view";

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        if (modelAndView == null || !modelAndView.hasView()) {
            return;
        }
        String originalViewName = modelAndView.getViewName();
        if (isRedirectOrForward(originalViewName)) {
            return;
        }
        String layoutName = getLayoutName(handler);
        modelAndView.setViewName(layoutName);
        modelAndView.addObject(DEFAULT_VIEW_ATTRIBUTE_NAME, originalViewName);
    }

    private boolean isRedirectOrForward(String viewName) {
        return viewName.startsWith("redirect:") || viewName.startsWith("forward:");
    }

    private String getLayoutName(Object handler) {
        HandlerMethod handlerMethod = (HandlerMethod) handler;
        Layout layout = handlerMethod.getMethodAnnotation(Layout.class);
        if (layout == null) {
            return DEFAULT_LAYOUT;
        } else {
            return layout.value();
        }
    }
}
```

Now, when the handler method is annotated with @Layout annotation, it get its value attribute. Works great. But when I started to change SignupController I realized I need to annotate both methods. It would be better if my annotation can be used for all methods at once, by annotating the @Controller class:

```java
@Controller
@Layout(value = "layouts/blank")
class SignupController {

}
```

So I did.

### Final touches

Firstly, I changed the annotation so it can be targeted at the type level:

```java
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Layout {
    String value() default "";
}
```

And the interceptor:

```java
public class ThymeleafLayoutInterceptor extends HandlerInterceptorAdapter {

    private static final String DEFAULT_LAYOUT = "layouts/default";
    private static final String DEFAULT_VIEW_ATTRIBUTE_NAME = "view";

    private String defaultLayout = DEFAULT_LAYOUT;
    private String viewAttributeName = DEFAULT_VIEW_ATTRIBUTE_NAME;

    public void setDefaultLayout(String defaultLayout) {
        Assert.hasLength(defaultLayout);
        this.defaultLayout = defaultLayout;
    }

    public void setViewAttributeName(String viewAttributeName) {
        Assert.hasLength(defaultLayout);
        this.viewAttributeName = viewAttributeName;
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
        if (modelAndView == null || !modelAndView.hasView()) {
            return;
        }
        String originalViewName = modelAndView.getViewName();
        if (isRedirectOrForward(originalViewName)) {
            return;
        }
        String layoutName = getLayoutName(handler);
        modelAndView.setViewName(layoutName);
        modelAndView.addObject(this.viewAttributeName, originalViewName);
    }

    private boolean isRedirectOrForward(String viewName) {
        return viewName.startsWith("redirect:") || viewName.startsWith("forward:");
    }

    private String getLayoutName(Object handler) {
        if (handler instanceof HandlerMethod) {
            HandlerMethod handlerMethod = (HandlerMethod) handler;
            Layout layout = getMethodOrTypeAnnotation(handlerMethod);
            if (layout != null) {
                return layout.value();
            }
        }
        return this.defaultLayout;
    }

    private Layout getMethodOrTypeAnnotation(HandlerMethod handlerMethod) {
        Layout layout = handlerMethod.getMethodAnnotation(Layout.class);
        if (layout == null) {
            return handlerMethod.getBeanType().getAnnotation(Layout.class);
        }
        return layout;
    }
}
```

As you can see method level annotation is more important than type level annotation, which gives some flexibility. In addition, I added a possibility to configure the interceptor. I thought, that setting the default layout name and view attribute name may be useful.

### Summary

The presented solution may need some polishing in order to use it in production, but it shows how simply we can build template layouts without adding extra libraries to our project and utilizing only core Thymeleaf features. Please share you comments and opinions about the solution.

**Please find the source code on GitHub: <https://github.com/kolorobot/thymeleaf-custom-layout>**
