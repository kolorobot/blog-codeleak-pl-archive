---
title: "Thymeleaf Page Layouts"
date: 2014-01-20T00:00:00.000+01:00
updated: 2017-04-25T21:26:12.127+02:00
author: "Rafał Borowiec"
tags: ["spring mvc", "thymeleaf"]
original_url: https://blog.codeleak.pl/2014/01/thymeleaf-page-layouts.html
---

# Thymeleaf Page Layouts

Usually websites share common page components like the header, footer, menu and possibly many more. These page components can be used by the same or different layouts. There are two main styles of organizing layouts in projects: **include** style and **hierarchical** style. Both styles can be easily utilized with Thymeleaf without losing its biggest value: **natural templating**.

*Update (25/04/2017):* Read about Thymeleaf 3 layout improvements : [Thymeleaf 3 Standard Layout System Improvements](../../../2017/04/thymeleaf-3-standard-layout-system/index.md)

### Include Style Layouts

In this style pages are built by embedding common page component code directly within each view to generate the final result. In Thymeleaf this can be done using **Thymeleaf Standard Layout System**:

```html
<body>
    <div th:include="footer :: copy"></div>
</body>
```

The include-style layouts are pretty simple to understand and implement and in fact they offer flexibility in developing views, which is their biggest advantage. The main disadvantage of this solution, though, is that some code duplication is introduced so modifying the layout of a large number of views in big applications can become a bit cumbersome.

### Hierarchical Style Layouts

In hierarchical style, the templates are usually created with a parent-child relation, from the more general part (layout) to the most specific ones (subviews; e.g. page content). Each component of the template may be included dynamically based on the inclusion and substitution of template fragments. In Thymeleaf this can be done using: **Thymeleaf Layout Dialect** and **Thymeleaf Tiles Integration**.

The main advantages of this solution are the reuse of atomic portions of the view and modular design, whereas the main disadvantage is that much more configuration is needed in order to use them, so the complexity of the views is bigger than with Include Style Layouts which are more "natural" to use.

### Thymeleaf Standard Layout System, Thymol, Tiles Integration, Layout Dialect, Custom Layout

The full version of this article, that I wrote for [thymeleaf.org](http://www.thymeleaf.org), with a great help of Daniel Fernández, can be found here: <http://www.thymeleaf.org/doc/articles/layouts.html>. The corresponding project can be found on GitHub: <https://github.com/thymeleaf/thymeleafexamples-layouts>
