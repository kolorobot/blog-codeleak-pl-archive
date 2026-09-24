---
title: "Pretty Time - timestamp formatting made easy"
date: 2011-09-07T22:07:00.001+02:00
updated: 2014-06-06T22:01:37.238+02:00
author: "Codeleak.pl"
tags: ["java", "tools"]
original_url: https://blog.codeleak.pl/2011/09/pretty-time-timestamp-formatting-made.html
---

# Pretty Time - timestamp formatting made easy

Today I was looking for an utility to help me with formating timestamps to user friendly string values like: "moments ago", "few minutes ago", "in couple minutes" etc. Why to write my own implementation, when for sure someone already did it before? And did it better? While googling ("pretty+time+in+java") I found Pretty Time library and I tried it out.  
  
  
With the maven it is just a second to have it in the project. You only add following dependency to the POM file:  

```xml
<dependency>
 <groupid>com.ocpsoft</groupid>
 <artifactid>ocpsoft-pretty-time</artifactid>
 <version>1.0.7</version>
</dependency>
```

To format a date to a human readable value, one line of code is enough:  

```java
String prettyTimeString = new PrettyTime().format(new Date());
```

The result is: "chwilę temu" ("moments ago"). Just as expected.  
Easy to use. Fully configurable. I18n support included.
Just checkout the project page: <http://ocpsoft.com/prettytime> and enjoy the ease of timestamp formating!
  
**Short note:** If you wish to force formatting in English (default), you need to pass locale object to the c-tor with the empty language value, like below. If you don't do this you get the output in the language of the current locale. In my case it was Polish.
  

```java
String prettyTimeString = new PrettyTime(new Locale("")).format(new Date());
```
