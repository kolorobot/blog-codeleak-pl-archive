---
title: "JUnit 5 and Selenium - Using Selenium built-in `PageFactory` to implement Page Object Pattern"
date: 2019-10-08T22:19:00.003+02:00
updated: 2023-02-09T22:44:39.557+01:00
author: "Rafał Borowiec"
tags: ["junit 5", "selenium"]
original_url: https://blog.codeleak.pl/2019/10/junit-5-and-selenium-using-selenium.html
---

# JUnit 5 and Selenium - Using Selenium built-in `PageFactory` to implement Page Object Pattern

Selenium is a set of tools and libraries supporting browser automation and it is mainly used for web applications testing. One of the Selenium's components is a Selenium WebDriver that provides client library, the JSON wire protocol (protocol to communicate with the browser drivers) and browser drivers. One of the main advantages of Selenium WebDriver is that it supported by all major programming languages and it can run on all major operating systems.

In this part of the *JUnit 5 with Selenium WebDriver - Tutorial* I will go though the implementation of Page Object pattern with Selenium's built-in PageFactory support class. `PageFactory` provides mechanism to initialize any Page Object that declares `WebElement` or `List<WebElement>` fields annotated with `@FindBy` annotation.

## Table of contents

- [About this Tutorial](#about-this-tutorial)
- [Introducing Page Object Pattern](#introducing-page-object-pattern)
- [Page API aka Page Object](#page-api-aka-page-object)
- [Creating tests](#creating-tests)
- [Using Selenium built-in PageFactory to implement Page Object Pattern](#using-selenium-built-in-pagefactory-to-implement-page-object-pattern)
  - [`@FindBys`](#findbys)
  - [`@FindAll`](#findall)
- [`PageFactory` - initialize the Page object](#pagefactory-initialize-the-page-object)
- [Locating elements](#locating-elements)
- [`@CacheLookup`](#cachelookup)
- [Running the tests](#running-the-tests)
- [Next steps](#next-steps)

## Changes

- *2023-02* - The project was updated to Gradle 7.2 and Java 17. Dependencies updated to newer versions.

## About this Tutorial

You are reading the second part of the *JUnit 5 with Selenium WebDriver - Tutorial*.

All articles in this tutorial:

- Part 1 - [Setup the project from the ground up - Gradle with JUnit 5 and Jupiter Selenium](../../../2019/09/junit-5-and-selenium-setup-project-with/index.md)
- Part 2 - [Using Selenium built-in `PageFactory` to implement Page Object Pattern](../../../2019/10/junit-5-and-selenium-using-selenium/index.md)
- Part 3 - [Improving the project configuration - executing tests in parallel, tests execution order, parameterized tests, AssertJ and more](../../../2019/12/junit-5-and-selenium-improving-project/index.md)

> The source code for this tutorial can be found on [Github](https://github.com/kolorobot/junit5-selenium-todomvc-demo)

## Introducing Page Object Pattern

We will be creating tests for JavaScript based Todo application available here: <http://todomvc.com/examples/vanillajs>. The application is created as a Single Page Application (SPA) and uses local storage as a task repository. The possible scenarios to be implemented include adding and editing todo, removing todo, marking single or multiple todos as done. The implementation will be done using Page Object pattern.

The goal of Page Object pattern is to abstract the application pages and functionality from the actual tests. Page Object pattern improves re-usability of the code across tests and fixtures but also makes the code easier to maintain.

> You can read more about this pattern in the Martin Fowler article: <https://martinfowler.com/bliki/PageObject.html>

## Page API aka Page Object

We will start the project from modelling the [TodoMVC](http://todomvc.com/examples/vanillajs) page as Page Object. This object will be representing the page API that will be used in tests. The API itself can be modelled using an interface. If you look at the methods of the below interface you notice that the methods are just user functions that are available on the page. User can *create todo*, user can *rename todo* or he can *remove todo*:

```java
public interface TodoMvc {
    void navigateTo();
    void createTodo(String todoName);
    void createTodos(String... todoNames);
    int getTodosLeft();
    boolean todoExists(String todoName);
    int getTodoCount();
    List<String> getTodos();
    void renameTodo(String todoName, String newTodoName);
    void removeTodo(String todoName);
    void completeTodo(String todoName);
    void completeAllTodos();
    void showActive();
    void showCompleted();
    void clearCompleted();
}
```

The above interface (obviously) hides all the implementation details but also it does not expose any Selenium WebDriver details to the potential client (in our case the client = the test method). In fact, it has no relation to Selenium WebDriver whatsoever. So in theory, we could have different implementations of this page for different devices (e.g. mobile native application, desktop application and web application).

## Creating tests

With the page API defined we can jump directly to creating the test methods. We will work on the page implementation after we confirm the API can be used for creating tests. This design technique allows to focus on the real usage of the application instead of jumping into implementation details too early.

The following tests were created:

```java
@ExtendWith(SeleniumJupiter.class)
@DisplayName("Managing Todos")
class TodoMvcTests {

    private TodoMvc todoMvc;

    private final String buyTheMilk = "Buy the milk";
    private final String cleanupTheRoom = "Clean up the room";
    private final String readTheBook = "Read the book";

    @BeforeEach
    void beforeEach(ChromeDriver driver) {
        this.todoMvc = null;
        this.todoMvc.navigateTo();
    }

    @Test
    @DisplayName("Creates Todo with given name")
    void createsTodo() {

        todoMvc.createTodo(buyTheMilk);

        assertAll(
                () -> assertEquals(1, todoMvc.getTodosLeft()),
                () -> assertTrue(todoMvc.todoExists(buyTheMilk))
        );
    }

    @Test
    @DisplayName("Creates Todos all with the same name")
    void createsTodosWithSameName() {

        todoMvc.createTodos(buyTheMilk, buyTheMilk, buyTheMilk);

        assertEquals(3, todoMvc.getTodosLeft());

        todoMvc.showActive();

        assertEquals(3, todoMvc.getTodoCount());
    }

    @Test
    @DisplayName("Edits inline double-clicked Todo")
    void editsTodo() {

        todoMvc.createTodos(buyTheMilk, cleanupTheRoom);

        todoMvc.renameTodo(buyTheMilk, readTheBook);

        assertAll(
                () -> assertFalse(todoMvc.todoExists(buyTheMilk)),
                () -> assertTrue(todoMvc.todoExists(readTheBook)),
                () -> assertTrue(todoMvc.todoExists(cleanupTheRoom))
        );
    }

    @Test
    @DisplayName("Removes selected Todo")
    void removesTodo() {

        todoMvc.createTodos(buyTheMilk, cleanupTheRoom, readTheBook);

        todoMvc.removeTodo(buyTheMilk);

        assertAll(
                () -> assertFalse(todoMvc.todoExists(buyTheMilk)),
                () -> assertTrue(todoMvc.todoExists(cleanupTheRoom)),
                () -> assertTrue(todoMvc.todoExists(readTheBook))
        );
    }

    @Test
    @DisplayName("Toggles selected Todo as completed")
    void togglesTodoCompleted() {
        todoMvc.createTodos(buyTheMilk, cleanupTheRoom, readTheBook);

        todoMvc.completeTodo(buyTheMilk);
        assertEquals(2, todoMvc.getTodosLeft());

        todoMvc.showCompleted();
        assertEquals(1, todoMvc.getTodoCount());

        todoMvc.showActive();
        assertEquals(2, todoMvc.getTodoCount());
    }

    @Test
    @DisplayName("Toggles all Todos as completed")
    void togglesAllTodosCompleted() {
        todoMvc.createTodos(buyTheMilk, cleanupTheRoom, readTheBook);

        todoMvc.completeAllTodos();
        assertEquals(0, todoMvc.getTodosLeft());

        todoMvc.showCompleted();
        assertEquals(3, todoMvc.getTodoCount());

        todoMvc.showActive();
        assertEquals(0, todoMvc.getTodoCount());
    }

    @Test
    @DisplayName("Clears all completed Todos")
    void clearsCompletedTodos() {
        todoMvc.createTodos(buyTheMilk, cleanupTheRoom);
        todoMvc.completeAllTodos();
        todoMvc.createTodo(readTheBook);

        todoMvc.clearCompleted();
        assertEquals(1, todoMvc.getTodosLeft());

        todoMvc.showCompleted();
        assertEquals(0, todoMvc.getTodoCount());

        todoMvc.showActive();
        assertEquals(1, todoMvc.getTodoCount());
    }
}
```

> More: If you are new to JUnit 5 you can read this introduction on my blog: [https://blog.codeleak.pl/2017/10/junit-5-basics.html](../../../2017/10/junit-5-basics/index.md). There is also a newer version of this article written in polish: <https://blog.qalabs.pl/junit/junit5-pierwsze-kroki/>.

In the above test class we see that before each test the ChromeDriver is initialized and injected into the setup method (`@BeforeEach`) by the Selenium Jupiter extension (hence the `@ExtendWith(SeleniumJupiter.class)`). The driver object will be used to initialize the page object.

There are different page objects modelling techniques and a lot depends on the characteristics of the project you are working on. You may want to use interfaces but it is not required. You may want to consider modelling on a bit lower level of abstraction, where the API is exposing more detailed methods like for example `setTodoInput(String value)`, `clickSubmitButton()`.

## Using Selenium built-in PageFactory to implement Page Object Pattern

As of now we have an interface that models the behaviour of the TodoMVC page and we have the failing tests that are using the API. The next step is to actually implement the page object. In order to do so, we will use Selenium built-in `PageFactory` class and its utilities.

`PageFactory` class simplifies implementation of Page Object pattern. The class provides mechanism to initialize any Page Object that declares `WebElement` or `List<WebElement>` fields annotated with `@FindBy` annotation. The `PageFactory` and all other annotations supporting implementation of Page Object pattern are available in the `org.openqa.selenium.support` package.

The below `TodoMvcPage` class implements the interface we created earlier. It declares several fields annotated with `@FindBy` annotation. It also declares a constructor taking `WebDriver` parameter used by the factory to initialize the fields:

```java
public class TodoMvcPage implements TodoMvc {

    private final WebDriver driver;

    private static final By byTodoEdit = By.cssSelector("input.edit");
    private static final By byTodoRemove = By.cssSelector("button.destroy");
    private static final By byTodoComplete = By.cssSelector("input.toggle");

    @FindBy(className = "new-todo")
    private WebElement newTodoInput;

    @FindBy(css = ".todo-count > strong")
    private WebElement todoCount;

    @FindBy(css = ".todo-list li")
    private List<WebElement> todos;

    @FindBy(className = "toggle-all")
    private WebElement toggleAll;

    @FindBy(css = "a[href='#/active']")
    private WebElement showActive;

    @FindBy(css = "a[href='#/completed']")
    private WebElement showCompleted;

    @FindBy(className = "clear-completed")
    private WebElement clearCompleted;

    public TodoMvcPage(WebDriver driver) {
        this.driver = driver;
    }

    @Override
    public void navigateTo() {
        driver.get("http://todomvc.com/examples/vanillajs");
    }

    public void createTodo(String todoName) {
        newTodoInput.sendKeys(todoName + Keys.ENTER);
    }

    public void createTodos(String... todoNames) {
        for (String todoName : todoNames) {
            createTodo(todoName);
        }
    }

    public int getTodosLeft() {
        return Integer.parseInt(todoCount.getText());
    }

    public boolean todoExists(String todoName) {
        return getTodos().stream().anyMatch(todoName::equals);
    }

    public int getTodoCount() {
        return todos.size();
    }

    public List<String> getTodos() {
        return todos
                .stream()
                .map(WebElement::getText)
                .collect(Collectors.toList());
    }

    public void renameTodo(String todoName, String newTodoName) {
        WebElement todoToEdit = getTodoElementByName(todoName);
        doubleClick(todoToEdit);

        WebElement todoEditInput = find(byTodoEdit, todoToEdit);
        executeScript("arguments[0].value = ''", todoEditInput);

        todoEditInput.sendKeys(newTodoName + Keys.ENTER);
    }

    public void removeTodo(String todoName) {
        WebElement todoToRemove = getTodoElementByName(todoName);
        moveToElement(todoToRemove);
        click(byTodoRemove, todoToRemove);
    }

    public void completeTodo(String todoName) {
        WebElement todoToComplete = getTodoElementByName(todoName);
        click(byTodoComplete, todoToComplete);
    }

    public void completeAllTodos() {
        toggleAll.click();
    }

    public void showActive() {
        showActive.click();
    }

    public void showCompleted() {
        showCompleted.click();
    }

    public void clearCompleted() {
        clearCompleted.click();
    }

    private WebElement getTodoElementByName(String todoName) {
        return todos
                .stream()
                .filter(el -> todoName.equals(el.getText()))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("Todo with name " + todoName + " not found!"));
    }

    private WebElement find(By by, SearchContext searchContext) {
        return searchContext.findElement(by);
    }

    private void click(By by, SearchContext searchContext) {
        WebElement element = searchContext.findElement(by);
        element.click();
    }

    private void moveToElement(WebElement element) {
        new Actions(driver).moveToElement(element).perform();
    }

    private void doubleClick(WebElement element) {
        new Actions(driver).doubleClick(element).perform();
    }

    private void executeScript(String script, Object... arguments) {
        ((JavascriptExecutor) driver).executeScript(script, arguments);
    }
}
```

`@FindBy` is not the only annotation used to lookup elements in a Page Object. There are also `@FindBys` and `@FindAll`.

### `@FindBys`

`@FindBys` annotation is used to mark a field on a Page Object to indicate that lookup should use a series of `@FindBy` tags. In this example, Selenium will search for the element with `class = "button"` that is **inside** the element with `id = "menu"`:

```java
@FindBys({
  @FindBy(id = "menu"),
  @FindBy(className = "button")
})
private WebElement element;
```

### `@FindAll`

`@FindAll` annotation is used to mark a field on a Page Object to indicate that lookup should use a series of @FindBy tags. In this example, Selenium will search for all the elements with `class = "button"` **and** all the elements with `id = "menu"`. Elements are not guaranteed to be in document order:

```java
@FindAll({
  @FindBy(id = "menu"),
  @FindBy(className = "button")
})
private List<WebElement> webElements;
```

## `PageFactory` - initialize the Page object

`PageFactory` provides several static methods to initialize Page Objects. In our test, in `beforeEach()` method we need to initialize `TodoMvcPage` object:

```java
@BeforeEach
void beforeEach(ChromeDriver driver) {
    this.todoMvc = PageFactory.initElements(driver, TodoMvcPage.class);
    this.todoMvc.navigateTo();
}
```

The `PageFactory` initializes the object using reflection and then it initializes all the `WebElement` or `List<WebElement>` fields marked with `@FindBy` annotation (no lookup is done at this momment, fields are proxied). Using this method requires that the Page Object has a single parameter constructor accepting `WebDriver` object.

## Locating elements

So when the elements are located? The lookup takes place each time the field is accessed. So the for example, when we execute the code: `newTodoInput.sendKeys(todoName + Keys.ENTER);` in `createTodo()` method the actual instruction that is executed is: `driver.findElement(By.className('new-todo')).sendKeys(todoName + Keys.ENTER)`. We can expect that potential exception that element was not found is thrown not during the object initialization but during the first element lookup.

> Selenium uses [Proxy](https://en.wikipedia.org/wiki/Proxy_pattern#Java) pattern to achieve described behaviour.

## `@CacheLookup`

There are situations when there is no need to lookup for elements each time the annotated field is accessed. In such a case we can use `@CacheLookup` annotation. In our example the input field does not change on the page so its lookup can be cached:

```java
@FindBy(className = "new-todo")
@CacheLookup
private WebElement newTodoInput;
```

## Running the tests

It is high time to execute the tests. It can be done either from IDE or using the terminal:

```
./gradlew clean test --tests "*TodoMvcTests"
```

The build was successful with all tests passed:

```
> Task :test

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > editsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesTodoCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > removesTodo() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > togglesAllTodosCompleted() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > createsTodosWithSameName() PASSED

pl.codeleak.demos.selenium.todomvc.TodoMvcTests > clearsCompletedTodos() PASSED

BUILD SUCCESSFUL in 27s
3 actionable tasks: 3 executed
```

## Next steps

In Part 3 - [Improving the project configuration - executing tests in parallel, tests execution order, parameterized tests, AssertJ and more](../../../2019/12/junit-5-and-selenium-improving-project/index.md) - you will learn how to utilize built-in features of JUnit 5 to improve your project configuration in terms of speed execution but not only. You will also learn about improving the project by utilizing certain Selenium Jupiter features.
