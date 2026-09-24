---
title: "${... } placeholders support in @Value annotations in Spring"
date: 2015-09-29T00:00:00.000+02:00
updated: 2015-09-29T00:00:12.029+02:00
author: "Rafał Borowiec"
tags: ["spring 4", "thymeleaf"]
original_url: https://blog.codeleak.pl/2015/09/placeholders-support-in-value.html
---

# ${... } placeholders support in @Value annotations in Spring

`${...}` placeholders in `@Value` annotation are used to access properties registered with `@PropertySource`. This is extremely useful with `@Configuration` beans in Spring applications, but not only. To be sure that this is possible, `PropertySourcesPlaceholderConfigurer` must be present in all application contexts that placeholders resolution is required.

In this blog post you will learn how to configure placeholders resolution in Spring 4 applications and how to inject different types of objects using `@Value` annotation, including JSR-310 Date-Time, JSR-354 Money & Currency or `java.util.Optional`.

## Registering `PropertySourcesPlaceholderConfigurer`

In Spring applications with no-xml configuration, a static `PropertySourcesPlaceholderConfigurer` bean must be registered in all application contexts.

To register `PropertySourcesPlaceholderConfigurer` simply add a static bean of the same type to the configuration together with the property source(s) you want to have access to. To import multiple property sources use `@PropertySources` annotation (prior to Java 8) or multiple `@PropertySource` annotations (Java 8).

```java
@Configuration
@PropertySource("classpath:application.properties")
@ComponentScan
class ApplicationConfig {

    @Bean
    public static PropertySourcesPlaceholderConfigurer placeholderConfigurer() {
        return new PropertySourcesPlaceholderConfigurer();
    }

}
```

The other way to add property source to the configurer is by calling its `setLocation` method:

```java
@Configuration
@ComponentScan
class ApplicationConfig {

    @Bean
    public static PropertySourcesPlaceholderConfigurer placeholderConfigurer() {
        PropertySourcesPlaceholderConfigurer c = new PropertySourcesPlaceholderConfigurer();
        c.setLocation(new ClassPathResource("application.properties"));
        return c;
    }

}
```

## Injecting simple properties

Now you can easily access the properties with `@Value` annotation and placeholders:

```
@Value("${my.string.property}")
private String stringProperty;
@Value("${my.int.property}")
private int intProperty;
@Value("${my.boolean.property}")
private boolean boolProperty;       
```

The properties are defined in the `application.properties` file:

```
my.string.property=Some text
my.int.property=42
my.boolean.property=true
```

When the property cannot be resolved you will get an exception:

```
java.lang.IllegalArgumentException: Could not resolve placeholder 'placeholder' in string value "${placeholder}"
```

## Ignoring unresolvable placeholders

If you want to ignore all unresolvable placeholders automatically, set a proper flag of the configurer:

```java
PropertySourcesPlaceholderConfigurer c = new PropertySourcesPlaceholderConfigurer();

c.setIgnoreUnresolvablePlaceholders(true);
```

## Default values

Default values can be provided with the following syntax:

```java
@Value("${my.string.property:Sample}")
private String stringProperty;
```

Empty default value is also supported, which results in an empty `stringProperty`:

```java
@Value("${my.string.property:}")
private String stringProperty;
```

## Null Values

If you want empty values to be treated as `null` you may set a `nullValue` property of the configurer like this:

```java
PropertySourcesPlaceholderConfigurer c = new PropertySourcesPlaceholderConfigurer();
c.setNullValue("");
```

This can be helpful, especially wile working with `java.util.Optional` (see below).

## Injecting non-simple properties

To inject complex properties using `@Value` annotation you need to make a Spring’s `ConversionService` available in the application context . Registering default conversion service gives the possibility to inject lists, arrays and other convertible types. Usually, in the Spring’s servlet context the `ConversionService` will be registered (e.g. via `@EnableWebMvc`), but in order to manually register it you can use the following code. Please note, the name of the bean must be `conversionService`:

```java
@Bean
public static ConversionService conversionService() {
    return new DefaultFormattingConversionService();
}
```

`DefaultFormattingConversionService` supports all common converters and formatters, including formatters for JSR-354 Money & Currency, JSR-310 Date-Time and/or Joda-Time.

### Injecting list / arrays

To inject a list or an array from a property you define the property’s value with comma separated string:

```
my.intList.property=1,2,3,4,5
my.stringArray.property=1,2,3,4,5
```

And inject them like this:

```java
@Value("${my.intList.property}")
private List<Integer> intList;

@Value("${my.stringArray.property}")
private List<Integer> stringArray;
```

### Injecting java.util.Optional

Java 8’s `Optional` gives a great opportunity to work with optional properties. The trick with injecting `Optional` with `@Value` is that property values must be parsed to `null` value and to achieve that `nullValue` property of the configurer must be set accordingly (as shown earlier).

```java
@Value("${my.optional.property:}")
private Optional<String> optional;
```

If there is no property `my.optional.property`, `optional` will contain `Optional.empty` and therefore it can be nicely used in the code:

```java
if (optional.isPresent()) {
    // do something cool
}
```

### Injecting `java.time` types

The `ConversionService` registered contains formatters for JSR-310 Date-Time. The below examples are for `LocalDate` and `LocalDateTime` in the current locale:

```
# format for en_US locale
my.localDate.property=9/28/15
my.localDateTime.property=9/28/15 10:05 PM
```

```java
@Value("${my.localDate.property}")
private LocalDate localDate;
@Value("${my.localDateTime.property}")
private LocalDateTime localDateTime;
```

### Injecting `javax.money` types

Once `javax.money` is on the classpath, you can inject `MonetaryAmount` and `CurrencyUnit`:

```
my.monetaryAmount.property=USD 299
my.currencyUnit.property=USD
```

```java
@Value("${my.monetaryAmount.property}")
private MonetaryAmount monetaryAmount;
@Value("${my.currencyUnit.property}")
private CurrencyUnit currencyUnit;
```

### Injecting custom types

WIth `ConversionService` it is relatively easy to register custom converters. In the below example `java.util.Pattern` object will be created from a string value: `my.pattern.property=[0-9].*`. In order to achieve that we need to add custom converted:

```java
DefaultFormattingConversionService cs = new DefaultFormattingConversionService();

cs.addConverter(String.class, Pattern.class, (Converter<String, Pattern>) Pattern::compile);
```

Now the property can be injected like below:

```java
@Value("${my.pattern.property}")
private Pattern pattern;
```

## Extras - Access Spring’s properties in Thymeleaf view

If you are working with [Thymeleaf](http://thymeleaf.org/) and you want to access properties registered with Spring’s environment (with `PropertySourcesPlaceholderConfigurer` or simply with `@PropertySource`) you may use Thymeleaf’s ability to access Spring beans properties using SpringEL’s syntax: ${@myBean.doSomething()}. All properties are available via `Environment` interface, so accessing it in Thymeleaf is as simple as calling its `getProperty` method:

```html
 <div th:fragment="footer" th:align="center">
    <span th:text="${@environment.getProperty('app.version')}"></span>
 </div>
```

## Closing note

You may find some simple usage of `@Value` annotation and `PropertySourcesPlaceholderConfigurer` in my Spring’s quickstart archetype here: <https://github.com/kolorobot/spring-mvc-quickstart-archetype>.

If you are working with Spring Boot, you may want to read about type safe configuration properties: <http://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#boot-features-external-config-typesafe-configuration-properties>
