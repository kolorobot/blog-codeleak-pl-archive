---
title: "Test Execution Order in JUnit 5"
date: 2019-03-24T21:57:00.000+01:00
updated: 2019-03-24T22:15:38.841+01:00
author: "Rafał Borowiec"
tags: ["junit 5", "unit testing"]
original_url: https://blog.codeleak.pl/2019/03/test-execution-order-in-junit-5.html
---

# Test Execution Order in JUnit 5

The general practices say that automated tests should be able to run independently and with no specific order as well as the result of the test should not depend on the results of previous tests. But there are situations where a specific order of test execution can be justified, especially in integration or end to end tests.

By default, in JUnit 5 the execution of test methods is repeatable between builds hence deterministic but the algorithm is intentionally non-obvious (as authors of the library state). Fortunately, execution order can be adjusted to our needs using either built-in method orderers or by creating custom ones.

## `org.junit.jupiter.api.TestMethodOrder`

In order to change test execution order we need to annotate the test class with `org.junit.jupiter.api.TestMethodOrder` and pass the type of method orderer as an argument. As of JUnit 5.4 there are three built-in method orderers: `OrderAnnotation`, `Alphanumeric` and `Random`. We can also easily create our own custom method orderer by implementing `org.junit.jupiter.api.MethodOrderer` interface.

### Ordering with `@Order` annotation

```java
package pl.codeleak.samples.junit5.basics;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class TestExecutionOrderWithOrderAnnotation {

    @Order(1)
    @Test
    void aTest() {}

    @Order(2)
    @Test
    void bTest() {}

    @Order(3)
    @Test
    void cTest() {}

}
```

### Alphanumeric ordering

```java
@TestMethodOrder(MethodOrderer.Alphanumeric.class)
class AlphanumericTestExecutionOrder {

    @Test
    void aTest() {}

    @Test
    void bTest() {}

    @Test
    void cTest() {}

}
```

### Random ordering

Random ordering can be useful if want to make sure that order of method execution is not deterministic between builds.

```java
@TestMethodOrder(MethodOrderer.Random.class)
class AlphanumericTestExecutionOrder {

    @Test
    void aTest() {}

    @Test
    void bTest() {}

    @Test
    void cTest() {}

}
```

Random method orderer is using `System.nanoTime()` as the seed but it can be changed using `junit.jupiter.execution.order.random.seed` configuration property. The value of this property should return any `String` that can be converted using `Long.valueOf(String)`.

One way of configuring the seed is to provide the configuration property in `junit-platform.properties` configuration file:

```
junit.jupiter.execution.order.random.seed=42
```

### Custom ordering

Creating a custom method orderer can be done by implementing `org.junit.jupiter.api.MethodOrderer` interface and providing it as the argument to `@TestMethodOrder`.

The below example is a method orderer that sorts methods by their names length:

```java
class MethodLengthOrderer implements MethodOrderer {

    private Comparator<MethodDescriptor> comparator =
            Comparator.comparingInt(methodDescriptor -> methodDescriptor.getMethod().getName().length());

    @Override
    public void orderMethods(MethodOrdererContext context) {
        context.getMethodDescriptors().sort(comparator);
    }
}
```

And the use:

```java
@TestMethodOrder(MethodLengthOrderer.class)
class CustomTestExecutionOrder {

    @Test
    void aTest() {}

    @Test
    void abTest() {}

    @Test
    void abcTest() {}

}
```

## Summary

Having a way of adjusting test execution order in JUnit 5 can be useful in certain situation and I am glad to see this feature. I believe in most cases built-in method orderers will be more than enough. If not, there is an easy way of implementing a custom one.

Find examples from used in this article (along with many more) on GitHub: <https://github.com/kolorobot/junit5-samples/tree/master/junit5-basics>

## See also

- [Temporary directories in JUnit 5 Tests](../../../2019/03/temporary-directories-in-junit-5-tests/index.md)
- [Cleaner parameterized tests with JUnit 5](../../../2017/06/cleaner-parameterized-tests-with-junit-5/index.md)
- [JUnit 5 meets AssertJ](../../../2017/11/junit-5-meets-assertj/index.md)
