---
title: "Yet another way to handle exceptions in JUnit: catch-exception"
date: 2014-04-09T00:00:00.003+02:00
updated: 2014-06-06T21:35:12.445+02:00
author: "Rafał Borowiec"
tags: ["java", "unit testing"]
original_url: https://blog.codeleak.pl/2014/04/yet-another-way-to-handle-exceptions-in.html
---

# Yet another way to handle exceptions in JUnit: catch-exception

There are many ways of handling exceptions in JUnit ([3 ways of handling exceptions in JUnit. Which one to choose?](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md), [JUnit ExpectedException rule: beyond basics](../../../2014/03/junit-expectedexception-rule-beyond/index.md)). In this post I will introduce *[catch-exception](https://code.google.com/p/catch-exception/)* library that I was recommended to give a try. In short, *[catch-exceptions](https://code.google.com/p/catch-exception/)* is a library that catches exceptions in a single line of code and makes them available for further analysis.

## Install via Maven

In order to get started quickly, I used my [Unit Testing Demo](https://github.com/kolorobot/unit-testing-demo) project with a set of test dependencies ([JUnit, Mocito, Hamcrest, AssertJ](../../../2014/03/how-to-test-dependencies-in-maven/index.md)) and added *catch-exceptions*:

```xml
<dependency>
    <groupId>com.googlecode.catch-exception</groupId>
    <artifactId>catch-exception</artifactId>
    <version>1.2.0</version>
    <scope>test</scope>
</dependency>
```

So the dependency tree looks as follows:

```
[INFO] --- maven-dependency-plugin:2.1:tree @ unit-testing-demo ---
[INFO] com.github.kolorobot:unit-testing-demo:jar:1.0.0-SNAPSHOT
[INFO] +- org.slf4j:slf4j-api:jar:1.5.10:compile
[INFO] +- org.slf4j:jcl-over-slf4j:jar:1.5.10:runtime
[INFO] +- org.slf4j:slf4j-log4j12:jar:1.5.10:runtime
[INFO] +- log4j:log4j:jar:1.2.15:runtime
[INFO] +- junit:junit:jar:4.11:test
[INFO] +- org.mockito:mockito-core:jar:1.9.5:test
[INFO] +- org.assertj:assertj-core:jar:1.5.0:test
[INFO] +- org.hamcrest:hamcrest-core:jar:1.3:test
[INFO] +- org.hamcrest:hamcrest-library:jar:1.3:test
[INFO] +- org.objenesis:objenesis:jar:1.3:test
[INFO] \- com.googlecode.catch-exception:catch-exception:jar:1.2.0:test
```

## Getting started

System under test (SUT):

```java
class ExceptionThrower {

    void someMethod() {
        throw new RuntimeException("Runtime exception occurred");
    }

    void someOtherMethod() {
        throw new RuntimeException("Runtime exception occurred",
                new IllegalStateException("Illegal state"));
    }

    void yetAnotherMethod(int code) {
        throw new CustomException(code);
    }
}
```

The basic *catch-exception* BDD-style approach example with *AssertJ* assertions:

```java
import org.junit.Test;

import static com.googlecode.catchexception.CatchException.*;
import static com.googlecode.catchexception.apis.CatchExceptionAssertJ.*;

public class CatchExceptionsTest {

    @Test
    public void verifiesTypeAndMessage() {
        when(new SomeClass()).someMethod();

        then(caughtException())
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Runtime exception occurred")
                .hasMessageStartingWith("Runtime")
                .hasMessageEndingWith("occured")
                .hasMessageContaining("exception")
                .hasNoCause();                
    }
}
```

Looks good. Concise, readable. No JUnit runners. Please note, that I specified which method of `SomeClass` I expect to throw an exception. As you can imagine, I can check multiple exceptions in one test. Although I would not recommend this approach as it may feel like violating a single responsibility of a test.

By the way, if you are working with Eclipse this may be handy for you: [Improve content assist for types with static members while creating JUnit tests in Eclipse](../../../2012/05/how-to-improve-content-assist-for-types/index.md)

## Verify the cause

I think there is no comment needed for the below code:

```java
import org.junit.Test;

import static com.googlecode.catchexception.CatchException.*;
import static com.googlecode.catchexception.apis.CatchExceptionAssertJ.*;

public class CatchExceptionsTest {

    @Test
    public void verifiesCauseType() {
        when(new ExceptionThrower()).someOtherMethod();
        then(caughtException())
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Runtime exception occurred")
                .hasCauseExactlyInstanceOf(IllegalStateException.class)
                .hasRootCauseExactlyInstanceOf(IllegalStateException.class);
    }
}
```

## Verify custom exception with Hamcrest

To verify a custom exception I used the Hamcrest matcher code from my previous [post](../../../2014/03/junit-expectedexception-rule-beyond/index.md):

```java
class CustomException extends RuntimeException {
    private final int code;

    public CustomException(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}

class ExceptionCodeMatches extends TypeSafeMatcher<CustomException> {

    private int expectedCode;

    public ExceptionCodeMatches(int expectedCode) {
        this.expectedCode = expectedCode;
    }

    @Override
    protected boolean matchesSafely(CustomException item) {
        return item.getCode() == expectedCode;
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("expects code ")
                .appendValue(expectedCode);
    }

    @Override
    protected void describeMismatchSafely(CustomException item, Description mismatchDescription) {
        mismatchDescription.appendText("was ")
                .appendValue(item.getCode());
    }
}
```

And the test:

```java
import org.junit.Test;

import static com.googlecode.catchexception.CatchException.*;
import static org.junit.Assert.*;

public class CatchExceptionsTest {

    @Test
    public void verifiesCustomException() {
        catchException(new ExceptionThrower(), CustomException.class).yetAnotherMethod(500);
        assertThat((CustomException) caughtException(), new ExceptionCodeMatcher(500));
    }
}
```

## Summary

*catch-exception* looks really good. It is easy to get started quickly. I see some advantages over method rule in JUnit. If I have a chance, I will investigate the library more thoroughly, hopefully in a real-world project.

The source code of this article can be found here: [Unit Testing Demo](https://github.com/kolorobot/unit-testing-demo)

In case you are interested, please have a look at my other posts:

- [3 ways of handling exceptions in JUnit. Which one to choose?](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)
- [JUnit ExpectedException rule: beyond basics](../../../2014/03/junit-expectedexception-rule-beyond/index.md)
- [HOW-TO: Test dependencies in a Maven project (JUnit, Mocito, Hamcrest, AssertJ)](../../../2014/03/how-to-test-dependencies-in-maven/index.md)
- [Improve content assist for types with static members while creating JUnit tests in Eclipse](../../../2012/05/how-to-improve-content-assist-for-types/index.md)
