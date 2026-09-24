---
title: "Spring Boot and Security Events with Actuator"
date: 2017-03-17T00:27:00.000+01:00
updated: 2017-03-17T00:27:00.689+01:00
author: "Rafał Borowiec"
tags: ["spring boot", "spring security"]
original_url: https://blog.codeleak.pl/2017/03/spring-boot-and-security-events-with-actuator.html
---

# Spring Boot and Security Events with Actuator

Spring Boot Actuator provides auditing capabilities for publishing and listening to security related events in a Spring Boot application with Spring Security enabled. The default events are authentication success, authentication failure and access denied, but they can be extended with custom events.

## Make sure you have Spring Boot Security and Actuator enabled in your project

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

## Actuator `/auditevents` endpoint

By default `/auditevents` endpoint is enabled so after starting the application (and logging in with username `user` and password that is provided in application log) you can see the current security events:

```
{
  "events": [
    {
      "timestamp": "2017-03-14T22:59:58+0000",
      "principal": "user",
      "type": "AUTHENTICATION_FAILURE",
      "data": {
        "details": {
          "remoteAddress": "0:0:0:0:0:0:0:1",
          "sessionId": null
        },
        "type": "org.springframework.security.authentication.BadCredentialsException",
        "message": "Bad credentials"
      }
    },
    {
      "timestamp": "2017-03-14T23:00:07+0000",
      "principal": "user",
      "type": "AUTHENTICATION_SUCCESS",
      "data": {
        "details": {
          "remoteAddress": "0:0:0:0:0:0:0:1",
          "sessionId": null
        }
      }
    }
  ]
}
```

The `/auditevents` endpoint accepts request optional parameters:

- `pricipal` - the principal name
- `after` - date after the event occurred in the following format: `yyyy-MM-dd'T'HH:mm:ssZ`
- `type` - the event type (e.g. AUTHORIZATION_FAILURE, AUTHENTICATION_SUCCESS, AUTHENTICATION_FAILURE, AUTHENTICATION_SWITCH)

Example request:

<http://localhost:8080/auditevents?type=AUTHORIZATION_FAILURE&after=2017-03-14T23%3A14%3A12%2B0000&principal=anonymousUser>

The endpoint implementation uses `org.springframework.boot.actuate.audit.AuditEventRepository` to return all the registered audit events.

- Customize `/auditevents` endpoint

You can customize the endpoint with `endpoints.auditevents.*` properties. For example, to change the path of audit events endpoint simply use `endpoints.auditevents.path` property.

## Listening to security audit events with `@EventListener`

Security events are represented by `org.springframework.boot.actuate.audit.AuditEvent` value object in actuator. This object contains timestamp, username, event type and event data.

The easiest way to get notified about audit events is to subscribe to `org.springframework.boot.actuate.audit.listener.AuditApplicationEvent` events via Spring’s `org.springframework.context.event.EventListener`:

```java
@Component
public class AuditApplicationEventListener {

    private static final Logger LOG = LoggerFactory.getLogger(AuditApplicationEventListener.class);

    @EventListener
    public void onAuditEvent(AuditApplicationEvent event) {
        AuditEvent actualAuditEvent = event.getAuditEvent();

        LOG.info("On audit application event: timestamp: {}, principal: {}, type: {}, data: {}",
            actualAuditEvent.getTimestamp(),
            actualAuditEvent.getPrincipal(),
            actualAuditEvent.getType(),
            actualAuditEvent.getData()
        );

    }
}
```

Example output:

```
2017-03-15 00:44:12.921  INFO 13316 --- [nio-8080-exec-1] p.c.d.s.s.AuditApplicationEventListener  : On audit event: timestamp: Wed Mar 15 00:44:12 CET 2017, principal: user, type: AUTHENTICATION_SUCCESS, data: {details=org.springframework.security.web.authentication.WebAuthenticationDetails@b364: RemoteIpAddress: 0:0:0:0:0:0:0:1; SessionId: null}
```

