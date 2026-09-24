---
title: "JUnit: testing exception with Java 8 and Lambda Expressions"
date: 2014-07-07T23:26:00.000+02:00
updated: 2014-08-06T13:30:14.337+02:00
author: "Rafał Borowiec"
tags: ["java 8", "unit testing"]
original_url: https://blog.codeleak.pl/2014/07/junit-testing-exception-with-java-8-and-lambda-expressions.html
---

# JUnit: testing exception with Java 8 and Lambda Expressions

![](junit.gif)

In JUnit there are many ways of testing exceptions in test code, including [`try-catch idiom`](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md), [`JUnit @Rule`](../../../2014/03/junit-expectedexception-rule-beyond/index.md), with [`catch-exception`](../../../2014/04/yet-another-way-to-handle-exceptions-in/index.md) library. As of Java 8 we have another way of dealing with exceptions: with lambda expressions. In this short blog post I will demonstrate a simple example how one can utilize the power of Java 8 and lambda expressions to test exceptions in JUnit.

Note: The motivation for writing this blog post was the message published on the `catch-exception` project page:

> Java 8’s lambda expressions will make catch-exception redundant. Therefore, this project won’t be maintained any longer

## SUT - System Under Test

We will test exceptions thrown by the below 2 classes.

The first one:

```java
class DummyService {
    public void someMethod() {
        throw new RuntimeException("Runtime exception occurred");
    }

    public void someOtherMethod(boolean b) {
        throw new RuntimeException("Runtime exception occurred",
                new IllegalStateException("Illegal state"));
    }
}
```

And the second:

```java
class DummyService2 {
    public DummyService2() throws Exception {
        throw new Exception("Constructor exception occurred");
    }

    public DummyService2(boolean dummyParam) throws Exception {
        throw new Exception("Constructor exception occurred");
    }
}
```

## Desired Syntax

My goal was to achieve syntax close to the one I had with `catch-exception` library:

```java
package com.github.kolorobot.exceptions.java8;

import org.junit.Test;
import static com.github.kolorobot.exceptions.java8.ThrowableAssertion.assertThrown;

public class Java8ExceptionsTest {

    @Test
    public void verifiesTypeAndMessage() {
        assertThrown(new DummyService()::someMethod) // method reference
                // assertions
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Runtime exception occurred")
                .hasNoCause();
    }

    @Test
    public void verifiesCauseType() {
        // lambda expression
        assertThrown(() -> new DummyService().someOtherMethod(true))
                // assertions
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Runtime exception occurred")
                .hasCauseInstanceOf(IllegalStateException.class);
    }

    @Test
    public void verifiesCheckedExceptionThrownByDefaultConstructor() {
        // constructor reference
        assertThrown(DummyService2::new)
                // assertions
                .isInstanceOf(Exception.class)
                .hasMessage("Constructor exception occurred");
    }

    @Test
    public void verifiesCheckedExceptionThrownConstructor() {
        // lambda expression
        assertThrown(() -> new DummyService2(true))
                // assertions
                .isInstanceOf(Exception.class)
                .hasMessage("Constructor exception occurred");
    }

    @Test(expected = ExceptionNotThrownAssertionError.class) // making test pass
    public void failsWhenNoExceptionIsThrown() {
        // expected exception not thrown
        assertThrown(() -> System.out.println());
    }
}
```

Note: The advantage over `catch-exception` is that we will be able to test constructors that throw exceptions.

## Creating the ‘library’

### Syntatic sugar

`assertThrown` is a static factory method creating a new instance of `ThrowableAssertion` with a reference to caught exception.

```java
package com.github.kolorobot.exceptions.java8;

public class ThrowableAssertion {
    public static ThrowableAssertion assertThrown(ExceptionThrower exceptionThrower) {
        try {
            exceptionThrower.throwException();
        } catch (Throwable caught) {
            return new ThrowableAssertion(caught);
        }
        throw new ExceptionNotThrownAssertionError();
    }

    // other methods omitted for now
}
```

The `ExceptionThrower` is a `@FunctionalInterface` which instances can be created with lambda expressions, method references, or constructor references. `assertThrown` accepting `ExceptionThrower` will expect and be ready to handle an exception.

```java
@FunctionalInterface
public interface ExceptionThrower {
    void throwException() throws Throwable;
}
```

### Assertions

To finish up, we need to create some assertions so we can verify our expactions in test code regarding teste exceptions. In fact, `ThrowableAssertion` is a kind of [custom assertion](../../../2014/05/spice-up-your-test-code-with-custom-assertions/index.md) providing us a way to fluently verify the caught exception. In the below code I used `Hamcrest` matchers to create assertions. The full source of `ThrowableAssertion` class:

