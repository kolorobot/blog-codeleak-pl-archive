---
title: "Thymeleaf 3 Standard Layout System Improvements"
date: 2017-04-25T21:22:00.000+02:00
updated: 2017-04-25T21:27:30.191+02:00
author: "Rafał Borowiec"
tags: ["thymeleaf"]
original_url: https://blog.codeleak.pl/2017/04/thymeleaf-3-standard-layout-system.html
---

# Thymeleaf 3 Standard Layout System Improvements

Thymeleaf 3 improved Standard Layout System so that creating layouts is more flexible as ever before.

## Use `th:insert` instead of `th:include`

`th:include` is not recommended anymore and it will be deprecated in future versions of Thymeleaf. `th:insert` is recommended as of Thymeleaf 3 and it behaves similarly to old `th:include` with the difference that it inserts the whole fragment into body, not only the fragment’s body.

Check this section in Thymeleaf documentation: [Difference between `th:insert` and `th:replace` and `th:include`](http://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#difference-between-thinsert-and-threplace-and-thinclude)

## Markup Selectors

Fragments don’t need to be explicitly specified using `th:fragment` at the page they are extracted from. Thymeleaf can select an arbitrary section of a page as a fragment (even a page living on an external server) by means of its `Markup Selector` (previously `DOM Selector`) syntax, similar to XPath expressions, CSS or jQuery selectors:

```
<div th:insert="template :: //div[@class='content']">

</div>
```

For the Markup Selector syntax reference checkout this section in Thymeleaf documentation: [Markup Selector syntax](http://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#appendix-c-markup-selector-syntax).

### Fragment Expressions

Fragment expressions allows creating fragments in a way such that they can be enriched with markup coming from the calling templates, resulting in a layout mechanism that is far more flexible than `th:insert` and `th:replace` only:

```
<div th:replace="${#authentication.principal.isAdmin()} ? ~{fragments/footer :: footer-admin} : ~{fragments/footer :: footer-admin}">

</div>
```

The idea of this syntax is to be able to use resolved fragments as any other kind of objects in the template execution context for later use.

Fragment Expression enables the customization of fragments in ways that until now were only possible using the 3rd party Layout Dialect. Read more about this topic in the Thymeleaf documentation: [Flexible layouts: beyond mere fragment insertion](http://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#flexible-layouts-beyond-mere-fragment-insertion)

## See more

- The updated version of `Thymeleaf Page Layouts` article can be found here: <http://www.thymeleaf.org/doc/articles/layouts.html>. The corresponding project (also updated) can be found on GitHub: <https://github.com/thymeleaf/thymeleafexamples-layouts>
- My `Thymeleaf Custom Layout` project also got updated: [Thymeleaf Custom Layout](../../../2013/11/thymeleaf-template-layouts-in-spring/index.md)
- To get started quickly with Thymeleaf 3 and Spring MVC please refer to this article: [Thymeleaf 3 - Get Started Quickly with Thymeleaf 3 and Spring MVC](../../../2016/05/thymeleaf-3-get-started-quickly-with/index.md)
