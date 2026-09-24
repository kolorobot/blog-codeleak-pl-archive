---
title: "Cleaner parameterized tests with JUnit 5"
date: 2017-06-08T01:04:00.000+02:00
updated: 2018-09-14T00:27:01.431+02:00
author: "Rafał Borowiec"
tags: ["unit testing"]
original_url: https://blog.codeleak.pl/2017/06/cleaner-parameterized-tests-with-junit-5.html
---

# Cleaner parameterized tests with JUnit 5

The general idea of parameterized unit tests is to run the same test method for different data.  
Creating parameterized tests in JUnit 4 is far from being perfect. There are many issues with the existing architecture: parameters are defined as class fields and constructor is needed to create them, parameterized and non-parameterized tests cannot be mixed in one test class and built-in data sources are very limited. Fortunately, all of this is improved in JUnit 5!

### *Change Log*

- **14/09/2017** - Source code and the article updated to the newest JUnit 5 version.
- **6/11/2017** - Source code updated. See <https://github.com/kolorobot/junit5-samples>

Note: As an alternative to JUnit 4 parameterized test you can use JUnitParams library that solves many of the issues I mentioned (see my blog post about JUnitParams here: [http://blog.codeleak.pl/2013/12/parametrized-junit-tests-with.html](../../../2013/12/parametrized-junit-tests-with/index.md)).

## How to get started?

To get started with parameterized tests in Junit 5 you need to add a required dependency to your project: add `org.junit.jupiter:junit-jupiter-params:${junitJupiterVersion}` dependency to the project to use parameterized tests, argument providers and converters.

## SUT - System Under Test

All the samples I created are testing FizzBuzz class:

```java
public class FizzBuzz {

    public String calculate(int number) {

        if (isDivisibleByThree(number) && isDivisibleByFive(number)) {
            return "FizzBuzz";
        }

        if (isDivisibleByThree(number)) {
            return "Fizz";
        }

        if (isDivisibleByFive(number)) {
            return "Buzz";
        }

        return String.valueOf(number);
    }

    private static boolean isDivisibleByThree(int dividend) {
        return isDivisibleBy(dividend, 3);
    }

    private static boolean isDivisibleByFive(int dividend) {
        return isDivisibleBy(dividend, 5);
    }

    private static boolean isDivisibleBy(int dividend, int divisor) {
        return dividend % divisor == 0;
    }
}
```

Although FizzBuzz is really simple, it can also be used to demonstrate more advanced unit testing techniques like implementing parametrized tests.

## My First Parameterized Test in JUnit 5

To create a parameterized test in JUnit 5 annotate a test method with `@org.junit.jupiter.params.ParameterizedTest` (instead of `@Test`) and provide the argument source:

```java
@ParameterizedTest(name = "{index} => calculate({0})")
@ValueSource(ints = {1, 2, 4, 7, 11, 13, 14})
void returnsNumberForNumberNotDivisibleByThreeAndFive(int number, TestInfo testInfo) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("" + number);
}
```

The annotation has optional `name` attribute that is used to customize invocation display names. Available template variables: {index} -> the current invocation index (1-based), {arguments} -> the complete, comma-separated arguments list, {0}, {1}, …​ -> an individual argument.

In this example `@org.junit.jupiter.params.provider.ValueSource` provides access to an array of literal values of integers. Exactly one type of input (either strings, insts, longs,doubles etc.) must be provided in this annotation.

I also provide additional parameters resolved by `org.junit.jupiter.api.extension.ParameterResolver`. Please note that method parameters that are resolved by argument sources need to come first in the argument list.

## More argument sources

### @MethodSource

```java
@ParameterizedTest(name = "{index} => calculate({0})")
@MethodSource({"divisibleByThree", "divisibleByThreeButNotFive"})
void returnFizzForNumberDivisibleByThree(int number) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("Fizz");
}
```

The `@org.junit.jupiter.params.provider.MethodSource` refers to methods (1 or more) returning argument source. In this example there are two methods:

```java
private static Stream<Integer> divisibleByThree() {
    int[] ints = new int[]{18, 21};
    return Stream.of(3, 6, 9, 12);
}

// The returned array will be converted to a Stream
private static String[] divisibleByThreeButNotFive() {
    return new String[]{"18", "21"};
}
```

The method that provides arguments must be static, must take no arguments and must return either Stream, Iterable, Iterator or array. What you probably noticed is that `divisibleByThreeButNotFive()` method returns an array of Strings. This will work perfectly fine thanks to built-in implicit **argument converters**. This is really useful when the argument source is a CSV (more on this below). In addition, arguments can be converted with a custom argument converters.

To resolve multiple arguments a method source will return a stream of `org.junit.jupiter.params.provider.Arguments` instances (`org.junit.jupiter.params.provider.ObjectArrayArguments`):

```java
@ParameterizedTest(name = "{index} => calculate({0}) should return {1}")
@MethodSource("fizzBuzz")
void fizzBuzz(int number, String expectedResult) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo(expectedResult);
}

private static Stream<Arguments> fizzBuzz() {
    return Stream.of(
        Arguments.of(1, "1"),
        Arguments.of(2, "2"),
        Arguments.of(3, "Fizz"),
        Arguments.of(4, "4"),
        Arguments.of(5, "Buzz"),
        Arguments.of(6, "Fizz"),
        Arguments.of(7, "7"),
        Arguments.of(8, "8"),
        Arguments.of(9, "Fizz"),
        Arguments.of(15, "FizzBuzz")
    );
}
```

### @CsvFileSource

Another very interesting way of providing argument source is `org.junit.jupiter.params.provider.CsvFileSource` that provides arguments from one of more CSV files from the classpath:

```java
@ParameterizedTest(name = "{index} => calculate({0}) should return {1}")
@CsvFileSource(resources = {"/fizzbuzz/fizzbuzz_1.csv", "/fizzbuzz/fizzbuzz_2.csv"}, delimiter = ';', numLinesToSkip = 1)
void fizzBuzzCsv(int number, String expectedResult) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo(expectedResult);
}
```

The CSV files:

```csv
number;expected_result
1;1
2;2
3;Fizz
4;4
```

and:

```csv
number;expected_result
5;Buzz
6;Fizz
15;FizzBuzz
```

### Other argument sources

- `@EnumSource` provides a convenient way to use Enum constants.
- `@CsvSource` allows you to express argument lists as comma-separated values
- `@ArgumentsSource` can be used to specify a custom, reusable arguments provider.

Enjoy parameterized tests in JUnit 5!

## Resources

- All the examples presented in this article can be found on GitHub: <https://github.com/kolorobot/unit-testing-demo>
- Look at the official JUnit 5 documentation to learn more: <http://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests>
