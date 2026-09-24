---
title: "Getting started with Jersey and Spring Boot"
date: 2015-01-05T19:41:00.000+01:00
updated: 2016-09-28T00:22:21.101+02:00
author: "Rafał Borowiec"
tags: ["jersey", "spring boot"]
original_url: https://blog.codeleak.pl/2015/01/getting-started-with-jersey-and-spring.html
---

# Getting started with Jersey and Spring Boot

![](jersey_spring.png)

Along many new features, Spring Boot 1.2 brings Jersey support. This is great step to attract those developers who like the standard approach as they can now build RESTful APIs using JAX-RS specification and easily deploy it to Tomcat or any other Spring’s Boot supported container. Jersey with Spring platform can play an important role in the development of mico services. In this article I will demonstrate how one can quickly build an application using Spring Boot (including: Spring Data, Spring Test, Spring Security) and Jersey.

## Bootstrap a new project

The application is a regular Spring Boot application and it uses Gradle and its latest 2.2 release. Gradle is less verbose than Maven and it is especially great for Spring Boot applications. Gradle can be downloaded from Gradle website: <http://www.gradle.org/downloads>.

The initial dependencies to start the project:

```
dependencies {
    compile("org.springframework.boot:spring-boot-starter-web")
    compile("org.springframework.boot:spring-boot-starter-jersey")
    compile("org.springframework.boot:spring-boot-starter-data-jpa")
    // HSQLDB for embedded database support
    compile("org.hsqldb:hsqldb")
    // Utilities
    compile("com.google.guava:guava:18.0")
    // AssertJ
    testCompile("org.assertj:assertj-core:1.7.0")
    testCompile("org.springframework.boot:spring-boot-starter-test")
}
```

The application entry point is a class containing `main` method and it is annotated with `@SpringBootApplication` annotation:

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

`@SpringBootApplication` annotation is a convenience annotation that is equivalent to declaring `@Configuration`, `@EnableAutoConfiguration` and `@ComponentScan` and it is new to Spring Boot 1.2.

## Jersey Configuration

Getting started can be as easy as creating root resource annotated with `@Path` and Spring’s `@Component`:

```java
@Component
@Path("/health")
public class HealthController {
    @GET
    @Produces("application/json")
    public Health health() {
        return new Health("Jersey: Up and Running!");
    }
}
```

and registering it within a Spring’s `@Configuration` class that extends from Jersey `ResourceConfig`:

```java
@Configuration
public class JerseyConfig extends ResourceConfig {
    public JerseyConfig() {
        register(HealthController.class);
    }
}
```

We could launch the application with `gradlew bootRun` visit: <http://localhost:8080/health> and we should see the following result:

```json
{
    "status": "Jersey: Up and Running!"
}
```

But it is also possible to write a Spring Boot integration test with fully loaded application context:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
@IntegrationTest("server.port=9000")
public class HealthControllerIntegrationTest {

    private RestTemplate restTemplate = new TestRestTemplate();

