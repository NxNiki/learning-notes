# Udemy_JavaScript
Udemy course on javascript and software engineering basic prep

## Resource:

- [Eloquent Javascript](https://eloquentjavascript.net/)

- [Udemy JavaScript: Understand the Weird Parts](https://www.udemy.com/course/understand-javascript/learn/lecture/2280580#overview)

- [Software Engineering Basic](https://learn-2.galvanize.com/cohorts/888)

- [SEI-Precourse](https://learn-2.galvanize.com/cohorts/3943)

- [HTML and CSS (module2.2 in recourse)](https://learn.shayhowe.com/html-css/)

- [CSS](https://developer.mozilla.org/en-US/docs/Learn/CSS/First_steps)

- [JQuery](https://learn.jquery.com/about-jquery/how-jquery-works/)

- [Asynchronous function](https://www.builder.io/blog/visualizing-nodejs-close-queue)

- [Udemy Beginning JavaScript](https://www.udemy.com/course/beginning-javascript/)
  This course turns out to have bad quality and is not suggested to take.

## Issues:

Install eslint:

`npm install eslint --save-dev`

Install promander:
`curl -s https://raw.githubusercontent.com/hackreactor/pomander-precourse/master/bin/install | bash`


I get this error when debugging vscode:
`Can't find Node.js binary "node": path does not exist. Make sure Node.js is installed and in your PATH, or set the "runtimeExecutable" in your launch.json.`

Solutions: https://github.com/microsoft/vscode-js-debug/issues/1150

adding to settings.json (`cmd` + `shift` + `p` and select Open User Settings):
get the path by `which node`:
```
"debug.javascript.defaultRuntimeExecutable": {
"pwa-node": "/path/to/.nvm/versions/node/vX.X.X/bin/node"
},
```

