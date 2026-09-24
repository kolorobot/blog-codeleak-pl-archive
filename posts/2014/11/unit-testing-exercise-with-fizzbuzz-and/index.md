---
title: "Unit Testing exercise with FizzBuzz and Mockito"
date: 2014-11-23T18:23:00.000+01:00
updated: 2014-11-23T18:23:06.298+01:00
author: "Rafał Borowiec"
tags: []
original_url: https://blog.codeleak.pl/2014/11/unit-testing-exercise-with-fizzbuzz-and.html
---

# Unit Testing exercise with FizzBuzz and Mockito

I sometimes use FizzBuzz to demonstrate the basics of unit testing to newbies. Although FizzBuzz is really simple problem, it can also be used to demonstrate more advanced unit testing techniques like **mocking**.

The FizzBuzz Kata: “*Write a program that prints the numbers from 1 to 100. But for multiples of three print “Fizz” instead of the number and for the multiples of five print “Buzz”. For numbers which are multiples of both three and five print “FizzBuzz”*“.

The possible solution to FizzBuzz algorithm:

```java
public class FizzBuzz {

    private static final int FIVE = 5;
    private static final int THREE = 3;

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

        return "" + number;
    }

    private boolean isDivisibleBy(int dividend, int divisor) {
        return dividend % divisor == 0;
    }
}
```

As the above code solves the FizzBuzz algorithm it does not solve the FizzBuzz problem. To finish it we need code to print the numbers from 1 to 100 using the algorithm. And this part of the code can be used to show the idea of mocking in JUnit with Mockito.

As the result of this exercise I ended up with a `NumberPrinter` that takes two arguments: `Printer` and `NumberCalculator` and has one public method to print numbers:

```java
public class NumberPrinter {

    private NumberCalculator numberCalculator;
    private Printer printer;

    public NumberPrinter(NumberCalculator numberCalculator, Printer printer) {
        this.numberCalculator = numberCalculator;
        this.printer = printer;
    }

    public void printNumbers(int limit) {
        if (limit < 1) {
            throw new RuntimeException("limit must be >= 1");
        }
        for (int i = 1; i <= limit; i++) {
            try {
                printer.print(numberCalculator.calculate(i));
            } catch (Exception e) {
                // noop
            }
        }
    }
}

public interface NumberCalculator {
    String calculate(int number);
}

public interface Printer {
    void print(String s);
}
```

With the interfaces introduced I have not only testable but more robust code. To test `NumberPrinter` I simply mock dependencies with the power and simplicity of Mockito. With Mockito annotations the configuration test code reads better.

Mockito features demonstrated:

- creating and injecting mocks
- stubbing methods also with setting different behavior for consecutive method calls.
- stubbing the void method with an exception
- verifications

Annotations used:

- `@RunWith(MockitoJUnitRunner.class)` - initializes `@Mock`s before each test method
- `@Mock` - marks a field as mock
- `@InjectMocks` - marks a field on which injection should be performed

```java
@RunWith(MockitoJUnitRunner.class)
public class NumberPrinterTest {

    @Mock
    private Printer printer;

    @Mock
    private NumberCalculator numberCalculator;

    @InjectMocks
    private NumberPrinter numberPrinter;

    @Test
    public void printsCalculatorResultsHundredTimes() {
        // arrange
        int limit = 100;
        when(numberCalculator.calculate(anyInt()))
                .thenReturn("0")  // first invocation returns "0"
                .thenReturn("1"); // other invocations return "1"
        // act
        numberPrinter.printNumbers(limit);
        // assert
        verify(numberCalculator, times(limit)).calculate(anyInt());
        verify(printer, times(1)).print("0");
        verify(printer, times(limit - 1)).print("1");
        verifyNoMoreInteractions(numberCalculator, printer);
    }

    @Test
    public void continuesOnCalculatorOrPrinterError() {
        // arrange
        when(numberCalculator.calculate(anyInt()))
                .thenReturn("1")
                .thenThrow(new RuntimeException())
                .thenReturn("3");
        // stub the void method with an exception
        doThrow(new RuntimeException()).when(printer).print("3");
        // act
        numberPrinter.printNumbers(3);
        // assert
        verify(numberCalculator, times(3)).calculate(anyInt());
        verify(printer).print("1");
        verify(printer).print("3");

        verifyNoMoreInteractions(numberCalculator, printer);
    }
}
```

Enjoy [Mockito](https://github.com/mockito/mockito)!

Want to learn more about Mockito annotations? Have a look at Eugen Paraschiv’s “Mockito – @Mock, @Spy, @Captor and @InjectMocks”: <http://www.baeldung.com/mockito-annotations>

Looking for code samples? Have a look at unit-testing-demo project presenting different aspects of unit testing, including mocking: <https://github.com/kolorobot/unit-testing-demo>
