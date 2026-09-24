---
title: "Test Data Builders and Object Mother: another look"
date: 2014-06-15T19:07:00.001+02:00
updated: 2014-06-15T19:07:11.519+02:00
author: "Rafał Borowiec"
tags: ["practices", "unit testing"]
original_url: https://blog.codeleak.pl/2014/06/test-data-builders-and-object-mother.html
---

# Test Data Builders and Object Mother: another look

Constructing objects in tests is usually a painstaking work and usually it produces a lot of repeatable and hard to read code. There are two common solutions for working with complex test data: `Object Mother` and `Test Data Builder`. Both has advantages and disadvantages, but (smartly) combined can bring new quality to your tests.

**Note:** There are already many articles you can find about both `Object Mother` and `Test Data Builder` so I will keep my description really concise.

## Object Mother

Shortly, an [Object Mother](http://martinfowler.com/bliki/ObjectMother.html) is a set of factory methods that allow us creating similar objects in tests:

```java
// Object Mother
public class TestUsers {

    public static User aRegularUser() {
        return new User("John Smith", "jsmith", "42xcc", "ROLE_USER");
    }

    // other factory methods

}

// arrange
User user = TestUsers.aRegularUser();
User adminUser = TestUsers.anAdmin();
```

Each time when a user with slightly different variation of data is required, new factory method is created, which makes that the `Object Mother` may grow in time. This is one of the disadvantages of `Object Mother`. This problem can be solved by introducing a [Test Data Builder](http://c2.com/cgi/wiki?TestDataBuilder).

## Test Data Builder

`Test Data Builder` uses the `Builder` pattern to create objects in Unit Tests. A short reminder of a `Builder`:

> The builder pattern is an object creation software design pattern. […] The intention of the builder pattern is to find a solution to the telescoping constructor anti-pattern.

Let’s look at the example of a `Test Data Builder`:

```java
public class UserBuilder {

    public static final String DEFAULT_NAME = "John Smith";
    public static final String DEFAULT_ROLE = "ROLE_USER";
    public static final String DEFAULT_PASSWORD = "42";

    private String username;
    private String password = DEFAULT_PASSWORD;
    private String role = DEFAULT_ROLE;
    private String name = DEFAULT_NAME;

    private UserBuilder() {
    }

    public static UserBuilder aUser() {
        return new UserBuilder();
    }

    public UserBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public UserBuilder withUsername(String username) {
        this.username = username;
        return this;
    }

    public UserBuilder withPassword(String password) {
        this.password = password;
        return this;
    }

    public UserBuilder withNoPassword() {
        this.password = null;
        return this;
    }

    public UserBuilder inUserRole() {
        this.role = "ROLE_USER";
        return this;
    }

    public UserBuilder inAdminRole() {
        this.role = "ROLE_ADMIN";
        return this;
    }

    public UserBuilder inRole(String role) {
        this.role = role;
        return this;
    }

    public UserBuilder but() {
        return UserBuilder
                .aUser()
                .inRole(role)
                .withName(name)
                .withPassword(password)
                .withUsername(username);
    }

    public User build() {
        return new User(name, username, password, role);
    }
}
```

In our test we can use the builder as follows:

```java
UserBuilder userBuilder = UserBuilder.aUser()
    .withName("John Smith")
    .withUsername("jsmith");

User user = userBuilder.build();
User admin = userBuilder.but()
    .withNoPassword().inAdminRole();
```

The above code seem pretty nice. We have a fluent API that improves the readability of the test code and for sure it eliminates the problem of having multiple factory methods for object variations that we need in tests while using `Object Mother`.

Please note that I added some default values of properties that may be not relevant for most of the tests. But since they are defined as public constants they can be used in assertions, if we want so.

**Note:** The example used in this article is relatively simple. It is used to visualize the solution.

## Object Mother and Test Data Builder combined

Neither solution is perfect. But what if we combine them? Imagine, that `Object Mother` returns a `Test Data Builder`. Having this, you can then manipulate the builder state before calling a terminal operation. It is a kind of a template.

Look at the example below:

```java
public final class TestUsers {

    public static UserBuilder aDefaultUser() {
        return UserBuilder.aUser()
                .inUserRole()
                .withName("John Smith")
                .withUsername("jsmith");
    }

    public static UserBuilder aUserWithNoPassword() {
        return UserBuilder.aUser()
                .inUserRole()
                .withName("John Smith")
                .withUsername("jsmith")
                .withNoPassword();
    }

    public static UserBuilder anAdmin() {
        return UserBuilder.aUser()
                .inAdminRole()
                .withName("Chris Choke")
                .withUsername("cchoke")
                .withPassword("66abc");
    }
}
```

Now, `TestUsers` provides factory method for creating similar test data in our tests. It returns a builder instance, so we are able to quickly and nicely modify the object in a our test as we need:

```java
UserBuilder user = TestUsers.aUser();
User admin = user.but().withNoPassword().build();
```

The benefits are great. We have a template for creating similar objects and we have the power of a builder if we need to modify the state of the returned object before using it.

### Enriching a Test Data Builder

While thinking about the above, I am not sure if keeping a separate `Object Mother` is really necessary. We could easily move the methods from `Object Mother` directly to `Test Data Builder`:

```java
public class UserBuilder {

    public static final String DEFAULT_NAME = "John Smith";
    public static final String DEFAULT_ROLE = "ROLE_USER";
    public static final String DEFAULT_PASSWORD = "42";

    // field declarations omitted for readability

    private UserBuilder() {}

    public static UserBuilder aUser() {
        return new UserBuilder();
    }

    public static UserBuilder aDefaultUser() {
        return UserBuilder.aUser()
                .withUsername("jsmith");
    }

    public static UserBuilder aUserWithNoPassword() {
        return UserBuilder.aDefaultUser()
                .withNoPassword();
    }

    public static UserBuilder anAdmin() {
        return UserBuilder.aUser()
                .inAdminRole();
    }

    // remaining methods omitted for readability

}
```

Thanks to that we can maintain the creation of `User`’s data inside a single class.

Please note, that in this that `Test Data Builder` is a test code. In case we have a builder already in a production code, creating an `Object Mother` returning an instance of `Builder` sounds like a better solution.

### What about mutable objects?

There are some possible drawbacks with `Test Data Builder` approach when it comes to mutable objects. And in many applications I mostly deal with mutable objects (aka `beans` or `anemic data model`) and probably many of you do as well.

The `Builder` pattern is meant for creating **immutable** value objects - in theory. Typically, if we deal with mutable objects `Test Data Builder` may seem like a duplication at first sight:

```java
// Mutable class with setters and getters
class User {
    private String name;
    public String getName() { ... }
    public String setName(String name) { ... }

    // ...
}

public class UserBuilder {
    private User user = new User();

    public UserBuilder withName(String name) {
        user.setName(name);
        return this;
    }

    // other methods

    public User build() {
        return user;
    }
}
```

In a test we can then create a user like this:

```java
User aUser = UserBuiler.aUser()
    .withName("John")
    .withPassword("42abc")
    .build();
```

Instead of:

```java
User aUser = new User();
aUser.setName("John");
aUser.setPassword("42abc");
```

In such a case creating `Test Data Builder` is a **trade off**. It requires writing more code that needs to be maintained. On the other hand, the readability is greatly improved.

## Summary

Managing test data in unit tests is not an easy job. If you don’t find a good solution, you end up with plenty of boilerplate code that is hard to read and understand, hard to maintain. On the other hand there is not silver bullet solution for that problem. I experimented with many approaches. Depending on the size of the problem I need to deal with I select a different approach, sometimes combining multiple approaches in one project.

***How do you deal with constructing data in your tests?***

## References

- Petri Kainulainen: [Writing Clean Tests – New Considered Harmful](http://www.petrikainulainen.net/programming/testing/writing-clean-tests-new-considered-harmful)
- `Growing Object-Oriented Software, Guided by Tests` - Chapter 22: `Constructing Complex Test Data`.
