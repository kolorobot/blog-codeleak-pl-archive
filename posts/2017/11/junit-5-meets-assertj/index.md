---
title: "JUnit 5 meets AssertJ"
date: 2017-11-23T01:21:00.000+01:00
updated: 2017-11-23T01:21:09.981+01:00
author: "Rafał Borowiec"
tags: ["assertj", "junit 5", "unit testing"]
original_url: https://blog.codeleak.pl/2017/11/junit-5-meets-assertj.html
---

# JUnit 5 meets AssertJ

JUnit 5 brings a lot of improvements in the assertions library, mainly thanks to Java 8 and Lambda Expression support and thanks to the presence of the new assertions like `assertAll`, `assertTimeout` or`assertThrows`. Although I really like JUnit 5 I believe that AssertJ is still a must in production grade unit tests and I will continue using it.

But I think there are potential scenarios of mixing both JUnit 5 and AssertJ in single unit test: one of them is mixing JUnit `assertAll` with AssertJ `assertThat`.

## JUnit 5 - assertAll

`Assertions.assertAll` asserts that all supplied executables do not throw exceptions:

```java
List<String> owners = Arrays.asList("Betty Davis", "Eduardo Rodriquez");

// assert
assertAll(
    () -> assertTrue(owners.contains("Betty Doe"), "Contains Betty Doe"),
    () -> assertTrue(owners.contains("John Doe"), "Contains John Doe"),
    () -> assertTrue(owners.contains("Eduardo Rodriquez"), "Eduardo Rodriquez")
);
```

The above will report 2 errors:

```
org.opentest4j.MultipleFailuresError: Multiple Failures (2 failures)
    Contains Betty Doe ==> expected: <true> but was: <false>
    Contains John Doe ==> expected: <true> but was: <false>
```

`assertAll` executes all passed executables and makes sure all pass (do not throw exception). In other words, `assertAll` allows grouped assertions.

In addition, `assertAll` can be used for creating dependent assertions:

```java
List<String> owners = Arrays.asList("Betty Davis", "Eduardo Rodriquez");

// assert
assertAll(
    () -> {
        assertTrue(owners.contains("Betty Doe"), "Contains Betty Doe");

        assertAll(
            () -> assertNotNull(owners),
            () -> assertTrue(owners.size() > 1)
        );
    }
);
```

In the above example, when the first `assertTrue` fails the subsequent `assertAll` will be skipped.

# AssertJ - SoftAssertions

Note: I wrote more about SoftAssertions in this article: [AssertJ soft assertions - do we need them?](../../../2015/09/assertjs-softassertions-do-we-need-them/index.md)

`AssertJ` offers `SoftAssertions` which basically do the same as JUnit 5 `assertAll` with the slight difference of not supporting dependent assertions.

```java
List<String> owners = Arrays.asList("Betty Davis", "Eduardo Rodriquez");

assertSoftly(
    softAssertions -> {
        softAssertions.assertThat(owners).contains("Betty Doe");
        softAssertions.assertThat(owners).contains("John Doe");
        softAssertions.assertThat(owners).contains("Eduardo Rodriquez");
    }
);
```

The reported errors:

```
1) 
Expecting:
 <["Betty Davis", "Eduardo Rodriquez"]>
to contain:
 <["Betty Doe"]>
but could not find:
 <["Betty Doe"]>

at AssertJAssertionsTest.lambda$assertsSoftly$0(AssertJAssertionsTest.java:26)
2) 
Expecting:
 <["Betty Davis", "Eduardo Rodriquez"]>
to contain:
 <["John Doe"]>
but could not find:
 <["John Doe"]>
```

# Mixing JUnit assertAll with AssertJ assertThat

Mixing JUnit 5 `assertAll` with AssertJ `assertThat` assertions seems to be like a nice option:

```java
// arrange
String givenName = "Jean";
String expectedCity = "Monona";
String expectedAddress = "105 N. Lake St.";

// act
Optional<Owner> result = testObj.findByName(givenName);

// assert
assertThat(result).isPresent();

assertAll(
    () -> assertThat(result.get().getFirstName()).isEqualTo(givenName),
    () -> assertThat(result.get().getCity()).isEqualTo(expectedCity),
    () -> assertThat(result.get().getAddress()).isEqualTo(expectedAddress)
);
```

On the other hand, `assertAll` can be used as a parameter to `assertThat`:

```java
// arrange
String givenName = "Jean";
String expectedCity = "Monona";
String expectedAddress = "105 N. Lake St.";

// act
Optional<Owner> result = testObj.findByName(givenName);

// assert
assertThat(result).hasValueSatisfying(owner -> assertAll(
    () -> assertThat(owner.getFirstName()).isEqualTo(givenName),
    () -> assertThat(owner.getCity()).isEqualTo(expectedCity),
    () -> assertThat(owner.getAddress()).isEqualTo(expectedAddress)
));
```

# Summary

Although JUnit 5 is a great framework and it offers a lot as it goes to assertions, I believe that 3rd party assertion library like AssertJ is needed anyways to spice up assertions a bit. I have been using AssertJ for several years now and I don’t think I will abandon it. But I definitely see a space for new JUnit 5 `assertAll` in my tests. Especially in integration tests.

All the examples from this blog post (and much more) can be found in this GitHub repository: <https://github.com/kolorobot/junit5-samples>*

** Big thanks to [Maciej Koziara](https://twitter.com/Pacific112v) who contributed to this repository.*
