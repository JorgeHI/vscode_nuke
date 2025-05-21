'use strict';
// Copyright (c) 2025 Jorge Hernandez. All rights reserved.
// This code is derived from https://github.com/minimalefforttech/vscode_blender_port/blob/main/vscode_extension/src/extension.ts
import * as vscode from 'vscode';
import { Socket } from 'net';
import * as os from 'os';
import * as fs from 'fs';
import * as path from 'path';
var net = require('net');
import { TelemetryReporter } from '@vscode/extension-telemetry';
import { TextEncoder } from 'util';

let nukeportStatusBar: vscode.StatusBarItem;
let socket_nuke: Socket;
let port_nuke: string;
let receiveBuffer: Buffer = Buffer.alloc(0);
// Removed reporter variable

const extensionId = 'jorgehi.nukeconnect';
const extensionVersion = vscode.extensions.getExtension(extensionId).packageJSON.version;

function updateStatusBarItem(): void {
  let text: string;
  if (socket_nuke instanceof Socket == true && 
      socket_nuke.destroyed == false) {
    text = `Nuke Port : ${port_nuke}`;
    nukeportStatusBar.text = text;
    nukeportStatusBar.show();
  } else {
    nukeportStatusBar.hide();
  }
}

export class Logger {
  private static _outputPanel;

  public static registerOutputPanel(outputPanel: vscode.OutputChannel) {
    this._outputPanel = outputPanel;
  }

  public static info(log: string) {
    this.typeLog(log, 'INFO');
  }

  public static error(log: string) {
    this.typeLog(log, 'ERROR');
    vscode.window.showErrorMessage(log);
  }

  private static typeLog(log: String, type: String) {
    if (!this._outputPanel) {
      return;
    }
    let util = require('util');
    let time = new Date().toISOString();
    this._outputPanel.appendLine(util.format('nukeconnect-%s [%s][%s]\t %s', extensionVersion, time, type, log));
  }
}

function handleNukeData(data: Buffer) {
  receiveBuffer = Buffer.concat([receiveBuffer, data]);
  while (receiveBuffer.length >= 8) {
    const len = parseInt(receiveBuffer.slice(0, 8).toString());
    if (receiveBuffer.length < 8 + len) {
      // Wait for more data
      break;
    }
    const message = receiveBuffer.slice(8, 8 + len).toString();
    Logger.info(`[Nuke Output]\n${message}`);
    // Show the output panel when output is received
    if (Logger['_outputPanel'] && typeof Logger['_outputPanel'].show === 'function') {
      Logger['_outputPanel'].show(true);
    }
    receiveBuffer = receiveBuffer.slice(8 + len);
  }
}

