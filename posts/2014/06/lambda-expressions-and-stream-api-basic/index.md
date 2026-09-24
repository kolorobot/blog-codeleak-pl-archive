---
title: "Lambda Expressions and Stream API: basic examples"
date: 2014-06-16T21:49:00.000+02:00
updated: 2014-06-16T21:49:24.455+02:00
author: "Rafał Borowiec"
tags: ["java 8"]
original_url: https://blog.codeleak.pl/2014/06/lambda-expressions-and-stream-api-basic.html
---

# Lambda Expressions and Stream API: basic examples

This blog post contains a list of basic Lambda expressions and Stream API examples I used in a live coding presentation I gave in June 2014 at [Java User Group - Politechnica Gedanensis](https://pgjug.pl/) (Technical University of Gdańsk) and at [Goyello](http://goyello.com).

## Lambda Expressions

### Syntax

The most common example:

```java
Runnable runnable = () -> System.out.println("Hello!");
Thread t = new Thread(runnable);
t.start();
t.join();
```

One can write this differently:

```java
Thread t = new Thread(() -> System.out.println("Hello!"));
t.start();
t.join();
```

What about arguments?

```java
Comparator<String> stringComparator = (s1, s2) -> s1.compareTo(s2);
```

And expanding to full expression:

```java
Comparator<String> stringComparator = (String s1, String s2) -> {
    System.out.println("Comparing...");
    return s1.compareTo(s2);
};
```

### Functional interface

Lambda expressions let you express instances of single-method classes more compactly. Single-method classes are called functional interfaces and **can** be annotated with `@FunctionalInterface`:

```java
@FunctionalInterface
public interface MyFunctionalInterface<T> {
    boolean test(T t);
} 

// Usage
MyFunctionalInterface<String> l = s -> s.startsWith("A");
```

### Method references

Method references are compact, easy-to-read lambda expressions for methods that already have a name. Let’s look at this simple example:

```java
public class Sample {

    public static void main(String[] args) {
       Runnable runnable = Sample::run;
    }

    private static void run() {
        System.out.println("Hello!");
    }
}
```

Another example:

```java
public static void main(String[] args) {
    Sample sample = new Sample();
    Comparator<String> stringLengthComparator = sample::compareLength;
}

private int compareLength(String s1, String s2) {
    return s1.length() - s2.length();
}
```

## Stream API - basics

A stream is a sequence of elements supporting sequential and parallel bulk operations.

### Iterating over a list

```java
List<String> list = Arrays.asList("one", "two", "three", "four", "five", "six");

list.stream()
        .forEach(s -> System.out.println(s));
```

### Filtering

Java 8 introduced default methods in interfaces. They are handy in Stream API:

```java
Predicate<String> lowerThanOrEqualToFour = s -> s.length() <= 4;
Predicate<String> greaterThanOrEqualToThree = s -> s.length() >= 3;

list.stream()
        .filter(lowerThanOrEqualToFour.and(greaterThanOrEqualToThree))
        .forEach(s -> System.out.println(s));
```

### Sorting

```java
Predicate<String> lowerThanOrEqualToFour = s -> s.length() <= 4;
Predicate<String> greaterThanOrEqualToThree = s -> s.length() >= 3;
Comparator<String> byLastLetter = (s1, s2) -> s1.charAt(s1.length() - 1) - s2.charAt(s2.length() - 1);
Comparator<String> byLength = (s1, s2) -> s1.length() - s2.length();

list.stream()
        .filter(lowerThanOrEqualToFour.and(greaterThanOrEqualToThree))
        .sorted(byLastLetter.thenComparing(byLength))
        .forEach(s -> System.out.println(s));
```

In the above example a default method `and` of `java.util.function.Predicate` is used. Default (and static) methods are new to interfaces in Java 8.

### Limit

```java
Predicate<String> lowerThanOrEqualToFour = s -> s.length() <= 4;
Predicate<String> greaterThanOrEqualToThree = s -> s.length() >= 3;
Comparator<String> byLastLetter = (s1, s2) -> s1.charAt(s1.length() - 1) - s2.charAt(s2.length() - 1);
Comparator<String> byLength = (s1, s2) -> s1.length() - s2.length();

list.stream()
        .filter(lowerThanOrEqualToFour.and(greaterThanOrEqualToThree))
        .sorted(byLastLetter.thenComparing(byLength))
        .limit(4)
        .forEach(s -> System.out.println(s));
```

### Collect to a list

```java
Predicate<String> lowerThanOrEqualToFour = s -> s.length() <= 4;
Predicate<String> greaterThanOrEqualToThree = s -> s.length() >= 3;
Comparator<String> byLastLetter = (s1, s2) -> s1.charAt(s1.length() - 1) - s2.charAt(s2.length() - 1);
Comparator<String> byLength = (s1, s2) -> s1.length() - s2.length();

List<String> result = list.stream()
        .filter(lowerThanOrEqualToFour.and(greaterThanOrEqualToThree))
        .sorted(byLastLetter.thenComparing(byLength))
        .limit(4)
        .collect(Collectors.toList());
```

## Parallel processing

I used quite common example with iterating over a list of files:

```java
public static void main(String[] args) {
    File[] files = new File("c:/windows").listFiles();
    Stream.of(files)
            .parallel()
            .forEach(Sample::process);
}

private static void process(File file) {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
    }

    System.out.println("Processing -> " + file);
}
```

Please note that while showing the examples I explained some known drawbacks with parallel processing of streams.

## Stream API - more examples

### Mapping

Iterate over files in a directory and return a `FileSize` object:

```java
class FileSize {

    private final File file;
    private final Long size;

    FileSize(File file, Long size) {
        this.file = file;
        this.size = size;
    }

    File getFile() {
        return file;
    }

    Long getSize() {
        return size;
    }

    String getName() {
        return getFile().getName();
    }

    String getFirstLetter() {
        return getName().substring(0, 1);
    }

    @Override
    public String toString() {
        return Objects.toStringHelper(this)
                .add("file", file)
                .add("size", size)
                .toString();
    }
}
```

The final code of a mapping:

```java
File[] files = new File("c:/windows").listFiles();
List<FileSize> result = Stream.of(files)
        .map(FileSize::new)
        .collect(Collectors.toList());
```

### Grouping

Group `FileSize` object by first letter of a file name:

```java
Map<String, List<FileSize>> result = Stream.of(files)
        .map(FileSize::new)
        .collect(Collectors.groupingBy(FileSize::getFirstLetter));
```

### Reduce

Get the biggest/smallest file in a directory:

```java
Optional<FileSize> filesize = Stream.of(files)
        .map(FileSize::new)
        .reduce((fs1, fs2) -> fs1.getSize() > fs2.getSize() ? fs1 : fs2);
```

In case you don’t need a `FileSize` object, but only a number:

```java
OptionalLong max = Stream.of(files)
        .map(FileSize::new)
        .mapToLong(fs -> fs.getSize())
        .max();
```
