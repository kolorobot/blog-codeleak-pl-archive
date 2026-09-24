---
title: "Quickstart: Angular2 with TypeScript and Gulp: TSLint"
date: 2016-03-03T23:20:00.003+01:00
updated: 2016-03-04T00:16:00.977+01:00
author: "Rafał Borowiec"
tags: ["angular2"]
original_url: https://blog.codeleak.pl/2016/03/quickstart-angular2-with-typescript-and_3.html
---

# Quickstart: Angular2 with TypeScript and Gulp: TSLint

In this part of *Quickstart: Angular2 with Typescript and Gulp* I will walk you through adding TypeScript Lint to angular2-typescript-gulp project.

[TSLint](http://palantir.github.io/tslint/) checks TypeScript code for readability, maintainability, and functionality errors and in Gulp it can be used with gulp-tslint plugin.

## tslint, gulp-tslint

> npm install tslint –save-dev   
> npm install gulp-tslint –save-dev

This command installs TypeScript linter and TypeScript linter Gulp plugin in your project. The dependencies are downloaded and saved in package.json:

```
  "devDependencies": {
    "gulp-tslint": "^4.3.3",
    "tslint": "^3.5.0",
  }
```

## Add Gulp task to Gulpfile.ts

```
let tslint = require('gulp-tslint');

/**
 * Lint all custom TypeScript files.
 */
gulp.task('tslint', () => {
    return gulp.src("src/**/*.ts")
        .pipe(tslint())
        .pipe(tslint.report('prose'));
});
```

For more information on configuring the task check TSLint project page: [TSLint](http://palantir.github.io/tslint/)

## Configure TSLint - tslint.json

`tslint.json` is used to configure which rules get run. Simply add the file to the root directory of the project. You should adjust rules to your needs.

```
{
  "rules": {
    "class-name": true

    [...]

  }
}
```

You can find more information about the rules here: [tslint.json](http://palantir.github.io/tslint/usage/tslint-json/)

## Run the task

Run the linter using:

> gulp tslint

In case of lint errors you may see:

```
[00:02:00] Starting 'tslint'...
[00:02:00] [gulp-tslint] error app/todo/services/task-service.ts[20, 47]: missing semicolon
[00:02:00] 'tslint' errored after 290 ms
[00:02:00] Error in plugin 'gulp-tslint'
Message:
    Failed to lint: app/todo/services/task-service.ts[20, 47]: missing semicolon.
```

## Make compile depends on tslint

To make sure `tslint` task runs before `compile`, add `tslint` as dependency to `compile` task:

```
gulp.task("compile", ["tslint"], () => {

});
```

## TSLint in IntelliJ

For IntelliJ users, configure TSLint as described here: <https://www.jetbrains.com/idea/help/tslint.html> to get instant notifications during file editing.

## Source code

Angular2 with TypeScript and Gulp on Github: <https://github.com/kolorobot/angular2-typescript-gulp>
