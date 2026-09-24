---
title: "JUnit 5 - Quick Tutorial"
date: 2017-10-05T00:56:00.000+02:00
updated: 2019-09-23T19:49:45.213+02:00
author: "Rafał Borowiec"
tags: ["junit 5"]
original_url: https://blog.codeleak.pl/2017/10/junit-5-basics.html
---

# JUnit 5 - Quick Tutorial

JUnit 5 is the next generation unit testing framework for Java equipped with many interesting features including nested tests, parameterized tests, new extension API or Java 8 support to mentioned a few.

This article shows basic concepts of JUnit 5 including test lifecycle, parameter injection and assertions (basic, timeout and exception).

### *Change Log*

- **6/11/2017** - Source code updated. See <https://github.com/kolorobot/junit5-samples>

## Documentation

First of all, JUnit 5 documentation is just great and in my opinion. Not only it contains comprehensive framework documentation, but also many examples including many samples. Don’t miss the documentation when learning JUnit 5: <http://junit.org/junit5/docs/current/user-guide/>

## Dependencies

Firstly, JUnit 5 requires Java 8 to run. Finally. This brings the possibility to use Lambda expressions in tests and make them more consise (Lambda expressions are mainly used in assertions). Secondly, JUnit 5 consists of multiple artifacts grouped by JUnit Platform, JUnit Jupiter, and JUnit Vintage. This can sound scary, but today with tools such as Maven or Gradle this is not a problem at all and to get started you actually need a single dependency. The basic Gradle configuration could look like below:

```
buildscript {
    ext {
        junitPlatformVersion = '1.0.3'
        junitJupiterVersion = '5.0.3'
    }
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath "org.junit.platform:junit-platform-gradle-plugin:${junitPlatformVersion}"
    }
}

apply plugin: 'java'
apply plugin: 'org.junit.platform.gradle.plugin'

sourceCompatibility = 1.8

repositories {
    mavenCentral()
}

dependencies { 
    testCompile("org.junit.jupiter:junit-jupiter-engine:${junitJupiterVersion}")
}

/* Support for ASCII emoji in tests */
compileTestJava {
    options.encoding = "UTF-8"
}

task wrapper(type: Wrapper) {
    gradleVersion = '4.5'
}
```

## JUnit 5 test classes and methods

The common test annotations used within a test class (imported from `org.junit.jupiter.api`) are:

- `@BeforeAll` - executed before **all** methods in test lass
- `@BeforeEach` - execute before **each** test method in test class
- `@Test` - actual test method
- `@AfterEach` - executed after **each** test method in test lass
- `@AfterAll` - executed after **all** methods in test lass

Other basic but useful annotations:

- `@DisplayName` - custom display name for test class or method
- `@Disabled` - disabling test class or method
- `@RepeatedTest` - make a test template out of the test method
- `@Tag` - tag a test class or method for further test selection

A basic example:

```
import org.junit.jupiter.api.*;

@DisplayName("JUnit5 - Test basics")
class JUnit5Basics {

    @BeforeAll
    static void beforeAll() {
        System.out.println("Before all tests (once)");
    }

    @BeforeEach
    void beforeEach() {
        System.out.println("Runs before each test");
    }

    @Test
    void standardTest() {
        System.out.println("Test is running");
    }

    @DisplayName("My #2 JUnit5 test")
    @Test
    void testWithCustomDisplayName() {
        System.out.println("Test is running");
    }

    @DisplayName("Tagged JUnit5 test ")
    @Tag("cool")
    @Test
    void tagged() {
        System.out.println("Test is running");
    }

    @Disabled("Failing due to unknown reason")
    @DisplayName("Disabled test")
    @Test
    void disabledTest() {
        System.out.println("Disabled, will not show up");
    }

    @DisplayName("Repeated test")
    @RepeatedTest(value = 2, name = "#{currentRepetition} of {totalRepetitions}")
    void repeatedTestWithRepetitionInfo() {
        System.out.println("Repeated test");
    }

    @AfterEach
    void afterEach() {
        System.out.println("Runs after each test");
    }
}
```

Note that test classes and methods does not need to be **public** - they can be **package private**.

## Test Execution Lifecycle

In JUnit 5, by default a new test instance is created for each test method in a test class. This behaviour can be adjusted with class level `@TestInstance` annotation:

```
import org.junit.jupiter.api.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@DisplayName("JUnit5 - Test lifecycle adjustments")
class JUnit5PerClassLifecycle {

    private Object first = new Object();
    private Object second;

    @BeforeAll
    void beforeAll() {
        this.second = this.first;
        System.out.println("Non static before all.");
    }

    @BeforeEach
    void beforeEach() {
        Assertions.assertEquals(first, second);
    }

    @Test
    void first() {
        Assertions.assertEquals(first, second);
    }

    @Test
    void second() {
        Assertions.assertEquals(first, second);
    }

    @AfterAll
    void afterAll() {
        System.out.println("Non static after all.");
    }

    @AfterEach
    void afterEach() {
        Assertions.assertEquals(first, second);
    }
}
```

In `PER_CLASS` mode a single test instance is created for all tests and `@BeforeAll` and `@AfterAll` methods does not need to be static anymore.

## Parameter resolution

Test and callback methods can now take arguments like `org.junit.jupiter.api.TestInfo`, `org.junit.jupiter.api.RepetitionInfo` or `org.junit.jupiter.api.TestReporter`.

In addition, thanks to really simple yet powerful JUnit 5 extension API, resolving custom parameters in methods is a matter of providing own implementation of `org.junit.jupiter.api.extension.ParameterResolver`.

