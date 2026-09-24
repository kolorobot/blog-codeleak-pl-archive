---
title: "Spring 3.1 HttpPutFormContentFilter: supporting PUT request with form encoded data"
date: 2011-09-11T13:30:00.000+02:00
updated: 2014-06-06T22:01:06.165+02:00
author: "Codeleak.pl"
tags: ["spring"]
original_url: https://blog.codeleak.pl/2011/09/spring-31-httpputformcontentfilter.html
---

# Spring 3.1 HttpPutFormContentFilter: supporting PUT request with form encoded data

Spring MVC 3.0 introduced many useful features to work with RESTful interface, including URI templates, content negotation, http method conversion and more. While dealing with RESTful or REST-like API you may like to utilize REST key principle - its Uniform Interface.  
  
  

## Problem

Recently, while developing such an API with Spring MVC, I experienced a problem with PUT method handling. I wanted to send form encoded data in PUT request (content type is application/x-www-form-urlencoded). The below code will not work in such case:
  

```java
@RequestMapping(method = RequestMethod.PUT)
public SomeObject update(@Valid SomeObject userData, BindingResult result) {

}
```

And why? Because of the servlet specification that does not handle form encoded data in PUT request properly.
  

## HttpPutFormContentFilter to the rescue!

There are at least couple of solutions or workarounds to have above problem resolved (see references). But there is one available in Spring 3.1 - org.springframework.web.filter.HttpPutFormContentFilter that makes form encoded data available through
ServletRequest.getParameter() family of methods during HTTP PUT requests and therefore makes that the automatic binding in Spring MVC works properly now!
To utilize the filter in your Spring MVC project, you need to modify web.xml by simply adding:
  

```xml
<filter>
 <filter-name>HttpPutFormContentFilter</filter-name>
 <filter-class>org.springframework.web.filter.HttpPutFormContentFilter</filter-class>
</filter>

<filter-mapping>
 <filter-name>HttpPutFormContentFilter</filter-name>
 <url-pattern>/*</url-pattern>
</filter-mapping>
```

What the filter does is: *it reads form encoded content from the body of the request, and wraps the ServletRequest in order to make the form data available as request parameters just like it is for HTTP POST requests.*.
And that is it! Works fine for me.
  

## Resources

[org.springframework.web.filter.HttpPutFormContentFilter](http://static.springsource.org/spring/docs/3.1.x/javadoc-api/org/springframework/web/filter/HttpPutFormContentFilter.html)  
<https://jira.springsource.org/browse/SPR-5628>  
<https://jira.springsource.org/browse/SPR-7030>
