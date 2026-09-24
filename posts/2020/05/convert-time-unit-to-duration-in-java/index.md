---
title: "Convert time unit to duration in Java"
date: 2020-05-16T17:30:00.000+02:00
updated: 2020-05-16T17:30:30.444+02:00
author: "Rafał Borowiec"
tags: ["java", "java 9 and beyond"]
original_url: https://blog.codeleak.pl/2020/05/convert-time-unit-to-duration-in-java.html
---

# Convert time unit to duration in Java

`java.util.concurrent.TimeUnit` represents time durations in Java at a given unit of granularity and provides utility methods to convert across units. `java.util.concurrent.TimeUnit` was introduced back in the old Java days (1.5) but since then it has been extended several times already. In this blog post you will learn how to use `java.util.concurrent.TimeUnit` to convert a given *time unit* to a *duration* .

# Prerequisites

You will need JDK 11+ for the examples to work.

> Learn how to [manage multiple Java SDKs with SDKMAN! with ease](../../../2020/01/manage-multiple-java-sdks-with-sdkman/index.md)

# Problem

Convert a given time unit to duration in Java

# Solution

Use `java.concurrent.TimeUnit` enum.

## Java 11

- `TimeUnit.convert(Duration duration)`:

```java
long yearInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofDays(365));
long hourInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofHours(1));
long minuteInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofMinutes(1));
```

- `TimeUnit.convert(Duration duration)` with `java.time.ChronoUnit`:

```java
long yearInMillis = TimeUnit.MILLISECONDS.convert(Duration.of(365, TimeUnit.DAYS.toChronoUnit()));
long hourInMillis = TimeUnit.MILLISECONDS.convert(Duration.of(1, TimeUnit.HOURS.toChronoUnit()));
long minuteInMillis = TimeUnit.MILLISECONDS.convert(Duration.of(1, TimeUnit.MINUTES.toChronoUnit()));
```

## Pre-Java 11

- Generic `TimeUnit.convert(long sourceDuration, TimeUnit sourceUnit)`

```java
long yearInMillis = TimeUnit.DAYS.toMillis(365);
long hourInMillis = TimeUnit.HOURS.toMillis(1);
long minuteInMillis = TimeUnit.MINUTES.toMillis(1);
```

- `TimeUnit.toMillis(long duration)`, `TimeUnit.toSeconds(long duration)` etc. methods:

```java
long yearInMillis = TimeUnit.MILLISECONDS.convert(365, TimeUnit.DAYS);
long hourInMillis = TimeUnit.MILLISECONDS.convert(1, TimeUnit.HOURS);
long minuteInMillis = TimeUnit.MILLISECONDS.convert(1, TimeUnit.MINUTES);
```

## Final example

```java
class Java11TimeUnitConvertTests {

    public static final long DAYS_IN_A_YEAR = 365L;
    public static final long HOURS_IN_A_DAY = 24L;
    public static final long MINUTES_IN_AN_HOUR = 60L;
    public static final long SECONDS_IN_A_MINUTE = 60L;
    public static final long MILLISECONDS_IN_A_SECOND = 1000L;
    @Test
    void aYearInMillis() {

        // A year in milliseconds
        long yearInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofDays(365)); // since Java 11

        assertThat(yearInMillis)
                .isEqualTo(DAYS_IN_A_YEAR * HOURS_IN_A_DAY * MINUTES_IN_AN_HOUR * SECONDS_IN_A_MINUTE * MILLISECONDS_IN_A_SECOND)
                .isEqualTo(TimeUnit.DAYS.toMillis(365))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(365, TimeUnit.DAYS))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(Duration.of(365, TimeUnit.DAYS.toChronoUnit()))); // since Java 11

    }

    @Test
    void anHourInMillis() {

        long hourInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofHours(1)); // since Java 11
        
        assertThat(hourInMillis)
                .isEqualTo(MINUTES_IN_AN_HOUR * SECONDS_IN_A_MINUTE * MILLISECONDS_IN_A_SECOND)
                .isEqualTo(TimeUnit.HOURS.toMillis(1))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(1, TimeUnit.HOURS))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(Duration.of(1, TimeUnit.HOURS.toChronoUnit()))); // since Java 11
    }

    @Test
    void aMinuteInMillis() {
        
        long minuteInMillis = TimeUnit.MILLISECONDS.convert(Duration.ofMinutes(1)); // since Java 11
        
        assertThat(minuteInMillis)
                .isEqualTo(SECONDS_IN_A_MINUTE * MILLISECONDS_IN_A_SECOND)
                .isEqualTo(TimeUnit.MINUTES.toMillis(1))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(1, TimeUnit.MINUTES))
                .isEqualTo(TimeUnit.MILLISECONDS.convert(Duration.of(1, TimeUnit.MINUTES.toChronoUnit()))); // since Java 11
    }

    @ParameterizedTest
    @MethodSource("timeUnitToDuration")
    void convertTimeUnitToDuration(TimeUnit unit, Duration duration, long expectedResult) {
        long actualResult = unit.convert(duration);

        assertThat(actualResult).isEqualTo(expectedResult);
    }

    private static Stream<Arguments> timeUnitToDuration() {
        return Stream.of(
                Arguments.of(TimeUnit.DAYS, Duration.ofHours(24), 1), // 24h = 1d
                Arguments.of(TimeUnit.DAYS, Duration.ofHours(40), 1), // 40h = 1d
                Arguments.of(TimeUnit.DAYS, Duration.ofHours(48), 2), // 48h = 2d
                Arguments.of(TimeUnit.DAYS, Duration.ofHours(50), 2),  // 50h = 2d
                Arguments.of(TimeUnit.MILLISECONDS, Duration.ofSeconds(1), 1000),  // 1s = 1000ms
                Arguments.of(TimeUnit.MILLISECONDS, Duration.ofSeconds(11), 11000),  // 1s = 11000ms
                Arguments.of(TimeUnit.SECONDS, Duration.ofHours(1), 3600),  // 1h = 3600s
                Arguments.of(TimeUnit.HOURS, Duration.ofSeconds(4_000), 1),  // 4000s = 1h
                Arguments.of(TimeUnit.HOURS, Duration.ofSeconds(1_0000), 2)  // 10000s = 2h
        );
    }
}
```

## Source code

The source code for this article can be found on Github: <https://github.com/kolorobot/java9-and-beyond>
