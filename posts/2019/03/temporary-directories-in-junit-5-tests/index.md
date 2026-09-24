---
title: "Temporary directories in JUnit 5 Tests"
date: 2019-03-17T19:39:00.000+01:00
updated: 2019-03-24T22:21:42.711+01:00
author: "Rafał Borowiec"
tags: ["junit 5", "unit testing"]
original_url: https://blog.codeleak.pl/2019/03/temporary-directories-in-junit-5-tests.html
---

# Temporary directories in JUnit 5 Tests

JUnit 4 `TemporaryFolder` `@Rule` allowed developers to create tests utilizing temporary directories. With JUnit 5, the `@Rule`s are not supported hence testing files and directories requireds a little bit of additional work. Fortunately, with JUnit 5.4 there is a new built-in extension to handle temporary directories in tests. And it is extremely easy to use.

> Are you still working with JUnit 4? See my previous post on [testing with files and directories in JUnit 4 with TemporaryFolder @Rule](../../../2015/01/testing-with-files-and-directories-in/index.md)

## `@TempDir`

`@org.junit.jupiter.api.io.TempDir` annotation can be used in order to annotate class field or a parameter in a lifecycle (e.g. `@BeforeEach`) or test method of type `File` or `Path`. Once this is done, the temporary directory will be be created. The directory with its contents created during test execution will be deleted once the test method or class has finished execution.

## The code to be tested

In this simple example, we will test the `FileWriter` class, that has a single method writing text contents to a new file:

```java
public class FileWriter {

    public void writeTo(String path, String content) throws IOException {
        Path target = Paths.get(path);
        if (Files.exists(target)) {
            throw new IOException("file already exists");
        }
        Files.copy(new ByteArrayInputStream(content.getBytes(StandardCharsets.UTF_8)), target);
    }
}
```

## `@TempDir` as test method parameter

In this example, we will annotate test parameter with `@TempDir` annotation:

```java
import org.junit.jupiter.api.io.TempDir;

@Test
void writesContentToFile(@TempDir Path tempDir) throws IOException {
    // arrange
    Path output = tempDir
            .resolve("output.txt");

    // act
    fileWriter.writeTo(output.toString(), "test");

    // assert
    assertAll(
            () -> assertTrue(Files.exists(output)),
            () -> assertLinesMatch(List.of("test"), Files.readAllLines(output))
    );
}
```

## `@TempDir` as an instance field

```java
import org.junit.jupiter.api.io.TempDir;

class FileWriterTest {

    private FileWriter fileWriter = new FileWriter();

    @TempDir
    Path tempDir;

    @BeforeEach
    void beforeEach() {
        assertTrue(Files.isDirectory(this.tempDir));
    }

    @RepeatedTest(3)
    void throwsErrorWhenTargetFileExists() throws IOException {
        // arrange
        Path output = Files.createFile(
                tempDir.resolve("output.txt")
        );

        // act & assert
        IOException expectedException = assertThrows(IOException.class, () -> fileWriter.writeTo(output.toString(), "test"));
        assertEquals("file already exists", expectedException.getMessage());
    }
}
```

Based on the above example, we can see that each repetition of the test uses a new temporary directory (according to the standard test class lifecycle) hence the arrange section of the method executes with no error.

## Shared `@TempDir`

In case there is a need to share a temporary directory between test methods, we can create a static field and reuse the temporary directory like in the below example:

```java
import org.junit.jupiter.api.io.TempDir;

class FileWriterTest {

    private FileWriter fileWriter = new FileWriter();

    @TempDir
    static Path tempDir;

    @BeforeAll
    static void setUp() {
        assertTrue(Files.isDirectory(tempDir));
    }

    @RepeatedTest(3)
    void throwsErrorWhenTargetFileExists(RepetitionInfo repetitionInfo) throws IOException {
        // arrange
        Path output = Files.createFile(
                tempDir.resolve(repetitionInfo.getCurrentRepetition() + "_output.txt")
        );

        // act & assert
        IOException expectedException = assertThrows(IOException.class, () -> fileWriter.writeTo(output.toString(), "test"));
        assertEquals("file already exists", expectedException.getMessage());
    }
}
```

Please note, that arrange section of the test method creates unique file name per execution (using current repetition counter) as otherwise the `FileAlreadyExistsException` would have been thrown.

## Summary

With `@TempDir` you get possibility to work with temporary directories in tests with ease. There is no magic here: you annotate `Path` or `File` objects and inject as you need them. The rest is taken care by JUnit for you.

Find the examples on GitHub: <https://github.com/kolorobot/junit5-samples/tree/master/junit5-built-in-extensions>

## See also

- [Test Execution Order in JUnit 5](../../../2019/03/test-execution-order-in-junit-5/index.md)
- [Cleaner parameterized tests with JUnit 5](../../../2017/06/cleaner-parameterized-tests-with-junit-5/index.md)
- [JUnit 5 meets AssertJ](../../../2017/11/junit-5-meets-assertj/index.md)
