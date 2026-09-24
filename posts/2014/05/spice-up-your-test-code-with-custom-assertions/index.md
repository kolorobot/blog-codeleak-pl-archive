---
title: "Spice up your test code with custom assertions"
date: 2014-05-22T20:48:00.003+02:00
updated: 2014-11-15T16:35:12.261+01:00
author: "Rafał Borowiec"
tags: ["assertj", "java", "unit testing"]
original_url: https://blog.codeleak.pl/2014/05/spice-up-your-test-code-with-custom-assertions.html
---

# Spice up your test code with custom assertions

Inspired by the [@tkaczanowski](https://twitter.com/tkaczanowski) talk during [GeeCON](2014.geecon.org) conference I decided to have a closer look at custom assertions with [AssertJ](https://github.com/joel-costigliola/assertj-core) library.

In my 'Dice' game I created a 'Chance' that is any combination of dice with the score calculated as a sum of all dice. This is relatively simple object:

```java
class Chance implements Scorable {

    @Override
    public Score getScore(Collection<Dice> dice) {
        int sum = dice.stream()
                .mapToInt(die -> die.getValue())
                .sum();
        return scoreBuilder(this)
                .withValue(sum)
                .withCombination(dice)
                .build();
    }
}

public interface Scorable {
    Score getScore(Collection<Dice> dice);
}
```

In my test I wanted to see how the score is calculated for different dice combination. I started with simple (and only one actually):

```java
public class ChanceTest {

    private Chance chance = new Chance();

    @Test
    @Parameters
    public void chance(Collection<Dice> rolled, int scoreValue) {
        // arrange
        Collection<Dice> rolled = dice(1, 1, 3, 3, 3);
        // act
        Score score = chance.getScore(rolled);
        // assert
        assertThat(actualScore.getScorable()).isNotNull();
        assertThat(actualScore.getValue()).isEqualTo(expectedScoreValue);
        assertThat(actualScore.getReminder()).isEmpty();
        assertThat(actualScore.getCombination()).isEqualTo(rolled);
    }

}
```

A single concept - score object - is validated in the test. To improve the readability and reusability of the score validation I will create a custom assertion. I would like my assertion is used like any other AssertJ assertion as follows:

```java
public class ChanceTest {

    private Chance chance = new Chance();

    @Test
    public void scoreIsSumOfAllDice() {
        Collection<Dice> rolled = dice(1, 1, 3, 3, 3);
        Score score = chance.getScore(rolled);

        ScoreAssertion.assertThat(score)
                .hasValue(11)
                .hasNoReminder()
                .hasCombination(rolled);
    }
}
```

In order to achieve that I need to create a `ScoreAssertion` class that extends from `org.assertj.core.api.AbstractAssert`. The class should have a public static factory method and all the needed verification methods. In the end, the implementation may look like the below one.

```java
class ScoreAssertion extends AbstractAssert<ScoreAssertion, Score> {

    protected ScoreAssertion(Score actual) {
        super(actual, ScoreAssertion.class);
    }

    public static ScoreAssertion assertThat(Score actual) {
        return new ScoreAssertion(actual);
    }

    public ScoreAssertion hasEmptyReminder() {
        isNotNull();
        if (!actual.getReminder().isEmpty()) {
            failWithMessage("Reminder is not empty");
        }
        return this;
    }

    public ScoreAssertion hasValue(int scoreValue) {
        isNotNull();
        if (actual.getValue() != scoreValue) {
            failWithMessage("Expected score to be <%s>, but was <%s>", 
                    scoreValue, actual.getValue());
        }
        return this;
    }

    public ScoreAssertion hasCombination(Collection<Dice> expected) {
        Assertions.assertThat(actual.getCombination())
                .containsExactly(expected.toArray(new Dice[0]));
        return this;
    }
}
```

The motivation of creating such an assertion is to have more readable and reusable code. But it comes with some price - more code needs to be created. In my example, I know I will create more `Scorables` quite soon and I will need to verify their scoring algorithm, so creating an additional code is justified. The gain will be visible. For example, I created a `NumberInARow` class that calculates the score for all consecutive numbers in a given dice combination. The score is a sum of all dice with the given value:

```java
class NumberInARow implements Scorable {

    private final int number;

    public NumberInARow(int number) {
        this.number = number;
    }

    @Override
    public Score getScore(Collection<Dice> dice) {

        Collection<Dice> combination = dice.stream()
                .filter(value -> value.getValue() == number)
                .collect(Collectors.toList());

        int scoreValue = combination
                .stream()
                .mapToInt(value -> value.getValue())
                .sum();

        Collection<Dice> reminder = dice.stream()
                .filter(value -> value.getValue() != number)
                .collect(Collectors.toList());

        return Score.scoreBuilder(this)
                .withValue(scoreValue)
                .withReminder(reminder)
                .withCombination(combination)
                .build();
    }
}
```

I started with the test that checks a two fives in a row and I already missed on assertion - `hasReminder` - so I improved the `ScoreAssertion`. I continued with changing the assertion with other tests until I got quite well shaped DSL I can use in my tests:

```java
public class NumberInARowTest {

    @Test
    public void twoFivesInARow() {
        NumberInARow numberInARow = new NumberInARow(5);
        Collection<Dice> dice = dice(1, 2, 3, 4, 5, 5);
        Score score = numberInARow.getScore(dice);
        
        // static import ScoreAssertion
        assertThat(score)
                .hasValue(10)
                .hasCombination(dice(5, 5))
                .hasReminder(dice(1, 2, 3, 4));
    }

    @Test
    public void noNumbersInARow() {
        NumberInARow numberInARow = new NumberInARow(5);
        Collection<Dice> dice = dice(1, 2, 3);
        Score score = numberInARow.getScore(dice);

        assertThat(score)
                .isZero()
                .hasReminder(dice(1, 2, 3));
    }
}

public class TwoPairsTest {

    @Test
    public void twoDistinctPairs() {
        TwoPairs twoPairs = new TwoPairs();
        Collection<Dice> dice = dice(2, 2, 3, 3, 1, 4);
        Score score = twoPairs.getScore(dice);

        assertThat(score)
                .hasValue(10)
                .hasCombination(dice(2, 2, 3, 3))
                .hasReminder(dice(1, 4));
    }
}
```

The assertion after changes looks as follows:

```java
class ScoreAssertion extends AbstractAssert<ScoreAssertion, Score> {

    protected ScoreAssertion(Score actual) {
        super(actual, ScoreAssertion.class);
    }

    public static ScoreAssertion assertThat(Score actual) {
        return new ScoreAssertion(actual);
    }

    public ScoreAssertion isZero() {
        hasValue(Score.ZERO);
        hasNoCombination();
        return this;
    }

    public ScoreAssertion hasValue(int scoreValue) {
        isNotNull();
        if (actual.getValue() != scoreValue) {
            failWithMessage("Expected score to be <%s>, but was <%s>",
                    scoreValue, actual.getValue());
        }
        return this;
    }

    public ScoreAssertion hasNoReminder() {
        isNotNull();
        if (!actual.getReminder().isEmpty()) {
            failWithMessage("Reminder is not empty");
        }
        return this;
    }

    public ScoreAssertion hasReminder(Collection<Dice> expected) {
        isNotNull();
        Assertions.assertThat(actual.getReminder())
                .containsExactly(expected.toArray(new Dice[0]));
        return this;
    }

    private ScoreAssertion hasNoCombination() {
        isNotNull();
        if (!actual.getCombination().isEmpty()) {
            failWithMessage("Combination is not empty");
        }
        return this;
    }

    public ScoreAssertion hasCombination(Collection<Dice> expected) {
        isNotNull();
        Assertions.assertThat(actual.getCombination())
                .containsExactly(expected.toArray(new Dice[0]));
        return this;
    }
}
```

I really like the idea of custom AssertJ assertions. They will improve the readability of my code in certain cases. On the other hand, I am pretty sure they cannot be used in all scenarios. Especially in those, where the chance of reusability is minimal. In such a case private methods with grouped assertions can be used.   
  

## References

- <https://github.com/joel-costigliola/assertj-core/wiki/Creating-specific-assertions>
- [The evolution of assertions via @tkaczanowski](https://twitter.com/kolorobot/status/466945515268345856)

## Source code

The source code for this article can be found in my general unit-testing-demo project at GitHub: <https://github.com/kolorobot/unit-testing-demo>.
