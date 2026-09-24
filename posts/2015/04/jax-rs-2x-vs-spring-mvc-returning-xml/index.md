---
title: "JAX-RS 2.x vs Spring MVC: Returning an XML representation of a list of objects"
date: 2015-04-21T00:35:00.000+02:00
updated: 2015-04-21T00:35:48.599+02:00
author: "Rafał Borowiec"
tags: ["jersey", "spring"]
original_url: https://blog.codeleak.pl/2015/04/jax-rs-2x-vs-spring-mvc-returning-xml.html
---

# JAX-RS 2.x vs Spring MVC: Returning an XML representation of a list of objects

JSON is King as it goes to all kinds of REST* APIs, but still you may need to expose multiple representations, including XML. With both JAX-RS and Spring MVC this is very simple. Actually, the only thing to do is to annotate POJOs returned from the API call with JAXB annotation and that’s it.

But when it goes to serializing a list of objects, JAX-RS will do a bit better than Spring MVC, in my opinion. Let’s see.

## POJO

The only requirement for both (assuming JAXB is used) is to annotate a POJO with JAXB annotation:

```java
@XmlRootElement
public class Incident {

}
```

## JAX-RS Way

```java
@GET
@Path("user/{userId}/incident")
public List<Incident> getUserIncidents(@PathParam("userId") long userId) {
    // return
}
```

When the above method is executed with `application/json` as accepted representation, JAX-RS will serialize a returned list properly to a JSON like the one below:

```json
[
  {
    "description": "Lorem ipsum..." ,
    "status": "NEW"
  },
  {
    "description": "Lorem ipsum..." ,
    "status": "NEW"
  }
]
```

No special wrapper objects. The resulting XML may look like below:

```xml
<incidents>
    <incident>
        <description>Lorem ipsum ...</description>
        <status>NEW</status>
    </incident>
    <incident>
        <description>Lorem ipsum ...</description>
        <status>NEW</status>
    </incident>
</incidents>
```

It just works. No wrapper objects. No extra work. We are done.

## Spring MVC Way (JAXB)

How would you do it in Spring (let’s say Spring Boot as it is the fastest to start with)?

```java
@RequestMapping(value = "user/{userId}/incident")
public List<Incident> getUserIncidents(@PathVariable("userId") long userId) {
    // return
}
```

Once JSON representation is requested with the following request:

```
$ curl -i http://localhost:8080/user/3/incident
```

The result is the same as in case of JAX-RS.

To get the server to render XML instead of JSON you might have to send an `Accept: text/xml` header:

```
$ curl -i -H "Accept: text/xml" http://localhost:8080/user/3/incident
```

But the result will be: *406 Not Acceptable. Could not find acceptable representation* in that case.

## Spring MVC Way (jackson-dataformat-xml)

With Spring MVC there is a solution that will work out-of-the-box, similarly to JAX-RS but with a bit *worse* output. The solution uses jackson-dataformat-xml. Add dependency to your project:

```xml
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>
```

With the new dependency, a call for an XML representation should return something like this:

```xml
<ArrayList>
    <item>
        <description>Lorem ipsum ...</description>
        <status>NEW</status>
    </item>
    <item>
        <description>Lorem ipsum ...</description>
        <status>NEW</status>
    </item>
</ArrayList>
```

Please note, that using JAXB annotations is not required with jackson-dataformat-xml.
