---
title: "Getting started with Thymeleaf 3 text templates"
date: 2017-03-07T23:23:00.001+01:00
updated: 2017-03-07T23:23:51.609+01:00
author: "Rafał Borowiec"
tags: ["thymeleaf"]
original_url: https://blog.codeleak.pl/2017/03/getting-started-with-thymeleaf-3-text.html
---

# Getting started with Thymeleaf 3 text templates

Text ((org.thymeleaf.templatemode.TemplateMode#TEXT)) templates in Thymeleaf allow creating templates with no markup. Such templates can be used to genere non-HTML content like e.g. source code, markdown files or text emails. See how easy it is to utilize text templates with Thymeleaf.

### Configure template engine with template resolver

```java
@Configuration
public static class ThymeleafConfig {

    @Bean(name = "textTemplateEngine")
    public TemplateEngine textTemplateEngine() {
        TemplateEngine templateEngine = new TemplateEngine();
        templateEngine.addTemplateResolver(textTemplateResolver());
        return templateEngine;
    }

    private ITemplateResolver textTemplateResolver() {
        ClassLoaderTemplateResolver templateResolver = new ClassLoaderTemplateResolver();
        templateResolver.setPrefix("/templates/text/");
        templateResolver.setSuffix(".txt");
        templateResolver.setTemplateMode(TemplateMode.TEXT);
        templateResolver.setCharacterEncoding("UTF8");
        templateResolver.setCheckExistence(true);
        templateResolver.setCacheable(false);
        return templateResolver;
    }
}
```

`textTemplateResolver()` method configures template resolver for text templates. In this example, templates will be read from classpath.

### Create text template

Create `/templates/text/text-template.txt` file on your classpath (e.g. `src/main/resources`)

```
Name: [(${name})]
Link: [(${url})]
Tags:
[# th:each="tag : ${tags}" ]
    [(${tag})]
[/]
```

### Process the template

```
TemplateEngine textTemplateEngine = ...;

Context context = new Context();
context.setVariable("name", "Spring");
context.setVariable("url", "http://spring.io");
context.setVariable("tags", "#framework #java #spring".split(" "));

String text = textTemplateEngine.process("text-template", context);
```

`text` variable will contain the output of processing `/templates/text/text-template.txt`

### More on textual syntax

- <http://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#textual-syntax>

### Source code

See `pl.codeleak.demos.sbt.thymeleaf.ThymeleafTextTemplates` class for the complete example. Repository: <https://github.com/kolorobot/spring-boot-thymeleaf>
