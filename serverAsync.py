import socket
#mport tqdm
import os
import asyncio
import pandas as pd
import random
from datetime import date
import json
#Above here is all and any imports

#Return Message Header Table
# 20: These messages are status returns to the client. EG: Confirmations, Information to be relayed about process status.
# 21: log in errors
# 30: These messages are file returns. When we send "Pages" of the table to the user, they will be conveyed in this way. Thus the client can implement as neccesary.
# More to be added if needed.

#Recieved Message Header definition list
#0=Login: The user client intends to log in a user. Treat the remaining data slots in the message as the log in info. Data slots can be expanded by the implementer if they need to carry more data, but we will have 2 slots.
#1=Row Add: The user client intends to add rows to the table. Treat the first data slot as the table file to be decoded. 
#2=Row Edit: The user client intends to edit rows to the table, treat the first data slot as a reference, then edit the row the reference row provides with the info.
#3=Row Delete: The user client intends to delete a row from the table. Treat first data slot as the ID to the row they want to delete.

#IP Address of the server
SERVER_HOST = "0.0.0.0"
#Port of the server
SERVER_PORT = 8000
# receive 4096 bytes each time
BUFFER_SIZE = 4096*4096
#I was going to use this seperator and then forgot and declared a new one, whatever.
SEPARATOR = "<SEPARATOR>"
#User-login table. Probably a better way to generate these but for now they are what they are.
#Should replace this later if I have the time.
userTable=pd.DataFrame(columns=['username','password','tableID','permLevel'])
#idNo=random.randint(0,99999)
idNo=9088
testuser=pd.DataFrame([['testUser','password1234',idNo,3]],columns=['username','password','tableID','permLevel'])
userTable = pd.concat([userTable,testuser])
#Server class
class Server: 
    #Init function. takes address and maps self.
    def __init__(self,address):
        self.address = address;
        print('Initialized') 
    #Here the server starts up
    async def start(self):
        #I printed the address for debugging
        print(self.address)
        #the server starts using asyncIO, and maps the function and address as parameters.
        self.server = await asyncio.start_server(self.handle_client,*self.address)
        #I added this to fix connection issues, seems to do the trick. Thanks StackOverflow!
        async with self.server:
            await self.server.serve_forever()
        #This print never happens because serve_forever never ends until the server does. Whatever.
        print('server start(self) completed')
    #function for the loginProcess, takes self,user,passwd. Not fully implemented yet but the skeleton is here.
    #After a log in I need to set some variables for the current session, send a message, etc
    #For user or password errors I need to send a message to the client. FML.
    #In here, I check if the username sent is in the table, and if it is, if the password matches.
    #Yeah plain-text is unsafe but I have 14 days to complete this junk so what gives.
    async def loginProcess(self,user,passwd):
        try:#if the username exists
            if(userTable['username'].isin([user]).any()==True):
            #if the password to that username is right
                if((userTable.loc[userTable['username']==user,'password'].item())==passwd):
                #Print a confirmation server side (debugging)
                    print("Username and password confirmed, logging in the user")
                #Change the current user to the just logged in one.
                    self.loggedInUser=user
                #return 0 to indicate a successful login.
                    return 0
                else:
                #if the password check failed, print a password error, then return 2 to indicate a password error.
                    print("Password Error")
                    return 2
            else:
            #if the username doesn't exist, print username error, then return 1 to indicate a username error (usually it just doesn't exist)
                print("Username Error")
                return 1
        except NameError:
            return 1
            #function to load the users table, to be called by the login function when it successfully logs in.
    async def loadBugTable(self,tablename):
        #try to load a table using the provided users tableID from the login function that called it.
        try:
           filename=str(tablename)+'.json'
           self.loadedTable=pd.read_json(filename)
           #return 0 if it loaded, to indicate a successful load
           return 0
        except FileNotFoundError:
            #if you got here, the json doesn't exist so it was never generated. Thus the user either lost the table or doesn't have one. In this case return 1 to indicate a load failure due to not found. 
            print('Table file not found')
            return 1
        #a function to create the pages of the table 
    async def createPages(self):
        self.pagedTable = self.loadedTable.groupby(self.loadedTable.index//5)
        #a function to return the page count
    async def enumeratePages(self):
        return self.pagedTable.ngroups
    #a function to return a specific page given a page number
    async def returnPage(self,pageNo):
        #if there are no groups at all, indicating an empty table or table that doesn't meet the criteria,
        #send the whole thing because it's probably really small?
        if(self.pagedTable.ngroups==0):
            return self.loadedTable
        #else send the page specified because it will exist I think to be bug tested later
        else:
            return self.pagedTable.get_group((pageNo-1))
    #Prepares the json page to be sent.
    async def prepareStartPage(self):
        await self.createPages()
        noOfPages=await self.enumeratePages()
        page=await self.returnPage(1)
        jsonPage=page.to_json()
        return jsonPage
    async def updatePages(self):
        await self.createPages()
        self.noOfPages=await self.enumeratePages()
        page=await self.returnPage(1)
        jsonPage=page.to_json()
        return jsonPage       
    #
    #TO DO: Decide where to send the page to the user. After first log-in perhaps? We will need to create the pages when their table is loaded.
    #
    #

    #All the juice happens in here. This is the handler/controller
    #We catch it all in a try so that if I fuck up it throws an error. So far so good.
    async def handle_client(self,reader,writer):
        try:
            self.loadedTable=pd.DataFrame(columns=['ID','Title','Description','Status','Date Created','Date Resolved','Assigned To'])
            self.pagedTable = self.loadedTable.groupby(self.loadedTable.index//5)
            self.noOfPages=0
            self.currentPage=0
            #starting table.
            while True:
                #read the data into the buffer.
                data = await reader.read(BUFFER_SIZE)
                #decode the message
                message = data.decode()
                #Split the data, messages to our API will have to be compliant to this. I'll document it later.
                dataParts = message.split(SEPARATOR)
                #Header definition list
                #0=Login
                #1=Row Add
                #2=Row Edit
                #3=Row Delete
                #if the message is 3 parted (Correctly formed), proceed, if not, then the Client will disconnect.
                #Clients should pad the additonal data slots with 0.
                if(len(dataParts)==3):
                    header = dataParts[0]
                    data1 = dataParts[1]
                    data2 = dataParts[2]
                    #if the header implies a log-in request
                    if(header=='0'):
                        print('Initiating Log In Process')
                        #duplication for my sanity, whatever.
                        username=data1
                        password=data2
                        loginResult = await self.loginProcess(username,password)
                        #Check if the login process returned 0 meaning a success!
                        if(loginResult==0):
                            #form a legit response message with header confirming the login
                            resp="20<SEPARATOR>Successfully logged in!"
                            #send it
                            writer.write(resp.encode())
                            await writer.drain()
                            #grab the id of the table the user has now that they are confirmed real. 
                            name=userTable.loc[userTable['username']==self.loggedInUser,'tableID'].item()
                            tableLoadStatus=await self.loadBugTable(name)
                            #if the table loaded, indicated by returning 0, then form a message with a header, then tell the client by sending it. Refer to the header table at the top of the file.
                            if(tableLoadStatus==0):
                                #split table if the table loaded?
                                #send the table
                                page=await self.prepareStartPage()
                                resp=f"30<SEPARATOR>{page}"
                                writer.write(resp.encode())
                                await writer.drain()
                                #else if no table was found, send a message telling this happened, and then send it.
                                #also send the table
                            elif(tableLoadStatus==1):
                                page=await self.prepareStartPage()
                                resp=f"30<SEPARATOR>{page}"
                                writer.write(resp.encode())
                                await writer.drain()
                                #if for some reason the Table loading function fails catastrophically outside of either loading the table or not, then throw this error to the client. Do not ask me to fix.
                                #don't send shit because there is nothing to send.
                            else:
                                resp="20<SEPARATOR>An Error Creating The Table Occured!"
                                writer.write(resp.encode())
                                await writer.drain()
                            #from here, the login process should be complete, as the user is logged in, and the table is loaded. We should update the user with the first ever page of their table by now. To be implemented. 
                        elif(loginResult==1):
                            resp="21<SEPARATOR>Log-In Error"
                            #send it
                            writer.write(resp.encode())
                            await writer.drain()
                    elif(header=='1'):
                        print('Adding Row To Table')
                        jsonTable=json.loads(data1)
                        tempTable=pd.read_json(json.dumps(jsonTable))
                        print(tempTable)
                        self.loadedTable=pd.concat([self.loadedTable,tempTable],ignore_index=True)
                        print(self.loadedTable)
                        page=await self.updatePages()
                        resp=f"30<SEPARATOR>{page}"
                        writer.write(resp.encode())
                        await writer.drain()
                    else:
                        raise NotImplementedError
                else:
                    #else if, the header is malformed or single messaged, for us it defaults to disconnect. But padding Data 1 and 2 stops crashes.
                    header=dataParts[0]
                    data1='No Data'
                    data2='No Data'
                if message:
                    #Debug message, likely to dissapear in the future.
                    print(f'Recieved header: {header}, with data slot 1: {data1} and data slot 2: {data2}')
                    #Sends the data right back to the client. Debugging for me.
                    #writer.write(data)
                    #Wait for the writer to finish
                    #await writer.drain()
                else:
                    #if the message was that malformed boi above, the client likely disconnected. Quit the handler.
                    print('Client disconnected')
                    await self.saveTheTable()
                    break
        except ConnectionResetError:
            print('Client connection reset')
        finally:
            writer.close()
        #close our writer if the connection dropped, no need for it anymore.
        #This function saves the table to JSON assuming the user disconnects in any way acceptable including just crashing out. If the server crashes then yikes bro, this isn't getting saved. 
    async def saveTheTable(self):
        #Grab the ID of the table,
        try:
            name=userTable.loc[userTable['username']==self.loggedInUser,'tableID'].item()
            filename=str(name)+'.json'
            #spits table to the working directory
            self.loadedTable.to_json(filename)
            self.loggedInUser='No One'
        except AttributeError:
            return 1
    #Function to neatly close the server. This is technically implemented but never called under real circumstances.
    async def stop(self):
        await self.saveTheTable()
        print('Server Stopping')
        self.server.close()
        await self.server.wait_closed()
    



#main function kicks this shit off. 
async def main():
    #create our server with the provided server and port
    server = Server((SERVER_HOST,SERVER_PORT))
    print('Server Starting')
    #run the start function.
    await server.start()
    print('Server Started.')

if __name__ == '__main__':
    asyncio.run(main())

    