### Async events

The `@EventListener` is synchronous, but if asynchronous behavior is desired you can annotate event listener method with `@Async` and make sure that async is enabled (e.g. via `@EnableAsync`):

```java
@Component
public class AuditApplicationEventListener {

    private static final Logger LOG = LoggerFactory.getLogger(AuditApplicationEventListener.class);

    @EventListener
    @Async
    public void onAuditEvent(AuditApplicationEvent event) {

    }
}
```

And the configuration:

```java
@SpringBootApplication
@EnableAsync
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class);
    }
}
```

## Listening to security audit events with `AbstractAuditListener`

Alternatively, you can extend `org.springframework.boot.actuate.audit.listener.AbstractAuditListener` and override its `org.springframework.boot.actuate.audit.listener.AbstractAuditListener#onAuditEvent` method:

```java
@Component
public class AuditEventListener extends AbstractAuditListener {

    private static final Logger LOG = LoggerFactory.getLogger(AuditEventListener.class);

    @Override
    protected void onAuditEvent(AuditEvent event) {
        LOG.info("On audit event: timestamp: {}, principal: {}, type: {}, data: {}",
            event.getTimestamp(),
            event.getPrincipal(),
            event.getType(),
            event.getData()
        );
    }
}
```

Note: No events will be stored in the event repository, hence `/auditevents` endpoint will always return an empty array. To fix this you can either inject audit repository or extend directly from `org.springframework.boot.actuate.audit.listener.AuditListener`:

```java
@Component
public class AuditEventListener extends AbstractAuditListener {

    private static final Logger LOG = LoggerFactory.getLogger(AuditEventListener.class);

    @Autowired
    private AuditEventRepository auditEventRepository;

    @Override
    protected void onAuditEvent(AuditEvent event) {

        LOG.info("On audit event: timestamp: {}, principal: {}, type: {}, data: {}",
            event.getTimestamp(),
            event.getPrincipal(),
            event.getType(),
            event.getData()
        );

        auditEventRepository.add(event);
    }
}
```

## Publishing own audits events with event publisher

In the example below the application event publisher (`org.springframework.context.ApplicationEventPublisher`) is used in order to publish a custom audit event with type `CUSTOM_AUDIT_EVENT`. The new listener method listens only for those new events whereas the previous method ignores them (note this is just an example). Like any other events, the custom one will be stored using audit event repository.

```java
@Component
public class AuditApplicationEventListener {

    private static final Logger LOG = LoggerFactory.getLogger(AuditApplicationEventListener.class);

    @Autowired
    private ApplicationEventPublisher applicationEventPublisher;

    @EventListener(condition = "#event.auditEvent.type != 'CUSTOM_AUDIT_EVENT'")
    @Async
    public void onAuditEvent(AuditApplicationEvent event) {
        AuditEvent actualAuditEvent = event.getAuditEvent();

        LOG.info("On audit application event: timestamp: {}, principal: {}, type: {}, data: {}",
            actualAuditEvent.getTimestamp(),
            actualAuditEvent.getPrincipal(),
            actualAuditEvent.getType(),
            actualAuditEvent.getData()
        );
        applicationEventPublisher.publishEvent(
            new AuditApplicationEvent(
                new AuditEvent(actualAuditEvent.getPrincipal(), "CUSTOM_AUDIT_EVENT")
            )
        );
    }

    @EventListener(condition = "#event.auditEvent.type == 'CUSTOM_AUDIT_EVENT'")
    public void onCustomAuditEvent(AuditApplicationEvent event) {
        LOG.info("Handling custom audit event ...");
    }
}
```

## Note on the sample code

The sample code for this article can be found in [spring-boot-thymeleaf](https://github.com/kolorobot/spring-boot-thymeleaf) repository. By default, the security is disabled in both profiles. Enable it by changing the `security.basic.enabled` property in `application.properties`.
