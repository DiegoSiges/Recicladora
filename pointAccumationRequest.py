#
# 
# Point Accumulation Request API call. This script requires to configuration files. One is siges_data.cfg, which consists of two lines. 
# The first line contains the apies, and the second contains the point of sale. 
# The second file is siges_numTrans.cfg, that contains only one number. This is the initial transaction number to be used in the API requests.
# This file is updated with the next transaction number to be used.  
#

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
     
# Produces current date and time in the following format: "09/09/2024 11:23:42"
def mkFecha():
    import datetime
    current_time = datetime.datetime.now()
    date = str(current_time.day) + '/' + str(current_time.month) + '/' +  str(current_time.year)
    time = str(current_time.hour) + ':' + str(current_time.minute) + ':' + str(current_time.second)
    return date + ' ' + time

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





import requests

paramsPuntoVenta = getSalesPointParams() # Reads point of sale params from cfg file
reqApies = paramsPuntoVenta[0]
reqSalePoint= paramsPuntoVenta[1]

# Print the retrieved data
print(f"apies {reqApies}\npuntoVenta: {reqSalePoint}")
reqApiUlrl = "https://siges.dev/api/YVOSGenerarAcumulacion"

reqNum = getNumTransaction()
reqId = f"Y_{reqApies}_Surtidor{reqSalePoint}_{reqNum}"
reqDate = mkFecha()
prodId = 1
prodIdPriceBook = None
prodCode = "Botella"
prodDescription = "Reciclado"
prodType = "store"
prodQuantity = 1
prodUnitPrice = 0.01
prodPriceChange = False
discounts = None


# The following are params specific for the bottle collector machine. Produce 200 from the test API
todo = {"apies": reqApies, "puntoVenta": reqSalePoint, "idTransaccion": reqId, \
        "fecha": reqDate, "productos": [{"Id": prodId, "IdPriceBook": prodIdPriceBook, \
        "codigo": prodCode, "descripcion": prodDescription, "tipo": prodType, \
        "cantidad": prodQuantity, "precUnit": prodUnitPrice, "cambioPrecio": prodPriceChange}], "descuentos": discounts}


print(todo)

response = requests.post(reqApiUlrl, json=todo)
print(response.json())
print(response.status_code)
incrTransactNum(int(reqNum))
recTransaction(reqApies, reqSalePoint, reqId, reqDate, prodId, prodCode,prodDescription,prodType, prodQuantity, prodUnitPrice, response.status_code, response.json());
