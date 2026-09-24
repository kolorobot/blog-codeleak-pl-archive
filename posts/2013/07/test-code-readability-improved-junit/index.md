---
title: "Test code readability improved: JUnit with Mockito and FEST Fluent Assertions"
date: 2013-07-14T17:10:00.001+02:00
updated: 2014-06-06T21:58:18.274+02:00
author: "Rafał Borowiec"
tags: ["java", "unit testing"]
original_url: https://blog.codeleak.pl/2013/07/test-code-readability-improved-junit.html
---

# Test code readability improved: JUnit with Mockito and FEST Fluent Assertions

To improve the readability of my unit tests I use *assertThat* with Hamcrest matchers. This is a good way to improve readability of your test code, especially when I statically import members of like *org.junit.Assert.assertThat* and *org.hamcrest.Matchers*. But when I add Mockito matchers on top of it, I experienced the problem of static import conflicts that ended up with "not nice" code (according to my definition).
Let's look at the (hypothetical) example:

```java
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class UserServiceTest {

    @InjectMocks
    private UserService userService = new UserService();
    @Mock
    private UserRepository userRepositoryMock;

    @Test
    public void returnsUserDetailsFoundInRepository() {
        // arrange
        User demoUser = new User("user", "demo", "ROLE_USER");
        when(userRepositoryMock.findByUsername("user")).thenReturn(demoUser);

        // act
        User userDetails = userService.loadUserByUsername("user");

        // assert
        assertThat(userDetails.getUsername(), org.hamcrest.Matchers.startsWith("user"));
        verify(userRepositoryMock).findByUsername(org.mockito.Matchers.startsWith("user"));
    }
}
```

In the *assert* section I must choose to statically import either *org.hamcrest.Matchers.startsWith* or *org.mockito.Matchers.startsWith*. And I don't really like it.
  
Then, some time ago, someone mentioned on Twitter that I should try FEST Fluent Assertions. So I gave it a try and I ended up with the below:

```java
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static org.fest.assertions.Assertions.assertThat;
import static org.mockito.Matchers.startsWith;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class UserServiceTest {

    @InjectMocks
    private UserService userService = new UserService();
    @Mock
    private UserRepository userRepositoryMock;

    @Test
    public void returnsUserDetailsFoundInRepository() {
        // arrange
        User demoUser = new User("user", "demo", "ROLE_USER");
        when(userRepositoryMock.findByUsername("user")).thenReturn(demoUser);

        // act
        User userDetails = userService.loadUserByUsername("user");

        // assert
        assertThat(userDetails.getUsername()).startsWith("user");        
        verify(userRepositoryMock).findByUsername(startsWith("user"));
    }
}
```

The changes are:

*import static org.fest.assertions.Assertions.assertThat* instead of *import static org.junit.Assert.assertThat;*
*import static org.mockito.Matchers.startsWith;*
Of course, FEST Fluent Assertions is not about solving the static import problem - it also (or first of all) "provides a fluent interface for assertions". And this is where the readability comes into play. Consider the below example:

```java
    @Test
    public void returnsMostActiveUsers() {
        List<User> users = userService.getMostActiveUsers();
        
        assertThat(users)
                .hasSize(3)
                .containsOnly(userWith10Activities, userWith5Activities);                                        
    }
```

To have all libraries available with Maven the following dependencies should be used:

```xml
        <!-- Test -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit-dep</artifactId>
            <version>4.11</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>1.9.5</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.easytesting</groupId>
            <artifactId>fest-assert</artifactId>
            <version>1.4</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
            <version>1.3</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <version>1.3</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.objenesis</groupId>
            <artifactId>objenesis</artifactId>
            <version>1.3</version>
        </dependency>
```

All of the above you can find on Github: [Unit Testing Demo](https://github.com/kolorobot/unit-testing-demo) and in [Spring MVC Quickstart Archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype).

## References

- [Static import conflicts between Mockito and Hamcrest](https://groups.google.com/forum/#!topic/mockito/SE1EnoKZaX8)
- [FEST](https://code.google.com/p/fest/)

## See also

[HOW-TO: Improve content assist for types with static members while creating JUnit tests in Eclipse](../../../2012/05/how-to-improve-content-assist-for-types/index.md)
