---
title: "Parameterized tests in JavaScript with Jest"
date: 2021-12-05T14:01:00.006+01:00
updated: 2021-12-06T08:54:08.261+01:00
author: "Rafał Borowiec"
tags: ["javascript", "jest", "unit testing"]
original_url: https://blog.codeleak.pl/2021/12/parameterized-tests-with-jest.html
---

# Parameterized tests in JavaScript with Jest

*Parameterized* tests are used to test the same code under different conditions. One can set up a test method that retrieves data from a data source. This data source can be a collection of objects, external file or maybe even a database. The general idea is to make it easy to test different conditions with the same test method to avoid duplication and make the code easier to read and maintain.

`Jest` has a built-in support for tests parameterized with data table that can be provided either by an *array of arrays* or as *tagged template literal*.

*Table of Contents*

- [The code](#the-code)
- [Parameterized (*data-driven*) tests in `jest`](#parameterized-data-driven-tests-in-jest)
  - [`test.each(table)(name, fn)`](#testeachtablename-fn)
  - [`` test.each`table`(name, fn) ``](#testeachtablename-fn-1)
  - [Ultimate parameterized test for the `Calculator`](#ultimate-parameterized-test-for-the-calculator)
- [In review](#in-review)
- [See also](#see-also)

# The code

Let’s consider a simple `Calculator` fn that accepts an operator and the numbers array:

```typescript
type Operator = '+' | '-' | '*' | '/';

export default function calculator(operator: Operator, inputs: number[]) {

    if (inputs.length < 2) {
        throw new Error(`inputs should have length >= 2`);
    }

    switch (operator) {
        case '+':
            return inputs.reduce((prev, curr) => prev + curr);
        case '-':
            return inputs.reduce((prev, curr) => prev - curr);
        case '*':
            return inputs.reduce((prev, curr) => prev * curr);
        case '/':
            return inputs.reduce((prev, curr) => prev / curr);
        default:
            throw new Error(`Unknown operator ${operator}`);
    }
}
```

The `Calculator` can be tested using the following scenarios:

```typescript
import calculator from './calculator';

describe('Calculator', () => {
    it('throws error when input.length < 2', () => {
        expect(() => calculator('+', [0])).toThrow('inputs should have length >= 2');
    });

    it('throws error when unsupported operator was used', () => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        expect(() => calculator('&', [0, 0])).toThrow('unknown operator &');
    });

    it('adds 2 or more numbers incl. `NaN` and `Infinity`', () => {
        expect(calculator('+', [1, 41])).toEqual(42);
        expect(calculator('+', [1, 2, 39])).toEqual(42);
        expect(calculator('+', [1, 2, NaN])).toEqual(NaN);
        expect(calculator('+', [1, 2, Infinity])).toEqual(Infinity);
    });

    it('subtracts 2 or more numbers incl. `NaN` and `Infinity`', () => {
        expect(calculator('-', [43, 1])).toEqual(42);
        expect(calculator('-', [44, 1, 1])).toEqual(42);
        expect(calculator('-', [1, 2, NaN])).toEqual(NaN);
        expect(calculator('-', [1, 2, Infinity])).toEqual(-Infinity);
    });

    it('multiplies 2 or more numbers incl. `NaN` and `Infinity`', () => {
        expect(calculator('*', [21, 2])).toEqual(42);
        expect(calculator('*', [3, 7, 2])).toEqual(42);
        expect(calculator('*', [42, NaN])).toEqual(NaN);
        expect(calculator('*', [42, Infinity])).toEqual(Infinity);
    });

    it('divides 2 or more numbers incl. `NaN` and `Infinity`', () => {
        expect(calculator('/', [84, 2])).toEqual(42);
        expect(calculator('/', [42, 0])).toEqual(Infinity);
        expect(calculator('/', [42, NaN])).toEqual(NaN);
        expect(calculator('/', [168, 2, 2])).toEqual(42);
    });
});
```

The most important scenarios are focused on the `Calculator` main features (*add*, *subtract*, *multiple* and *divide*) and each of the features is tested with differect set of data values. These tests could be *parameterized* as they are duplicating the same test logic with different data.

# Parameterized (*data-driven*) tests in `jest`

In `Jest`, paramaterized tests can be created with `.each` that come with the APIs: `.each(table)(name, fn)` and `` .each`table`(name, fn) `` where the difference is how the test data is provided.

## `test.each(table)(name, fn)`

In this example, data is provided as an *array of arrays* with the arguments that are injected into the test function for each row. Unique test names are created by positioinally injecting parameters:

```typescript
import calculator from './calculator';

describe('Calculator', () => {
    it.each([
        [[1, 41], 42],
        [[1, 2, 39], 42],
        [[1, 2, NaN], NaN],
        [[1, 2, Infinity], Infinity],
    ])('adds %p expecting %p', (numbers: number[], result: number) => {
        expect(calculator('+', numbers)).toEqual(result);
    });

    it.each([
        [[43, 1], 42],
        [[44, 1, 1], 42],
        [[1, 2, NaN], NaN],
        [[1, 2, Infinity], -Infinity],
    ])('subtracts %p expecting %p', (numbers: number[], result: number) => {
        expect(calculator('-', numbers)).toEqual(result);
    });

    it.each([
        [[21, 2], 42],
        [[3, 7, 2], 42],
        [[42, NaN], NaN],
        [[42, Infinity], Infinity],
    ])('multiplies %p expecting %p', (numbers: number[], result: number) => {
        expect(calculator('*', numbers)).toEqual(result);
    });

    it.each([
        [[84, 2], 42],
        [[168, 2, 2], 42],
        [[168, 2, 2], 42],
        [[42, 0], Infinity],
        [[42, NaN], NaN],
    ])('divides %p expecting %p', (numbers: number[], result: number) => {
        expect(calculator('/', numbers)).toEqual(result);
    });
});
```

Please note that in a *parameterized* test, each data table row creates a new test that has exactly the same lifecylce as the regular test created with the test clousure. For this example, there are **16** tests (**4** tests and *each* with **4** sets of data values):

```
 PASS  src/parameterized/calculatorParameterized1.test.ts
  Calculator
    ✓ adds [1, 41] expecting 42 (2 ms)
    ✓ adds [1, 2, 39] expecting 42
    ✓ adds [1, 2, NaN] expecting NaN
    ✓ adds [1, 2, Infinity] expecting Infinity
    ✓ subtracts [43, 1] expecting 42
    ✓ subtracts [44, 1, 1] expecting 42
    ✓ subtracts [1, 2, NaN] expecting NaN
    ✓ subtracts [1, 2, Infinity] expecting -Infinity
    ✓ multiplies [21, 2] expecting 42 (1 ms)
    ✓ multiplies [3, 7, 2] expecting 42 (1 ms)
    ✓ multiplies [42, NaN] expecting NaN
    ✓ multiplies [42, Infinity] expecting Infinity (1 ms)
    ✓ divides [84, 2] expecting 42
    ✓ divides [168, 2, 2] expecting 42
    ✓ divides [168, 2, 2] expecting 42
    ✓ divides [42, 0] expecting Infinity
    ✓ divides [42, NaN] expecting NaN (1 ms)

Test Suites: 1 passed, 1 total
Tests:       17 passed, 17 total
Snapshots:   0 total
Time:        2.361 s, estimated 3 s
Ran all test suites matching /src\/parameterized\/calculatorParameterized1.test.ts/i.
✨  Done in 3.55s.
```

In case of a failure you may expect only failed tests are reported, like in the example below:

```
 FAIL  src/parameterized/calculatorParameterized1.test.ts
  Calculator
    ✓ adds [1, 41] expecting 42 (1 ms)
    ✓ adds [1, 2, 39] expecting 42 (3 ms)
    ✕ adds [1, 2, NaN] expecting Infinity (1 ms)
    ✓ adds [1, 2, Infinity] expecting Infinity
    ✓ subtracts [43, 1] expecting 42 (1 ms)
    ✓ subtracts [44, 1, 1] expecting 42
    ✓ subtracts [1, 2, NaN] expecting NaN (1 ms)
    ✓ subtracts [1, 2, Infinity] expecting -Infinity
    ✓ multiplies [21, 2] expecting 42
    ✓ multiplies [3, 7, 2] expecting 42
    ✓ multiplies [42, NaN] expecting NaN
    ✓ multiplies [42, Infinity] expecting Infinity
    ✓ divides [84, 2] expecting 42 (1 ms)
    ✓ divides [168, 2, 2] expecting 42
    ✓ divides [168, 2, 2] expecting 42
    ✓ divides [42, 0] expecting Infinity
    ✕ divides [42, NaN] expecting Infinity (1 ms)

  ● Calculator › adds [1, 2, NaN] expecting Infinity

    expect(received).toEqual(expected) // deep equality

    Expected: Infinity
    Received: NaN

       8 |         [[1, 2, Infinity], Infinity],
       9 |     ])('adds %p expecting %p', (numbers: number[], result: number) => {
    > 10 |         expect(calculator('+', numbers)).toEqual(result);
         |                                          ^
      11 |     });
      12 |
      13 |     it.each([

      at src/parameterized/calculatorParameterized1.test.ts:10:42

  ● Calculator › divides [42, NaN] expecting Infinity

    expect(received).toEqual(expected) // deep equality

    Expected: Infinity
    Received: NaN

      36 |         [[42, NaN], Infinity],
      37 |     ])('divides %p expecting %p', (numbers: number[], result: number) => {
    > 38 |         expect(calculator('/', numbers)).toEqual(result);
         |                                          ^
      39 |     });
      40 | });
      41 |

      at src/parameterized/calculatorParameterized1.test.ts:38:42

Test Suites: 1 failed, 1 total
Tests:       2 failed, 15 passed, 17 total
Snapshots:   0 total
Time:        2.493 s, estimated 3 s
```

## `` test.each`table`(name, fn) ``

In this example, data is provided with *template literal*, where the first row represents name of variables and the subsequent rows provide test data object injected into the test function for each row. The unique test names are created by injecting parameters by their name.

```typescript
import calculator from './calculator';

describe('Calculator', () => {
    it.each`
    numbers             | result
    ${[1, 41]}          | ${42} 
    ${[1, 2, 39]}       | ${42} 
    ${[1, 2, NaN]}      | ${NaN} 
    ${[1, 2, Infinity]} | ${Infinity}  
    `('adds $numbers expecting $result', ({ numbers, result }) => {
        expect(calculator('+', numbers)).toEqual(result);
    });

    it.each`
    numbers             | result
    ${[43, 1]}          | ${42} 
    ${[44, 1, 1]}       | ${42}
    ${[1, 2, NaN]}      | ${NaN} 
    ${[1, 2, Infinity]} | ${-Infinity} 
    `('subtracts $numbers expecting $result', ({ numbers, result }) => {
        expect(calculator('-', numbers)).toEqual(result);
    });

    it.each`
    numbers           | result
    ${[21, 2]}        | ${42} 
    ${[3, 7, 2]}      | ${42} 
    ${[42, NaN]}      | ${NaN}  
    ${[42, Infinity]} | ${Infinity}  
    `('multiples $numbers expecting $result', ({ numbers, result }) => {
        expect(calculator('*', numbers)).toEqual(result);
    });

    it.each`
    numbers        | result
    ${[84, 2]}     | ${42} 
    ${[168, 2, 2]} | ${42} 
    ${[42, 0]}     | ${Infinity}  
    ${[42, NaN]}   | ${NaN}  
    `('divides $numbers expecting $result', ({ numbers, result }) => {
        expect(calculator('/', numbers)).toEqual(result);
    });
});
```

In this example, also **16** tests were created:

```
 PASS  src/parameterized/calculatorParameterized2.test.ts
  Calculator
    ✓ adds [1, 41] expecting 42 (1 ms)
    ✓ adds [1, 2, 39] expecting 42
    ✓ adds [1, 2, NaN] expecting NaN (1 ms)
    ✓ adds [1, 2, Infinity] expecting Infinity
    ✓ subtracts [43, 1] expecting 42 (1 ms)
    ✓ subtracts [44, 1, 1] expecting 42
    ✓ subtracts [1, 2, NaN] expecting NaN
    ✓ subtracts [1, 2, Infinity] expecting -Infinity
    ✓ multiples [21, 2] expecting 42
    ✓ multiples [3, 7, 2] expecting 42 (1 ms)
    ✓ multiples [42, NaN] expecting NaN (1 ms)
    ✓ multiples [42, Infinity] expecting Infinity
    ✓ divides [84, 2] expecting 42 (1 ms)
    ✓ divides [168, 2, 2] expecting 42
    ✓ divides [42, 0] expecting Infinity
    ✓ divides [42, NaN] expecting NaN

Test Suites: 1 passed, 1 total
Tests:       16 passed, 16 total
Snapshots:   0 total
Time:        2.432 s, estimated 3 s
Ran all test suites matching /src\/parameterized\/calculatorParameterized2.test.ts/i.
✨  Done in 3.36s.
```

## Ultimate parameterized test for the `Calculator`

The previous example could be further improved by adding an additional test param: `operator` which in the end reduces the code repeatition:

```typescript
import calculator from './calculator';

describe('Calculator', () => {
    it.each`
    numbers             | operator | result
    ${[1, 41]}          | ${"+"}   | ${42} 
    ${[1, 2, 39]}       | ${"+"}   | ${42} 
    ${[1, 2, NaN]}      | ${"+"}   | ${NaN} 
    ${[1, 2, Infinity]} | ${"+"}   | ${Infinity}  
    ${[43, 1]}          | ${"-"}   | ${42} 
    ${[44, 1, 1]}       | ${"-"}   | ${42}
    ${[1, 2, NaN]}      | ${"-"}   | ${NaN} 
    ${[1, 2, Infinity]} | ${"-"}   | ${-Infinity} 
    ${[21, 2]}          | ${"*"}   | ${42} 
    ${[3, 7, 2]}        | ${"*"}   | ${42} 
    ${[42, NaN]}        | ${"*"}   | ${NaN}  
    ${[42, Infinity]}   | ${"*"}   | ${Infinity}
    ${[84, 2]}          | ${"/"}   | ${42} 
    ${[168, 2, 2]}      | ${"/"}   | ${42} 
    ${[42, 0]}          | ${"/"}   | ${Infinity}  
    ${[42, NaN]}        | ${"/"}   | ${NaN}    
    `('verifies "$operator" on $numbers expecting $result', ({ numbers, operator, result }) => {
        expect(calculator(operator, numbers)).toEqual(result);
    });
});
```

And the test run:

```
 PASS  src/parameterized/calculatorParameterized3.test.ts
  Calculator
    ✓ verifies "+" on [1, 41] expecting 42
    ✓ verifies "+" on [1, 2, 39] expecting 42
    ✓ verifies "+" on [1, 2, NaN] expecting NaN
    ✓ verifies "+" on [1, 2, Infinity] expecting Infinity
    ✓ verifies "-" on [43, 1] expecting 42
    ✓ verifies "-" on [44, 1, 1] expecting 42
    ✓ verifies "-" on [1, 2, NaN] expecting NaN
    ✓ verifies "-" on [1, 2, Infinity] expecting -Infinity
    ✓ verifies "*" on [21, 2] expecting 42
    ✓ verifies "*" on [3, 7, 2] expecting 42
    ✓ verifies "*" on [42, NaN] expecting NaN
    ✓ verifies "*" on [42, Infinity] expecting Infinity
    ✓ verifies "/" on [84, 2] expecting 42
    ✓ verifies "/" on [168, 2, 2] expecting 42
    ✓ verifies "/" on [42, 0] expecting Infinity
    ✓ verifies "/" on [42, NaN] expecting NaN

Test Suites: 1 passed, 1 total
Tests:       16 passed, 16 total
Snapshots:   0 total
Time:        2.463 s, estimated 3 s
✨  Done in 3.66s.
```

# In review

- Use *parameterized* tests when you duplicate test logic for different test data.
- Don’t overuse *parameterized* tests especially in slower ones like *integration* or *e2e*.
- Generate unique test names for better error messages and easier debugging of failed tests.
- Remember, that each data row creates a new test with a default test lifecycle.

# See also

- [Learn more about the `.each` APIs in the official documentation](https://jestjs.io/docs/api#testeachtablename-fn-timeout)
- [Testing exceptions in JavaScript with Jest](../../../2021/11/testing-exceptions-in-javascript/index.md)
- [Testing promise rejection in JavaScript with Jest](../../../2021/11/testing-promise-rejection-with-jest/index.md)
