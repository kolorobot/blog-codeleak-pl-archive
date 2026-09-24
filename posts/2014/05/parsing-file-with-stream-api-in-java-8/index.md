---
title: "Parsing a file  with Stream API in Java 8"
date: 2014-05-24T20:55:00.002+02:00
updated: 2014-05-31T14:20:38.661+02:00
author: "Rafał Borowiec"
tags: ["java", "java 8"]
original_url: https://blog.codeleak.pl/2014/05/parsing-file-with-stream-api-in-java-8.html
---

# Parsing a file  with Stream API in Java 8

Streams are everywhere in Java 8. Just look around and for sure you will find them. It also applies to `java.io.BufferedReader`. Parsing a file in Java 8 with Stream API is extremely easy.

I have a CSV file that I want to be read. An example below:

```
username;visited
jdoe;10
kolorobot;4
```

A contract for my reader is to provide a header as list of strings and all records as list of lists of strings. My reader accepts `java.io.Reader` as a source to read from.   
  
I will start with reading the header. The algorithm for reading the header is as follows:

- Open a source for reading,
- Get the first line and parse it,
- Split line by a separator,
- Get the first line and parse it,
- Convert the line to list of strings and return.

And the implementation:

```java
class CsvReader {

    private static final String SEPARATOR = ";";

    private final Reader source;

    CsvReader(Reader source) {
        this.source = source;
    }
    List<String> readHeader() {
        try (BufferedReader reader = new BufferedReader(source)) {
            return reader.lines()
                    .findFirst()
                    .map(line -> Arrays.asList(line.split(SEPARATOR)))
                    .get();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }    
}
```

Fairly simple. Self-explanatory. Similarly, I created a method to read all records. The algorithm for reading the records is as follows:

- Open a source for reading,
- Skip the first line,
- Split line by a separator,
- Apply a mapper on each line that maps a line to a list of strings

And the implementation:

```java
class CsvReader {

    List<List<String>> readRecords() {
        try (BufferedReader reader = new BufferedReader(source)) {
            return reader.lines()
                    .substream(1)
                    .map(line -> Arrays.asList(line.split(separator)))
                    .collect(Collectors.toList());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }  
}
```

Nothing fancy here. What you could notice that a mapper in both methods is exactly the same. In fact, it can be easily extracted to a variable:

```java
Function<String, List<String>> mapper 
    = line -> Arrays.asList(line.split(separator));
```

To finish up, I created a simple test.

```java
public class CsvReaderTest {

    @Test
    public void readsHeader() {
        CsvReader csvReader = createCsvReader();
        List<String> header = csvReader.readHeader();
        assertThat(header)
                .contains("username")
                .contains("visited")
                .hasSize(2);
    }

    @Test
    public void readsRecords() {
        CsvReader csvReader = createCsvReader();
        List<List<String>> records = csvReader.readRecords();
        assertThat(records)
                .contains(Arrays.asList("jdoe", "10"))
                .contains(Arrays.asList("kolorobot", "4"))
                .hasSize(2);
    }

    private CsvReader createCsvReader() {
        try {
            Path path = Paths.get("src/test/resources", "sample.csv");
            Reader reader = Files.newBufferedReader(
                path, Charset.forName("UTF-8"));
            return new CsvReader(reader);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
```
