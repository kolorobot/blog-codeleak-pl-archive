---
title: "Testing exceptions with JUnit 5"
date: 2017-06-06T23:23:00.001+02:00
updated: 2019-09-23T19:49:32.583+02:00
author: "Rafał Borowiec"
tags: ["junit 5"]
original_url: https://blog.codeleak.pl/2017/06/testing-exceptions-with-junit-5.html
---

# Testing exceptions with JUnit 5

JUnit 5 brought pretty awesome improvements and it differs a lot from its predecessor. JUnit 5 requires Java 8 at runtime hence Lambda expressions can be used in tests, especially in assertions. One of those assertions is perfectly suited for testing exceptions.

*Change Log*

**14/09/2018** - source code updated

## Setup the project

To demonstrate JUnit 5 usage I used my long-lived unit-testing-demo Github project as it already contains many unit testing samples: <https://github.com/kolorobot/unit-testing-demo>. Adding JUnit 5 support to an existing project was straightforward: apart from all standard JUnit 5 dependencies a junit-vintage-engine must exist in test runtime path:

```
    // JUnit 5 Jupiter API and TestEngine implementation
    testCompile("org.junit.jupiter:junit-jupiter-api:5.3.1")
    testRuntime("org.junit.jupiter:junit-jupiter-engine:5.3.1")

    // Support JUnit 4 tests
    testCompile("junit:junit:4.12")
    testRuntime("org.junit.vintage:junit-vintage-engine:5.3.1")
```

## JUnit 5 assertThrows

JUnit 5 built-in `org.junit.jupiter.api.Assertions#assertThrows` gets expected exception class as first parameter and the executable (functional interface) potentially throwing an exception as the second. The method will fail if no exception or exception of different type is thrown. The method returns the exception itself that can be used for further assertions:

```
import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.*;

class Junit5ExceptionTestingTest { // non public, new to JUnit5

    @Test
    @DisplayName("Junit5 built-in Assertions.assertThrows and Assertions.assertAll")
    @Tag("exception-testing")
    void verifiesTypeAndMessage() {
        Throwable throwable = assertThrows(MyRuntimeException.class, new Thrower()::throwsRuntime);

        assertAll(
            () -> assertEquals("My custom runtime exception", throwable.getMessage()),
            () -> assertNull(throwable.getCause())
        );
    }
}
```

## Summary

In JUnit 4 there are many ways of testing exceptions in test code, including try-catch idiom, JUnit @Rule or AssertJ (3+). As of JUnit 5 a built-in assertion can be used.

## References

- [Testing exceptions - JUnit 4 and AssertJ](../../../2015/04/junit-testing-exceptions-with-java-8/index.md)
- [Testing exceptions - JUnit 4, Java 8 and Lambda expressions](../../../2014/07/junit-testing-exception-with-java-8-and-lambda-expressions/index.md)
- [Different ways of testing exceptions in JUnit](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)
