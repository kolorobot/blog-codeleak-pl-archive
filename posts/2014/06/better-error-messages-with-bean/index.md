---
title: "Better error messages with Bean Validation 1.1 in Spring MVC application"
date: 2014-06-19T20:16:00.000+02:00
updated: 2016-03-30T21:21:22.073+02:00
author: "Rafał Borowiec"
tags: ["spring boot", "spring mvc"]
original_url: https://blog.codeleak.pl/2014/06/better-error-messages-with-bean.html
---

# Better error messages with Bean Validation 1.1 in Spring MVC application

![](logo-spring-io.png)

[Bean Validation 1.1](http://beanvalidation.org/1.1/), among many new features, introduced error message interpolation using Unified Expression Language (EL) expressions. *This allows to define error messages based on conditional logic and also enables advanced formatting options*. Added to a Spring MVC application let you display more friendly error messages quite simply.

In the first part of this article I will shortly describe message interpolation with EL expressions, in the second part we will build a simple web application with Spring Boot and Thymeleaf that runs on Tomcat 8.

> 30/03/2016 - The project referenced in this article got a solid upgrade, as well as the related blog post: [Different ways of validating @RequestBody in Spring MVC with @Valid annotation](../../../2013/09/request-body-validation-in-spring-mvc-3.2/index.md).

## EL expressions in messages - examples

To visualize some possibilities of a better message interpolation with EL expressions I will use the following class:

```java
public class Bid {
    private String bidder;
    private Date expiresAt;
    private BigDecimal price;
}
```

### Example 1: The currently validated value

The validation engine makes currently validated value available in the EL context as `validatedValue`:

```java
@Size(min = 5, message = "\"${validatedValue}\" is too short.")
private String bidder;
```

The error message when for a bidder equal to “John” will be:

> “John” is too short.

### Example 2: Conditional logic

Conditional logic with EL expression is possible in error messages. In the below example, if the length of a validated bidder is shorter than 2, we display a different message:

```java
@Size(min = 5, message = "\"${validatedValue}\" is ${validatedValue.length() < 2 ? 'way' : ''} too short.")
private String bidder;
```

When a bidder is equal to “J” the message will be:

> “J” is way too short.

When a bidder is equal to “John” the message will be:

> “John” is too short.

### Example 3: Formatter

The validation engine makes `formatter` object available in the EL context. `formatter` behaves `java.util.Formatter.format(String format, Object... args)`. In the below example the date is formatted to ISO Date:

```java
@Future(message = "The value \"${formatter.format('%1$tY-%1$tm-%1$td', validatedValue)}\" is not in future!")
private Date expiresAt;
```

When expiration date is equal to 2001-01-01 the message will be:

> The value “2001-01-01” is not in future!

Please note that the `java.util.Date` is used in this example. Hibernate Validator 5.1.1 does not support validation of new Date-Time types yet. It will be introduced in Hibernate Validator 5.2. See [Hibernate Validator Roadmap](http://hibernate.org/validator/roadmap/).

## Creating Spring MVC application

To visualize how Bean Validation 1.1 can be utilized with Spring MVC, we will build a simple web application using Spring Boot.

Firstly, we need to create a Spring Boot project. We can start with [Spring Initializr](http://start.spring.io) and generate a project with the following characteristics:

- **Group**: pl.codeleak.beanvalidation11-demo
- **Artifact**: beanvalidation11-demo
- **Name**: Bean Validation 1.1 Demo
- **Package** Name: pl.codeleak.demo
- **Styles**: Web, Thymeleaf
- **Type**: Maven Project
- **Packaging**: War
- **Java Version**: 1.8
- **Language**: Java

After clicking generate, the file will downloaded. The structure of the generated project is as follows:

```
src
├───main
│   ├───java
│   │   └───pl
│   │       └───codeleak
│   │           └───demo
│   └───resources
│       ├───static
│       └───templates
└───test
    └───java
        └───pl
            └───codeleak
                └───demo
```

As of June 2014, the generated POM looked like below:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>pl.codeleak.beanvalidation11-demo</groupId>
    <artifactId>beanvalidation11-demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>war</packaging>

    <name>Bean Validation 1.1 Demo</name>
    <description></description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>1.1.1.RELEASE</version>
        <relativePath/>
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <start-class>pl.codeleak.demo.Application</start-class>
        <java.version>1.8</java.version>
    </properties>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

That was fast! Spring Initializr is really handy! While having the project generated, you can import it to to your favorite IDE.

### Modifying project properties

Bean Validation 1.1 is implemented by [Hibernate Validator 5.x](http://hibernate.org/validator/). We will use Hibernate Validator 5.1.1, so we will need to add it to our project and as Spring Boot 1.1.1.RELEASE uses Hibernate Validator 5.0.3 we will need to modify one of the POM properties:

```xml
<properties>
    <hibernate-validator.version>5.1.1.Final</hibernate-validator.version>
</properties>
```

In the project we will use Tomcat 8. But why we can’t work with Tomcat 7? Hibernate Validator 5.x requires Expression EL API 2.2.4 and its implementation. And the implementation is provided in Tomcat 8. To run Spring Boot application on Tomcat 8 we will need to add another property:

```xml
<properties>
    <tomcat.version>8.0.8</tomcat.version>
</properties>
```

### Creating a Bid: Controller

In order to create a bid we will need a controller. The controller has two methods: to display the form and to create a bid:

```java
@Controller
public class BidController {

    @RequestMapping(value = "/")
    public String index(Model model) {
        model.addAttribute("bid", new Bid("John", new Date(), BigDecimal.valueOf(5.00)));
        return "index";
    }

    @RequestMapping(value = "/", method = RequestMethod.POST)
    public String create(@ModelAttribute @Valid Bid bid, Errors errors) {
        if (errors.hasErrors()) {
            return "index";
        }

        // create a bid here

        return "redirect:/";
    }
}
```

The final `Bid` class code is below. Please note that messages are not directly specified in the `Bid` class. I moved them to `ValidationMessages` bundle file (`ValidationMessages.properties` in `src/main/resources`).

```java
public class Bid {

    @Size.List({
        @Size(min = 5, message = "{bid.bidder.min.message}"),
        @Size(max = 10, message = "{bid.bidder.max.message}")
    })
    private String bidder;

    @NotNull
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    @Future(message = "{bid.expiresAt.message}")
    private Date expiresAt;

    @NotNull
    @DecimalMin(value = "10.00", message = "{bid.price.message}")
    @NumberFormat(style = NumberFormat.Style.CURRENCY)
    private BigDecimal price;

    protected Bid() {}

    public Bid(String bidder, Date expiresAt, BigDecimal price) {
        this.bidder = bidder;
        this.expiresAt = expiresAt;
        this.price = price;
    }

    public String getBidder() {
        return bidder;
    }
    public Date getExpiresAt() {
        return expiresAt;
    }
    public BigDecimal getPrice() {
        return price;
    }

    public void setBidder(String bidder) {
        this.bidder = bidder;
    }
    public void setExpiresAt(Date expiresAt) {
        this.expiresAt = expiresAt;
    }
    public void setPrice(BigDecimal price) {
        this.price = price;
    }
}
```

### Creating a Bid: View

We will now create a simple page in Thymeleaf that contains our bid form. The page will be `index.html` and it will go to `src/main/resources/templates`.

```html
<form 
    class="form-narrow form-horizontal" method="post" 
    th:action="@{/}" th:object="${bid}">

[...]

</form>
```

In case of a validation error, we will display a general message:

```html
<th:block th:if="${#fields.hasErrors('${bid.*}')}">
    <div class="alert alert-dismissable" th:classappend="'alert-danger'">
        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
        <span th:text="Form contains errors. Please try again.">Test</span>
    </div>
</th:block>
```

Each form field will be marked as red and the appropriate message will be displayed:

```html
<div class="form-group" 
    th:classappend="${#fields.hasErrors('bidder')}? 'has-error'">
    <label for="bidder" class="col-lg-4 control-label">Bidder</label>
    <div class="col-lg-8">
        <input type="text" class="form-control" id="bidder" th:field="*{bidder}" />
        <span class="help-block" 
            th:if="${#fields.hasErrors('bidder')}" 
            th:errors="*{bidder}">
            Incorrect
        </span>
    </div>
</div>
```

### Creating some tests

At this stage we could run the application, but instead we will create some tests to check if the validation works as expected. In order to do so, we will create `BidControllerTest`:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class BidControllerTest {

    @Autowired
    private WebApplicationContext wac;
    private MockMvc mockMvc;

    @Before
    public void setup() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(this.wac).build();
    }
}
```

The test stub is ready. It is time for some tests. Let’s firstly check if the form is “shown” correctly by verifying the model contains a bid object and the view name is equal to `index`:

```java
@Test
public void displaysABidForm() throws Exception {
    this.mockMvc.perform(get("/"))
            .andExpect(status().isOk())
            .andExpect(model().attribute("bid", any(Bid.class)))
            .andExpect(view().name("index"));
}
```

In the next test we will verify that, if correct data is entered, the form **does not** contain an error message (happy flow scenario). Please note that with Thymeleaf as a view engine we can simply verify the generated view.

```java
@Test
public void postsAValidBid() throws Exception {
    this.mockMvc.perform(post("/")
            .param("bidder", "John Smith")
            .param("expiresAt", "2020-01-01")
            .param("price", "11.88"))
            .andExpect(content().string(
                not(
                        containsString("Form contains errors. Please try again.")
                    )
                )
            );
}
```

In the next few tests we will be checking validation of certain objects. The names of the tests should be descriptive enough, so no further explanation is needed. Look at the code:

```java
@Test
public void postsABidWithBidderTooShort() throws Exception {
    this.mockMvc.perform(post("/").param("bidder", "John")) // too short
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("&quot;John&quot; is too short. Should not be shorter than 5")
                    )
                )
            );
}

