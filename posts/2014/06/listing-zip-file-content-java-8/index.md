---
title: "Listing a ZIP file contents with Stream API in Java 8"
date: 2014-06-09T23:51:00.000+02:00
updated: 2014-06-09T23:56:17.654+02:00
author: "Rafał Borowiec"
tags: ["java 8"]
original_url: https://blog.codeleak.pl/2014/06/listing-zip-file-content-java-8.html
---

# Listing a ZIP file contents with Stream API in Java 8

In Java 8 `java.util.zip.ZipFile` was equipped with a `stream` method that allows navigating over a ZIP file entries very easily. In this blog post I will show a bunch of examples showing how quickly we can navigate over ZIP file entries.

Note: For the purpose of this blog post I downloaded one of my GitHub repositories as a ZIP file and I copied it to `c:/tmp`.

## Prior to Java 7

Reading ZIP file entries in Java prior to Java 7 is a kind of hmm… tricky? This is how one can start hating Java while looking at this code:

```java
public class Zipper {
    public void printEntries(PrintStream stream, String zip)  {
        ZipFile zipFile = null;
        try {
            zipFile = new ZipFile(zip);
            Enumeration<? extends ZipEntry> entries = zipFile.entries();
            while (entries.hasMoreElements()) {
                ZipEntry zipEntry = entries.nextElement();
                stream.println(zipEntry.getName());
            }
        } catch (IOException e) {
            // error while opening a ZIP file
        } finally {
            if (zipFile != null) {
                try {
                    zipFile.close();
                } catch (IOException e) {
                    // do something
                }
            }
        }
    }
}
```

## Java 7

With Java 7 the same can be much simpler - thanks to `try-with-resources` but we are still “forced” to use `Enumeration` in order to navigate over ZIP file entries:

```java
public class Zipper {
    public void printEntries(PrintStream stream, String zip) {
        try (ZipFile zipFile = new ZipFile(zip)) {
            Enumeration<? extends ZipEntry> entries = zipFile.entries();
            while (entries.hasMoreElements()) {
                ZipEntry zipEntry = entries.nextElement();
                stream.println(zipEntry.getName());
            }
        } catch (IOException e) {
            // error while opening a ZIP file
        }
    }
}
```

## Using Stream API

The real fun starts with Java 8. As of Java 8 `java.util.zip.ZipFile` has a new method `stream` that returns an ordered stream over the ZIP file entries. This gives many opportunities while working with ZIP files in Java. Previous examples can be simply written as follows in Java 8:

```java
public class Zipper {
    public void printEntries(PrintStream stream, String zip) {
        try (ZipFile zipFile = new ZipFile(zip)) {
            zipFile.stream()
                    .forEach(stream::println);
        } catch (IOException e) {
            // error while opening a ZIP file
        }
    }
}
```

With Stream API we can play with the `ZipFile` in many ways. See below..

### Filtering and sorting ZIP file contents

```java
public void printEntries(PrintStream stream, String zip) {
    try (ZipFile zipFile = new ZipFile(zip)) {
        Predicate<ZipEntry> isFile = ze -> !ze.isDirectory();
        Predicate<ZipEntry> isJava = ze -> ze.getName().matches(".*java");
        Comparator<ZipEntry> bySize = 
                (ze1, ze2) -> Long.valueOf(ze2.getSize() - ze1.getSize()).intValue();
        zipFile.stream()
                .filter(isFile.and(isJava))
                .sorted(bySize)
                .forEach(ze -> print(stream, ze));
    } catch (IOException e) {
        // error while opening a ZIP file
    }
}

private void print(PrintStream stream, ZipEntry zipEntry) {
    stream.println(zipEntry.getName() + ", size = " + zipEntry.getSize());
}
```

While iterating over ZIP entries, I check if the entry is a file and if it matches a given name (harcoded in this example, for sake of simlicity) and then I sort it by size using a given comparator.

### Create files index of a ZIP file

In this example I group ZIP entries by first letter of a file name to create `Map<String, List<ZipEntry>>` index. The expected result should look similar to the below one:

```
a = [someFile/starting/with/an/A]
u = [someFile/starting/with/an/U, someOtherFile/starting/with/an/U]
```

Again, with Stream API it is really easy:

```java
public void printEntries(PrintStream stream, String zip) {
    try (ZipFile zipFile = new ZipFile(zip)) {
        Predicate<ZipEntry> isFile = ze -> !ze.isDirectory();
        Predicate<ZipEntry> isJava = ze -> ze.getName().matches(".*java");
        Comparator<ZipEntry> bySize =
            (ze1, ze2) -> Long.valueOf(ze2.getSize()).compareTo(Long.valueOf(ze1.getSize()));

        Map<String, List<ZipEntry>> result = zipFile.stream()
                .filter(isFile.and(isJava))
                .sorted(bySize)
                .collect(groupingBy(this::fileIndex));

        result.entrySet().stream().forEach(stream::println);

    } catch (IOException e) {
        // error while opening a ZIP file
    }
}

private String fileIndex(ZipEntry zipEntry) {
    Path path = Paths.get(zipEntry.getName());
    Path fileName = path.getFileName();
    return fileName.toString().substring(0, 1).toLowerCase();
}
```

### Find a text within a ZIP file entry

In the last example, I search for a `@Test` text occurrence in all files with `java` extension. This time I will utilize `BufferedReader`’s `lines` method that returns a stream of lines.

```java
public void printEntries(PrintStream stream, String zip) {

    try (ZipFile zipFile = new ZipFile(zip)) {
        Predicate<ZipEntry> isFile = ze -> !ze.isDirectory();
        Predicate<ZipEntry> isJava = ze -> ze.getName().matches(".*java");

        List<ZipEntry> result = zipFile.stream()
                .filter(isFile.and(isJava))
                .filter(ze -> containsText(zipFile, ze, "@Test"))
                .collect(Collectors.toList());

        result.forEach(stream::println);

    } catch (IOException e) {
        // error while opening a ZIP file
    }
}

private boolean containsText(ZipFile zipFile, ZipEntry zipEntry, String needle) {
    try (InputStream inputStream = zipFile.getInputStream(zipEntry);
         BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {

        Optional<String> found = reader.lines()
                .filter(l -> l.contains(needle))
                .findFirst();

        return found.isPresent();

    } catch (IOException e) {
        return false;
    }
}
```

## Summary

Stream API in Java 8 is kind a powerful solution that helps in solving relatively easy tasks **easily**. And that its power, in my opinion.

The examples presented in this article are relatively simple and they were created for visualization purpose only. But I hope you like them and find them useful.

## References

<http://docs.oracle.com/javase/tutorial/index.html>
