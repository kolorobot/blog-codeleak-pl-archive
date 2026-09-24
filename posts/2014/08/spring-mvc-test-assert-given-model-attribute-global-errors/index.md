---
title: "Spring MVC Integration Testing: Assert the given model attribute(s) have global errors"
date: 2014-08-05T06:24:00.000+02:00
updated: 2016-03-30T21:20:25.295+02:00
author: "Rafał Borowiec"
tags: ["spring mvc"]
original_url: https://blog.codeleak.pl/2014/08/spring-mvc-test-assert-given-model-attribute-global-errors.html
---

# Spring MVC Integration Testing: Assert the given model attribute(s) have global errors

![](logo-spring-io.png)

In order to report a global error in Spring MVC using Bean Validation we can create a custom class level constraint annotation. Global errors are not associated with any specific fields in the validated bean. In this article I will show how to write a test with Spring Test that verifies if the given model attribute has global validation errors.

> 30/03/2016 - The project referenced in this article got a solid upgrade, as well as the related blog post: [Different ways of validating @RequestBody in Spring MVC with @Valid annotation](../../../2013/09/request-body-validation-in-spring-mvc-3.2/index.md).

## Custom (Class Level) Constraint

For the sake of this article, I created a relatively simple class level constraint called `SamePassword`, validated by `SamePasswordValidator`:

```java
@Target({TYPE, ANNOTATION_TYPE})
@Retention(RUNTIME)
@Constraint(validatedBy = SamePasswordsValidator.class)
@Documented
public @interface SamePasswords {
    String message() default "passwords do not match";
    Class<?>[] groups() default {}; 
    Class<? extends Payload>[] payload() default {};
}
```

As you can see below, the validator is really simple:

```java
public class SamePasswordsValidator implements ConstraintValidator<SamePasswords, PasswordForm> {

    @Override
    public void initialize(SamePasswords constraintAnnotation) {}

    @Override
    public boolean isValid(PasswordForm value, ConstraintValidatorContext context) {
        if(value.getConfirmedPassword() == null) {
            return true;
        }
        return value.getConfirmedPassword()
                    .equals(value.getPassword());
    }
}
```

The `PasswordForm` is just a POJO with some constraint annotations, inclduing the once I have just created:

```java
@SamePasswords
public class PasswordForm {
    @NotBlank
    private String password;
    @NotBlank
    private String confirmedPassword;

    // getters and setters omitted for redability

}
```

## @Controller

The controller has two methods: to display the form and to handle the submission of the form:

```java
@Controller
@RequestMapping("globalerrors")
public class PasswordController {

    @RequestMapping(value = "password")
    public String password(Model model) {
        model.addAttribute(new PasswordForm());
        return "globalerrors/password";
    }

    @RequestMapping(value = "password", method = RequestMethod.POST)
    public String stepTwo(@Valid PasswordForm passwordForm, Errors errors) {
        if (errors.hasErrors()) {
            return "globalerrors/password";
        }
        return "redirect:password";
    }
}
```

When the password validation fails, a global error is registered in a `BindingResult` (`Errors` in the above example) object. We could then display this error on top of the form in a HTML page for example. In Thymeleaf this would be:

```html
<div th:if="${#fields.hasGlobalErrors()}">
  <p th:each="err : ${#fields.globalErrors()}" th:text="${err}">...</p>
</div>
```

## Integration Testing with Spring Test

Let’s setup an integration test:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@SpringApplicationConfiguration(classes = Application.class)
@WebAppConfiguration
public class AccountValidationIntegrationTest {

    @Autowired
    private WebApplicationContext wac;
    private MockMvc mockMvc;

    @Before
    public void setUp() throws Exception {
        mockMvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }
}
```

The first test verifies that sending a form with empty `password` and `confirmedPassword` fails:

```java
    @Test
    public void failsWhenEmptyPasswordsGiven() throws Exception {
        this.mockMvc.perform(post("/globalerrors/password")
                .param("password", "").param("confirmedPassword", ""))
                .andExpect(
                    model().attributeHasFieldErrors(
                        "passwordForm", "password", "confirmedPassword"
                    )
                )
                .andExpect(status().isOk())
                .andExpect(view().name("globalerrors/password"));
    }
```

In the above example, the test verifies if there are field errors for both `password` and `confirmedPassword` fields.

Similarly, I would like to verify that when given passwords do not match, I get a specific, global error. So I would expect something like this: `.andExpect(model().hasGlobalError("passwordForm", "passwords do not match"))`. Unfortunately, `ModelResultMatchers` returned by `MockMvcResultMatchers#model()` does not provide methods **to assert the given model attribute(s) have global errors**

Since it is not there, I created my own matcher that extends from `ModelResultMatchers`. The Java 8 version of the code is below:

```java
public class GlobalErrorsMatchers extends ModelResultMatchers {

    private GlobalErrorsMatchers() {
    }

    public static GlobalErrorsMatchers globalErrors() {
        return new GlobalErrorsMatchers();
    }

    public ResultMatcher hasGlobalError(String attribute, String expectedMessage) {
        return result -> {
            BindingResult bindingResult = getBindingResult(
                result.getModelAndView(), attribute
            );
            bindingResult.getGlobalErrors()
                .stream()
                .filter(oe -> attribute.equals(oe.getObjectName()))
                .forEach(oe -> assertEquals(
                    "Expected default message", expectedMessage, oe.getDefaultMessage())
                );
        };
    }

    private BindingResult getBindingResult(ModelAndView mav, String name) {
        BindingResult result = (BindingResult) mav.getModel().get(BindingResult.MODEL_KEY_PREFIX + name);
        assertTrue(
            "No BindingResult for attribute: " + name, result != null
        );
        assertTrue(
            "No global errors for attribute: " + name, result.getGlobalErrorCount() > 0
        );
        return result;
    }
}
```

With the above addition I am now able to verify global validation errors like here below:

```java
import static pl.codeleak.demo.globalerrors.GlobalErrorsMatchers.globalErrors;

@Test
public void failsWithGlobalErrorWhenDifferentPasswordsGiven() throws Exception {
    this.mockMvc.perform(post("/globalerrors/password")
            .param("password", "test").param("confirmedPassword", "other"))
            .andExpect(globalErrors().hasGlobalError(
                "passwordForm", "passwords do not match")
            )
            .andExpect(status().isOk())
            .andExpect(view().name("globalerrors/password"));
}
```

As you can see extending Spring Test’s matchers and providing you own is relatively easy and can be used to improve validation verification in an integration test.

## Resources

The source code for this article can be found here: <https://github.com/kolorobot/spring-mvc-beanvalidation11-demo>
