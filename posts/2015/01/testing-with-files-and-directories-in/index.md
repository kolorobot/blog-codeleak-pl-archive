---
title: "Testing with files and directories in JUnit with @Rule"
date: 2015-01-12T20:00:00.000+01:00
updated: 2015-01-12T22:14:28.807+01:00
author: "Rafał Borowiec"
tags: ["unit testing"]
original_url: https://blog.codeleak.pl/2015/01/testing-with-files-and-directories-in.html
---

# Testing with files and directories in JUnit with @Rule

![](junit.gif)

Testing with Files and directories in JUnit is easy thanks to `TemporaryFolder` `@Rule`.   
In JUnit rules (`@Rule`) can be used as an alternative or an addition to fixture setup and   
cleanup methods (`org.junit.Before`, `org.junit.After`, `org.junit.BeforeClass`, and `org.junit.AfterClass`), but they are more powerful, and can be more easily shared between projects and classes.

## The code to be tested

```java
public void writeTo(String path, String content) throws IOException {
    Path target = Paths.get(path);
    if (Files.exists(target)) {
        throw new IOException("file already exists");
    }
    Files.copy(new ByteArrayInputStream(content.getBytes("UTF8")), target);
}
```

The above method can write a given String content to a non existing file. There are two cases that can be tested.

## The Test

```java
public class FileWriterTest {

    private FileWriter fileWriter = new FileWriter();

    @Rule
    public TemporaryFolder temporaryFolder = new TemporaryFolder();

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Test
    public void throwsErrorWhenTargetFileExists() throws IOException {
        // arrange
        File output = temporaryFolder.newFile("output.txt");

        thrown.expect(IOException.class);
        thrown.expectMessage("file already exists");

        // act
        fileWriter.writeTo(output.getPath(), "test");
    }

    @Test
    public void writesContentToFile() throws IOException {
        // arrange
        File output = temporaryFolder.newFolder("reports")
                .toPath()
                .resolve("output.txt")
                .toFile();

        // act
        fileWriter.writeTo(output.getPath(), "test");

        // assert
        assertThat(output)
                .hasContent("test")
                .hasExtension("txt")
                .hasParent(resolvePath("reports"));
    }

    private String resolvePath(String folder) {
        return temporaryFolder
                .getRoot().toPath()
                .resolve(folder)
                .toString();
    }
}
```

The `TemporaryFolder` rule provides two method to manage files and directories: `newFile` and `newFolder`. Both method return desired object under the temporary folder created in the setup method. In case the path of the temporary folder itself is needed `getRoot` method of `TemporaryFolder` can be used.

Everything that will be added to the temp folder during tests will be automatically removed when test finishes, despite it was successful or not.

This example can be found in my [`unit-testing-demo`](https://github.com/kolorobot/unit-testing-demo) project on GitHub along with many other examples.

Interested in more articles about Unit Testing on my blog? See: <http://blog.codeleak.pl/search/label/unit%20testing>
