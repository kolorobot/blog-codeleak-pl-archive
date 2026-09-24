---
title: "JUnit: Testing Exceptions with Java 8 and AssertJ 3.0.0"
date: 2015-04-21T22:27:00.000+02:00
updated: 2015-04-21T22:27:30.391+02:00
author: "Rafał Borowiec"
tags: ["assertj", "java 8", "unit testing"]
original_url: https://blog.codeleak.pl/2015/04/junit-testing-exceptions-with-java-8.html
---

# JUnit: Testing Exceptions with Java 8 and AssertJ 3.0.0

AssertJ 3.0.0 release for Java 8 makes testing exceptions much easier than before. In one of my previous [blog post](../../../2014/07/junit-testing-exception-with-java-8-and-lambda-expressions/index.md) I described how to utilize *plain* Java 8 to achieve this, but with AssertJ 3.0.0 much of the code I created may be removed.

Warning: this blog post contains mostly the code examples.

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

## assertThatThrownBy() examples

Note: static import of `org.assertj.core.api.Assertions.assertThatThrownBy` is required in order to make the below code work properly.

```java
@Test
public void verifiesTypeAndMessage() {
    assertThatThrownBy(new DummyService()::someMethod) 
            .isInstanceOf(RuntimeException.class)
            .hasMessage("Runtime exception occurred")
            .hasNoCause();
}

@Test
public void verifiesCauseType() {
    assertThatThrownBy(() -> new DummyService().someOtherMethod(true))
            .isInstanceOf(RuntimeException.class)
            .hasMessage("Runtime exception occurred")
            .hasCauseInstanceOf(IllegalStateException.class);
}

@Test
public void verifiesCheckedExceptionThrownByDefaultConstructor() {
    assertThatThrownBy(DummyService2::new)
            .isInstanceOf(Exception.class)
            .hasMessage("Constructor exception occurred");
}

@Test
public void verifiesCheckedExceptionThrownConstructor() {
    assertThatThrownBy(() -> new DummyService2(true))
            .isInstanceOf(Exception.class)
            .hasMessage("Constructor exception occurred");
}
```

The assertions presented comes from `AbstractThrowableAssert` and there are much more of them for you to use!

## No exception thrown!

The below test will fail as no exception is thrown:

```java
@Test
public void failsWhenNoExceptionIsThrown() {    
    assertThatThrownBy(() -> System.out.println());
}
```

The message is:

```
java.lang.AssertionError: Expecting code to raise a throwable.
```

## AAA Style

If you wish to distinguish act and assert phases of the test for improving readability, it is also possible:

```java
@Test
public void aaaStyle() {
    // arrange
    DummyService dummyService = new DummyService();

    // act
    Throwable throwable = catchThrowable(dummyService::someMethod);

    // assert
    assertThat(throwable)
            .isNotNull()
            .hasMessage("Runtime exception occurred");
}
```

## References

- [Source code](https://github.com/kolorobot/unit-testing-demo) for this article is available on GitHub (have a look at `com.github.kolorobot.assertj.exceptions` package)
- [AssertJ 3.0.0](http://joel-costigliola.github.io/assertj/assertj-core-news.html#assertj-core-3.0.0) for Java 8 release
