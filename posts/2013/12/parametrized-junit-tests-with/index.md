---
title: "Parametrized JUnit tests with JUnitParams"
date: 2013-12-19T22:51:00.000+01:00
updated: 2016-06-13T23:44:06.804+02:00
author: "Rafał Borowiec"
tags: ["unit testing"]
original_url: https://blog.codeleak.pl/2013/12/parametrized-junit-tests-with.html
---

# Parametrized JUnit tests with JUnitParams

![](junit.gif)

Parameterized unit tests are used to to test the same code under different conditions. Thanks to parameterized unit tests we can set up a test method that retrieves data from some data source. This data source can be a collection of test data objects, external file or maybe even a database. The general idea is to make it easy to test different conditions with the same unit test method, which will limit the source code we need to write and makes the test code more robust. We can call these tests data-driven unit tests.

The best way to achieve data-driven unit tests in JUnit is to use a JUnit's custom runner - `Parameterized` or [JUnitParams'](https://code.google.com/p/junitparams/) `JUnitParamsRunner`. Using JUnit's approach may work in many cases, but the latter seems to be more easy to use and more powerfull.

### *Change Log*

- 13/06/2016 - JUnitParams 1.0.5 released. The utility method *$* deprecated. I updated the Github repository (unit-testing-demo). See the link on the bottom of this article.

### Basic example

In our example, a poker dice, we need to calculate the score of a full house. As in card poker, a Full House is a roll where you have both a 3 of a kind, and a pair. For the sake of simplicity, the score is a sum of all dice in a roll. So let's see the code:

```java
class FullHouse implements Scoreable {

    @Override
    public Score getScore(Collection<Dice> dice) {
        Score pairScore = Scorables.pair().getScore(dice);
        Score threeOfAKindScore = Scorables.threeOfAKind().getScore(pairScore.getReminder());
        if (bothAreGreaterThanZero(pairScore.getValue(), threeOfAKindScore.getValue())) {
            return new Score(pairScore.getValue() + threeOfAKindScore.getValue()); // no reminder
        }
        return new Score(0, dice);
    }

    private boolean bothAreGreaterThanZero(int value1, int value2) {
        return value1 > 0 && value2 > 0;
    }
}
```

I would like to be sure that the roll is properly scored (of course I have unit tests for both Pair and ThreeOfAKind already). So I would like to test the following conditions:

- Score is 11 for: 1, 1, 3, 3, 3
- Score is 8 for: 2, 2, 2, 1, 1
- Score is 0 for: 2, 3, 4, 1, 1
- Score is 25 for: 5, 5, 5, 5, 5

Let's investigate two possible ways of writing data-driven test for that method. Firstly, **JUnit's Parameterized**:

```java
@RunWith(Parameterized.class)
public class FullHouseTest {

    private Collection<Dice> rolled;
    private int score;

    public FullHouseTest(Collection<Dice> rolled, int score) {
        this.rolled = rolled;
        this.score = score;
    }

    @Test
    public void fullHouse() {
        assertThat(new FullHouse().getScore(rolled).getValue()).isEqualTo(score);
    }

    @Parameterized.Parameters
    public static Iterable<Object[]> data() {
        return Arrays.asList(
                new Object[][]{
                        {roll(1, 1, 3, 3, 3), score(11)},
                        {roll(2, 2, 2, 1, 1), score(8)},
                        {roll(2, 3, 4, 1, 1), score(0)},
                        {roll(5, 5, 5, 5, 5), score(25)}
                }
        );
    }

    private static int score(int score) {
        return score;
    }
}
```

And the other one, with **JUnitParams**:

```java
@RunWith(JUnitParamsRunner.class)
public class FullHouseTest {

    @Test
    @Parameters
    public void fullHouse(Collection<Dice> rolled, int score) {
        assertThat(new FullHouse().getScore(rolled).getValue()).isEqualTo(score);
    }

    public Object[] parametersForFullHouse() {
        return $(
                $(roll(1, 1, 3, 3, 3), score(11)),
                $(roll(2, 2, 2, 1, 1), score(8)),
                $(roll(2, 3, 4, 1, 1), score(0)),
                $(roll(5, 5, 5, 5, 5), score(25))
        );
    }

    private static int score(int score) {
        return score;
    }
}
```

At first glance, both look very similar. And that's true. So what are the differences between JUnit `Parameterized` (1) and JUnitParams (2)? The most important one is the way of passing the parameters, so in fact the architecture of the solution. In (1) parameters are passed in constructor whereas in (2) parameters are passed directly to test method. Should I care? Yes. One of the reason is, in (2), we can have multiple parameterized tests methods with different data for each of the method, like in the below example:

```java
@RunWith(JUnitParamsRunner.class)
public class NumberOfAKindTest {

    @Test
    @Parameters
    public void pair(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(2);
        doTest(rolled, expected, score, sut);
    }

    @Test
    @Parameters
    public void threeOfAKind(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(3);
        doTest(rolled, expected, score, sut);
    }

    public Object[] parametersForPair() {
        return $(
                $(roll(1, 1, 1, 2, 3), hand(1, 1), score(2)),
                $(roll(2, 1, 1, 1, 1), hand(1, 1), score(2)),
                $(roll(2, 3, 4, 1, 1), hand(1, 1), score(2)),
                $(roll(2, 3, 5, 5, 5), hand(5, 5), score(10)),
                $(roll(2, 1, 5, 4, 3), null, score(0))
        );
    }

    public Object[] parametersForThreeOfAKind() {
        return $(
                $(roll(1, 1, 1, 2, 3), hand(1, 1, 1), score(3)),
                $(roll(2, 1, 1, 1, 3), hand(1, 1, 1), score(3)),
                $(roll(2, 3, 1, 1, 1), hand(1, 1, 1), score(3)),
                $(roll(2, 3, 5, 5, 5), hand(5, 5, 5), score(15)),
                $(roll(2, 5, 5, 5, 6), hand(5, 5, 5), score(15)),
                $(roll(2, 2, 5, 5, 3), null, score(0))
        );
    }

    private static int[] hand(int... dice) {
        return dice;
    }

    private static int score(int score) {
        return score;
    }

}
```

In simpler examples, parameters can be defined as a String array directly in @Parameters annotation via value method. We can also extract the data to an external class and have our tests more clean and readable. The complete test for `NumberOfAKind` reads as following:

```java
@RunWith(JUnitParamsRunner.class)
public class NumberOfAKindTest {

    @Test
    @Parameters(source = NumberOfAKindProvider.class, method = "providePair")
    public void pair(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(2);
        doTest(rolled, expected, score, sut);
    }

    @Test
    @Parameters(source = NumberOfAKindProvider.class, method = "provideThreeOfAKind")
    public void threeOfAKind(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(3);
        doTest(rolled, expected, score, sut);
    }

    @Test
    @Parameters(source = NumberOfAKindProvider.class, method = "provideFourOfAKind")
    public void fourOfAKind(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(4);
        doTest(rolled, expected, score, sut);
    }

    @Test
    @Parameters(source = NumberOfAKindProvider.class, method = "provideFiveOfAKind")
    public void fiveOfAKind(Collection<Dice> rolled, int[] expected, int score) {
        NumberOfAKind sut = new NumberOfAKind(5);
        doTest(rolled, expected, score, sut);
    }

    private void doTest(Collection<Dice> rolled, int[] expected, int score, NumberOfAKind sut) {
        Collection<Dice> consecutiveDice = sut.getConsecutiveDice(rolled);

        assertDiceContainsValues(consecutiveDice, expected);
        assertThat(sut.getScore(rolled).getValue()).isEqualTo(score);
    }

    private void assertDiceContainsValues(Collection<Dice> dice, int[] expected) {
        Collection<Integer> values = toInts(dice);
        if (expected == null) {
            assertThat(values).isEmpty();
            return;
        }
        for (int i = 0; i < expected.length; i++) {
            assertThat(values).hasSize(expected.length).contains(expected[i]);
        }
    }

    private Collection<Integer> toInts(Collection<Dice> dice) {
        return Collections2.transform(dice, new Function<Dice, Integer>() {
            @Override
            public Integer apply(Dice input) {
                return input.getValue();
            }
        });
    }

}
```

Each method specifies a provider class and the provider's method name. Look at the provider below:

```java
public class NumberOfAKindProvider {

    public static Object[] providePair() {
        return $(
                $(roll(1, 1, 1, 2, 3), hand(1, 1), score(2)),
                $(roll(2, 1, 1, 1, 1), hand(1, 1), score(2)),
                $(roll(2, 3, 4, 1, 1), hand(1, 1), score(2)),
                $(roll(2, 3, 5, 5, 5), hand(5, 5), score(10)),
                $(roll(2, 1, 5, 4, 3), null, score(0))
        );
    }

    public static Object[] provideThreeOfAKind() {
        return $(
                $(roll(1, 1, 1, 2, 3), hand(1, 1, 1), score(3)),
                $(roll(2, 1, 1, 1, 3), hand(1, 1, 1), score(3)),
                $(roll(2, 3, 1, 1, 1), hand(1, 1, 1), score(3)),
                $(roll(2, 3, 5, 5, 5), hand(5, 5, 5), score(15)),
                $(roll(2, 5, 5, 5, 6), hand(5, 5, 5), score(15)),
                $(roll(2, 2, 5, 5, 3), null, score(0))
        );
    }

    public static Object[] provideFourOfAKind() {
        return $(
                $(roll(1, 1, 1, 1, 3), hand(1, 1, 1, 1), score(4)),
                $(roll(2, 1, 1, 1, 1), hand(1, 1, 1, 1), score(4)),
                $(roll(2, 5, 5, 5, 5), hand(5, 5, 5, 5), score(20)),
                $(roll(2, 3, 4, 5, 5), null, score(0))
        );
    }

    public static Object[] provideFiveOfAKind() {
        return $(
                $(roll(1, 1, 1, 1, 1), hand(1, 1, 1, 1, 1), score(5)),
                $(roll(6, 6, 6, 6, 6), hand(6, 6, 6, 6, 6), score(30)),
                $(roll(6, 6, 6, 6), null, score(0)),
                $(roll(2, 3, 4, 6, 6), null, score(0))
        );
    }

    private static int[] hand(int... dice) {
        return dice;
    }

    private static int score(int score) {
        return score;
    }
}
```

### Summary

To me `JUnitParams` is a better solution for writing good data-driven unit tests. But what is presented above, is not everything the library has to offer to a developer. There are more features. Params can be passed as a CSV string, we can mix both parameterized and non-parameterized tests just to mention a few.

Please visit the project's website to find out more about this library: <https://github.com/Pragmatists/junitparams>

Looking for simpler example? Check out this post: [Unit testing exercise with FizzBuzz and JUnitParams](../../../2014/11/unit-testing-excercise-with-fizzbuzz/index.md). Please also have a look at unit-testing-demo project presenting different aspects of unit testing, including parametrized tests: [https://github.com/kolorobot/unit-testing-demo](https://github.com/kolorobot/unit-testing-demo )