```
class JUnit5BuiltInParameterResolution {

    @BeforeAll
    static void beforeAll(TestInfo testInfo) {
        System.out.println("Before all can take parameters. Started: " + testInfo.getDisplayName());
    }

    @BeforeAll
    static void beforeAll(TestReporter testReporter) {
        testReporter.publishEntry("myEntry", "myValue");
    }

    @BeforeAll
    static void beforeAll(TestInfo testInfo, TestReporter testReporter) {
        testReporter.publishEntry("myOtherEntry", testInfo.getDisplayName());
    }

    @BeforeEach
    void beforeEach(TestInfo testInfo) {

    }

    @Test
    void standardTest(TestInfo testInfo) {

    }

    @DisplayName("Repeated test")
    @RepeatedTest(value = 2, name = "#{currentRepetition} of {totalRepetitions}")
    void repeatedTest(RepetitionInfo repetitionInfo) {
        System.out.println("Repeated test - " + repetitionInfo.toString());
    }

    @AfterAll
    static void afterAll() {

    }

    @AfterAll
    static void afterAll(TestInfo testInfo) {

    }

    @AfterEach
    void afterEach() {

    }
}
```

## Assertions

JUnit 5 comes with many standard assertions that can be found in `org.junit.jupiter.api.Assertions` class.

### Basic assertions

Basic assertions are: `assertEquals`, `assertArrayEquals`, `assertSame`, `assertNotSame`, `assertTrue`, `assertFalse`, `assertNull`, `assertNotNull`,`assertLinesMatch`, `assertIterablesMatch`

Example:

```
@Test
void basicAssertions() {
    // arrange
    List<String> owners = Lists.newArrayList("Betty Davis", "Eduardo Rodriquez");

    // assert
    assertNotNull(owners);
    assertSame(owners, owners);
    assertFalse(owners::isEmpty); // Lambda expression
    assertEquals(2, owners.size(), "Found owner names size is incorrect");
    assertLinesMatch(newArrayList("Betty Davis", "Eduardo Rodriquez"), owners);
    assertArrayEquals(
        new String[]{"Betty Davis", "Eduardo Rodriquez"}, 
        owners.toArray(new String[0])
    );
}
```

### Assert all

`Assertions.assertAll` asserts that all supplied executables do not throw exceptions:

```
Assertions.assertAll(
    () -> Assertions.assertNotNull(null, "May not be null"),
    () -> Assertions.assertTrue(false, "Must be true")
);
```

The above will report multiple failures:

```
org.opentest4j.MultipleFailuresError: Multiple Failures (2 failures)
    May not be null ==> expected: not <null>
    Must be true
```

Note: You may want to read about alternative in JUnit 4 and AssertJ - [http://blog.codeleak.pl/2015/09/assertjs-softassertions-do-we-need-them.html](../../../2015/09/assertjs-softassertions-do-we-need-them/index.md)

### Timeout assertions

Timeout assertions are use in order to verify execution time of a task is not exceeded. There are two flavours of timeout assertion: `assertTimeout` and `assertTimeoutPreemptively`. Both are taking two

- Execute the task synchronously, waiting for its completion and then asserts timeouts:

```
@Test
void assertTimeout() {
    // arrange
    Executable task = () -> Thread.sleep(1000);

    // waits for the task to finish before failing the test
    Assertions.assertTimeout(Duration.ofMillis(100), task::execute);
}

@Test
void assertTimeoutWithThrowingSupplier() {
    // arrange
    ThrowingSupplier<String> task = () -> "result";

    // waits for the task to finish before failing the test
    Assertions.assertTimeout(Duration.ofMillis(100), task::get);
}
```

- Execute the task assynchronously (in a new thread), abort the execution when timeout reached:

```
@Test
void assertTimeoutPreemptively() {
    // arrange
    Executable task = () -> Thread.sleep(1000);

    // abort execution when timeout exceeded
    Assertions.assertTimeoutPreemptively(Duration.ofMillis(100), task::execute);
}

@Test
void assertTimeoutPreemptivelyWithThrowingSupplier() {
    // arrange
    ThrowingSupplier<String> task = () -> "result";

    // abort execution when timeout exceeded, return the result
    String result = Assertions.assertTimeoutPreemptively(Duration.ofMillis(100), task::get);

    Assertions.assertEquals("result", result);
}
```

### Exception assertions

JUnit 5 built-in `assertThrows` gets expected exception type as first parameter and the executable (functional interface) potentially throwing an exception as the second. The method will fail if no exception or exception of different type is thrown. The method returns the exception itself that can be used for further assertions:

```
@Test
void assertException() {
    // arrange
    Executable throwingExecutable = () -> {
        throw new RuntimeException("Unexpected error!");
    };

    // act and assert
    RuntimeException thrown = Assertions.assertThrows(
        RuntimeException.class, throwingExecutable::execute, "???"
    );

    Assertions.assertAll(
        () -> Assertions.assertEquals("Unexpected error!", thrown.getMessage()),
        () -> Assertions.assertNotNull(thrown.getCause())
    );
}
```

Note: You may want to read about alternatives in JUnit 4 - [http://blog.codeleak.pl/2013/07/3-ways-of-handling-exceptions-in-junit.html](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)

## Summary

JUnit 5 is packed with plenty features. In this article only basics were demonstrated but this should be enough for you to start writing your first JUnit 5 tests.

## See also

- Cleaner parameterized tests with JUnit 5 - [http://blog.codeleak.pl/2017/06/cleaner-parameterized-tests-with-junit-5.html](../../../2017/06/cleaner-parameterized-tests-with-junit-5/index.md)
