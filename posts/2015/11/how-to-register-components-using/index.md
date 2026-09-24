---
title: "HOW-TO: Register components using @Conditional and Condition in Spring"
date: 2015-11-25T23:42:00.000+01:00
updated: 2015-11-25T23:42:19.758+01:00
author: "Rafał Borowiec"
tags: ["spring", "spring 4"]
original_url: https://blog.codeleak.pl/2015/11/how-to-register-components-using.html
---

# HOW-TO: Register components using @Conditional and Condition in Spring

`@Profile` annotation in Spring can be used on any Spring components (e.g. `@Component`, `@Service`, `@Configuration` etc.) that are candidates for auto-detection. `@Profile` annotation accepts a single profile or a set of profiles that must be active in order to make the annotated component eligible for auto-detection. For a given `@Profile({"p1", "!p2"})`, registration will occur if profile `p1` is active **or** if profile `p2` is not active. The **or** is crucial here.

But how to achieve this with `@Profile`: we want to activate a given component if profile `p1` is active **and** if profiles `p2` **and** `p3` are both inactive?

Let’s assume the following situation: we have a`NotificationSender` interface that is implemented by:   
- `SendGridNotificationSender` - active only if `sendgrid` profile is active,   
- `EmailNotificationSender` - active only if `email` profile is active.   
- `NoOpNotificationSender` - active only if `development` profile is active and none of `sendgrid` and `email` are active.

In addition: only one `NotificationSender` can be registered at a time and `development` profile can be used in conjunction with `sendgrid` and `email` profiles.

In the above situation using the `@Profile` annotation seems not enough. Maybe I am complicating things a bit, but actually I really wanted to achieve the above without introducing another profile. And how I did it?

I used Spring’s 4 `@Conditional` annotation. `@Conditional` allow registration of component when all specified `Condition`(s) match:

```java
@Component
@Conditional(value = NoOpNotificationSender.ProfilesCondition.class)
class NoOpNotificationSender extends NotificationSenderAdapter {

}
```

`ProfilesCondition` implements `org.springframework.context.annotation.Condition` interface:

```java
public static class ProfilesCondition implements Condition {
    @Override
    public boolean matches(ConditionContext c, AnnotatedTypeMetadata m) {

    }
}
```

The whole solution to the problem:

```java
@Component
@Conditional(value = NoOpNotificationSender.ProfilesCondition.class)
class NoOpNotificationSender extends NotificationSenderAdapter {

    static class ProfilesCondition implements Condition {
        @Override
        public boolean matches(ConditionContext c, AnnotatedTypeMetadata m) {
            return accepts(c, Profiles.DEVELOPMENT)
                && !accepts(c, Profiles.MAIL)
                && !accepts(c, Profiles.SEND_GRID);
        }

        private boolean accepts(ConditionContext c, String profile) {
            return c.getEnvironment().acceptsProfiles(profile);
        }
    }
}
```

The other components will be activated when appropriate profile is active:

```java
@Component
@Profile(value = Profiles.SEND_GRID)
public class SendGridNotificationSender extends NotificationSenderAdapter {

}

@Component
@Profile(value = Profiles.MAIL)
class EmailNotificationSender extends NotificationSenderAdapter {

}
```

Usage examples:

| Active profiles | Bean |
| --- | --- |
| development | NoOpNotificationSender |
| development,sendgrid | SendGridNotificationSender |
| development,mail | EmailNotificationSender |
| sendgrid | SendGridNotificationSender |
| mail | EmailNotificationSender |

What do you think? How would you solve this problem?
