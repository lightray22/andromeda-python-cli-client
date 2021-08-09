#!/usr/bin/env python3

### simple python script to emulate the Andromeda CLI interface over HTTP ###
### As this is not an actual console, extra options like dry runs, 
# changing the debug level, and changing DB config are not possible ###

import os, sys, requests, json

def exithelp():
    print("general usage: a2cli.py url app action [--$param value] [--$param@ file] [--$param!] [--$param% file [name]] [--$param-]"+os.linesep+
          "\t param@ puts the content of the file in the parameter"+os.linesep+
          "\t param! will prompt interactively or read stdin for the parameter value"+os.linesep+
          "\t param% gives the file path as a direct file input (optionally with a new name)"+os.linesep+
          "\t param- will attach the stdin stream as a direct file input"+os.linesep+
          "get actions:   a2cli.py url server usage")
    sys.exit(1)

def backend(url, app, action, post={}, files=None):

    params = {'app':app,'action':action}
    resp = requests.post(url,params=params,data=post,files=files)

    if resp.headers.get('content-type') == 'application/json':
        return resp.json()
    else: return resp.content


if __name__ == '__main__':

    args = sys.argv[1:]

    if (len(args) < 3):
        exithelp()

    url = args[0]
    app = args[1]
    action = args[2]

    args = args[3:]
    params = { }
    files = { }

    envargs = [ ]
    for key,val in os.environ.items():
        key = key.split('_',1)
        if key[0] == 'andromeda' and len(key) == 2:
            envargs.append("--"+key[1]); envargs.append(val)
    args = envargs + args

    i = 0    
    while i < len(args):

        key = args[i]; i+=1

        if key[0:2] != "--": exithelp()
        else: key = key[2:]

        if len(args) > i and args[i][0:2] != "--":
            value = args[i]; i+=1
        else: value = "true"

        if key[-1] == '@':
            key = key[:-1]
            value = open(value,'rb').read().strip()
        elif key[-1] == '!':
            key = key[:-1]
            value = input("enter {}...".format(key)+os.linesep)

        if key[-1] == '%':
            key = key[:-1]
            if len(args) > i and args[i][0:2] != "--":
                name = args[i]; i+=1
            else: name = os.path.basename(value)
            files[key] = (name,open(value,'rb'))
        elif key[-1] == '-':
            files[key[:-1]] = sys.stdin
        else: params[key] = value

    result = backend(url, app, action, params, files)

    if type(result) is dict:
        result = json.dumps(result, indent=4)

    print(result)
