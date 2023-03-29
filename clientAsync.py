import socket
#mport tqdm
import os
import asyncio
import pandas as pd

# device's IP address
SERVER_HOST = "localhost"
SERVER_PORT = 8000
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
#BIG BOILER PLATE CODE. Doesn't need anything the server doesn't already document. 
#To be edited when the serverside functions are done being implemented. 
#Testing each using main on a case by case basis for now. 
class Client: 
    def __init__(self, address):
        self.address=address

    async def connect(self):
        self.reader,self.writer=await asyncio.open_connection(*self.address)
    
    async def send_message(self,message):
        self.writer.write(message.encode())
        await self.writer.drain()
        response = await self.reader.read(BUFFER_SIZE)
        print(f'Recieved Response: {response.decode()}')

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

async def main():
    client=Client((SERVER_HOST,SERVER_PORT))
    await client.connect()
    #Header definition list
    #0=Login
    #1=Row Add
    #2=Row Edit
    #3=Row Delete
    await client.send_message('0,testUser,password1234')
    await client.close()

if __name__ == '__main__':
    asyncio.run(main())

