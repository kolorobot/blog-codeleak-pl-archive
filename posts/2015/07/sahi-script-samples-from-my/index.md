---
title: "Sahi Script Samples from my presentation at TrojQA"
date: 2015-07-01T23:08:00.000+02:00
updated: 2015-07-01T23:08:50.066+02:00
author: "Rafał Borowiec"
tags: ["testing"]
original_url: https://blog.codeleak.pl/2015/07/sahi-script-samples-from-my.html
---

# Sahi Script Samples from my presentation at TrojQA

Sahi is an web automation tool that can be used to test modern web applications in a variety of browsers. Sahi comes in two flavors: open-source and commercial. Some of the key Sahi features include:

- recording on most modern browsers - including Internet Explorer,
- automatic AJAX waits
- easy to learn and robust scripting - Sahi Script
- built-in tools like reporting, logging etc.

This blog post contains some code snippets of Sahi Script that I presented during my talk at [TrojQA](http://trojqa.pl/?p=642) in 2015. TrojQA is a [Tricity (Poland)](https://en.wikipedia.org/wiki/Tricity,_Poland) community focused on software testing and quality assurance.

If you are interested in learning more about Sahi, please visit its official website here: <http://sahipro.com/>.

# Sahi Script

Sahi Script is a scripting language based on JavaScript. The main difference from JavaScript is that in Sahi Script variables must be prefixed with *$*.

```javascript
_include("StringUtils.js")
var _system = (function () {
    var getenv = function ($name, $default) {
        var $env = java.lang.System.getenv($name);
        if ($env == null && $default) {
            return $default;
        }
        return $env;
    };
    var os = function () {
        var $os = java.lang.System.getProperty("os.name");
        return $os;
    };
    return {
        getenv: getenv,
        os: os
    }
})(); 
```

The snippet above creates a module that can be used in retrieving system properties (using Java code).

# Sahi API

The power of Sahi Scripts is a Sahi API. Sahi API, among others, allows accessing elements on the browser and interact with them (Accessor API and Action API). To learn more about Sahi API please visit: <http://sahipro.com/docs/sahi-apis/index.html>.

## Basics

Let’s have a look at a really basic script:

```javascript
_navigateTo("http://themicon.co/theme/angle/v2.4/backend-angular/#/app/dashboard");
_assertEqual(1700, _getText(_div(0, _near(_div("Uploads")))));
```

The script is self exploratory and it instructs Sahi to do the following:

- vavigate to a given URL
- assert that the text in the first `div` that is located near `div` with the text *Uploads* is equal to *1700*

## Tables

While working with tables the Sahi API is really handy mostly due to well named methods and the relation API. The relation API allows matching elements that are related to each other. With tables this is extremely useful.

```javascript
// find a table header with a given text
_highlight(_tableHeader("CSS grade"));

// find a table header with a given text within a concrete table
_highlight(_tableHeader("Platform(s)"), _in(_table("datatable1")));

// find a cell containing a text within a concrete table
_highlight(_cell("Gecko"), _in(_table("datatable1")));

// assert that table header's attribute is not empty
_assert(_tableHeader("Rendering engine").getAttribute("aria-sort") != "");

// compare text of the first row
_assertEqual("Gecko Firefox 1.0 Win 98+ / OSX.2+ 1.7 A", _getText(_row(1)));

// scrolling with JavaScript
_call(_div("Demo Table #2").scrollIntoView());

// fancy finding a checkbox within a table
_click(_span("fa fa-check", _near(_cell(/Holly Wallace/), _in(_table("table-ext-2")))));
```

## Forms

Accessing and interacting with HTML form elements is

```javascript
// click the link near a label containing a given text
_click(_link(0, _near(_label("Email:"))));
// set a value of email field
_setValue(_emailbox("Email:"), "john@doe.com");
// click submit button near email field
_click(_submit("btn btn-success btn-sm", _near(_emailbox("Email:"))));

// some other fields

_setValue(_telephonebox("Tel:"), "000-00-00");
_setValue(_numberbox("Number:"), "35");
_setValue(_rangebox("range"), "55");
_setValue(_urlbox("Url:"), "http://google.com");
_setValue(_datebox("Date:"), "2015-05-20");
_setValue(_timebox("Time:"), "01:00");
```

# Page Object Pattern with Sahi Script

As Sahi Script can be easily modularized (`_include`) applying Page Object Pattern is possible. For small and medium project this should work pretty fine.

The Test Script:

```javascript
// arrange
var $dashboardPage = new DashboardPage();

// act
$dashboardPage.navigateTo();

// verify statistics
_assert($dashboardPage.isAt());
_assertEqual(1700, $dashboardPage.statistics().uploads);
_assertEqual("700 GB", $dashboardPage.statistics().quota);
_assertEqual(500, $dashboardPage.statistics().reviews);
_assertEqual(70, $dashboardPage.statistics().averageMonthlyUploads);
```

The Page:

```javascript
var DashboardPage = function () {

    var $_inboundVisitorStatistics = _div("Inbound visitor statistics");
    var $_inboundVisitorStatisticsCanvas = _canvas(0, _in(_div("panelChart9")));

    this.navigateTo = function () {
        _navigateTo($BASE_URL + "dashboard");
    };

    this.isAt = function () {
        return "Angle - Dashboard" == _title();
    };

    this.statistics = function () {

        var valueOf = function (name) {
            return _getText(_div(0, _near(_div(name))))
        };

        var getAverageMonthlyUploads = function () {
            return _canvas(0, _near(_div("Average Monthly Uploads"))).getAttribute("data-percentage");
        };

        return {
            uploads: valueOf("Uploads"),
            quota:   valueOf("Quota"),
            reviews: valueOf("Reviews"),
            // fits in statistics
            averageMonthlyUploads: getAverageMonthlyUploads()
        }
    };

    this.isInboundVisitorStatisticsVisible = function () {
        _log("Calling isInboundVisitorStatisticsVisible");
        return _isVisible($_inboundVisitorStatisticsCanvas);
    };

    this.collapseInboundVisitorStatistics = function () {
        if (!this.isInboundVisitorStatisticsVisible()) {
            _fail("Inbound visitor statistics are not visible. Can't collapse.");
        }
        _click(_link(0, _near($_inboundVisitorStatistics)));
        // let the panel collapse, 2nd argument must be a Sahi expression
        _wait(2000, !_isVisible($_inboundVisitorStatisticsCanvas));
    };

    this.expandInboundVisitorStatistics = function () {
        if (this.isInboundVisitorStatisticsVisible()) {
            _fail("Inbound visitor statistics are already visible. Can't expand.");
        }
        _click(_link(0, _near($_inboundVisitorStatistics)));
        // let the panel collapse, 2nd argument must be a Sahi expression
        _wait(2000, _isVisible($_inboundVisitorStatisticsCanvas));
    };

};
```

## Source code

A full list of examples can be found here: <https://github.com/kolorobot/sahi-script-samples>

## Running the scripts

- Download and install Sahi OS
- Download the scripts, unpack it and move to *userdata/sahi-demo* directory
- Add *sahi-demo* to *scripts.dir* property in *userdata/config/userdata.properties*
- Run Sahi Dashboard
- Run a selected browser and open Sahi Controller
- Switch to Playback tab and select *sahi-demo* script directory
- Select a file, click *Set* and then *Play*