@Test
public void postsABidWithBidderWayTooShort() throws Exception {
    this.mockMvc.perform(post("/").param("bidder", "J")) // way too short
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("&quot;J&quot; is way too short. Should not be shorter than 5")
                    )
                )
            );
}

@Test
public void postsABidWithBidderTooLong() throws Exception {
    this.mockMvc.perform(post("/").param("bidder", "John S. Smith")) // too long
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("&quot;John S. Smith&quot; is too long. Should not be longer than 10")
                    )
                )
            );
}

@Test
public void postsABidWithBidderWayTooLong() throws Exception {
    this.mockMvc.perform(post("/").param("bidder", "John The Saint Smith"))
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("&quot;John The Saint Smith&quot; is way too long. Should not be longer than 10")
                    )
                )
            );
}

@Test
public void postsABidWithExpiresAtInPast() throws Exception {
    this.mockMvc.perform(post("/").param("expiresAt", "2010-01-01"))
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("Value &quot;2010-01-01&quot; is not in future!")
                    )
                )
            );
}

@Test
public void postsABidWithPriceLowerThanFive() throws Exception {
    this.mockMvc.perform(post("/").param("price", "4.99"))
            .andExpect(content().string(
                allOf(
                        containsString("Form contains errors. Please try again."),
                        containsString("Value &quot;4.99&quot; is incorrect. Must be greater than or equal to 10.00")
                    )
                )
            );
}
```

Fairly simple.

### Running the application

Since the application has packaging type `war`, you may need to download Tomcat 8.0.8 server, create a package with `mvn clean package` and deploy the application to the server.

To use embedded Tomcat runner you will need to change packaging type to `jar`, and set `spring-boot-starter-tomcat` dependency scope to default (`compile`) in `pom.xml`:

```xml
[...]

