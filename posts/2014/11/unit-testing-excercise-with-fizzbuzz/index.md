---
title: "Unit Testing exercise with FizzBuzz and JUnitParams"
date: 2014-11-15T21:11:00.000+01:00
updated: 2014-11-23T17:23:41.906+01:00
author: "Rafał Borowiec"
tags: ["unit testing"]
original_url: https://blog.codeleak.pl/2014/11/unit-testing-excercise-with-fizzbuzz.html
---

# Unit Testing exercise with FizzBuzz and JUnitParams

I sometimes use FizzBuzz to demonstrate the basics of unit testing to newbies. Although FizzBuzz is really simple problem, it can also be used to demonstrate more advanced unit testing techniques like implementing **parametrized tests**.

The FizzBuzz Kata: “*Write a program that prints the numbers from 1 to 100. But for multiples of three print “Fizz” instead of the number and for the multiples of five print “Buzz”. For numbers which are multiples of both three and five print “FizzBuzz”*“.

One of the possible solutions to FizzBuzz algorithm is:

```java
public class FizzBuzz {

    private static final int THREE = 3;
    private static final int FIVE = 5;

    public String calculate(int number) {
        if (isDivisibleBy(number, THREE) && isDivisibleBy(number, FIVE)) {
            return "FizzBuzz";
        }

        if (isDivisibleBy(number, THREE)) {
            return "Fizz";
        }

        if (isDivisibleBy(number, FIVE)) {
            return "Buzz";
        }

        return String.valueOf(number);
    }

    private boolean isDivisibleBy(int dividend, int divisor) {
        return dividend % divisor == 0;
    }
}
```

The above example is ideal to show parametrized tests with JUnitParams. We could create 4 test methods, each for different FizzBuzz case:

```java
@Test
@Parameters({"1", "2", "4", "7", "11", "13", "14"})
public void returnsNumberForNumberNotDivisibleByThreeAndFive(int number) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("" + number);
}

@Test
@Parameters({"3", "6", "9", "12", "18", "21", "24"})
public void returnFizzForNumberDivisibleByThree(int number) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("Fizz");
}

@Test
@Parameters({"5", "10", "20", "25", "35", "40", "50"})
public void returnBuzzForNumberDivisibleByFive(int number) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("Buzz");
}

@Test
@Parameters({"15", "30", "45", "60"})
public void returnsFizzBuzzForNumberDivisibleByThreeAndFive(int number) {
    assertThat(fizzBuzz.calculate(number)).isEqualTo("FizzBuzz");
}
```

But we could also cover all the cases in one parametrized test method:

```java
@Test
@Parameters
public void fizzBuzz(int given, String expected) {
    assertThat(fizzBuzz.calculate(given)).isEqualTo(expected);
}

public Object[] parametersForFizzBuzz() {
    return $(
            $(1, "1"),
            $(2, "2"),
            $(3, "Fizz"),
            $(4, "4"),
            $(5, "Buzz"),
            $(6, "Fizz"),
            $(7, "7"),
            $(10, "Buzz"),
            $(15, "FizzBuzz"),
            $(30, "FizzBuzz")
    );
}
```

Enjoy [JunitParams](https://github.com/Pragmatists/junitparams)!

Have a look at unit-testing-demo project presenting different aspects of unit testing, including parametrized tests: <https://github.com/kolorobot/unit-testing-demo>
