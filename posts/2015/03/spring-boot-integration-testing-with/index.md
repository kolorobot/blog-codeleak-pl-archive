---
title: "Spring Boot Integration Testing with Selenium"
date: 2015-03-11T21:49:00.000+01:00
updated: 2016-09-28T00:17:22.105+02:00
author: "Rafał Borowiec"
tags: ["selenium", "spring boot", "unit testing"]
original_url: https://blog.codeleak.pl/2015/03/spring-boot-integration-testing-with.html
---

# Spring Boot Integration Testing with Selenium

![](Seleniumlogo.png)

Web integration tests allow integration testing of Spring Boot application without any mocking. By using `@WebIntegrationTest` and `@SpringApplicationConfiguration` we can create tests that loads the application and listen on *normal* ports. This small addition to Spring Boot makes much easier to create integration tests with Selenium WebDriver.

# Test Dependencies

The application that we will be testing is a simple Spring Boot / Thymeleaf application with `spring-boot-starter-web`, `spring-boot-starter-thymeleaf` and `spring-boot-starter-actuator` dependencies. See references for the link to the GitHub project.

The test dependencies are:

*Update (21/3/2016):* Dependencies in the project got updated (io.spring.platform, bootstrap, jquery, assertj and selenium). Link to source code in [references](#references)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>1.5.0</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.seleniumhq.selenium</groupId>
    <artifactId>selenium-java</artifactId>
    <version>2.45.0</version>
    <scope>test</scope>
</dependency>
```

# Web Integration Test

With classic Spring Test, using `MockMvc`, you would create test like below:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class HomeControllerClassicTest {

    @Autowired
    private WebApplicationContext wac;

    private MockMvc mockMvc;

    @Before
    public void setUp() throws Exception {
        mockMvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }

    @Test
    public void verifiesHomePageLoads() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/"))
                .andExpect(MockMvcResultMatchers.status().isOk());
    }
}
```

`@SpringApplicationConfiguration` extends capabilities of `@ContextConfiguration` and loads application context for integration test. To create a test without mocked environment we should define our test using `@WebIntegrationTest` annotation:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebIntegrationTest(value = "server.port=9000")
public class HomeControllerTest {

}
```

This will start full application within JUnit test, listening on port `9000`. Having such test we can easily add Selenium and execute real functional tests using a browser (will not work in headless environment, unless we use HtmlUnit driver - but this is beyond scope of this article).

# Adding Selenium

Adding Selenium to the test is very simple, but I wanted to achieve a bit more than that hence I created a custom annotation to mark my tests as Selenium tests. I also configured it the way it allows injecting `WebDriver` to the test instance:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebIntegrationTest(value = "server.port=9000")
@SeleniumTest(driver = ChromeDriver.class, baseUrl = "http://localhost:9000")
public class HomeControllerTest {

    @Autowired
    private WebDriver driver;

}
```

## `@SeleniumTest`

`@SeleniumTest` is a custom annotation:

```java
@Documented
@Inherited
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@TestExecutionListeners(
        listeners = SeleniumTestExecutionListener.class,
        mergeMode = MERGE_WITH_DEFAULTS)
public @interface SeleniumTest {

    Class<? extends WebDriver> driver() default FirefoxDriver.class;

    String baseUrl() default "http://localhost:8080";
}
```

The annotation uses adds test execution listener that will create a `WebDriver` instance that can be used in the integration test. `TestExecutionListener` defines a listener API for reacting to test execution events. It can be used to instrument the tests. Example implementations in Spring Test are used to support test-managed transactions or dependency injection into test instances, for instance.

## TestExecutionListener

Note: Some parts of the code of `SeleniumTestExecutionListener` are skipped for better readability.

`SeleniumTestExecutionListener` provides way to inject configured `WebDriver` into test instances. The driver instance will be created only once and the driver used can be simply changed with `@SeleniumTest` annotation. The most important thing was to register the driver with Bean Factory.

```java
@Override
public void prepareTestInstance(TestContext testContext) throws Exception {
    ApplicationContext context = testContext.getApplicationContext();
    if (context instanceof ConfigurableApplicationContext) {

        SeleniumTest annotation = findAnnotation(
                testContext.getTestClass(), SeleniumTest.class);
        webDriver = BeanUtils.instantiate(annotation.driver());

        // register the bean with bean factory

    }
}
```

Before each test method base URL of the application will be opened by a `WebDriver`:

```java
@Override
public void beforeTestMethod(TestContext testContext) throws Exception {
    SeleniumTest annotation = findAnnotation(
            testContext.getTestClass(), SeleniumTest.class);
    webDriver.get(annotation.baseUrl());

}
```

In addition, on every failure a screenshot will be generated:

```java
@Override
public void afterTestMethod(TestContext testContext) throws Exception {
    if (testContext.getTestException() == null) {
        return;
    }

    File screenshot = ((TakesScreenshot) webDriver).getScreenshotAs(OutputType.FILE);

    // do stuff with the screenshot

}
```

After each test the driver will be closed:

```java
@Override
public void afterTestClass(TestContext testContext) throws Exception {
    if (webDriver != null) {
        webDriver.quit();
    }
}
```

This is just an example. Very simple implementation. We could extend the capabilities of the annotation and the listener.

## The test

Running the below test will start the Chrome browser and execute some simple checks with Selenium:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebIntegrationTest(value = "server.port=9000")
@SeleniumTest(driver = ChromeDriver.class, baseUrl = "http://localhost:9000")
public class HomeControllerTest {

    @Autowired
    private WebDriver driver;

    private HomePage homePage;

    @Before
    public void setUp() throws Exception {
        homePage = PageFactory.initElements(driver, HomePage.class);
    }

    @Test
    public void containsActuatorLinks() {
        homePage.assertThat()
                .hasActuatorLink("autoconfig", "beans", "configprops", "dump", "env", "health", "info", "metrics", "mappings", "trace")
                .hasNoActuatorLink("shutdown");
    }

    @Test
    public void failingTest() {
        homePage.assertThat()
                .hasNoActuatorLink("autoconfig");
    }
}
```

The test uses simple page object with custom AssertJ assertions. You can find the full source code in GitHub. See references.

In case of a failure, the screenshot taken by the driver, will be stored in appropriate directory.

# Summary

Integration testing of fully loaded Spring Boot application is possible in regular JUnit test thanks to `@WebIntegrationTest` and `@SpringApplicationConfiguration` annotations. Having the application running within a test opens a possibility to hire Selenium and run functional tests using the browser. If you combine it with profiles and some more features of Spring Test (e.g. `@Sql`, `@SqlConfig`) you may end up with quite powerful yet simple solution for your integration tests.

# References

- Source code: <https://github.com/kolorobot/spring-boot-thymeleaf>
- Spring Boot Testing: <http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#boot-features-testing>
- Spring Testing: <http://docs.spring.io/spring/docs/current/spring-framework-reference/html/testing.html>