```java
package com.github.kolorobot.exceptions.java8;

import org.hamcrest.Matchers;
import org.junit.Assert;

public class ThrowableAssertion {

    public static ThrowableAssertion assertThrown(ExceptionThrower exceptionThrower) {
        try {
            exceptionThrower.throwException();
        } catch (Throwable caught) {
            return new ThrowableAssertion(caught);
        }
        throw new ExceptionNotThrownAssertionError();
    }

    private final Throwable caught;

    public ThrowableAssertion(Throwable caught) {
        this.caught = caught;
    }

    public ThrowableAssertion isInstanceOf(Class<? extends Throwable> exceptionClass) {
        Assert.assertThat(caught, Matchers.isA((Class<Throwable>) exceptionClass));
        return this;
    }

    public ThrowableAssertion hasMessage(String expectedMessage) {
        Assert.assertThat(caught.getMessage(), Matchers.equalTo(expectedMessage));
        return this;
    }

    public ThrowableAssertion hasNoCause() {
        Assert.assertThat(caught.getCause(), Matchers.nullValue());
        return this;
    }

    public ThrowableAssertion hasCauseInstanceOf(Class<? extends Throwable> exceptionClass) {
        Assert.assertThat(caught.getCause(), Matchers.notNullValue());
        Assert.assertThat(caught.getCause(), Matchers.isA((Class<Throwable>) exceptionClass));
        return this;
    }
}
```

### AssertJ Implementation

In case you use `AssertJ` library, you can easily create `AssertJ` version of `ThrowableAssertion` utilizing `org.assertj.core.api.ThrowableAssert` that provides many useful assertions out-of-the-box. The implementation of that class is even simpler than with `Hamcrest`presented above.

```java
package com.github.kolorobot.exceptions.java8;

import org.assertj.core.api.Assertions;
import org.assertj.core.api.ThrowableAssert;

public class AssertJThrowableAssert {
    public static ThrowableAssert assertThrown(ExceptionThrower exceptionThrower) {
        try {
            exceptionThrower.throwException();
        } catch (Throwable throwable) {
            return Assertions.assertThat(throwable);
        }
        throw new ExceptionNotThrownAssertionError();
    }
}
```

An example test with `AssertJ`:

```java
public class AssertJJava8ExceptionsTest {
    @Test
    public void verifiesTypeAndMessage() {
        assertThrown(new DummyService()::someMethod)
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Runtime exception occurred")
                .hasMessageStartingWith("Runtime")
                .hasMessageEndingWith("occurred")
                .hasMessageContaining("exception")
                .hasNoCause();
    }
}
```

## Update - AAA Style

Frank Appel in his [Clean JUnit Throwable-Tests with Java 8 Lambdas](http://www.codeaffine.com/2014/07/28/clean-junit-throwable-tests-with-java-8-lambdas/) post suggests to distinguish`act` and `assert` phases of the test for the clear visual separation (improving readability). The idea is to return the `Throwable` (instead of `ThrowableAssert`) in an `act` phase of the test and then pass it for assertion in the `assert` phase, so the test will look like the below:

```java
@Test
public void aaaStyle() {
    // arrange
    DummyService dummyService = new DummyService();

    // act
    Throwable throwable = ThrowableCaptor.captureThrowable(dummyService::someMethod);

    // assert
    assertThat(throwable)
            .isNotNull()
            .hasMessage("Runtime exception occurred");
}
```

Where `ThrowableCaptor` is defined as follows:

```java
public class ThrowableCaptor {
    public static Throwable captureThrowable(ExceptionThrower exceptionThrower) {
        try {
            exceptionThrower.throwException();
            // not exception was thrown
            return null;
        } catch (Throwable caught) {
            return caught;
        }
    }
}
```

## Summary

With just couple of lines of code, we built quite cool code helping us in testing exceptions in JUnit without any additional library. And this was just a start. Harness the power of Java 8 and lambda expressions!

## References

- [Source code](https://github.com/kolorobot/unit-testing-demo) for this article is available on GitHub (have a look at `com.github.kolorobot.exceptions.java8` package)
- Some other articles of mine about testing exceptions in JUnit. Please have a look:   
  - [Custom assertions](../../../2014/05/spice-up-your-test-code-with-custom-assertions/index.md)
  - [Catch-exception library](../../../2014/04/yet-another-way-to-handle-exceptions-in/index.md)
  - [Junit @Rule: beyond basics](../../../2014/03/junit-expectedexception-rule-beyond/index.md)
  - [Different ways of testing exceptions in Junit](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)

If you like my articles, please subscribe to <http://blog.codeleak.pl> here: <http://feeds.feedburner.com/codeleak> or follow me on twitter: <https://twitter.com/kolorobot>. I usually blog and tweet about Java and Spring.
