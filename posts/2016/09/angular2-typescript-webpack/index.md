---
title: "Angular2 Typescript Webpack Quickstart"
date: 2016-09-30T00:06:00.000+02:00
updated: 2016-09-30T00:06:36.894+02:00
author: "Rafał Borowiec"
tags: ["angular2"]
original_url: https://blog.codeleak.pl/2016/09/angular2-typescript-webpack.html
---

# Angular2 Typescript Webpack Quickstart

Get started quickly with Angular2 Typescript and Webpack: A skeleton / seed Angular2 application that was created by following the official [WEBPACK: AN INTRODUCTION](https://angular.io/docs/ts/latest/guide/webpack.html) on [angular.io](https://angular.io). I have built this small seed project to get better understanding of the Webpack mechanics as I have never worked with this tool before. I suggest reading the original article, but if you look to start quickly you can use the code and start your own seed project immediately.

Note: You can also use Angular2 CLI that uses Webpack.

The source code: <https://github.com/kolorobot/angular2-typescript-webpack>

- Prerequisites

Make sure you are using at least *node* v.5+ and latest *npm*

- Clone the repository:

> git clone <https://github.com/kolorobot/angular2-typescript-webpack.git>

Navigate to `angular2-typescript-webpack` directory:

> cd angular2-typescript-webpack

- Install dependencies by running the following command:

> npm install

`node_modules` and `typings` directories will be created during the install.

- Run tests

> npm test

- Start the application

> npm start

All changes done to `src` directory will be automatically refreshed

- Create distribution

Build the project by running the following command:

> npm run build

`dist` directory will be created during the build

## See also

[Angular2 Typescript Gulp](../../../2016/03/quickstart-angular2-with-typescript-and/index.md)
