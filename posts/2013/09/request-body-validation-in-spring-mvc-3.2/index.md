---
title: "Different ways of validating @RequestBody in Spring MVC with @Valid annotation"
date: 2013-09-22T19:48:00.001+02:00
updated: 2016-03-30T00:14:22.119+02:00
author: "Rafał Borowiec"
tags: ["spring mvc"]
original_url: https://blog.codeleak.pl/2013/09/request-body-validation-in-spring-mvc-3.2.html
---

# Different ways of validating @RequestBody in Spring MVC with @Valid annotation

In Spring MVC the [@RequestBody](https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/web/bind/annotation/RequestBody.html) annotation indicates a method parameter should be bound to a body of the request. @RequestBody parameter can treated as any other parameter in a [@RequestMapping](https://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/web/bind/annotation/RequestMapping.html) method and therefore it can also be validated by a standard validation mechanism.

In this post I will show 3 ways of validating the @RequestBody parameter in your Spring MVC application.

> Note: This blog post got a solid update (30/03/2016). The source code got migrated to new repository and it is Spring Boot driven. If you still prefer classic Spring MVC application you may use my [spring-mvc-quickstart-archetype](https://github.com/kolorobot/spring-mvc-quickstart-archetype)

## Task @RestController

In my sample application I want to create a new Task with non blank name and description. In order to do it I create an API endpoint that supports POST method and accepts Task JSON object.

Let’s start with the task

```java
public class Task {

    @NotBlank(message = "Task name must not be blank!")
    private String name;

    @NotBlank(message = "Task description must not be blank!")
    private String description;

    // getters and setters

}
```

To handle the task we need a @RestController:

```java
@RestController // since Spring 4.0
@RequestMapping(value = "task")
public class TaskController {

    @RequestMapping(value = "", method = RequestMethod.POST)
    public Task post(Task task) {
        // create a task   
    }
}
```

## ValidationError object

Before we jump into a validation let’s create the ValidationError object that holds validation errors:

```java
public class ValidationError {

    @JsonInclude(JsonInclude.Include.NON_EMPTY)
    private List<String> errors = new ArrayList<>();

    private final String errorMessage;

    public ValidationError(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public void addValidationError(String error) {
        errors.add(error);
    }

    public List<String> getErrors() {
        return errors;
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}
```

The sample JSON error:

```json
{
  "errorMessage": "Validation failed. 1 error(s)",
  "errors": [
    "Task name must not be blank!"
  ]
}
```

The ValidationError can be easily created from BindingResult. We may need a simple helper in order to do so:

```java
public class ValidationErrorBuilder {

    public static ValidationError fromBindingErrors(Errors errors) {
        ValidationError error = new ValidationError("Validation failed. " + errors.getErrorCount() + " error(s)");
        for (ObjectError objectError : errors.getAllErrors()) {
            error.addValidationError(objectError.getDefaultMessage());
        }
        return error;
    }
}
```

The next thing we need to do is the actual validation. So let’s do it.

## Validation with @ExceptionHandler

As of [Spring 3.1](http://blog.goyello.com/2011/12/16/enhancements-spring-mvc31/) the @RequestBody method argument can be annotated with @Valid or @Validated annotation to invoke automatic validation.

In such a case Spring automatically performs the validation and in case of error MethodArgumentNotValidException is thrown.

Optional @ExceptionHandler method may be easily created to add custom behavior for handling this type of exception. MethodArgumentNotValidException holds both the parameter that failed the validation and the result of validation.

Now, we can easily extract error messages and return it in an error object as JSON.

```java
@RestController
@RequestMapping("task")
public class TaskController {

    @RequestMapping(value = "", method = RequestMethod.POST)
    public Task createTask(@Valid @RequestBody Task task) {
        return task;
    }

    @ExceptionHandler
    @ResponseStatus(value = HttpStatus.BAD_REQUEST)
    public ValidationError handleException(MethodArgumentNotValidException exception) {
        return createValidationError(exception);
    }

    private ValidationError createValidationError(MethodArgumentNotValidException e) {
        return ValidationErrorBuilder.fromBindingErrors(exception.getBindingResult());
    }
}
```

> Note: Exception handler method does not need to be located in the same controller class. It can be a global handler for all you API calls.

## Validation with @ControllerAdvice

@ControllerAdvice is a specialization of a @Component that is used to define @ExceptionHandler, @InitBinder, and @ModelAttribute methods that apply to all @RequestMapping methods.

As of Spring 4 @ControllerAdvice may be configured to support defined subset of controllers, whereas the default behavior can be still utilized.

> Note: If you want to learn more read this article: [@ControllerAdvice improvements in Spring 4](../../../2013/11/controlleradvice-improvements-in-spring/index.md)

To assist only TaskController, we may create the following @ControllerAdvice:

```java
@ControllerAdvice(assignableTypes = TaskController2.class)
public class TaskController2Advice extends ResponseEntityExceptionHandler {

    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException exception, HttpHeaders headers, HttpStatus status, WebRequest request) {
        ValidationError error = ValidationErrorBuilder.fromBindingErrors(exception.getBindingResult());
        return super.handleExceptionInternal(exception, error, headers, status, request);
    }
}
```

## Validation with Errors/BindingResult object

As of Spring 3.2 @RequestBody method argument may be followed by Errors object, hence allowing handling of validation errors in the same @RequestMapping. Let’s look at the code:

```java
@RestController
@RequestMapping("task")
public class TaskController3 {

    @RequestMapping(value = "", method = RequestMethod.POST)
    public ResponseEntity createTask(@Valid @RequestBody Task task, Errors errors) {
        if (errors.hasErrors()) {
            return ResponseEntity.badRequest().body(ValidationErrorBuilder.fromBindingErrors(errors));
        }
        return ResponseEntity.ok(task);
    }
}
```

## Integration testing

All three approaches produce exactly the same result in case of validation error. We can quickly check that using an integration test. For each solution the same test will pass.

> Note: The below code uses org.skyscreamer.jsonassert.JSONAssert. As of Spring 4.1 it is much easier to test JSON content in integration tests.

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class TaskControllerTest2 {

    @Autowired
    private WebApplicationContext wac;
    private MockMvc mockMvc;

    @Before
    public void setup() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(this.wac).build();
    }

    @Test
    public void validRequestReturns200OK() throws Exception {
        String jsonTask = String.format("{\"name\": \"Task 1\",\"description\": \"Description\"}");

        this.mockMvc.perform(post("task")
            .contentType(MediaType.APPLICATION_JSON)
            .content(jsonTask))
                    .andDo(print())
                    .andExpect(status().isOk())
                    .andExpect(content().json(jsonTask)); // Spring 4.1. Requires org.skyscreamer.jsonassert.JSONAssert
    }

    @Test
    public void invalidNameError() throws Exception {
        String jsonTaskWithBlankName = String.format("{\"name\": \"\",\"description\": \"Description\"}");

        this.mockMvc.perform(post("task")
            .contentType(MediaType.APPLICATION_JSON)
            .content(jsonTaskWithBlankName))
                    .andDo(print())
                    .andExpect(status().isBadRequest())
                    .andExpect(content().json("{\"errors\":[\"Task name must not be blank!\"],\"errorMessage\":\"Validation failed. 1 error(s)\"}"));

    }
}
```

## Source code

The source code contains all three approaches, so that you can quickly compare them: <https://github.com/kolorobot/spring-mvc-beanvalidation11-demo>

## Similar articles

In case you find this article interesting, have a look at my other blog posts:

- [Better Error Messages with Bean Validation 1.1](../../../2014/06/better-error-messages-with-bean/index.md)
- [Validation Groups in Spring MVC](../../../2014/08/validation-groups-in-spring-mvc/index.md)
- [Spring MVC Integration Testing: Assert the given model attribute(s) have global errors](../../../2014/08/spring-mvc-test-assert-given-model-attribute-global-errors/index.md)
- [Spring 4.1 and Java 8: java.util.Optional as a @RequestParam, @RequestHeader and @MatrixVariable in Spring MVC](../../../2014/07/Spring41-and-Java8-Optional-as-RequestParam-RequestHeader-MatrixVariable/index.md)
