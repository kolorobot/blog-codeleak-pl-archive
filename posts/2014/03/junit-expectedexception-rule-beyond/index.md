---
title: "JUnit ExpectedException rule: beyond basics"
date: 2014-03-01T15:44:00.000+01:00
updated: 2014-06-06T21:32:50.484+02:00
author: "Rafał Borowiec"
tags: ["java", "unit testing"]
original_url: https://blog.codeleak.pl/2014/03/junit-expectedexception-rule-beyond.html
---

# JUnit ExpectedException rule: beyond basics

![](junit.gif)

There are different ways of handling exceptions in JUnit tests. As I wrote in one of my [previous posts](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md), my preferable way is using `org.junit.rules.ExpectedException` rule. Basically, rules are used as an alternative (or an addition) to methods annotated with `org.junit.Before`, `org.junit.After`, `org.junit.BeforeClass`, or `org.junit.AfterClass`, but they are more powerful, and more easily shared between projects and classes. In this post I will show more advanced usage of `org.junit.rules.ExpectedException` rule.

## Verify the exception message

Standard JUnit's `org.junit.Test` annotation offers `expected` attribute that allows you specifying the a `Throwable` to cause a test method to succeed if an exception of the specified class is thrown by the method. In many cases this seems enough, but if you want to verify an exception message - you must find other way. With `ExpectedException` is pretty straightforward:

```java
public class ExpectedExceptionsTest {

    @Rule
    public ExpectedException thrown = ExpectedException.none();
    
    @Test
    public void verifiesTypeAndMessage() {

        thrown.expect(RuntimeException.class);
        thrown.expectMessage("Runtime exception occurred");
        
        throw new RuntimeException("Runtime exception occurred");
    }
}
```

In the above snippet, we expect that a message `contains` a given substring. Comparing to type check only, it is much safer. Why? Let's assume that we have an `ExceptionThrower` that looks like follows:

```java
class ExceptionsThrower {
    void throwRuntimeException(int i) {
        if (i <= 0) {
            throw new RuntimeException("Illegal argument: i must be <= 0");
        }
        throw new RuntimeException("Runtime exception occurred");
    }
}
```

As you can see both exceptions thrown by a method are `RuntimeException`s, so in case we do not check the message, we are not 100% sure which exception will be thrown by a method. The following tests will pass:

```java
    @Test
    public void runtimeExceptionOccurs() {
        thrown.expect(RuntimeException.class);
        // opposite to expected
        exceptionsThrower.throwRuntimeException(0);
    }

    @Test
    public void illegalArgumentExceptionOccurs() {
        thrown.expect(RuntimeException.class);
        // opposite to expected
        exceptionsThrower.throwRuntimeException(1);
    }
```

Checking for the message in an exception will solve the problem and make sure you are verifying a wanted exception. This is already an advantage over `expected` attribute of `@Test` annotated methods.

But what if, you need to verify an exception message in a more sophisticated way? `ExpectedException` allows you that by providing a [Hamcrest](https://code.google.com/p/hamcrest/)  matcher to `expectMessage` method (instead of a String). Let's look at the example below:

```java
    @Test
    public void verifiesMessageStartsWith() {
        thrown.expect(RuntimeException.class);
        thrown.expectMessage(startsWith("Illegal argument:"));

        throw new RuntimeException("Illegal argument: i must be <= 0");
    }
```

As you can expect, you can provide your own matchers, to verify the message. Let's look at the example.

```java
    @Test
    public void verifiesMessageMatchesPattern() {
        thrown.expect(RuntimeException.class);
        thrown.expectMessage(new MatchesPattern("[Ii]llegal .*"));

        throw new RuntimeException("Illegal argument: i must be <= 0");
    }

    class MatchesPattern extends TypeSafeMatcher<String> {
        private String pattern;

        public MatchesPattern(String pattern) {
            this.pattern = pattern;
        }

        @Override
        protected boolean matchesSafely(String item) {
            return item.matches(pattern);
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("matches pattern ")
                .appendValue(pattern);
        }

        @Override
        protected void describeMismatchSafely(String item, Description mismatchDescription) {
            mismatchDescription.appendText("does not match");
        }
    }
```

## Verify the exception object

Matching messages may not be enough in certain scenarios. You may have an exception with custom methods and you want to verify them too. No problem at all. `ExpectedException` allows that with `expect` method that takes matcher.

```java
    @Test
    public void verifiesCustomException() {
        thrown.expect(RuntimeException.class);
        thrown.expect(new ExceptionCodeMatches(1));

        throw new CustomException(1);
    }

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
        private int code;

        public ExceptionCodeMatches(int code) {
            this.code = code;
        }

        @Override
        protected boolean matchesSafely(CustomException item) {
            return item.getCode() == code;
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("expects code ")
                    .appendValue(code);
        }

        @Override
        protected void describeMismatchSafely(CustomException item, Description mismatchDescription) {
            mismatchDescription.appendText("was ")
                    .appendValue(item.getCode());
        }
    }
```

Please note, that I implemented both `describeTo` and `describeMismatchSafely` methods of `TypeSafeMatcher`. I need them to produce nicely looking error messages when the test fails. Have a look at an example below:

```
java.lang.AssertionError: 
Expected: (an instance of java.lang.RuntimeException and expects code <1>)
     but: expects code <1> was <2>
```

## Checking a cause

One additional thing you can do with `ExpectedException` is to verify the cause of a thrown exception. This also can be done with custom matchers:

```java
    @Test
    public void verifiesCauseTypeAndAMessage() {
        thrown.expect(RuntimeException.class);
        thrown.expectCause(new CauseMatcher(IllegalStateException.class, "Illegal state"));

        throw new RuntimeException("Runtime exception occurred",
                new IllegalStateException("Illegal state"));
    }

    private static class CauseMatcher extends TypeSafeMatcher<Throwable> {

        private final Class<? extends Throwable> type;
        private final String expectedMessage;

        public CauseMatcher(Class<? extends Throwable> type, String expectedMessage) {
            this.type = type;
            this.expectedMessage = expectedMessage;
        }

        @Override
        protected boolean matchesSafely(Throwable item) {
            return item.getClass().isAssignableFrom(type)
                    && item.getMessage().contains(expectedMessage);
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("expects type ")
                    .appendValue(type)
                    .appendText(" and a message ")
                    .appendValue(expectedMessage);
        }
    }
```

## Summary

`ExpectedException` rule is a powerful feature. With an addition of `Hamcrest` matchers you are able to easily create robust and reusable code for you exceptions tests.

The code samples can be found on [GitHub](https://github.com/kolorobot/unit-testing-demo/blob/master/src/test/java/com/github/kolorobot/exceptions/ExpectedExceptionsTest.java). Please also check my previous post: [3 ways of handling exceptions in JUnit. Which one to choose?](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md). If you want to get started quickly with JUnit and other testing frameworks you may be interested in [HOW-TO: Test dependencies in a Maven project](../../../2014/03/how-to-test-dependencies-in-maven/index.md)

If you are looking for another way of handling exceptions in JUnit, check this post: [Yet another way to handle exceptions in JUnit: catch-exception](../../../2014/04/yet-another-way-to-handle-exceptions-in/index.md)
