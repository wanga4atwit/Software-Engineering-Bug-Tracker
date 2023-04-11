# Software-Engineering-Bug-Tracker
Bug Tracker for Software Engineering Project - Also known as BugTrackerNeo


## Features

- Handwritten Database
- Handmade connectivity using Socket Programming
- CLI Interface with multiple options
- You can close the client and open the client as many times as you want, the server will serve you the table where you left off

## Installation

Built EXE files are provided in the releases section. Download and unzip the folder wherever you want. Run serverAsync.exe first to run the backend. Then run clientAsync.exe. WAIT. The built version takes an excruciatingly long time to connect to the server compared to the standalone script. The built version is preloaded with a users table that contains one user "testUser" who's password is "password1234". (I know, so very unsafe. but this is for demo's sake). Once you log in further instructions will greet you so you can test functionality.

If you wish to build the code yourself...you don't. These can be run as scripts from the command line. Simply use "pip install -r requirements.txt" to install the required libraries, then run the files in the same order using a command line. The previously mentioned built EXE files were made using auto-py-to-exe for convenience but not required. 

## License
Copyright 2023 Aleksander Ziobro "Sky" - Alex Wang

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
