---
title: "HOW-TO: Custom error pages in Tomcat with Spring MVC"
date: 2013-04-07T22:06:00.000+02:00
updated: 2014-06-06T21:59:05.527+02:00
author: "Rafał Borowiec"
tags: ["java", "spring"]
original_url: https://blog.codeleak.pl/2013/04/how-to-custom-error-pages-in-tomcat.html
---

# HOW-TO: Custom error pages in Tomcat with Spring MVC

Default Tomcat error pages look scary. In addition, they may expose valuable information including server version and exception stack trace. Servlet specification provides a way to configure an exceptional behavior through web.xml. One can configure either reaction on a specific Java exception or to a selected Http response code(s).
`error-page` element specifies a mapping between an error code or exception type to the path of a resource in the Web application:

```xml
<web-app>
 
 <!-- Prior to Servlet 3.0 define either an error-code or an exception-type but not both -->
 <error-page>
  <!-- Define error page to react on Java exception -->
  <exception-type>java.lang.Throwable</exception-type>
  <!-- The location of the resource to display in response to the error will point to the Spring MVC handler method -->
  <location>/error</location>
 </error-page>

 <error-page>
  <error-code>404</error-code>
  <location>/error</location>
 </error-page>
 
 <!-- With Servlet 3.0 and above general error page is possible --> 
 <error-page>
  <location>/error</location>
 </error-page>

</web-app>
```

Having the custom error pages defined in our web.xml, we need to add the Spring MVC `@Controller`. The `customError` handler method wraps the information, that we retrieve from the request, and returns it to the view.

```java
@Controller
class CustomErrorController {

 @RequestMapping("error") 
 public String customError(HttpServletRequest request, HttpServletResponse response, Model model) {
  // retrieve some useful information from the request
  Integer statusCode = (Integer) request.getAttribute("javax.servlet.error.status_code");
  Throwable throwable = (Throwable) request.getAttribute("javax.servlet.error.exception");
  // String servletName = (String) request.getAttribute("javax.servlet.error.servlet_name");
  String exceptionMessage = getExceptionMessage(throwable, statusCode);
  
  
  String requestUri = (String) request.getAttribute("javax.servlet.error.request_uri");
  if (requestUri == null) {
   requestUri = "Unknown";
  }
  
  String message = MessageFormat.format("{0} returned for {1} with message {3}", 
   statusCode, requestUri, exceptionMessage
  ); 
  
  model.addAttribute("errorMessage", message);  
  return "customError";
 }

 private String getExceptionMessage(Throwable throwable, Integer statusCode) {
  if (throwable != null) {
   return Throwables.getRootCause(throwable).getMessage();
  }
  HttpStatus httpStatus = HttpStatus.valueOf(statusCode);
  return httpStatus.getReasonPhrase();
 }
}
```

The produced message may look like following: `404 returned for /sandbox/bad with message Not Found`.   
To see the code in action, browse the source code of [Spring MVC Quickstart Archretype](https://github.com/kolorobot/spring-mvc-quickstart-archetype), or even better, generare a new project with it.
