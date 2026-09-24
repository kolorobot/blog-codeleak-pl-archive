---
title: "Testing exceptions in JavaScript with Jest"
date: 2021-11-19T10:55:00.019+01:00
updated: 2021-11-19T20:48:01.635+01:00
author: "Rafał Borowiec"
tags: ["javascript", "jest", "testing", "unit testing"]
original_url: https://blog.codeleak.pl/2021/11/testing-exceptions-in-javascript.html
---

# Testing exceptions in JavaScript with Jest

## The code

Let’s consider a simple function that checks for equality of two passwords, and it throws an error when the first one is not provided:

```javascript
export default function samePasswordsValidator(password, otherPassword) {
    if (!password) {
        throw new Error("no password given");
    }
    return password === otherPassword;
}
```

## Try-catch idiom (bad)

When testing the code that throws exceptions, one immediately comes up with the idea of using the `try-catch` idiom in the test code:

```javascript
it('throws an error when first argument is `null`', () => {
    try {
        samePasswordsValidator(null, "bar");
    } catch (error) {
        expect(error.message).toBe("no password given");
    }
});
```

Generally speaking, this is not the best approach. The test passes when the first argument is `null` as expected. But when the code is about to change and the exception won’t be thrown anymore the test still passes. So, the code change won’t be detected by the test.

## Try-catch idiom (better)

To overcome that issue, one could expect that actual assertion will be executed and fail the test if it does not happen. This can be done pretty easily with `expect.assertions` which verifies that a certain number of assertions are called during a test:

```javascript
it('throws an error when first argument is `null`', () => {
    expect.assertions(1);
    try {
        samePasswordsValidator(null, "bar");
    } catch (error) {
        expect(error.message).toBe("no password given");
    }
});
```

Now, when no exception is thrown, the test fails:

```
Error: expect.assertions(1)

Expected one assertion to be called but received zero assertion calls.
```

## `toThrow` assertions (best)

To make the code even more expressive a built-in `toThrow` matcher can be used:

```javascript
it('throws an error when first argument is `null`', () => {
    expect(() => samePasswordsValidator(null, "bar")).toThrow("no password given");
});
```

And again, when no exception is thrown, Jest informs us clearly about it with a failed test:

```
Error: expect(received).toThrow(expected)

Expected substring: "no password given"

Received function did not throw
```

Note that `toThrow` matcher can be used to not only check the error message, but also the exact type of the error:

```javascript
it('throws an error when first argument is `null`', () => {
    expect(() => samePasswordsValidator(null, "bar")).toThrow(Error);
    expect(() => samePasswordsValidator(null, "bar")).toThrow(new Error("no password given"));
});
```

## See also

- [Testing promise rejection in JavaScript with Jest](../../../2021/11/testing-promise-rejection-with-jest/index.md)
- [Jest Vanilla JS Starter](https://github.com/kolorobot/jest-js-starter)
- [Different ways of handling exceptions in JUnit. Which one to choose?](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)