export function activate(context: vscode.ExtensionContext) {
  let outputPanel = vscode.window.createOutputChannel('Nuke');
  Logger.registerOutputPanel(outputPanel);

  var config = vscode.workspace.getConfiguration('nukeconnect');

  // Removed telemetry event due to compatibility issues

  function ensureConnection() {
    let hostname: string = config.get('hostname');
    let port: number = config.get('port');

    port_nuke = port.toString();

    if (socket_nuke instanceof Socket && socket_nuke.destroyed === false) {
      updateStatusBarItem();
      return socket_nuke;
    }

    // Always create a new socket and assign to socket_nuke
    socket_nuke = net.createConnection({ port: port, host: hostname }, () => {
      Logger.info(`Connected to Nuke on Port ${port}`);
      updateStatusBarItem();
    });

    socket_nuke.on('error', (error) => {
      let errorMsg = `Unable to connect to Nuke on Port ${port}. Ensure Nuke is running with the correct port open.`;
      Logger.error(errorMsg);
    });

    socket_nuke.on('data', (data: Buffer) => {
      handleNukeData(data);
    });

    socket_nuke.on('end', () => {
      Logger.info(`Disconnected from Nuke on Port ${port}`);
      updateStatusBarItem();
    });

    return socket_nuke;
  }

  function sendPythonCodeToNuke(text: string) {
    // Stream: send 8-byte header (code length), then code
    const encoder = new TextEncoder();
    const codeBuffer = encoder.encode(text);
    const lengthHeader = Buffer.byteLength(codeBuffer).toString().padStart(8, '0');
    send(Buffer.concat([Buffer.from(lengthHeader), codeBuffer]));
  }


  function send(data: Buffer | string) {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let buffer: Buffer;
      if (typeof data === 'string') {
        buffer = Buffer.from(data + '\n');
      } else {
        buffer = data;
      }
      let success = socket_nuke.write(buffer);
      if (success) {
        Logger.info(`Sent ${buffer.length} bytes of Python code to Nuke`);
      }
    }
  }
  function getText() {
    let editor = vscode.window.activeTextEditor;
    let selection = editor.selection;
    let text: string;

    if (!selection.isEmpty) {
      text = editor.document.getText(selection);
    } else {
      text = editor.document.getText();
    }
    return text;
  }

  // Register commands
  const sendCommand = vscode.commands.registerCommand('nukeconnect.sendPythonToNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      sendPythonCodeToNuke(text);
    }
  });

  context.subscriptions.push(sendCommand);
  
  const printCommand = vscode.commands.registerCommand('nukeconnect.printSelectedInNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      const wrappedText = `print(${text})`;
      sendPythonCodeToNuke(wrappedText);
    }
  });

  context.subscriptions.push(printCommand);
  const pprintCommand = vscode.commands.registerCommand('nukeconnect.prettyPrintSelectedInNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      const wrappedText = `import pprint;pprint.pprint(${text})`;
      sendPythonCodeToNuke(wrappedText);
    }
  });

  context.subscriptions.push(pprintCommand);

  const describeCommand = vscode.commands.registerCommand('nukeconnect.describeSelectedInNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      const wrappedText = `import inspect
for name in dir(${text}):
    if name.startswith('__') and name.endswith('__'):
        continue
    attr = getattr(${text}, name)
    if inspect.isfunction(attr) or inspect.ismethod(attr):
        try:
            sig = str(inspect.signature(attr))
        except Exception:
            sig = '(...)'
        print(f"{name}{sig}")
    else:
        t = type(attr).__name__
        ann = getattr(type(${text}), '__annotations__', {})
        t_ann = ann.get(name, t)
        if t_ann != t:
            t = t_ann
        if t and t != 'NoneType':
            print(f"{name}:{t}")
        else:
            print(f"{name}")
`;
      sendPythonCodeToNuke(wrappedText);
    }
  });

  context.subscriptions.push(describeCommand);

  const helpCommand = vscode.commands.registerCommand('nukeconnect.printHelpInNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      const wrappedText = `help(${text})`;
      sendPythonCodeToNuke(wrappedText);
    }
  });

  context.subscriptions.push(helpCommand);

  const dirCommand = vscode.commands.registerCommand('nukeconnect.printDirInNuke', () => {
    socket_nuke = ensureConnection();
    if (!socket_nuke.destroyed) {
      let text = getText();
      const wrappedText = `import inspect
for name in dir(${text}):
    if name.startswith('__') and name.endswith('__'):
        continue
    attr = getattr(${text}, name)
    if inspect.isfunction(attr) or inspect.ismethod(attr):
        try:
            sig = str(inspect.signature(attr))
        except Exception:
            sig = '(...)'
        print(f"{name}{sig}")
    else:
        t = type(attr).__name__
        ann = getattr(type(${text}), '__annotations__', {})
        t_ann = ann.get(name, t)
        if t_ann != t:
            t = t_ann
        if t and t != 'NoneType':
            print(f"{name}:{t}")
        else:
            print(f"{name}")
`;
      sendPythonCodeToNuke(wrappedText);
    }
  });

  context.subscriptions.push(dirCommand);

  nukeportStatusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  context.subscriptions.push(nukeportStatusBar);

  updateStatusBarItem();
}

export function deactivate() {
  // No reporter to dispose
}
