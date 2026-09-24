---
title: "8 ways of handling exceptions in JUnit. Which one to choose?"
date: 2013-07-15T23:21:00.000+02:00
updated: 2017-06-06T23:29:45.262+02:00
author: "Rafał Borowiec"
tags: ["java", "unit testing"]
original_url: https://blog.codeleak.pl/2013/07/3-ways-of-handling-exceptions-in-junit.html
---

# 8 ways of handling exceptions in JUnit. Which one to choose?

In JUnit there are many ways of handling exceptions in your test code:

- try-catch idiom
- With JUnit rule
- With @Test annotation
- With catch-exception library
- With custom annotation
- With Lambda expression (as of Java 1.8)
- With AssertJ 3.0.0 for Java 8
- **(NEW!)** With JUnit 5 built-in assertThrows

Which one should we use and when?

## try-catch idiom

This idiom is one of the most popular one, because it was used already in JUnit 3.

```java
    @Test
    public void throwsExceptionWhenNegativeNumbersAreGiven() {
        try {
            calculator.add("-1,-2,3");
            fail("Should throw an exception if one or more of given numbers are negative");
        } catch (Exception e) {
            assertThat(e)
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("negatives not allowed: [-1, -2]");
        }
    }
```

The above approach is a common pattern. The test will fail when no exception is thrown and the exception itself is verified in a catch clause (in the above example I used the FEST Fluent Assertions) and although it is perfectly fine I prefer the approach with *ExpectedException* rule.

## With JUnit rule

The same example can be created using *ExceptedException* rule. The rule must be a public field marked with @Rule annotation. Please note that the "thrown" rule may be reused in many tests.

```java
    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Test
    public void throwsExceptionWhenNegativeNumbersAreGiven() {
        // arrange
        thrown.expect(IllegalArgumentException.class);
        thrown.expectMessage(equalTo("negatives not allowed: [-1, -2]"));
        // act
        calculator.add("-1,-2,3");
    }
```

In general, I find the above code more readable hence I use this approach in my projects.

When the exception isn't thrown you will get the following message: *java.lang.AssertionError: Expected test to throw (an instance of java.lang.IllegalArgumentException and exception with message "negatives not allowed: [-1, -2]")*. Pretty nice.

But not all exceptions I check with the above approach. Sometimes I need to check only the type of the exception thrown and then I use @Test annotation.

## With annotation

```java
    @Test (expected = IllegalArgumentException.class)
    public void throwsExceptionWhenNegativeNumbersAreGiven() {
        // act
        calculator.add("-1,-2,3");
    }
```

When the exception wasn't thrown you will get the following message: *java.lang.AssertionError: Expected exception: java.lang.IllegalArgumentException*

With this approach you need to be careful though. Sometimes it is tempting to expect general *Exception*, *RuntimeException* or even a *Throwable*. And this is considered as a bad practice, because your code may throw exception in other place than you actually expected and your test will still pass!

To sum up, in my code I use two approaches: ***with JUnit rule*** and ***with annotation***. The advantages are:

- Error messages when the code does not throw an exception are automagically handled
- The readability is improved
- There is less code to be created

## catch-exceptions

