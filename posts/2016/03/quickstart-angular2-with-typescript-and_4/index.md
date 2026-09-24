---
title: "Quickstart: Angular2 with TypeScript and Gulp: Watch For File Changes"
date: 2016-03-04T00:13:00.001+01:00
updated: 2016-03-04T00:13:37.342+01:00
author: "Rafał Borowiec"
tags: []
original_url: https://blog.codeleak.pl/2016/03/quickstart-angular2-with-typescript-and_4.html
---

# Quickstart: Angular2 with TypeScript and Gulp: Watch For File Changes

In this part of *Quickstart: Angular2 with Typescript and Gulp* I will walk you through adding `watch` task to angular2-typescript-gulp project so changes in source directory are reflected in the build directory.

## Add Gulp task to Gulpfile.ts

I want to watch changes in TypeScript, HTML and CSS files in the source directory. When any of these file changes an appropriate task will run.

```
/**
 * Watch for changes in TypeScript, HTML and CSS files.
 */
gulp.task('watch', function () {
    gulp.watch(["src/**/*.ts"], ['compile']).on('change', function (e) {
        console.log('TypeScript file ' + e.path + ' has been changed. Compiling.');
    });
    gulp.watch(["src/**/*.html", "src/**/*.css"], ['resources']).on('change', function (e) {
        console.log('Resource file ' + e.path + ' has been changed. Updating.');
    });
});
```

## Modify server script in package.json

At this stage of the project, npm `server` script is running the lite-server but I want this script runs watch and lite-server tasks concurrently. This can be done with `concurrently`.

`concurrently` package was added to package json before:

```
{
  "devDependencies": {
    "concurrently": "^2.0.0",
  }
}
```

Modify the server script as follows:

```
"scripts": {
  "server": "concurrent --kill-others \"gulp watch\" \"lite-server\"",
},
```

## Running the script

> npm run server

## Running the script in IntelliJ

For IntelliJ users, right click on the package.json, select *Show npm Scripts* and double click `server` task in the list.

## Modify source files and watch for changes

When the task is running, the build directory will be updated upon changes in source folder.

## Source code

Angular2 with TypeScript and Gulp on Github: <https://github.com/kolorobot/angular2-typescript-gulp>
