---
title: "Spring 4.1 and Java 8: java.util.Optional as a @RequestParam, @RequestHeader and @MatrixVariable in Spring MVC"
date: 2014-07-28T18:26:00.000+02:00
updated: 2014-07-28T18:26:35.266+02:00
author: "Rafał Borowiec"
tags: ["java 8", "spring 4"]
original_url: https://blog.codeleak.pl/2014/07/Spring41-and-Java8-Optional-as-RequestParam-RequestHeader-MatrixVariable.html
---

# Spring 4.1 and Java 8: java.util.Optional as a @RequestParam, @RequestHeader and @MatrixVariable in Spring MVC

![](logo-spring-io.png)

As of Spring 4.1 Java 8’s `java.util.Optional`, a container object which may or may not contain a non-null value, is supported with `@RequestParam`, `@RequestHeader` and `@MatrixVariable`. While using Java 8’s `java.util.Optional` you make sure your parameters are never `null`.

## Request Params

In this example we will bind `java.time.LocalDate` as `java.util.Optional` using `@RequestParam`:

```java
@RestController
@RequestMapping("o")
public class SampleController {

    @RequestMapping(value = "r", produces = "text/plain")
    public String requestParamAsOptional(
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            @RequestParam(value = "ld") Optional<LocalDate> localDate) {

        StringBuilder result = new StringBuilder("ld: ");
        localDate.ifPresent(value -> result.append(value.toString()));
        return result.toString();
    }
}
```

Prior to Spring 4.1, we would get an exception that no matching editors or conversion strategy was found. As of Spring 4.1, this is no more an issue. To verify the binding works properly, we may create a simple integration test:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class SampleSomeControllerTest {

    @Autowired
    private WebApplicationContext wac;
    private MockMvc mockMvc;

    @Before
    public void setUp() throws Exception {
        mockMvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }

    // ...

}
```

In the first test, we will check if the binding works properly and if the proper result is returned:

```java
@Test
public void bindsNonNullLocalDateAsRequestParam() throws Exception {
    mockMvc.perform(get("/o/r").param("ld", "2020-01-01"))
            .andExpect(content().string("ld: 2020-01-01"));
}
```

In the next test, we will not pass `ld` parameter:

```java
@Test
public void bindsNoLocalDateAsRequestParam() throws Exception {
    mockMvc.perform(get("/o/r"))
            .andExpect(content().string("ld: "));
}
```

Both test should be green!

## Request Headers

Similarly, we can bind `@RequestHeader` to `java.util.Optional`:

```java
@RequestMapping(value = "h", produces = "text/plain")
public String requestHeaderAsOptional(
        @RequestHeader(value = "Custom-Header") Optional<String> header) {

    StringBuilder result = new StringBuilder("Custom-Header: ");
    header.ifPresent(value -> result.append(value));

    return result.toString();
}
```

And the tests:

```java
@Test
public void bindsNonNullCustomHeader() throws Exception {
    mockMvc.perform(get("/o/h").header("Custom-Header", "Value"))
            .andExpect(content().string("Custom-Header: Value"));
}

@Test
public void noCustomHeaderGiven() throws Exception {
    mockMvc.perform(get("/o/h").header("Custom-Header", ""))
            .andExpect(content().string("Custom-Header: "));
}
```

## Matrix Variables

Introduced in Spring 3.2 `@MatrixVariable` annotation indicates that a method parameter should be bound to a name-value pair within a path segment:

```java
@RequestMapping(value = "m/{id}", produces = "text/plain")
public String execute(@PathVariable Integer id,
                      @MatrixVariable Optional<Integer> p,
                      @MatrixVariable Optional<Integer> q) {

    StringBuilder result = new StringBuilder();
    result.append("p: ");
    p.ifPresent(value -> result.append(value));
    result.append(", q: ");
    q.ifPresent(value -> result.append(value));

    return result.toString();
}
```

The above method can be called via `/o/m/42;p=4;q=2` url. Let’s create a test for that:

```java
 @Test
public void bindsNonNullMatrixVariables() throws Exception {
    mockMvc.perform(get("/o/m/42;p=4;q=2"))
            .andExpect(content().string("p: 4, q: 2"));
}
```

Unfortunatelly, the test will fail, because support for `@MatrixVariable` annotation is **disabled by default in Spring MVC**. In order to enable it we need to tweak the configuration and set the `removeSemicolonContent` property of `RequestMappingHandlerMapping` to `false`. By default it is set to `true`. I have done with `WebMvcConfigurerAdapter` like below:

```java
@Configuration
public class WebMvcConfig extends WebMvcConfigurerAdapter {
    @Override
    public void configurePathMatch(PathMatchConfigurer configurer) {
        UrlPathHelper urlPathHelper = new UrlPathHelper();
        urlPathHelper.setRemoveSemicolonContent(false);
        configurer.setUrlPathHelper(urlPathHelper);
    }
}
```

And now all tests passes! Please find the source code for this article here: <https://github.com/kolorobot/spring41-samples>
