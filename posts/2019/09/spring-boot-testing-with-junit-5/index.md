---
title: "Spring Boot testing with JUnit 5"
date: 2019-09-24T23:55:00.000+02:00
updated: 2019-10-21T22:56:23.959+02:00
author: "Rafał Borowiec"
tags: ["junit 5", "spring boot", "testing"]
original_url: https://blog.codeleak.pl/2019/09/spring-boot-testing-with-junit-5.html
---

# Spring Boot testing with JUnit 5

`JUnit 5` (JUnit Jupiter) is around for quite some time already and it is equipped with tons of features and as of Spring Boot 2.2 `JUnit 5` it the default test library dependency. In this blog post you will find some basic test examples in Spring Boot and `JUnit 5` against basic web application.

## Table of contents

- [Table of contents](#table-of-contents)
- [Source code](#source-code)
- [Setup the project](#setup-the-project)
- [Run the test](#run-the-test)
- [Sample application with a single REST controller](#sample-application-with-a-single-rest-controller)
- [Creating Spring Boot tests](#creating-spring-boot-tests)
  - [Spring Boot test with web server running on random port](#spring-boot-test-with-web-server-running-on-random-port)
  - [Spring Boot test with web server running on random port with mocked dependency](#spring-boot-test-with-web-server-running-on-random-port-with-mocked-dependency)
  - [Spring Boot test with mocked MVC layer](#spring-boot-test-with-mocked-mvc-layer)
  - [Spring Boot test with mocked MVC layer and mocked dependency](#spring-boot-test-with-mocked-mvc-layer-and-mocked-dependency)
  - [Spring Boot test with mocked web layer](#spring-boot-test-with-mocked-web-layer)
  - [Spring Boot test with mocked web layer and mocked dependency](#spring-boot-test-with-mocked-web-layer-and-mocked-dependency)
  - [Run all tests](#run-all-tests)
- [References](#references)
- [See also](#see-also)
- [Source code](#source-code-1)

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/spring-boot-junit5>.

## Setup the project

Spring Boot 2.2 added default support for JUnit Jupiter. Every project generated with `Initializr` (<https://start.spring.io>) has all required dependencies and the generated test class uses `@SpringBootTest` annotation that configures the test with JUnit 5:

```java
package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {

 @Test
 void contextLoads() {
 }

}
```

> Tip: If you are new to JUnit 5 see my other posts about JUnit 5: [https://blog.codeleak.pl/search/label/junit 5](https://blog.codeleak.pl/search/label/junit%205)

## Run the test

We can run the test either with `Maven Wrapper`: `./mvnw clean test` or with `Gradle Wrapper`: `./gradlew clean test`.

## Sample application with a single REST controller

The sample application is containing a single REST controller with three endpoints:

- `/tasks/{id}`
- `/tasks`
- `/tasks?title={title}`

Each of the controller’s method is calling internally [JSONPlaceholder](https://jsonplaceholder.typicode.com) - fake online REST API for testing and prototyping.

The structure of the project files is as follows:

```text
$ tree src/main/java
src/main/java
└── pl
    └── codeleak
        └── samples
            └── springbootjunit5
                ├── SpringBootJunit5Application.java
                ├── config
                │   ├── JsonPlaceholderApiConfig.java
                │   └── JsonPlaceholderApiConfigProperties.java
                └── todo
                    ├── JsonPlaceholderTaskRepository.java
                    ├── Task.java
                    ├── TaskController.java
                    └── TaskRepository.java
```

It also have the following static resources:

```text
$ tree src/main/resources/
src/main/resources/
├── application.properties
├── static
│   ├── error
│   │   └── 404.html
│   └── index.html
└── templates
```

The `TaskController` is delegating its work to the `TaskRepository`:

```java
@RestController
class TaskController {

    private final TaskRepository taskRepository;

    TaskController(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    @GetMapping("/tasks/{id}")
    Task findOne(@PathVariable Integer id) {
        return taskRepository.findOne(id);
    }

    @GetMapping("/tasks")
    List<Task> findAll() {
        return taskRepository.findAll();
    }

    @GetMapping(value = "/tasks", params = "title")
    List<Task> findByTitle(String title) {
        return taskRepository.findByTitle(title);
    }
}
```

The `TaskRepository` is implemented by `JsonPlaceholderTaskRepository` that is using internally `RestTemplate` for calling JSONPlaceholder (<https://jsonplaceholder.typicode.com>) endpoint:

```java
public class JsonPlaceholderTaskRepository implements TaskRepository {

    private final RestTemplate restTemplate;
    private final JsonPlaceholderApiConfigProperties properties;

    public JsonPlaceholderTaskRepository(RestTemplate restTemplate, JsonPlaceholderApiConfigProperties properties) {
        this.restTemplate = restTemplate;
        this.properties = properties;
    }

    @Override
    public Task findOne(Integer id) {
        return restTemplate
                .getForObject("/todos/{id}", Task.class, id);
    }

    // other methods skipped for readability

}
```

The application is configured via `JsonPlaceholderApiConfig` that is using `JsonPlaceholderApiConfigProperties` to bind some sensible properties from `application.properties`:

```java
@Configuration
public class JsonPlaceholderApiConfig {

    private final JsonPlaceholderApiConfigProperties properties;

    public JsonPlaceholderApiConfig(JsonPlaceholderApiConfigProperties properties) {
        this.properties = properties;
    }

    @Bean
    RestTemplate restTemplate() {
        return new RestTemplateBuilder()
                .rootUri(properties.getRootUri())
                .build();
    }

    @Bean
    TaskRepository taskRepository(RestTemplate restTemplate, JsonPlaceholderApiConfigProperties properties) {
        return new JsonPlaceholderTaskRepository(restTemplate, properties);
    }
}
```

> Note: As of Spring Boot 2.2 you don’t need to enable the configuration properties with `@EnableConfigurationProperties`

The `application.properties` contain several properties related to the JSONPlaceholder endpoint configuration:

```text
json-placeholder.root-uri=https://jsonplaceholder.typicode.com
json-placeholder.todo-find-all.sort=id
json-placeholder.todo-find-all.order=desc
json-placeholder.todo-find-all.limit=20
```

> Read more about `@ConfigurationProperties` in this blog post: [https://blog.codeleak.pl/2014/09/using-configurationproperties-in-spring.html](../../../2014/09/using-configurationproperties-in-spring/index.md)

## Creating Spring Boot tests

Spring Boot provides a number of utilities and annotations that support testing applications.

Different approaches can be used while creating the tests. Below you will find the most common cases for creating Spring Boot tests.

### Spring Boot test with web server running on random port

In the below test the web environment will be created using a random port. This port is then injected into field annotated with `@LocalServerPort`. In this mode, the application is executed using an embedded server.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class TaskControllerIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void findsTaskById() {
        // act
        var task = restTemplate.getForObject("http://localhost:" + port + "/tasks/1", Task.class);

        // assert
        assertThat(task)
                .extracting(Task::getId, Task::getTitle, Task::isCompleted, Task::getUserId)
                .containsExactly(1, "delectus aut autem", false, 1);
    }
}
```

### Spring Boot test with web server running on random port with mocked dependency

If you need to mock any of the beans you can use `@MockBean` annotation to mark any dependency as a *mock*. Spring Boot creates the mock object using Mockito. In the below example the application will be started using an embedded server running on a default port.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class TaskControllerIntegrationTestWithMockBeanTest {

    @LocalServerPort
    private int port;

    @MockBean
    private TaskRepository taskRepository;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void findsTaskById() {

        // arrange
        var taskToReturn = new Task();
        taskToReturn.setId(1);
        taskToReturn.setTitle("delectus aut autem");
        taskToReturn.setCompleted(true);
        taskToReturn.setUserId(1);

        when(taskRepository.findOne(1)).thenReturn(taskToReturn);

        // act
        var task = restTemplate.getForObject("http://localhost:" + port + "/tasks/1", Task.class);

        // assert
        assertThat(task)
                .extracting(Task::getId, Task::getTitle, Task::isCompleted, Task::getUserId)
                .containsExactly(1, "delectus aut autem", true, 1);
    }
}
```

### Spring Boot test with mocked MVC layer

Starting the Spring Boot application using a fully configured embedded server may be time consuming and it is not always the best option for the integration tests. If you don’t need the full server capabilities in your tests you can utilize mocked MVC layer (`MockMvc`). This can be done by adding `@AutoConfigureMockMvc` to `@SpringBootTest`.

```java
@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerMockMvcTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void findsTaskById() throws Exception {
        mockMvc.perform(get("/tasks/1"))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json("{\"id\":1,\"title\":\"delectus aut autem\",\"userId\":1,\"completed\":false}"));
    }
}
```

### Spring Boot test with mocked MVC layer and mocked dependency

`@MockedBean` can be used alongside auto configured `MockMvc`.

```java
@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerMockMvcWithMockBeanTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TaskRepository taskRepository;

    @Test
    void findsTaskById() throws Exception {
        // arrange
        var taskToReturn = new Task();
        taskToReturn.setId(1);
        taskToReturn.setTitle("delectus aut autem");
        taskToReturn.setCompleted(true);
        taskToReturn.setUserId(1);

        when(taskRepository.findOne(1)).thenReturn(taskToReturn);

        // act and assert
        mockMvc.perform(get("/tasks/1"))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json("{\"id\":1,\"title\":\"delectus aut autem\",\"userId\":1,\"completed\":true}"));
    }
}
```

### Spring Boot test with mocked web layer

In case only web layer is needed (not the context configuration), you can use `@WebMvcTest`:

```java
@WebMvcTest
@Import(JsonPlaceholderApiConfig.class)
class TaskControllerWebMvcTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void findsTaskById() throws Exception {
        mockMvc.perform(get("/tasks/1"))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json("{\"id\":1,\"title\":\"delectus aut autem\",\"userId\":1,\"completed\":false}"));
    }
}
```

### Spring Boot test with mocked web layer and mocked dependency

`@MockedBean` can be used alongside `@WebMvcTest`.

```java
@WebMvcTest
class TaskControllerWebMvcWithMockBeanTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TaskRepository taskRepository;

    @Test
    void findsTaskById() throws Exception {
        // arrange
        var taskToReturn = new Task();
        taskToReturn.setId(1);
        taskToReturn.setTitle("delectus aut autem");
        taskToReturn.setCompleted(true);
        taskToReturn.setUserId(1);

        when(taskRepository.findOne(1)).thenReturn(taskToReturn);

        // act and assert
        mockMvc.perform(get("/tasks/1"))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(content().json("{\"id\":1,\"title\":\"delectus aut autem\",\"userId\":1,\"completed\":true}"));
    }
}
```

### Run all tests

We can run all tests either with `Maven Wrapper`: `./mvnw clean test` or with `Gradle Wrapper`: `./gradlew clean test`.

The results of running the tests with `Gradle`:

```text
$ ./gradlew clean test

> Task :test

pl.codeleak.samples.springbootjunit5.SpringBootJunit5ApplicationTests > contextLoads() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerWebMvcTest > findsTaskById() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerIntegrationTestWithMockBeanTest > findsTaskById() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerWebMvcWithMockBeanTest > findsTaskById() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerIntegrationTest > findsTaskById() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerMockMvcTest > findsTaskById() PASSED

pl.codeleak.samples.springbootjunit5.todo.TaskControllerMockMvcWithMockBeanTest > findsTaskById() PASSED

BUILD SUCCESSFUL in 7s
5 actionable tasks: 5 executed
```

## References

- <https://docs.spring.io/spring-boot/docs/2.1.8.RELEASE/reference/html/boot-features-testing.html>
- <https://spring.io/guides/gs/testing-web/>
- <https://github.com/spring-projects/spring-boot/issues/14736>

## See also

- [https://blog.codeleak.pl/search/label/junit 5](https://blog.codeleak.pl/search/label/junit%205)
- [https://blog.codeleak.pl/2014/09/using-configurationproperties-in-spring.html](../../../2014/09/using-configurationproperties-in-spring/index.md)
- [https://blog.codeleak.pl/2015/03/spring-boot-integration-testing-with.html](../../../2015/03/spring-boot-integration-testing-with/index.md)
- [https://blog.codeleak.pl/2014/09/testing-mail-code-in-spring-boot.html](../../../2014/09/testing-mail-code-in-spring-boot/index.md)

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/spring-boot-junit5>.