<packaging>jar</packaging>

[...]

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-tomcat</artifactId>
</dependency>

[...]
```

Now you can create a package with `mvn clean package` and run the generated jar file with the `java -jar` command. Of course, you can run the project from the IDE as well, by running `pl.codeleak.demo.Application` class.

### Summary

If you are interested in seeing the full source code of the presented example, please check my GitHub repository: [spring-mvc-beanvalidation11-demo](https://github.com/kolorobot/spring-mvc-beanvalidation11-demo).

After reading this article you should know:

- How to use Bean Validation 1.1 in your Spring MVC application with Tomcat 8
- How to improve the error messages using EL expressions
- How to build an application from scratch with Spring Boot
- How to test the validation using Spring Test

You may be interested in my previous post about bootstrapping a Spring MVC application with Thymeleaf and Maven: [HOW-TO: Spring Boot and Thymeleaf with Maven](../../../2014/04/how-to-spring-boot-and-thymeleaf-with-maven/index.md).

You may also want to have a look at some other posts about validation I wrote in the past:

- [Validation Groups in Spring MVC](../../../2011/03/how-to-jsr303-validation-groups-in/index.md)
- [Method Level Validation in Spring](../../../2012/03/how-to-method-level-validation-in/index.md)
- [Request Body Validation in Spring MVC](../../../2013/09/request-body-validation-in-spring-mvc-3.2/index.md)
