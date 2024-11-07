# File to handle the data passed by Arduino to siges py script.
# Data passed to Siges Python script: 0 to reinitiate bottle counter; 4 to increment counter; 
# 1 to send accumulation intention.
# The counter is stored in siges_bottleCounter.cfg. The script opens the file, reads 
# and updates the counter.


import sys

input=sys.argv[1]


# Increments counter in bottles counter file
def incrBottleCounter():
    counter=0

    with open("siges_bottleCounter.cfg", "r") as file:
        counter = int(file.readline())
        
    counter+=1
    with open("siges_bottleCounter.cfg", "w") as file:
        file.write(str(counter))
    return


def reinitBottleCounter():
    counter=0
    with open("siges_bottleCounter.cfg", "w") as file:
        file.write(str(counter))
    return

# Gets the number of bottles. To be used in the API call 
def getNumBottles():
    with open("siges_bottleCounter.cfg", "r") as file:
        numBottles = int(file.readline())
    return numBottles


# Gets the next transaction number to be used in an API call 
def getNumTransaction():
    with open("siges_numTrans.cfg", "r") as file:
        num_transaccion = file.readline()
    return num_transaccion

# Increments the transaction number in the transaction number file
def incrTransactNum(numTransaction):
    numTransaction+=1
    with open("siges_numTrans.cfg", "w") as file:
        file.write(str(numTransaction))
    return
     
# Produces current date and time in the following format: "YYYY-MM-DDTHH:MM:SS. E.g. "2024-11-01T09:11:42"
# Follows a working example I was given, but does not comply fully with the format in "API SIGES Integracion IVOS
#  Acumulacion_V1.0.pdf, because it does not specify time zone.
def mkFecha():
    import datetime
    current_time = datetime.datetime.now().isoformat(timespec='seconds')
    return current_time

# Function to get the Punto de Venta params from cfg file in plain txt format of one param per line. Previous file format was 
# JSON. Returns list with params.    
def getSalesPointParams():
        paramsList = []
        with open("siges_data.cfg", "r") as file:
                for line in file:
                        paramsList.append(line.strip())
        if len(paramsList)!=2:
               print("Bad siges_data.cfg")
               quit()        
        return paramsList

# Function to record the request results in a req history log. Before logging the new entry, the function checks if the file size is too big
# already, and in that case it eliminates the oldest entry first. The maximum log file size is defined in fileMaxSize. Each record consumes 
# a little over 100 bytes. A fileMaxSize of 400 bytes will allow 4 entries tops. 

def recTransaction (reqApies, reqSalePoint, reqId, reqDate, prodId, prodCode,prodDescription,prodType, prodQuantity, prodUnitPrice, HTTPStatusCode, jsonResp):
        record = f"{reqApies}, {reqSalePoint}, {reqId}, {reqDate}, {prodId}, {prodCode}, {prodDescription}, {prodType}, {prodQuantity}, {prodUnitPrice}, {HTTPStatusCode}, {jsonResp}\n"

        import os
        fileMaxSize = 400

        if os.path.isfile('siges_transactionRecords.log'): 
                file_size = os.path.getsize('siges_transactionRecords.log')  
                # print("filesize: " + str(file_size))   
        
                if file_size>fileMaxSize:
                        with open("siges_transactionRecords.log", "r+") as file:
                                lines = file.readlines()
                                file.seek(0)
                                file.truncate()
                                file.writelines(lines[1:])
        
        with open("siges_transactionRecords.log", "a") as file:
                file.write(record)
        
        return

# 
# Point Accumulation Request API call. This script requires to configuration files. 
# One is siges_data.cfg, which consists of two lines. 
# The first line contains the apies, and the second contains the point of sale. 
# 
# The second file is siges_numTrans.cfg, that contains only one number. This is the 
# initial transaction number to be used in the API requests.
# This file is updated with the next transaction number to be used.  
#


def sendAccRequest():
        import requests
        import time

        paramsPuntoVenta = getSalesPointParams() # Reads point of sale params from cfg file
        reqApies = paramsPuntoVenta[0]
        reqSalePoint= paramsPuntoVenta[1]

        # Print the retrieved data
        # print(f"apies {reqApies}\npuntoVenta: {reqSalePoint}")

        reqApiUlrl = "https://siges.dev/api/YVOSGenerarAcumulacion"

        reqNum = getNumTransaction()
        reqId = f"Y_{reqApies}_Surtidor{reqSalePoint}_{reqNum}"
        reqDate = mkFecha()
        prodId = 1
        prodIdPriceBook = None
        prodCode = "Botella"
        prodDescription = "Reciclado"
        prodType = "store"
        prodQuantity = getNumBottles()
        prodUnitPrice = 0.01
        prodPriceChange = False
        discounts = None


        # The following are params specific for the bottle collector machine. Produce 200 from the test API
        todo = {"apies": reqApies, "puntoVenta": reqSalePoint, "idTransaccion": reqId, \
                "fecha": reqDate, "productos": [{"Id": prodId, "IdPriceBook": prodIdPriceBook, \
                "codigo": prodCode, "descripcion": prodDescription, "tipo": prodType, \
                "cantidad": prodQuantity, "precUnit": prodUnitPrice, "cambioPrecio": prodPriceChange}], "descuentos": discounts}


        # Initiating API request cycle. Will try 3 times or until a 200 status code is received

        i=0 #Initial value for the loop counter
        responseStatus='999'
        while i<3 :
            response = requests.post(reqApiUlrl, json=todo)
            responseStatus=str(response.status_code)
            incrTransactNum(int(reqNum))
            recTransaction(reqApies, reqSalePoint, reqId, reqDate, prodId, prodCode,prodDescription,prodType, prodQuantity, prodUnitPrice, responseStatus, response.json());
            if responseStatus<"200" or responseStatus>"299":
                time.sleep(2) # Attempt failed. Waiting 2 seconds before next attempt
            else:
                 break
            i=i+1

        print (responseStatus, flush=True, end='') #Sending response to js 


# Main routine. Selects operation based on input from Arduino
if input=="0":
    reinitBottleCounter()
elif input== "4":
    incrBottleCounter()
elif input== "1":
    sendAccRequest()
else:
    print("900", flush=True, end='')