In short, *[catch-exception](https://code.google.com/p/catch-exception/)* is a library that catches exceptions in a single line of code and makes them available for further analysis.

Please read a separate post I created about it here: [Yet another way to handle exceptions in JUnit: catch-exception](../../../2014/04/yet-another-way-to-handle-exceptions-in/index.md)

## Lambda expressions

As of Java 8 we have another way of dealing with exceptions: with lambda expressions, that make catch-exception library redundant. With just couple of lines of code, one can build quite cool code for testing exceptions in JUnit without any additional library. See: [JUnit: testing exception with Java 8 and Lambda Expressions](../../../2014/07/junit-testing-exception-with-java-8-and-lambda-expressions/index.md)

## AssertJ 3.0.0 for Java 8

AssertJ 3.0.0 release for Java 8 makes testing exceptions much easier than before. Minimal code. Please read a separate post I created about it here: [JUnit: Testing Exceptions with Java 8 and AssertJ 3.0.0](../../../2015/04/junit-testing-exceptions-with-java-8/index.md)

## Custom annotation

I have heard of another way of handling the exception (one of my colleagues suggested it after reading this post) - use custom annotation.

Actually the solution seems nice at first glance, but it requires your own JUnit runner hence it has disadvantage: you cannot use this annotation with e.g. Mockito runner.

As a coding practice I have created such an annotation, so maybe someone finds it useful

**The usage**

```java
@RunWith(ExpectsExceptionRunner.class)
public class StringCalculatorTest {
    @Test
    @ExpectsException(type = IllegalArgumentException.class, message = "negatives not allowed: [-1]")
    public void throwsExceptionWhenNegativeNumbersAreGiven() throws Exception {
        // act
        calculator.add("-1,-2,3");
    }
  
}
```

The above test will fail with a message: *java.lang.Exception: Unexpected exception message, expected but was*

**An annotation**

```java
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD})
public @interface ExpectsException {
    Class<? extends Throwable> type();

    String message() default "";
}
```

**A runner** with some copy & paste code

```java
public class ExpectsExceptionRunner extends BlockJUnit4ClassRunner {
    public ExpectsExceptionRunner(Class<?> klass) throws InitializationError {
        super(klass);
    }

    @Override
    protected Statement possiblyExpectingExceptions(FrameworkMethod method, Object test, Statement next) {
        ExpectsException annotation = method.getAnnotation(ExpectsException.class);
        if (annotation == null) {
            return next;
        }
        return new ExpectExceptionWithMessage(next, annotation.type(), annotation.message());
    }

    class ExpectExceptionWithMessage extends Statement {

        private final Statement next;
        private final Class<? extends Throwable> expected;
        private final String expectedMessage;

        public ExpectExceptionWithMessage(Statement next, Class<? extends Throwable> expected, String expectedMessage) {
            this.next = next;
            this.expected = expected;
            this.expectedMessage = expectedMessage;
        }

        @Override
        public void evaluate() throws Exception {
            boolean complete = false;
            try {
                next.evaluate();
                complete = true;
            } catch (AssumptionViolatedException e) {
                throw e;
            } catch (Throwable e) {
                if (!expected.isAssignableFrom(e.getClass())) {
                    String message = "Unexpected exception, expected<"
                            + expected.getName() + "> but was <"
                            + e.getClass().getName() + ">";
                    throw new Exception(message, e);
                }

                if (isNotNull(expectedMessage) && !expectedMessage.equals(e.getMessage())) {
                    String message = "Unexpected exception message, expected<"
                            + expectedMessage + "> but was<"
                            + e.getMessage() + ">";
                    throw new Exception(message, e);
                }
            }
            if (complete) {
                throw new AssertionError("Expected exception: "
                        + expected.getName());
            }
        }

        private boolean isNotNull(String s) {
            return s != null && !s.isEmpty();
        }
    }

}
```

## JUnit 5 built-in assertThrows

JUnit 5 brought pretty awesome improvements and it differs a lot from its predecessor. JUnit 5 requires Java 8 at runtime hence Lambda expressions can be used in tests, especially in assertions. One of those assertions is perfectly suited for testing exceptions.

Read this short writeup on JUnit 5 and assertThrows [http://blog.codeleak.pl/2017/06/testing-exceptions-with-junit-5.html](../../../2017/06/testing-exceptions-with-junit-5/index.md)

And what is your preference?

## Update (*1/10/2015*)

Yet another blog post - a guest one - at [http://blog.goyello.com](http://blog.goyello.com/2015/10/01/different-ways-of-testing-exceptions-in-java-and-junit). It is more up to date and it summarizes most of the approaches in a single read: [Different ways of testing exceptions in Java and JUnit](http://blog.goyello.com/2015/10/01/different-ways-of-testing-exceptions-in-java-and-junit)
