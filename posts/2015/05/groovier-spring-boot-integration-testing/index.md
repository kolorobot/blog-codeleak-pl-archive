---
title: "Groovier Spring Boot Integration Testing"
date: 2015-05-27T22:14:00.000+02:00
updated: 2015-05-27T22:14:28.475+02:00
author: "Rafał Borowiec"
tags: ["spring boot", "testing"]
original_url: https://blog.codeleak.pl/2015/05/groovier-spring-boot-integration-testing.html
---

# Groovier Spring Boot Integration Testing

Recently I had a chance to use Groovy’s `groovy.json.JsonSlurper` in a soapUI REST project. The usage scenario in soapUI (in particular, soapUI Open Source) was very simple: in a Groovy assertion, load the content of a response into a variable and than verify it like this:

```groovy
import groovy.json.JsonSlurper;

def slurper = new JsonSlurper()
def result = slurper.parseText(messageExchange.responseContent)

assert result.incidentType == 'Lorem ipsum'
```

This works well in soapUI. But what about **Spring Boot** integration tests? Can I make integration testing of REST API groovier?

## API to be tested

For the purpose of this article I used existing Spring Boot Jersey Demo application: <https://github.com/kolorobot/spring-boot-jersey-demo>.

## Adding Groovy to Spring Boot project

Add Groovy and HTTPBuilder (Easy HTTP client for Groovy) dependencies.

```groovy
testCompile 'org.codehaus.groovy:groovy-all:2.4.3'
testCompile 'org.codehaus.groovy.modules.http-builder:http-builder:0.7.1'
```

All Groovy tests will be kept in `src/test/groovy` folder.

## First integration test

The first test will verify `/customer` endpoint:

```groovy
@RunWith(SpringJUnit4ClassRunner.class)
@ApplicationTest
class FindAllCustomersGroovyTest {

    RESTClient client = new RESTClient("http://localhost:9000")

    @Before
    def void before() {
        client.auth.basic("demo", "123")
    }

    @Test
    def void findsAll() {
        def response = client.get(path: "/customer")

        def json = response.responseData

        assert json.number == 0
        assert json.totalPages == 1
        assert json.totalElements == 3
        assert json.content.size() == 3
        assert json.content.firstname.any() {
            firstname ->
                firstname.equals("Boyd")
                firstname.equals("Carter")
                firstname.equals("Dave")
        }
    }

}
```

- `@ApplicationTest` - is a grouping annotation that wraps several Spring’s annotation. Groovy tests can be annotated with any JUnit and/or Spring annotations.

```java
@Documented
@Inherited
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
@org.springframework.boot.test.IntegrationTest("server.port=9000")
@ActiveProfiles("web")
@Sql(scripts = "classpath:data.sql", executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
public @interface ApplicationTest {

}
```

- HTTPBuilder module provides an RESTClient extension that allows querying REST API with ease. HTTPBuilder will be used instead of Spring Boot’s `TestRestClient`.
- API requires Basic Auth and configuring it with RESTClient is very easy. For more complex scenarios, it allows more sophisticated authentication mechanisms to be used.
- RESTClient response contains responseData that is JSONSlurper parsed object. And since we are groovy, asserting content of the response is very easy.

## Sending JSON content

Let’s see how to send JSON data along with the request:

```groovy
@RunWith(SpringJUnit4ClassRunner.class)
@ApplicationTest
class SaveCustomerGroovyTest {

    @Test
    public void savesCustomer() {
        def response = client.post(
                path: '/customer',
                requestContentType: "application/json",
                body: [
                        firstname: "John",
                        lastname: "Doe",
                        emailAddress:
                                [value: "john@dummy.com"]
                ]
        )

        assert 201 == response.status
        assert response.headers.location
    }

}
```

Note: No further explanation is needed, I believe.
