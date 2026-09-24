---
title: "Testing promise rejection in JavaScript with Jest"
date: 2021-11-19T20:42:00.004+01:00
updated: 2021-11-19T20:47:33.636+01:00
author: "Rafał Borowiec"
tags: ["javascript", "jest", "testing", "unit testing"]
original_url: https://blog.codeleak.pl/2021/11/testing-promise-rejection-with-jest.html
---

# Testing promise rejection in JavaScript with Jest

## The code

Let’s consider a simple function that returns a `Promise` that can either resolve or reject depending on the value of  
the first argument:

```javascript
export default function promiseMe(result, timeout = 1000) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (result instanceof Error || result.startsWith("Error")) {
                reject(result)
            } else {
                resolve(result)
            }
        }, timeout)
    })
}
```

While testing async code with Jest the only thing to remember is to return `Promise` from the test so that Jest can  
wait for it to resolve or to reject. The cleanest way is to do it with `.resolves` matcher:

```javascript
const successMessage = "Done.";

// with async/await
it("resolves (1)", async () => {
    await expect(promiseMe(successMessage)).resolves.toEqual(successMessage);
});

// without async/await
it("resolves (2)", () => {
    return expect(promiseMe(successMessage)).resolves.toEqual(successMessage);
});
```

In case the `Promise` rejects and the test did not expect that, Jest reports an error:

```
Error: expect(received).resolves.toEqual()

Received promise rejected instead of resolved
Rejected to value: [...]
```

But what if one want to test `Promise` rejection and verify the rejection reason?

## Try-catch with async/await (bad)

It looks like using `try-catch` with `async/await` is the easiest way to achieve this as the rejected value is thrown:

```javascript
it("rejects (bad)", async () => {
    try {
        await promiseMe("Error");
    } catch (e) {
        expect(e).toEqual("Error");
    }
});
```

But wait. What happens when the `Promise` returned by `promiseMe` function won’t reject, but it resolves instead? Well, the test still passes, as the catch block is never reached.

> See <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await#promise_rejection>

## Try-catch with async/await (better)

To overcome that issue, one could expect that the actual assertion will be executed and fail the test if it does not happen.  
This can be done pretty easily with `expect.assertions` which verifies that a certain number of assertions are called  
during a test:

```javascript
it("rejects (better)", async () => {
    expect.assertions(1);
    try {
        await promiseMe("Error");
    } catch (e) {
        expect(e).toEqual("Error");
    }
});
```

Now, when there is no rejection, the test fails:

```
Error: expect.assertions(1)

Expected one assertion to be called but received zero assertion calls.
```

## `.rejects` (best)

To make the code even more expressive `.rejects` matcher can be used:

```javascript
it("rejects (best)", async () => {
    await expect(promiseMe("Error")).rejects.toEqual("Error");
});
```

When there is no rejection, Jest reports an error:

```
Error: expect(received).rejects.toEqual()  
  
Received promise resolved instead of rejected  
Resolved to value: [...]  
```

If the rejected value is an `Error` object, `toThrow` matcher can be used:

```javascript
it("rejects (best)", async () => {
    await expect(promiseMe(new Error(errorMessage))).rejects.toThrow(errorMessage);
    await expect(promiseMe(new Error(errorMessage))).rejects.toThrow(Error); // type check
    await expect(promiseMe(new Error(errorMessage))).rejects.toThrow(new Error(errorMessage));
});
```

## See also

- [Testing exceptions in JavaScript with Jest](../../../2021/11/testing-exceptions-in-javascript/index.md)
- [Jest Vanilla JS Starter](https://github.com/kolorobot/jest-js-starter)
- [Different ways of handling exceptions in JUnit. Which one to choose?](../../../2013/07/3-ways-of-handling-exceptions-in-junit/index.md)
