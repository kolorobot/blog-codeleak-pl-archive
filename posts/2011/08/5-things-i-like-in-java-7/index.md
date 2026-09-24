---
title: "5 things I like in Java 7"
date: 2011-08-01T20:47:00.007+02:00
updated: 2012-03-12T21:31:36.401+01:00
author: "Codeleak.pl"
tags: ["java"]
original_url: https://blog.codeleak.pl/2011/08/5-things-i-like-in-java-7.html
---

# 5 things I like in Java 7

Java Platform, Standard Edition 7 was finally released. And even though Lambda, Jigsaw, and part of Coin were dropped from Java 7, it still has some features that I belive will speed up and generally improve development of Java applications. The below list is my personal choice.  
  
  

### 1. Diamond operator

With diamond operator we have possibility to remove unnecessary duplication when working with generics. That makes the code less verbose, more maintainable and readable.  
Prior to Java 6 when declaring a generic collection we used following code:  

```java
Map map<String, List<String>> = new HashMap<String, List<String>>();
map.put("one", new ArrayList<String>());
map.put("two", new ArrayList<String>());
```

With Java 7 it looks now much better:  

```java
Map map<String, List<String>> = new HashMap<>();
map.put("one", new ArrayList<>());
map.put("two", new ArrayList<>());
```

### 2. Multi-catch statements

Multiple exception types can be handled by a single catch block. The grammar of a catch clause of a try statement is extended to allow a series of exception types, separated by the "OR" operator symbol, "|". This allows us to group exception handling for one or more grouped exception types. Example:  

```java
public void doSomething() {
 try {
  throwsException();
 } catch (MyException | OtherException e) {
  // do something
    
 } catch (Exception e) {
  // do something else    
 }
}
```

### 3. try-with-resources statement

The try-with-resources feature brings to Java ease of management of objects that require freeing up some underlying resource when the object is no longer in use. These objects are usually system resources, like streams. The example should explain everything:  

```java
public List readLine(Path path) {
    List lines = new ArrayList();
    try (BufferedReader reader = new BufferedReader(new FileReader(path.toFile()))) {
        String line;
        while ((line = reader.readLine()) != null) {
            lines.add(line);
        }
    } catch (IOException e) {
        // do something
    }
    return lines;
}
```

With above code reader is closed after "try" code. And this happens automatically. So we do need to handle resource closing within "finally" block with additional "try-catch".  
If we need to create auto-closeable resource on our own, we just need to implement java.lang.AutoCloseable interface and put resource creation in "try". If we try to use new try-with-resources with type not implementing java.lang.AutoCloseable we get following error:  
 `try-with-resources not applicable to variable type  
 required: java.lang.AutoCloseable  
 found: java.lang.String`   

### 4. Underscores in numeric literals

To improve readability of the code we can now use any number of underscore characters (_) anywhere between digits in a numerical literal, similar to how we would use a comma, or a space, as a separator.  

```java
long creditCardNumber = 1234_5678_9012_3456L;
long socialSecurityNumber = 999_99_9999L;
```

### 5. NIO.2: File I/O

NIO.2 (JSR-203) brings useful features to input/output APIs for Java including an extensive File I/O API. This new API is included in java.nio.file and java.nio.file.attribute packages, provide comprehensive support for file I/O and for accessing the default file system and it addresses: paths, file operations, managing metadata, walking the file tree, watching directory for changes and much more.  
What I find useful is a java.nio.file.Files with static methods that operate on files, directories, or other types of files. Finally, we don't need Apache Commons IO to perform basic operations on files.  

### Summary

Java 7 release is not revolutionary release. After 4+ years since Java 6 was released we could expect much more. So I am a bit disappointed. On the other hand I belive that incoming Java 8 release will be more revolutionary and I really can't wait to see it next year..  
Don't forget to check out the full change list in official Java 7 documentation: http://download.oracle.com/javase/7/docs/.
