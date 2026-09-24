---
title: "Switch as an expression in Java with Lambda-like syntax"
date: 2020-05-14T21:28:00.000+02:00
updated: 2020-05-16T17:26:08.040+02:00
author: "Rafał Borowiec"
tags: ["java", "java 9 and beyond"]
original_url: https://blog.codeleak.pl/2020/05/switch-as-an-expression-in-java.html
---

# Switch as an expression in Java with Lambda-like syntax

As of Java 14, the `switch` expression has an additional *Lambda-like* (`case ... -> labels`) syntax and it can be used not only as a statement, but also as an expression that evaluates to a single value.

## *Lambda-like* syntax (`case ... -> labels`)

With the new *Lambda-like* sytax, if a label is matched, then only the expression or statement to the right of the arrow is executed; there is no fall through:

```java
var result = switch (str) {
    case "A" -> 1;
    case "B" -> 2;
    case "C" -> 3;
    case "D" -> 4;
    default -> throw new IllegalStateException("Unexpected value: " + str);
};
```

The above is an example of `switch` as an expression returning an single integer value. The same syntax can be used in `switch` as a statement:

```java
int result;
switch (str) {
    case "A" -> result = 1;
    case "B" -> result = 2;
    case "C" -> {
        result = 3;
        System.out.println("3!");
    }
    default -> {
        System.err.println("Unexpected value: " + str);
        result = -1;
    }
}
```

## `yield`

In the situation when a block is needed in a `case`, `yield` can be used to return a value from it:

```java
var result = switch (str) {
    case "A" -> 1;
    case "B" -> 2;
    case "C" -> {
        System.out.println("3!");
        yield 3; // return
    }
    default -> throw new IllegalStateException("Unexpected value: " + str);
};
```

## Mutliple constants per `case`

It is also possible to use mutliple constants per `case`, separated by comma, which futher simplifies the usage of `switch`:

```java
var result = switch (str) {
    case "A" -> 1;
    case "B" -> 2;
    case "C" -> 3;
    case "D", "E", "F" -> 4;
    default -> 5;
};
```

## Final example

To demonstrate new `switch` syntax I created this tiny calculator:

```java
double calculate(String operator, double x, double y) {
    return switch (operator) {
        case "+" -> x + y;
        case "-" -> x - y;
        case "*" -> x * y;
        case "/" -> {
            if (y == 0) {
                throw new IllegalArgumentException("Can't divide by 0");
            }
            yield x / y;
        }
        default -> throw new IllegalArgumentException("Unknown operator '%s'".formatted(operator));
    };
}
```

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/java9-and-beyond>

## References

- <https://openjdk.java.net/jeps/361>
