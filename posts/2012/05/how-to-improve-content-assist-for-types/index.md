---
title: "HOW-TO: Improve content assist for types with static members while creating JUnit tests in Eclipse"
date: 2012-05-08T21:53:00.000+02:00
updated: 2012-05-08T21:53:44.613+02:00
author: "Rafał Borowiec"
tags: ["eclipse", "tools"]
original_url: https://blog.codeleak.pl/2012/05/how-to-improve-content-assist-for-types.html
---

# HOW-TO: Improve content assist for types with static members while creating JUnit tests in Eclipse

Usually while creating JUnit tests we statically import `org.junit.Assert`, `org.hamcrest.Matchers`, `org.mockito.Mockito`, `org.mockito.Matchers` when we want to use static members of these types.

To make that Eclipse proposes members of mentioned types (or any other) without explicit static import we need to define the list in Eclipse's content assist configuration

In order to modify the content assist settings, open Preferences, type **favorites** in the filter and add all types with static members to the list:

![](si1.png)

Thanks to that simple change we may enjoy improved content assist:

![](si2.png)

![](sc3.png)
