---
title: "Unit test names describe features"
date: 2013-07-14T13:22:00.001+02:00
updated: 2013-07-14T20:52:06.105+02:00
author: "Rafał Borowiec"
tags: ["java", "unit testing"]
original_url: https://blog.codeleak.pl/2013/07/unit-test-names-describe-features.html
---

# Unit test names describe features

I have been working with unit testing for several years and I always had problems in finding the best names for my tests. I have been trying different conventions and I ended up with the practice of naming tests based on the behavior they test.
For the following class:

```java
public class SamePasswordsValidator {
    public boolean isValid(PasswordAware value) {...}
}
```

I would create a test:

```java
public class SamePasswordsValidatorTest {
    @Test
    public void shouldReturnTrueWhenPasswordsMatch() {...}
}
```

Or:

```java
public class SamePasswordsValidatorTest {
    @Test
    public void shouldBeValidWhenPasswordsMatch() {...}
}
```

When creating the names I think of the scenario and the expected behavior. One thing that still I am not sure about is the word *"should"*, that is repeated (prefix) in all test names (DRY?). So maybe we "should" try to remove it:

```java
public class SamePasswordsValidatorTest {
    @Test
    public void isValidWhenPasswordsMatch() {...}
}
```

## References

- Growing Object-Oriented Software, Guided by Tests (http://www.amazon.com/Growing-Object-Oriented-Software-Guided-Tests/dp/0321503627/ref=sr_1_1?ie=UTF8&qid=1373800858&sr=8-1&keywords=guided+by+tests)
- BDD (http://en.wikipedia.org/wiki/Behavior-driven_development)
