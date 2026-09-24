---
title: "Quickstart: Angular2 with TypeScript and Gulp"
date: 2016-03-01T23:27:00.000+01:00
updated: 2017-12-14T23:37:55.308+01:00
author: "Rafał Borowiec"
tags: ["angular2"]
original_url: https://blog.codeleak.pl/2016/03/quickstart-angular2-with-typescript-and.html
---

# Quickstart: Angular2 with TypeScript and Gulp

![](angular2.png)

Angular2 is out. The new version of the framework is much simpler to learn thanks to easier and more concise concepts like component-based architecture, new dependency injection or built-in modularity. In this step-by-step tutorial you will learn how how to get started with Angular2 with TypeScript and Gulp. Source code available on Github.

## General notes

***Note the code and the article itself is not maintained anymore.***

### *Change Log*

- **15/09/2016 - Upgraded Angular2 to 2.0.0** Revisited the article, added new code to reflect code in the repository. Added quickstart guide.
- 06/09/2016 - Upgraded Angular2 to 2.0.0-rc.6
- 05/06/2016 - typings updated to 1.0.4. Section related to that part changed too.
- 05/05/2016 - Upgraded Angular2 to 2.0.0-rc.1
- 22/04/2016 - Upgraded Angular2 to 2.0.0-beta.15
- 26/03/2016 - Upgraded Angular2 to 2.0.0-beta.12, README, npm start instead of npm run server, minor gulpfile.ts adjustments (const instead of let)
- 21/03/2016 - Upgraded Angular2 to 2.0.0-beta.11 (the post itself as well as the source code)

### Get started quickly

If you are not interested in a step by step tutorial, simply follow the below steps to get started quickly.

#### 1. Prerequisites

nodejs must be installed on your system and the below global node packages must be installed:

- gulp

> npm i -g gulp

- gulp-cli

> npm i -g gulp-cli

- typings

> npm i -g typings@1.3.3

- typescript

> npm i -g typescript@2.0.2

- ts-node

> npm i -g ts-node@1.3.0

#### 2. Cloning the repository

Clone the repository:

> git clone <https://github.com/kolorobot/angular2-typescript-gulp.git>

Navigate to `angular2-typescript-gulp` directory:

> cd angular2-typescript-gulp

#### 3. Installing dependencies

Install dependencies by running the following command:

> npm install

`node_modules` and `typings` directories will be created during the install.

#### 4. Building the project

Build the project by running the following command:

> npm run clean & npm run build

`build` directory will be created during the build

#### 5. Starting the application

Start the application by running the following command:

> npm start

The application will be displayed in the browser.

## Introduction

Angular 1.x is probably still the most popular Front-end framework these days and there is no doubt Angular 1.x is a great framework. However it is incredibly difficult to master. The complex API and many concepts introduced since its launch make understanding the framework and thus using it effectively really hard.

Angular2, on the other hand, is a new opening. The new version of the framework is much simpler to learn thanks to easier and more concise concepts like component-based architecture, new dependency injection or built-in modularity.

