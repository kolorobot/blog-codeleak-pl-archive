---
title: "Spring 4: CGLIB-based proxy classes with no default constructor"
date: 2014-07-02T17:05:00.000+02:00
updated: 2014-08-06T13:33:37.038+02:00
author: "Rafał Borowiec"
tags: ["java", "spring 4"]
original_url: https://blog.codeleak.pl/2014/07/spring-4-cglib-based-proxy-classes-with-no-default-ctor.html
---

# Spring 4: CGLIB-based proxy classes with no default constructor

![](logo-spring-io.png)

In Spring, if the class of a target object that is to be proxied doesn’t implement any interfaces, then a CGLIB-based proxy will be created. Prior to Spring 4, CGLIB-based proxy classes require a default constructor. And this is not the limitation of CGLIB library, but Spring itself. Fortunately, as of Spring 4 this is no longer an issue. CGLIB-based proxy classes no longer require a default constructor. How can this impact your code? Let’s see.

One of the idioms of dependency injection is constructor injection. It can be generally used when the injected dependencies are required and must not change after the object is initiated. In this article I am not going to discuss why and when you should use constructor dependency injection. I assume you use this idiom in your code or you consider using it. If you are interested in learning more, see the resources section in the bottom of this article.

## Contructor injection with no-proxied beans

Having the following collaborator:

```java
package pl.codeleak.services;

import org.springframework.stereotype.Service;

@Service
public class Collaborator {
    public String collaborate() {
        return "Collaborating";
    }
}
```

we can easily inject it via constructor:

```java
package pl.codeleak.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SomeService {

    private final Collaborator collaborator;

    @Autowired
    public SomeService(Collaborator collaborator) {
        this.collaborator = collaborator;
    }

    public String businessMethod() {
        return collaborator.collaborate();
    }

}
```

You may notice the both `Collaborator` and the `Service` has no interfaces, but they are no proxy candidates. So this code will work perfectly fine with Spring 3 and Spring 4:

```java
package pl.codeleak.services;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import pl.codeleak.Configuration;

import static org.assertj.core.api.Assertions.assertThat;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = Configuration.class)
public class WiringTests {

    @Autowired
    private SomeService someService;

    @Autowired
    private Collaborator collaborator;

    @Test
    public void hasValidDependencies() {
        assertThat(someService)
                .isNotNull()
                .isExactlyInstanceOf(SomeService.class);

        assertThat(collaborator)
                .isNotNull()
                .isExactlyInstanceOf(Collaborator.class);

        assertThat(someService.businessMethod())
                .isEqualTo("Collaborating");
    }
}
```

## Contructor injection with proxied beans

In many cases your beans need to be decorated with an `AOP proxy` at runtime, e.g when you want to use declarative transactions with `@Transactional` annotation. To visualize this, I created an aspect that will advice all methods in `SomeService`. With the below aspect defined, `SomeService` becomes a candidate for proxying:

```java
package pl.codeleak.aspects;

import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class DummyAspect {

    @Before("within(pl.codeleak.services.SomeService)")
    public void before() {
        // do nothing
    }

}
```

When I re-run the test with Spring 3.2.9, I get the following exception:

```
Could not generate CGLIB subclass of class [class pl.codeleak.services.SomeService]: Common causes of this problem include using a final class or a non-visible class; nested exception is java.lang.IllegalArgumentException: Superclass has no null constructors but no arguments were given
```

This can be simply fixed by providing a default, no argument, constructor to `SomeService`, but this is not what I want to do - as I would also need to make dependencies non-final.

Another solution would be to provide an interface for `SomeService`. But again, there are many situation when you don’t need to create interfaces.

Updating to Spring 4 solves the problem immediately. As documentation states:

> CGLIB-based proxy classes no longer require a default constructor. Support is provided via the objenesis library which is repackaged inline and distributed as part of the Spring Framework. With this strategy, no constructor at all is being invoked for proxy instances anymore.

The test I created will fail, but it visualizes that CGLIB proxy was created for `SomeService`:

```
java.lang.AssertionError: 
Expecting:
 <pl.codeleak.services.SomeService@6a84a97d>
to be exactly an instance of:
 <pl.codeleak.services.SomeService>
but was an instance of:
 <pl.codeleak.services.SomeService$$EnhancerBySpringCGLIB$$55c3343b>
```

After removing the first assertion from the test, it will run just perfectly fine.

## Resources

In case you need read more about constructor dependency injection, have a look at this great article by Petri Kainulainen: <http://www.petrikainulainen.net/software-development/design/why-i-changed-my-mind-about-field-injection>.

Core Container Improvements in Spring 4: <http://docs.spring.io/spring/docs/current/spring-framework-reference/html/new-in-4.0.html#_core_container_improvements>

You may also be interested in reading my other articles about Spring: [Spring 4: @DateTimeFormat with Java 8 Date-Time API](../../../2014/06/spring-4-datetimeformat-with-java-8/index.md) and [Better error messages with Bean Validation 1.1 in Spring MVC application](../../../2014/06/better-error-messages-with-bean/index.md)
