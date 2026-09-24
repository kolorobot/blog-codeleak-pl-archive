---
title: "Testing mail code in Spring Boot application"
date: 2014-09-16T21:54:00.001+02:00
updated: 2014-09-17T23:03:38.265+02:00
author: "Rafał Borowiec"
tags: ["spring boot", "unit testing"]
original_url: https://blog.codeleak.pl/2014/09/testing-mail-code-in-spring-boot.html
---

# Testing mail code in Spring Boot application

![](logo-spring-io.png)

Whilst building a Spring Boot application you may encounter a need of adding a mail configuration. Actually, configuring the mail in Spring Boot does not differ much from configuring it in Spring Bootless application. But how to test that mail configuration and submission is working fine? Let’s have a look.

I assume that we have a simple Spring Boot application bootstrapped. If not, the easiest way to do it is by using the [Spring Initializr](http://start.spring.io/).

## Adding javax.mail dependency

We start by adding `javax.mail` dependency to `build.gradle`: `compile 'javax.mail:mail:1.4.1'`. We will also need `Spring Context Support` (if not present) that contains `JavaMailSender` support class. The dependency is: `compile("org.springframework:spring-context-support")`

## Java-based Configuration

Spring Boot favors Java-based configuration. In order to add mail configuration, we add `MailConfiguration` class annotated with `@Configuration` annotation. The properties are stored in `mail.properties` (it is not required, though). Property values can be injected directly into beans using the `@Value` annotation:

```java
@Configuration
@PropertySource("classpath:mail.properties")
public class MailConfiguration {

    @Value("${mail.protocol}")
    private String protocol;
    @Value("${mail.host}")
    private String host;
    @Value("${mail.port}")
    private int port;
    @Value("${mail.smtp.auth}")
    private boolean auth;
    @Value("${mail.smtp.starttls.enable}")
    private boolean starttls;
    @Value("${mail.from}")
    private String from;
    @Value("${mail.username}")
    private String username;
    @Value("${mail.password}")
    private String password;

    @Bean
    public JavaMailSender javaMailSender() {
        JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
        Properties mailProperties = new Properties();
        mailProperties.put("mail.smtp.auth", auth);
        mailProperties.put("mail.smtp.starttls.enable", starttls);
        mailSender.setJavaMailProperties(mailProperties);
        mailSender.setHost(host);
        mailSender.setPort(port);
        mailSender.setProtocol(protocol);
        mailSender.setUsername(username);
        mailSender.setPassword(password);
        return mailSender;
    }
}
```

The `@PropertySource` annotation makes `mail.properties` available for injection with `@Value`. annotation. If not done, you may expect an exception: `java.lang.IllegalArgumentException: Could not resolve placeholder '<name>' in string value "${<name>}"`.

And the `mail.properties`:

```
mail.protocol=smtp
mail.host=localhost
mail.port=25
mail.smtp.auth=false
mail.smtp.starttls.enable=false
mail.from=me@localhost
mail.username=
mail.password=
```

EDIT: As [Phillip Web](https://twitter.com/phillip_webb) mentioned in one of the tweets regarding this blog post, the configuration could be also made using `@ConfigurationProperties` beans. I created a follow up post that describes how to use `@ConfigurationProperties` in Spring Boot. Have a look here: [Using @ConfigurationProperties in Spring Boot](../../../2014/09/using-configurationproperties-in-spring/index.md)

## Mail endpoint

In order to be able to send an email in our application, we can create a REST endpoint. We can use Spring’s `SimpleMailMessage` in order to quickly implement this endpoint. Let’s have a look:

```java
@RestController
class MailSubmissionController {

    private final JavaMailSender javaMailSender;

    @Autowired
    MailSubmissionController(JavaMailSender javaMailSender) {
        this.javaMailSender = javaMailSender;
    }

    @RequestMapping("/mail")
    @ResponseStatus(HttpStatus.CREATED)
    SimpleMailMessage send() {        
        SimpleMailMessage mailMessage = new SimpleMailMessage();
        mailMessage.setTo("someone@localhost");
        mailMessage.setReplyTo("someone@localhost");
        mailMessage.setFrom("someone@localhost");
        mailMessage.setSubject("Lorem ipsum");
        mailMessage.setText("Lorem ipsum dolor sit amet [...]");
        javaMailSender.send(mailMessage);
        return mailMessage;
    }
}
```

## Running the application

We are now ready to run the application. If you use CLI, type: `gradle bootRun`, open the browser and navigate to `localhost:8080/mail`. What you should see is actually an error, saying that mail server connection failed. As expected.

## Fake SMTP Server

[FakeSMTP](http://nilhcem.github.io/FakeSMTP/index.html) is a free Fake SMTP Server with GUI, written in Java, for testing emails in applications. We will use it to verify if the submission works. Please download the application and simply run it by invoking: `java -jar fakeSMTP-<version>.jar`. After launching Fake SMTP Server, start the server.

Now you can invoke REST endpoint again and see the result in Fake SMTP!

But by testing I did not mean manual testing! The application is still useful, but we want to **automatically** test mail code.

## Unit testing mail code

To be able to automatically test the mail submission, we will use [Wiser](https://code.google.com/p/subethasmtp/wiki/Wiser) - a framework / utility for unit testing mail based on [SubEtha SMTP](https://code.google.com/p/subethasmtp/). *SubEthaSMTP’s simple, low-level API is suitable for writing almost any kind of mail-receiving application.*

Using Wiser is very simple. Firstly, we need to add a test dependency to `build.gradle`: `testCompile("org.subethamail:subethasmtp:3.1.7")`. Secondly, we create an integration test with, JUnit, Spring and and Wiser:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class MailSubmissionControllerTest {

    private Wiser wiser;

    @Autowired
    private WebApplicationContext wac;
    private MockMvc mockMvc;

    @Before
    public void setUp() throws Exception {
        wiser = new Wiser();
        wiser.start();
        mockMvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }

    @After
    public void tearDown() throws Exception {
        wiser.stop();
    }

    @Test
    public void send() throws Exception {
        // act
        mockMvc.perform(get("/mail"))
                .andExpect(status().isCreated());
        // assert
        assertReceivedMessage(wiser)
                .from("someone@localhosts")
                .to("someone@localhost")
                .withSubject("Lorem ipsum")
                .withContent("Lorem ipsum dolor sit amet [...]");
    }
}
```

The SMTP server is initialized, started in `@Before` method and stopped in `@Teardown` method. After sending a message, the assertion is made. The assertion needs to be created, as the framework does not provide any. As you will notice, we need to operate on Wiser object, that provides a list of received messages:

```java
public class WiserAssertions {

    private final List<WiserMessage> messages;

    public static WiserAssertions assertReceivedMessage(Wiser wiser) {
        return new WiserAssertions(wiser.getMessages());
    }

    private WiserAssertions(List<WiserMessage> messages) {
        this.messages = messages;
    }

    public WiserAssertions from(String from) {
        findFirstOrElseThrow(m -> m.getEnvelopeSender().equals(from),
                assertionError("No message from [{0}] found!", from));
        return this;
    }

    public WiserAssertions to(String to) {
        findFirstOrElseThrow(m -> m.getEnvelopeReceiver().equals(to),
                assertionError("No message to [{0}] found!", to));
        return this;
    }

    public WiserAssertions withSubject(String subject) {
        Predicate<WiserMessage> predicate = m -> subject.equals(unchecked(getMimeMessage(m)::getSubject));
        findFirstOrElseThrow(predicate,
                assertionError("No message with subject [{0}] found!", subject));
        return this;
    }

    public WiserAssertions withContent(String content) {
        findFirstOrElseThrow(m -> {
            ThrowingSupplier<String> contentAsString = 
                () -> ((String) getMimeMessage(m).getContent()).trim();
            return content.equals(unchecked(contentAsString));
        }, assertionError("No message with content [{0}] found!", content));
        return this;
    }

    private void findFirstOrElseThrow(Predicate<WiserMessage> predicate, Supplier<AssertionError> exceptionSupplier) {
        messages.stream().filter(predicate)
                .findFirst().orElseThrow(exceptionSupplier);
    }

    private MimeMessage getMimeMessage(WiserMessage wiserMessage) {
        return unchecked(wiserMessage::getMimeMessage);
    }

    private static Supplier<AssertionError> assertionError(String errorMessage, String... args) {
        return () -> new AssertionError(MessageFormat.format(errorMessage, args));
    }

    public static <T> T unchecked(ThrowingSupplier<T> supplier) {
        try {
            return supplier.get();
        } catch (Throwable e) {
            throw new RuntimeException(e);
        }
    }

    interface ThrowingSupplier<T> {
        T get() throws Throwable;
    }
}
```

## Summary

With just couple of lines of code we were able to automatically test mail code. The example presented in this article is not sophisticated but it shows how easy it is to get started with SubEtha SMTP and Wiser.

How do you test your mail code?
