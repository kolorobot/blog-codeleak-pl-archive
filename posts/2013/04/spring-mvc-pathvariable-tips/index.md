---
title: "Spring MVC @PathVariable Tips"
date: 2013-04-08T21:55:00.000+02:00
updated: 2014-08-12T23:36:50.945+02:00
author: "Rafał Borowiec"
tags: ["spring", "spring mvc"]
original_url: https://blog.codeleak.pl/2013/04/spring-mvc-pathvariable-tips.html
---

# Spring MVC @PathVariable Tips

`@PathVariable` annotation is one of the Spring MVC features that allows creating RESTful Web application much easier. It indicates that a handler method parameter should be bound to a URI template. In this post I will present two useful tips for working with this annotation.

### `@PathVariable` is merged into the model

As of Spring MVC 3.1 `@PathVariable` method argument values are merged into the model. The following example illustrates this behavior:

```java
@RequestMapping(value = "resource/{resourceId}", method = GET)
public String trello(@PathVariable ObjectId resourceId) {

 // resourceId will be merged into the model 
 return "resource/details";
}
```

In a view you can use the variable (e.g. to generate an action url of a form):

```xml
<c:url value="/resource/${resourceId}" var="action" />
```

### `@PathVariable` in a redirect string

Another useful feature is that a redirect string can contain placeholders for URI variables as shown below:

```java
@RequestMapping(value = "resource/{resourceId}", method = POST)
public String trello(@PathVariable ObjectId resourceId, 
  @ModelAttribute @Valid Resource resource) {

 // resourceId will be considered while expanding the placeholders
 return "redirect:/mail/{resourceId}/trello";
}
```

More on request mapping you can find in  [Spring MVC documentation](http://static.springsource.org/spring/docs/current/spring-framework-reference/html/mvc.html#mvc-ann-requestmapping)
