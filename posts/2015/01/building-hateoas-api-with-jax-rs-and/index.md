---
title: "Building a HATEOAS API with JAX-RS and Spring"
date: 2015-01-06T18:51:00.000+01:00
updated: 2016-09-28T00:20:31.900+02:00
author: "Rafał Borowiec"
tags: ["jersey", "spring boot"]
original_url: https://blog.codeleak.pl/2015/01/building-hateoas-api-with-jax-rs-and.html
---

# Building a HATEOAS API with JAX-RS and Spring

![](jersey_spring.png)

In my previous [blog post](../../../2015/01/getting-started-with-jersey-and-spring/index.md) I showed how easy Jersey can be configured with Spring Boot. My exploration on Spring Boot and Jersey did not end and I investigated the possibility of using [Spring HATEOAS](https://github.com/spring-projects/spring-hateoas) along with Jersey in Spring Boot application. Spring HATEOS allows creating REST representations that follow the HATEOAS principle and (as of writing this article) has basic JAX-RS support for working with links. In this blog post I will share some examples of how I integrated Spring HATEOAS with Jersey in a Spring Boot application.

## Introduction

As the foundation for this article I used the example I created previously: (<https://github.com/kolorobot/spring-boot-jersey-demo>).

To get started with Spring HATEOAS I added the valid dependency to `build.gradle`:

```
compile("org.springframework.hateoas:spring-hateoas:0.16.0.RELEASE")
```

## Quick approach with `Resources` helper

The quickest approach for generating representation of entity object (`Customer`) is using Spring HATEOAS `Resource` and `Resources` helpers. The latter wrap a collection of entities returned by `CustomerRepository`. To generate a link I used `JaxRsLinkBuilder` which helps building resources links to JAX-RS resources by discovering the paths based on the `@Path` annotation.

```java
@Component
@Path("/customer")
@Produces(MediaType.APPLICATION_JSON)
public class CustomerController {

    @Inject
    private CustomerRepository customerRepository;

    @GET
    public Response findAll() {
        Resources<Customer> resources = new Resources<>(
                customerRepository.findAll(),
                JaxRsLinkBuilder
                        .linkTo(CustomerController.class)
                        .withSelfRel()
        );
        return Response.ok(resources).build();
    }
```

The result of calling the above method will be a collection resource with a self rel link:

```json
{
  "links": [
    {
      "rel": "self",
      "href": "http://localhost:8080/customer"
    }
  ],
  "content": [
    {
      "id": 1,
      "firstname": "Dave",
      "lastname": "Matthews",
      "emailAddress": {
        "value": "dave@dmband.com"
      }
    }
  ]
}
```

## Building representations with `ResourceAssemblerSupport` class

The `Resource`, `Resources`, `PagedResources` helpers are pretty handy, but there are situations where more control over created resources is needed.

To create custom transfer object from an entity `ResourceSupport` base class can be used:

```java
public class CustomerResource extends ResourceSupport {

    private String fullName;
    private String email;

}
```

To assemble `CustomerResource` from an entity and automatically add self rel link to it `ResourceAssemblerSupport` class should be used. Basically this class is responsible for instantiating the resource and adding a link with rel self pointing to the resource:

```java
public class CustomerResourceAssembler extends ResourceAssemblerSupport<Customer, CustomerResource> {

    public CustomerResourceAssembler() {
        super(CustomerController.class, CustomerResource.class);
    }

    @Override
    public CustomerResource toResource(Customer entity) {
            CustomerResource resource = createResourceWithId(
                    entity.getId(),
                    entity
            );

            // initialize the resource        

            return resource;
    }
}
```

The problem I had with the above code is that `ResourceAssemblerSupport` class internally uses a link builder for building links to Spring MVC controllers (`ControllerLinkBuilder`). This causes that links are invalid.

I did not find other way than creating a new support class that extends from `ResourceAssemblerSupport` and overrides the behavior of its parent:

```java
public abstract class JaxRsResourceAssemblerSupport<T, D extends ResourceSupport>
        extends ResourceAssemblerSupport<T, D> {

    private final Class<?> controllerClass;

    public JaxRsResourceAssemblerSupport(
            Class<?> controllerClass, Class<D> resourceType) {

        super(controllerClass, resourceType);
        this.controllerClass = controllerClass;
    }

    @Override
    protected D createResourceWithId(Object id, T entity, Object... parameters) {
        Assert.notNull(entity);
        Assert.notNull(id);

        D instance = instantiateResource(entity);

        instance.add(
                JaxRsLinkBuilder.linkTo(controllerClass, parameters)
                        .slash(id)
                        .withSelfRel());
        return instance;
    }
}
```

I don’t really like the above solution as I needed to copy and paste some code, but I did not find a better way to achieve what I wanted.

My assembler extends now from newly created `JaxRsResourceAssemblerSupport`:

```java
public class CustomerResourceAssembler 
        extends JaxRsResourceAssemblerSupport<Customer, CustomerResource> {

}
```

Finally I could modify controller’s method to return resources assembled by my assembler. Please note the `ResourceAssemblerSupport` provides convenient method to converts all given entities into resources:

```java
@GET
@Path("/resources")
public Response findAll() {
    Iterable<Customer> customers = customerRepository.findAll();

    CustomerResourceAssembler assembler = new CustomerResourceAssembler();
    List<CustomerResource> resources = assembler.toResources(customers);

    return Response.ok(wrapped).build();
}
```

To add a link with self rel link to the collection resource, I needed to wrap it using previously mentioned `Resources` class:

```java
// wrap to add link
Resources<CustomerResource> wrapped = new Resources<>(resources);
wrapped.add(
        JaxRsLinkBuilder
                .linkTo(CustomerController.class)
                .withSelfRel()
);
```

Now the returned representation looks more HATEOAS:

```json
{
  "links": [
    {
      "rel": "self",
      "href": "http://localhost:8080/customer"
    }
  ],
  "content": [
    {
      "fullName": "Matthews, Dave",
      "email": "dave@dmband.com",
      "links": [
        {
          "rel": "self",
          "href": "http://localhost:8080/customer/1"
        }
      ]
    }
  ]
}
```

## Using `LinksBuilder`

The `EntityLinks` interface provide API to create links based on entity type and are available for dependency injection when `@EnableEntityLinks` or `@EnableHypermadiaSupport` are used with `@ExposesResourceFor`. `@ExposesResourceFor`exposes which entity type the Spring MVC controller or JAX-RS resource manages.

In configuration class we need to activate entity links:

```java
@SpringBootApplication
@EnableEntityLinks
public class Application {

}
```

Note: Please note that when using entity links and `@EnableEntityLinks` the following dependency must be on the classpath:

```
 compile("org.springframework.plugin:spring-plugin-core:1.1.0.RELEASE")
```

Any JAX-RS resource supporting an entity type must be marked with `@ExposesResourceFor`, so `EntityLinks` can be injected:

```java
@ExposesResourceFor(Customer.class)
public class CustomerController {
    @Inject
    private EntityLinks entityLinks;
}
```

Basically, `EntityLinks` interface provides methods returning links to a collection resource or a single resource. Example:

```java
Link selfRel = entityLinks.linkToSingleResource(
        Customer.class, customer.getId()
).withSelfRel();
```

## Update: Integration Testing with Groovy

Integration testing of the API with Groovy and HTTPBuilder module, utilizing JSONSlurper: [Groovier Spring Boot Integration Testing](../../../2015/05/groovier-spring-boot-integration-testing/index.md)

## Summary

Spring HATEOAS is not the only option to build HATEOAS API with JAX-RS and Jersey, but with the possibility of having Jersey in a Spring Boot application Spring HATEOAS may be a nice supplement, especially that it was designed with JAX-RS in mind.

Note: This article is just a research I conducted regarding the topic described. I did not use the approach in any project yet.

## Resources

- Project source code: <https://github.com/kolorobot/spring-boot-jersey-demo>
- Spring HATEOAS project page: <https://github.com/spring-projects/spring-hateoas> and sample: <https://github.com/olivergierke/spring-hateoas-sample>