    @Test
    public void health() {
        ResponseEntity<Health> entity = 
                restTemplate.getForEntity("http://localhost:9000/health", Health.class);

        assertThat(entity.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(entity.getBody().getStatus()).isEqualTo("Jersey: Up and Running!");
    }
}
```

Jersey 2.x has native Spring support (`jersey-spring3`) and Spring Boot provides auto-configuration support for it with `spring-boot-starter-jersey` starter. For more details have a look at`JerseyAutoConfiguration` class.

Depending on the `spring.jersey.type` property value either Jersey Servlet or Filter is registered as a Spring Bean:

```
Mapping servlet: 'jerseyServlet' to [/*]
```

The default mapping path can be changed via `javax.ws.rs.ApplicationPath` annotation added to `ResourceConfig` configuration class:

```java
@Configuration
@ApplicationPath("/jersey")
public class JerseyConfig extends ResourceConfig {}
```

The JSON media type support comes with `jersey-media-json-jackson` dependency that registers Jackson JSON providers to be used by Jersey.

# Spring Data JPA Integration

*Spring Data JPA, part of the larger Spring Data family, makes it easy to easily implement JPA based repositories.* For those who are not familiar with the project please visit: <http://projects.spring.io/spring-data-jpa/>

## Customer and CustomerRepository

Domain model for this sample project is just a `Customer` with some basic fields:

```java
@Entity
public class Customer extends AbstractEntity {

    private String firstname, lastname;

    @Column
    private EmailAddress emailAddress;   
```

The `Customer`needs a `@Repository`, so we I created a basic one using Spring’s Data repository. Spring Data repositories reduce much of the boilerplate code thanks to a simple interface definition:

```java
public interface CustomerRepository extends PagingAndSortingRepository<Customer, Long> {

}
```

With the domain model in place some test data can be handy. The easiest way is to provide a `data.sql` file with the SQL script to be executed on the application start-up. The file is placed in `src/main/resources` and it will be automatically picked up by Spring. The script contains several SQL inserts to fill in the `customer` table. E.g:

```
insert into customer (id, email, firstname, lastname) values (1, 'joe@doe.com', 'Joe', 'Doe');
```

## Customer Controller

Having Spring Data JPA repository in place, I created a controller (in terms of JAX-RS - resource) that allows CRUD operations on `Customer`object.

Note: I stick to Spring MVC naming conventions for HTTP endpoints, but feel free to call them JAX-RS way.

### Get Customers

Let’s start with a method returning all customers:

```java
@Component
@Path("/customer")
@Produces(MediaType.APPLICATION_JSON)
public class CustomerController {

    @Autowired
    private CustomerRepository customerRepository;

    @GET
    public Iterable<Customer> findAll() {
        return customerRepository.findAll();
    }
}
```

Using `@Component` guarantees `CustomerController` is a Spring managed object. `@Autowired` can be easily replaced with standard `javax.inject.@Inject` annotation.

Since we are using Spring Data in the project I could easily utilize pagination offered by `PagingAndSortingRepository.` I modified the resource method to support some of the page request parameters:

```java
@GET
public Page<Customer> findAll(
        @QueryParam("page") @DefaultValue("0") int page,
        @QueryParam("size") @DefaultValue("20") int size,
        @QueryParam("sort") @DefaultValue("lastname") List<String> sort,
        @QueryParam("direction") @DefaultValue("asc") String direction) {

    return customerRepository.findAll(
            new PageRequest(
                    page, 
                    size, 
                    Sort.Direction.fromString(direction), 
                    sort.toArray(new String[0])
            )
    );
}
```

To verify the above code I created Spring integration test. In first test I will call for all the records, and based on test data previously prepared I expect to have total 3 customers in 1 page of size 20:

```java
@Test
public void returnsAllPages() {
    // act
    ResponseEntity<Page<Customer>> responseEntity = getCustomers(
            "http://localhost:9000/customer"
    );
    Page<Customer> customerPage = responseEntity.getBody();
    // assert
    PageAssertion.assertThat(customerPage)
            .hasTotalElements(3)
            .hasTotalPages(1)
            .hasPageSize(20)
            .hasPageNumber(0)
            .hasContentSize(3);
}
```

In the second test I will call for page 0 of size 1 and sorting by `firstname` and sorting direction `descending`. I expect total elements did not change (3), total pages returned are 3 and content size of the page returned is 1:

```java
@Test
public void returnsCustomPage() {

    // act
    ResponseEntity<Page<Customer>> responseEntity = getCustomers(
            "http://localhost:9000/customer?page=0&size=1&sort=firstname&direction=desc"
    );
    // assert
    Page<Customer> customerPage = responseEntity.getBody();

    PageAssertion.assertThat(customerPage)
            .hasTotalElements(3)
            .hasTotalPages(3)
            .hasPageSize(1)
            .hasPageNumber(0)
            .hasContentSize(1);
}
```

The code can be also checked with `curl`:

```
$ curl -i http://localhost:8080/customer

HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Content-Type: application/json;charset=UTF-8
Content-Length: 702
Date: Sat, 03 Jan 2015 14:27:01 GMT

{...}
```

Please note that for ease of testing the pagination with `RestTemplate` I created some helper classes: `Page`, `Sort` and `PageAssertion`. You will find them in the source code of the application in Github.

### Add New Customer

In this short snippet I used some of the Jersey features like injecting a `@Context`. In case of creating new entity, we usually want to return a link to the resource in the header. In the below example, I inject `UriBuilder` into the endpoint class and use it to build a location URI of newly created customer:

```java
@Context
private UriInfo uriInfo;

@POST
public Response save(Customer customer) {

    customer = customerRepository.save(customer);

    URI location = uriInfo.getAbsolutePathBuilder()
            .path("{id}")
            .resolveTemplate("id", customer.getId())
            .build();

    return Response.created(location).build();
}
```

While invoking a `POST` method (with non existent email):

```
$ curl -i -X POST -H 'Content-Type:application/json' -d '{"firstname":"Rafal","lastname":"Borowiec","emailAddress":{"value": "rafal.borowiec@somewhere.com"}}' http://localhost:8080/customer
```

We will get:

```
HTTP/1.1 201 Created
Server: Apache-Coyote/1.1
Location: http://localhost:8080/customer/4
Content-Length: 0
Date: Sun, 21 Dec 2014 22:49:30 GMT
```

Naturally, an integration test can be created too. It uses `RestTemplate` to save the customer with `postForLocation` method and then retrieve it with `getForEntity`:

```java
@Test
public void savesCustomer() {
    // act
    URI uri = restTemplate.postForLocation("http://localhost:9000/customer",
            new Customer("John", "Doe"));
    // assert
    ResponseEntity<Customer> responseEntity =
            restTemplate.getForEntity(uri, Customer.class);

    Customer customer = responseEntity.getBody();

    assertThat(customer.getFirstname())
            .isEqualTo("John");
    assertThat(customer.getLastname())
            .isEqualTo("Doe");
}
```

### Update: Integration Testing with Groovy

Integration testing of the API with Groovy and HTTPBuilder module, utilizing JSONSlurper: [Groovier Spring Boot Integration Testing](../../../2015/05/groovier-spring-boot-integration-testing/index.md)

### Other methods

The remaining methods of the endpoint are really easy to implement:

```java
@GET
@Path("{id}")
public Customer findOne(@PathParam("id") Long id) {
    return customerRepository.findOne(id);
}

@DELETE
@Path("{id}")
public Response delete(@PathParam("id") Long id) {
    customerRepository.delete(id);
    return Response.accepted().build();
}
```

## Security

Adding Spring Security to the application can be done quickly by adding new dependency to the project:

```
compile("org.springframework.boot:spring-boot-starter-security")
```

With Spring Security in classpath application will be secured with basic authentication on all HTTP endpoints. Default username and password can be changed with two following application settings (`src/main/resources/application.properties`):

```
security.user.name=demo
security.user.password=123
```

After running the application with Spring Security application we need to provide a valid authentication parameters to each request. With curl we can use `--user` switch:

```
$ curl -i --user demo:123 -X GET http://localhost:8080/customer/1
```

With the addition of Spring Security our previously created tests will fail, so we need to provide username and password parameters to `RestTemplate`:

```java
private RestTemplate restTemplate = new TestRestTemplate("demo", "123");
```

## Dispatcher Servlet

Spring’s Dispatcher Servlet is registered along with Jersey Servlet and they are both mapped to the *root resource*. I extended`HealthController` and I added Spring MVC request mapping to it:

```java
@Component
@RestController // Spring MVC
@Path("/health")
public class HealthController {

    @GET
    @Produces({"application/json"})
    public Health jersey() {
        return new Health("Jersey: Up and Running!");
    }

    @RequestMapping(value = "/spring-health", produces = "application/json")
    public Health springMvc() {
        return new Health("Spring MVC: Up and Running!");
    }
}
```

With the above code I expected to have both *health* and *spring-health* endpoints available in the root context but apparently it did not work. I tried several configuration options, including setting `spring.jersey.filter.order` but with no success.

The only solution I found was to either change Jersey `@ApplicationPath` or to change Spring MVC `server.servlet-path` property:

```
server.servlet-path=/s
```

In the latter example calling:

```
$ curl -i --user demo:123 -X GET http://localhost:8080/s/spring-health
```

returned expected result:

```json
{
    "status":"Spring MVC: Up and Running!"
}
```

## Use Undertow instead of Tomcat

As of Spring Boot 1.2 Undertow lightweight and performant Servlet 3.1 container is supported. In order to use Undertow instead of Tomcat, Tomcat dependencies must be exchanged with Undertow ones:

```
buildscript {
    configurations {
        compile.exclude module: "spring-boot-starter-tomcat"
    }
}    

dependencies {
    compile("org.springframework.boot:spring-boot-starter-undertow:1.2.0.RELEASE")
}
```

When running the application the log will contain:

```
org.xnio: XNIO version 3.3.0.Final
org.xnio.nio: XNIO NIO Implementation Version 3.3.0.Final
Started Application in 4.857 seconds (JVM running for 5.245)
```

## Summary

In this blog post I demonstrated a simple example how to get started with Spring Boot and Jersey. Thanks to Jersey auto-configuration adding JAX-RS support to Spring application is extremely easy.

In general, Spring Boot 1.2 makes building applications with Java EE easier: JTA transactions using either an Atomikos or Bitronix embedded transaction manager, JNDI Lookups for both DataSource and JMS ConnectionFactory in JEE Application Server and easier JMS configuration.

## Resources

- Project source code: <https://github.com/kolorobot/spring-boot-jersey-demo>
- Follow up: [Building a HATEOAS API with JAX-RS and Spring](../../../2015/01/building-hateoas-api-with-jax-rs-and/index.md)