If you want to practice and start learning Angular2 there is no better place than [angular.io](http://angular.io). But if you are looking for the ways of utilizing Angular2 with Gulp - this tutorial is for you.

***Note***: The source code for this article can be found on Github: <https://github.com/kolorobot/angular2-typescript-gulp>.

## Project layout

The initial project is based on the Angular2 Quickstart: <https://angular.io/docs/ts/latest/quickstart.html> with some changes. The most important change is to separate source files from build files: `src` directory contains all the source files and `build` contains all compiled and processed files. The server uses `build` directory as a base directory to serve content.

```
angular2-typescript-gulp
|   .gitignore
|   bs-config.json  -> BrowserSync configuration
|   gulpfile.ts     -> Gulp in TypeScript
|   package.json    -> npm configuration
|   tsconfig.json   -> TypeScript configuration
|   typings.json    -> TypeScript typings definitions
|   tslint.json     -> tslint configuration
|
\---src
│   │   index.html                 -> Starting point for the application
│   │   systemjs.config.js         -> SystemJS configuration
│   │
│   \---app                       -> Application modules
│       │   app.component.ts          -> Main application component
│       │   app.html              -> Main application template 
│       │   app.module.ts         -> Application module definition       
│       │   app.routing.ts        -> Routing configuration      
│       │   main.ts               -> Application bootstrap   
│       │
│       \---about 
│       │   └───components
│       │           about.components.ts
│       │           about.html
│       │
│       \---todo
│           ├───components
│           │       task-list.component.ts
│           │       task-list.css
│           │       task-list.html
│           │       task.component.ts
│           │       task.html
│           │
│           \---models
│           │       task.ts
│           │
│           \---services
│                   task-service.ts
```

## NPM global dependencies

Assuming node and npm is already installed, you may install global dependencies by invoking the following command:

> `npm i -g <dependency>`

Required global dependencies in order to run the project:

- gulp and gulp-cli

> npm i -g gulp   
> npm i -g gulp-cli

- typings

> npm i -g typings@1.3.3

- typescript

> npm i -g typescript@2.0.2

- ts-node

> npm i -g ts-node@1.3.0

Note: To check global dependencies use the following command:

> npm -g –depth 0 ls

## Creating project directories and files

Create directory and files structure as presented above.

## Build configuration

### 1. TypeScript confguration - tsconfig.ts

Compiled files will be saved intto `build/app`. Please note that `gulpfile.ts` is excluded from the compilation.

```json
{
  "compilerOptions": {
    "outDir": "build/app",
    "target": "es5",
    "module": "system",
    "moduleResolution": "node",
    "sourceMap": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "removeComments": false,
    "noImplicitAny": false
  },
  "exclude": [
    "gulpfile.ts",
    "node_modules"
  ]
}
```

Note: If you import your project to IDE (e.g. IntelliJ) let the IDE use this file too.

### 2. Typings - typings.json

To get started we need some definitions to be installed. Run the following commands:

> typings install –global –save dt~core-js   
> typings install –global –save dt~node

which will append to `typings.json`

```json
{
  "globalDependencies": {
    "core-js": "registry:dt/core-js#0.0.0+20160725163759",
    "node": "registry:dt/node#6.0.0+20160909174046",
  }
}
```

Typings will be download to `typings` directory and they will be downloaded on `npm install`.

### 3. npm packages and scripts configuration - package.json

A word about the scripts:

- `clean` - removes `build` directory
- `compile` - TypeScript compilation (with sourcemaps)
- `build` - build the project
- `start` - runs lite server which uses configuration from `bs-config.json` It also uses `watch` tasks to synchronize any changes to the source directory

```json
{
  "name": "angular2-typescript-gulp",
  "version": "1.0.0",
  "description": "Angular2 with TypeScript and Gulp QuickStart",
  "scripts": {
    "clean": "gulp clean",
    "compile": "gulp compile",
    "build": "gulp build",
    "start": "concurrent --kill-others \"gulp watch\" \"lite-server\"",
    "postinstall": "typings install"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/kolorobot/angular2-typescript-gulp.git"
  },
  "author": "Rafał Borowiec",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/kolorobot/angular2-typescript-gulp/issues"
  },
  "dependencies": {
    "@angular/common": "2.0.0",
    "@angular/compiler": "2.0.0",
    "@angular/core": "2.0.0",
    "@angular/forms": "2.0.0",
    "@angular/http": "2.0.0",
    "@angular/platform-browser": "2.0.0",
    "@angular/platform-browser-dynamic": "2.0.0",
    "@angular/router": "3.0.0",
    "@angular/upgrade": "2.0.0",

    "core-js": "^2.4.1",
    "reflect-metadata": "^0.1.3",
    "rxjs": "5.0.0-beta.12",
    "systemjs": "0.19.27",
    "zone.js": "^0.6.23"
  },
  "devDependencies": {
    "concurrently": "^2.2.0",
    "del": "^2.2.0",
    "gulp": "^3.9.1",
    "gulp-sourcemaps": "^1.6.0",
    "gulp-tslint": "^6.1.1 ",
    "gulp-typescript": "^2.13.6",
    "lite-server": "^2.2.2",
    "tslint": "^3.5.0",
    "typescript": "^2.0.2",
    "typings": "^1.3.3",
    "ts-node": "^1.3.0"
  }
}
```

### 4. BrowserSync configuration - lite-server

By default the content is served from the current directory so this needs to be changed. And since Lite Server uses BrowserSync it enough to provide `bs-config.json` that configures the server to serve content from `build` directory.

```
{
  "port": 8000,
  "files": [
    "build/**/*.{html,htm,css,js}"
  ],
  "server": {
    "baseDir": "build"
  }
}
```

### 5. tslint - tslint.json

TSLint checks TypeScript code for readability, maintainability, and functionality errors and in Gulp it can be used with gulp-tslint plugin.

tslint.json is used to configure which rules that get run. Simply add the file to the root directory of the project. You should adjust rules to your needs. You can find more information about the rules here: <http://palantir.github.io/tslint/usage/tslint-json/>

```
{
  "rules": {
    "class-name": true,
    "curly": true,
    "eofline": false,
    "forin": true,
    "indent": [
      true,
      4
    ],
    "label-position": true,
    "label-undefined": true,
    "max-line-length": [
      true,
      140
    ],
    "no-arg": true,
    "no-bitwise": true,
    "no-console": [
      true,
      "debug",
      "info",
      "time",
      "timeEnd",
      "trace"
    ],
    "no-construct": true,
    "no-debugger": true,
    "no-duplicate-key": true,
    "no-duplicate-variable": true,
    "no-empty": false,
    "no-eval": true,
    "no-string-literal": false,
    "no-trailing-whitespace": true,
    "no-unused-variable": false,
    "no-unreachable": true,
    "no-use-before-declare": true,
    "one-line": [
      true,
      "check-open-brace",
      "check-catch",
      "check-else",
      "check-whitespace"
    ],
    "radix": true,
    "semicolon": true,
    "triple-equals": [
      true,
      "allow-null-check"
    ],
    "variable-name": false,
    "whitespace": [
      true,
      "check-branch",
      "check-decl",
      "check-operator",
      "check-separator"
    ]
  }
}
```

Note: For IntelliJ users, configure TSLint as described here: <https://www.jetbrains.com/idea/help/tslint.html> to get instant notifications during file editing.

### 6. Build configuration with Gulp - gulpfile.ts

To get started we need a task(s) that compiles TypeScript files, copies assets and dependencies to a `build` directory. Several tasks are needed in order to achieve it.

Note: Gulp file is created in TypeScript instead of JavaScript. It requires ts-node to execute as stated in the beginning of this tutorial.

```
"use strict";

const gulp = require("gulp");
const del = require("del");
const tsc = require("gulp-typescript");
const sourcemaps = require('gulp-sourcemaps');
const tsProject = tsc.createProject("tsconfig.json");
const tslint = require('gulp-tslint');

/**
 * Remove build directory.
 */
gulp.task('clean', (cb) => {
    return del(["build"], cb);
});

/**
 * Lint all custom TypeScript files.
 */
gulp.task('tslint', () => {
    return gulp.src("src/**/*.ts")
        .pipe(tslint({
            formatter: 'prose'
        }))
        .pipe(tslint.report());
});

/**
 * Compile TypeScript sources and create sourcemaps in build directory.
 */
gulp.task("compile", ["tslint"], () => {
    let tsResult = gulp.src("src/**/*.ts")
        .pipe(sourcemaps.init())
        .pipe(tsc(tsProject));
    return tsResult.js
        .pipe(sourcemaps.write(".", {sourceRoot: '/src'}))
        .pipe(gulp.dest("build"));
});

/**
 * Copy all resources that are not TypeScript files into build directory.
 */
gulp.task("resources", () => {
    return gulp.src(["src/**/*", "!**/*.ts"])
        .pipe(gulp.dest("build"));
});

/**
 * Copy all required libraries into build directory.
 */
gulp.task("libs", () => {
    return gulp.src([
            'core-js/client/shim.min.js',
            'systemjs/dist/system-polyfills.js',
            'systemjs/dist/system.src.js',
            'reflect-metadata/Reflect.js',
            'rxjs/**',
            'zone.js/dist/**',
            '@angular/**'
        ], {cwd: "node_modules/**"}) /* Glob required here. */
        .pipe(gulp.dest("build/lib"));
});

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

/**
 * Build the project.
 */
gulp.task("build", ['compile', 'resources', 'libs'], () => {
    console.log("Building the project ...");
});
```

### 7. Installing dependencies and checking the build

It is a high time to install all dependencies. Run:

> npm install

`node_modules` and `typings` directories should be created during the install.

Build the project:

> npm run clean & npm run build

`build` directory should be created during the build

Note: Make sure you have at least `ts-node` 1.3.0 if you see the below during the compilation:

```
[00:49:42] Failed to load external module ts-node/register
[00:49:42] Failed to load external module typescript-node/register
[00:49:42] Failed to load external module typescript-register
[00:49:42] Failed to load external module typescript-require
```

## Project configuration

### 1. Index - src/index.html

The libraries are reference from `lib` directory that is created during the `build` task.

```
<html>
<head>
    <title>Angular 2 TypeScript Gulp QuickStart</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- 1. Load libraries -->
    <!-- Polyfill(s) for older browsers -->
    <script src="lib/core-js/client/shim.min.js"></script>

    <script src="lib/zone.js/dist/zone.js"></script>
    <script src="lib/reflect-metadata/Reflect.js"></script>
    <script src="lib/systemjs/dist/system.src.js"></script>

    <!-- 2. Configure SystemJS -->
    <script src="systemjs.config.js"></script>
    <script>
        System.import('app')
                .then(null, console.error.bind(console));
    </script>

</head>

<!-- 3. Display the application -->
<body>
<app>Loading...</app>
</body>

</html>
```

### 2. SystemJS configuration - src/systemjs.config.js

```
(function (global) {
    System.config({
        paths: {
            // paths serve as alias
            'npm:': 'lib/'
        },
        // map tells the System loader where to look for things
        map: {
            // our app is within the app folder
            app: 'app',
            // angular bundles
            '@angular/core': 'npm:@angular/core/bundles/core.umd.js',
            '@angular/common': 'npm:@angular/common/bundles/common.umd.js',
            '@angular/compiler': 'npm:@angular/compiler/bundles/compiler.umd.js',
            '@angular/platform-browser': 'npm:@angular/platform-browser/bundles/platform-browser.umd.js',
            '@angular/platform-browser-dynamic': 'npm:@angular/platform-browser-dynamic/bundles/platform-browser-dynamic.umd.js',
            '@angular/http': 'npm:@angular/http/bundles/http.umd.js',
            '@angular/router': 'npm:@angular/router/bundles/router.umd.js',
            '@angular/forms': 'npm:@angular/forms/bundles/forms.umd.js',
            // other libraries
            'rxjs': 'npm:rxjs'
        },
        // packages tells the System loader how to load when no filename and/or no extension
        packages: {
            app: {
                main: './main.js',
                defaultExtension: 'js'
            },
            rxjs: {
                defaultExtension: 'js'
            }
        }
    });
})(this);
```

## Application components

### 1. Main application component - src/app/app.component.ts

```
import {Component, OnInit} from "@angular/core";

@Component({
    selector: "app",
    templateUrl: "./app/app.html"
})
export class AppComponent implements OnInit {
    ngOnInit() {
        console.log("Application component initialized ...");
    }
}
```

And its template (`src/app/app.html`):

```
<p>Angular 2 is running ... </p>
```

### 2. About module

About module consists of two basic building blocks - component and its template.

#### src/app/about/components/about.component.ts

```
import {Component} from "@angular/core";
import {OnInit} from "@angular/core";

@Component({
    templateUrl: './app/about/components/about.html'
})
export class AboutComponent implements OnInit {

    ngOnInit() {

    }
}
```

#### src/app/about/components/about.html

```
<h1>About</h1>
<p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</p>
```

### 3. Todo module

Todo module is a bit complicated - it contains components, models and services sub-packages.

#### src/app/todo/components/task.component.ts

```
import {Component} from "@angular/core";
import {Input} from "@angular/core";

import {Task} from "../models/task";
import {Output} from "@angular/core";
import {EventEmitter} from "@angular/core";

@Component({
    selector: 'task',
    templateUrl: './app/todo/components/task.html'
})
export class TaskComponent {
    @Input() task:Task;
    @Output() statusChanged:any = new EventEmitter<any>();

    toggleDone() {
        this.task.toggleDone();
        this.statusChanged.emit(null);
    }
}
```

#### src/app/todo/components/task.html

```
<form role="form">
    <input title="Name" type="text" [(ngModel)]="task.name" name="name" [disabled]="task.done" />
    <input title="Done" type="checkbox" (click)="toggleDone()" [checked]="task.done" />
</form>
```

#### src/app/todo/components/task-list.component.ts

```
import {Component} from "@angular/core";
import {Task} from "../models/task";
import {OnInit} from "@angular/core";
import {TaskService} from "../services/task-service";
import {TaskComponent} from "./task.component";

@Component({
    selector: 'task-list',
    templateUrl: './app/todo/components/task-list.html',
    styleUrls: ['./app/todo/components/task-list.css'],
    providers: [TaskService]
})
export class TaskListComponent implements OnInit {

    todoCount:number;
    selectedTask:Task;
    tasks:Array<Task>;

    constructor(private _taskService:TaskService) {
        this.tasks = _taskService.getTasks();
        this.calculateTodoCount();
    }

    ngOnInit() {
        console.log("Todo component initialized with " + this.tasks.length + " tasks.");
    }

    calculateTodoCount() {
        this.todoCount = this.tasks.filter(t => !t.done).length;
    }

    select(task:Task) {
        this.selectedTask = task;
    }
}
```

#### src/app/todo/components/task-list.css

```
li.selected {
    background-color: #8a8a8a;
}
```

#### src/app/todo/components/task-list.html

```
<h1>Todo tasks ({{todoCount}})</h1>
<ul>
    <li *ngFor="let task of tasks" [class.selected]="task == selectedTask">
        <a href="javascript:void(0)" (click)="select(task)">
            {{task.name}}
            <span [ngSwitch]="task.done">
                <template [ngSwitchCase]="true">[Done]</template>
                <template [ngSwitchCase]="false">[Todo]</template>
            </span>
        </a>
    </li>
</ul>

<task *ngIf="selectedTask" [task]="selectedTask" (statusChanged)="calculateTodoCount()"></task>
```

#### src/app/todo/models/task.ts

```
export class Task {

    constructor(public name:string, public done:boolean) {
    }

    toggleDone() {
        this.done = !this.done;
    }
}
```

#### src/app/todo/services/task-service.ts

```
import {Injectable} from "@angular/core";
import {Task} from "../models/task";

@Injectable()
export class TaskService {

    private tasks:Array<Task> = [
        new Task("Task 1", false),
        new Task("Task 2", false),
        new Task("Task 3", false),
        new Task("Task 4", false),
        new Task("Task 5", false)
    ];

    getTasks():Array<Task> {
        return this.tasks;
    }

    addTask(name:string) {
        this.tasks.push(new Task(name, false));
    }

}
```

### 4. Angular2 Router - src/app/app.routing.ts

```
import {Routes, RouterModule} from '@angular/router';
import {TaskListComponent} from "./todo/components/task-list.component";
import {AboutComponent} from "./about/components/about.component";
import {ModuleWithProviders} from "@angular/core";

const appRoutes: Routes = [
    {path: 'tasks', component: TaskListComponent, data: {title: 'TaskList'}},
    {path: 'about', component: AboutComponent, data: {title: 'About'}}
];

export const appRoutingProviders: any[] = [];
export const routing: ModuleWithProviders = RouterModule.forRoot(appRoutes, { useHash: true });
```

### 5. Module definition - src/app/app.module.ts

*Angular Modules help organize an application into cohesive blocks of functionality.*

```
import {NgModule}      from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppComponent} from "./app.component";
import {TaskListComponent} from "./todo/components/task-list.component";
import {AboutComponent} from "./about/components/about.components";
import {TaskComponent} from "./todo/components/task.component";

import {routing, appRoutingProviders} from './app.routing';
import {FormsModule} from "@angular/forms";

@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        routing
    ],
    declarations: [
        AppComponent,
        TaskComponent,
        TaskListComponent,
        AboutComponent
    ],
    providers: [
        appRoutingProviders
    ],
    bootstrap: [AppComponent]
})
export class AppModule {
}
```

### 6. Application bootstrap - src/app/main.ts

```
///<reference path="../../typings/index.d.ts"/>

import {platformBrowserDynamic} from '@angular/platform-browser-dynamic';
import {AppModule} from './app.module';

const platform = platformBrowserDynamic();

platform.bootstrapModule(AppModule);
```

## Building and running

> npm run clean & npm run build   
> npm start

You should see the application running in your browser.

## Notes on IntelliJ

IntelliJ handles the proposed setup with no problem. If TypeScript compiler is used in IntelliJ it should use the project’s tsconfig.json. In such case, changes to ts files will be reflected in `build` directory immediately.

## Source code

<https://github.com/kolorobot/angular2-typescript-gulp>

## What’s next?

Much more is needed to make real use of this project. Therefore more features will be added soon. If you have any suggestion, comment or add Github issues.

## angular2-seed

If you need more mature starter, have a look at angular2-seed project <https://github.com/mgechev/angular2-seed>. angular2-seed uses gulp in much more advanced way and it is already supporting production and development build, unit and integration tests and many more.
