---
title: "JUnit 5 and Selenium - improving project configuration"
date: 2019-12-03T22:30:00.001+01:00
updated: 2023-02-09T22:47:21.301+01:00
author: "Rafał Borowiec"
tags: ["junit 5", "selenium"]
original_url: https://blog.codeleak.pl/2019/12/junit-5-and-selenium-improving-project.html
---

# JUnit 5 and Selenium - improving project configuration

Selenium is a set of tools and libraries supporting browser automation and it is mainly used for web applications testing. One of the Selenium's components is a Selenium WebDriver that provides client library, the JSON wire protocol (protocol to communicate with the browser drivers) and browser drivers. One of the main advantages of Selenium WebDriver is that it supported by all major programming languages and it can run on all major operating systems.

In this part of the *JUnit 5 with Selenium WebDriver - Tutorial* you will learn about additional capabilities of JUnit 5 that will help you in decreasing the execution time of your tests by running tests in parallel, configuring the order of your tests and creating parameterized tests.

You will also learn how to take advantage of Selenium Jupiter features like tests execution configuration through system properties, single browser session tests to speed up tests execution or screenshots taking in your tests. Finally, you will learn how to add AssertJ library to your project.

## Table of Contents

- [About this Tutorial](#about-this-tutorial)
- [Parallel tests execution with JUnit 5](#parallel-tests-execution-with-junit-5)
- [Tests execution order with JUnit 5](#tests-execution-order-with-junit-5)
- [Single browser session with Selenium Jupiter](#single-browser-session-with-selenium-jupiter)
  - [Parallel execution of single browser session tests](#parallel-execution-of-single-browser-session-tests)
- [Saving screenshots with Selenium Jupiter](#saving-screenshots-with-selenium-jupiter)
- [Parameterized tests with JUnit 5](#parameterized-tests-with-junit-5)
- [Better assertions with AssertJ](#better-assertions-with-assertj)
- [Summary](#summary)

## Changes

- *2023-02* - The project was updated to Gradle 7.2 and Java 17. Dependencies updated to newer versions.

## About this Tutorial

You are reading the third part of the *JUnit 5 with Selenium WebDriver - Tutorial*.

All articles in this tutorial:

- Part 1 - [Setup the project from the ground up - Gradle with JUnit 5 and Jupiter Selenium](../../../2019/09/junit-5-and-selenium-setup-project-with/index.md)
- Part 2 - [Using Selenium built-in `PageFactory` to implement Page Object Pattern](../../../2019/10/junit-5-and-selenium-using-selenium/index.md)
- Part 3 - [Improving the project configuration - executing tests in parallel, tests execution order, parameterized tests, AssertJ and more](../../../2019/12/junit-5-and-selenium-improving-project/index.md)

> The source code for this tutorial can be found on [Github](https://github.com/kolorobot/junit5-selenium-todomvc-demo)

## Parallel tests execution with JUnit 5

JUnit 5 comes with built-in parallel tests execution support.

The below command will run test methods from TodoMvcTests in parallel:

```
./gradlew clean test --tests "*TodoMvcTests" -Djunit.jupiter.execution.parallel.enabled=true -Djunit.jupiter.execution.parallel.mode.default=concurrent
```

The build was successful and during its execution you should notice that two instances of Chrome browser are running. Execution time of all tests decreased to 10 seconds in this run:

```
> Task :test

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodosWithSameName() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesAllTodosCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesTodoCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > clearsCompletedTodos() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > editsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > removesTodo() PASSED

BUILD SUCCESSFUL in 10s
4 actionable tasks: 4 executed
```

> Tip: Consult the documentation for more options: <https://junit.org/junit5/docs/current/user-guide/#writing-tests-parallel-execution>

## Tests execution order with JUnit 5

Automated tests should be able to run independently and with no specific order as well as the result of the test should not depend on the results of previous tests. But there are situations where a specific order of test execution can be justified.

By default, in JUnit 5 the execution of test methods is repeatable between builds hence deterministic but the algorithm is intentionally non-obvious (as authors of the library state). Fortunately, execution order can be adjusted to our needs using either built-in method orderers or by creating custom ones. We will use `@Order` annotation to provide ordering of test methods and we will annotate the class with `@TestMethodOrder` to instruct JUnit 5 that methods are ordered.

```java
@ExtendWith(SeleniumJupiter.class)
@SingleSession
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("Managing Todos")
class TodoMvcTests {

    @Test
    @Order(1)
    @DisplayName("Creates Todo with given name")
    void createsTodo() {

    }

    @Test
    @Order(2)
    @DisplayName("Creates Todos all with the same name")
    void createsTodosWithSameName() {

    }

    // rest of the methods omitted for readability

}
```

> Read more on the test execution order in JUnit 5 in this article: [https://blog.codeleak.pl/2019/03/test-execution-order-in-junit-5.html](../../../2019/03/test-execution-order-in-junit-5/index.md)

## Single browser session with Selenium Jupiter

As you probably notices, for each test in `TodoMvcTests` class a new Chrome browser instance is started and after each test it is shutdown. This behaviour causes that the execution of the whole suite is taking quite significant time (27s in the previous execution). Selenium Jupiter comes with a handy class level annotation that allows changing this behaviour. `@SingleSession` annotation changes the behaviour so that an instance of the browser is initialized once before all tests and shutdown after all tests.

To apply `@SingleSession` we need to slightly modify the test class and inject the driver object into a constructor instead into `@BeforeEach` method. We also need to take care about proper state for each test. This can be done by clearing the local storage where todos are stored in the `@AfterEach` method. I also created a field `driver` that keeps the driver object instance used in all tests.

I tested the `@SingleSession` with driver injected into `@BeforeEach` and `@AfterEach` method, but it seems that this is not working as expected and each time a new test is executed a new instance of the driver is created. I believe this is another design flaw of the library.

```java
private final ChromeDriver driver;

public TodoMvcTests(ChromeDriver driver) {
    this.driver = driver;
    this.todoMvc = PageFactory.initElements(driver, TodoMvcPage.class);
    this.todoMvc.navigateTo();
}

@AfterEach
void storageCleanup() {
    driver.getLocalStorage().clear();
}
```

When we execute the tests we can observe the time for executing all tests decreased significantly:

```
./gradlew clean test

> Task :test

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > editsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesTodoCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > removesTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesAllTodosCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodosWithSameName() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > clearsCompletedTodos() PASSED

pl.codeleak.demos.selenium.todomvc.SeleniumTest > projectIsConfigured(ChromeDriver) PASSED

BUILD SUCCESSFUL in 9s
3 actionable tasks: 3 executed
```

> Tip: If you wish to run tests from selected classes you can use test filtering that comes with Gradle test task. For example this command will run only tests from TodoMvcTests class: `./gradlew clean test --tests *.todomvc.TodoMvcTests`

### Parallel execution of single browser session tests

Please note that if you will now try to execute tests in parallel using JUnit 5 parallelism the tests will fail. In parallel execution each method requires separate driver instance and with `@SingleSession` enabled we have a single instance shared for all tests. To fix this we need to run test configure parallel execution so that top-level classes run in parallel but methods in same thread.

Just duplicate TodoMvcTests class and try the following command:

```
./gradlew clean test --tests "*TodoMvcTests" -Djunit.jupiter.execution.parallel.enabled=true -Djunit.jupiter.execution.parallel.mode.default=same_thread -Djunit.jupiter.execution.parallel.mode.classes.default=concurrent
```

When execution in progress you should see 3 browsers running and output in terminal similar to the following:

```
<===========--> 87% EXECUTING [3s]
> :test > 0 tests completed
> :test > Executing test pl.codeleak.demos.selenium.todomvc.MoreTodoMvcTests
> :test > Executing test pl.codeleak.demos.selenium.todomvc.EvenMoreTodoMvcTests
> :test > Executing test pl.codeleak.demos.selenium.todomvc.TodoMvcTests
```

## Saving screenshots with Selenium Jupiter

Selenium Jupiter allows saving screenshots at the end of tests - always or only on failure. You can also customize the output directory and format. The below command will run tests with screenshots enabled and save them in PNG format in `/tmp` directory:

```
./gradlew clean test --tests "*TodoMvcTests" -Dsel.jup.screenshot=true -Dsel.jup.screenshot.format=png -Dsel.jup.output.folder=/tmp
```

> Tip: Consult the documentation for more options: <https://bonigarcia.github.io/selenium-jupiter/#screenshots>

## Parameterized tests with JUnit 5

The general idea of parameterized unit tests is to run the same test method for different test data. To create a parameterized test in JUnit 5 you annotate a test method with `@ParameterizedTest` and provide the argument source for the test method. There are several argument sources available including:

- `@ValueSource` - provided access to array of literal values i.e. shorts, ints, strings etc.
- `@MethodSource` - provides access to values returned from factory methods
- `@CsvSource` - which reads comma-separated values (CSV) from one or more supplied CSV lines
- `@CsvFileSource` - which is used to load comma-separated value (CSV) files

In the next examples we will use the following CSV that is stored in the `src/test/resources` directory:

```csv
todo;done
Buy the milk;false
Clean up the room;true
Read the book;false
```

In order to use the above CSV file in our test, we need to annotate the test with `@ParameterizedTest` annotation (instead of `@Test`) followed by `@CsvFileSource` annotation pointing to the file:

```java
@ParameterizedTest
@CsvFileSource(resources = "/todos.csv", numLinesToSkip = 1, delimiter = ';')
@DisplayName("Creates Todo with given name")
void createsTodo(String todo) {
    todoMvc.createTodo(todo);
    assertSingleTodoShown(todo);
}
```

Each record in the CSV file has two fields: `name` and `done`. In the above test only the name of the todo is used. But we can of course **complicate** the test a bit and use both properties:

```java
@ParameterizedTest(name = "{index} - {0}, done = {1}" )
@CsvFileSource(resources = "/todos.csv", numLinesToSkip = 1, delimiter = ';')
@DisplayName("Creates and optionally removes Todo with given name")
void createsAndRemovesTodo(String todo, boolean done) {

    todoMvc.createTodo(todo);
    assertSingleTodoShown(todo);

    todoMvc.showActive();
    assertSingleTodoShown(todo);

    if (done) {
        todoMvc.completeTodo(todo);
        assertNoTodoShown(todo);

        todoMvc.showCompleted();
        assertSingleTodoShown(todo);
    }

    todoMvc.removeTodo(todo);
    assertNoTodoShown(todo);
}
```

Please note, that multiple parameterized tests are allowed within the same test class/

Read more about parameterized tests in this article: [https://blog.codeleak.pl/2017/06/cleaner-parameterized-tests-with-junit-5.html](../../../2017/06/cleaner-parameterized-tests-with-junit-5/index.md) but also go through the JUnit 5 documentation: <https://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests>

## Better assertions with AssertJ

JUnit 5 has a lot of built-in assertions but when the real work starts you may need much more than JUnit 5 has to offer. In such cases, I recommend AssertJ library. [AssertJ](https://assertj.github.io/doc/) *AssertJ is a Java library providing a rich set of assertions, truly helpful error messages, improves test code readability and is designed to be super easy to use within your favorite IDE.*

Some of the AssertJ features:

- Fluent assertions on many Java types including Dates, Collections, Files etc.
- SoftAssertions (similar to JUnit 5's assertAll)
- Complex field comparison
- Can be easily extended - custom conditions and custom assertions

To use AssertJ in a project, we need to add a single dependency to `build.gradle`:

```
testCompile('org.assertj:assertj-core:3.21.0')
```

To get started, we need to statically import `org.assertj.core.api.Assertions.*` and use the code completion with `assertThat` method: `assertThat(objectUnderTest).`

For example, you would write `assertThat(todoMvc.getTodosLeft()).isEqualTo(3);` with AssertJ instead of `assertEquals(3, todoMvc.getTodosLeft());` in plain JUnit 5 or `assertThat(todoMvc.todoExists(readTheBook)).isTrue()` instead of `assertTrue(todoMvc.todoExists(readTheBook))`.

Working with complex types is even better:

```java
todoMvc.createTodos(buyTheMilk, cleanupTheRoom, readTheBook);

assertThat(todoMvc.getTodos())
        .hasSize(3)
        .containsSequence(buyTheMilk, cleanupTheRoom, readTheBook);
```

Visit the official documentation to learn more about AssertJ: <https://assertj.github.io/doc/>

> Tip: Read more on integrating AssertJ with JUnit 5: [https://blog.codeleak.pl/2017/11/junit-5-meets-assertj.html](../../../2017/11/junit-5-meets-assertj/index.md)

## Summary

In this article I presented how you can utilize built-in features of JUnit 5 to improve your project configuration in terms of speed execution but not only. You also learned about improving the the project by utilizing certain Selenium Jupiter features.

As it may look like a lot already, both JUnit 5 and Selenium Jupiter has much more to offer. Have a look at both projects docs and find out what else you can find useful for your current or future projects:

- <https://bonigarcia.github.io/selenium-jupiter/>
- <https://junit.org/junit5/>
