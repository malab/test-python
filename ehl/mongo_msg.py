'''
Created on 15/12/2014

@author: aurelio
'''
import re
from pymongo import MongoClient as mc
from datetime import datetime
from pprint import pprint

def insertSummary(filename, mydb):
    up = mydb.mess_ids
    with open(filename, 'rt', encoding='utf-8') as mes:
        lines = mes.readlines() 
        num = 0  
        lista = []
        for line in lines:
            if num == 0:
                num +=1
                continue
            datos = line[:-1].split('\t')
            dato = {}
            dato['num'] = num
            fecha = datos[0]
            dato['fecha'] = fecha[0:4] + '-' + fecha[4:6] + '-' + fecha[6:8] + ' ' + fecha[8:10] + ':' + fecha[10:12]
            dato['msg_id'] = datos[1]
            from_ = datos[2].replace('"', '').split()
            if len(from_) == 1:
                from_.append(from_[0])
            dato['fr_alias'] =  from_[0]
            dato['fr_email'] =  from_[1]
            dato['ngroup'] = datos[3]
            dato['subject'] = datos[4]
            dato['ref'] = datos[5]
            dato['length'] = datos[7]
            up.insert(dato)
            num +=1   

def insertDetails(filename, mydb):
    up = mydb.messages
    with open(filename, 'rt', encoding="iso-8859-15", errors="surrogateescape") as mes:
        lines = mes.readlines() 
        num = 1
        dato = {}
        msg = ''
        for line in lines:  
            if line.startswith("From nobody"):
                if dato:
                    dato['msg'] = msg
                    num +=1
                    #pprint(dato)
                    if msg:
                        up.insert(dato)
                dato = {}
                msg = ''
            else:
                if not msg:
                    dato['num'] = num
                    if "Re:" in  line:
                        line = line.replace("Re:", "Re-")
                    tipo = line.split(":")  
                    if len(tipo) > 1:
                        if tipo[0].startswith("X-"):
                            pass
                        elif tipo[0].startswith("NNTP"):
                            pass
                        elif tipo[0] == "Path":
                            dato['path'] = tipo[1].strip()
                        elif tipo[0] == "From":
                            from_ = tipo[1].replace('"', '').split()
                            if len(from_) == 1:
                                from_.append(from_[0])
                            if from_:
                                dato['fr_alias'] =  from_[0]
                                dato['fr_email'] =  from_[1]
                        elif tipo[0] == "Newsgroups":
                            pass
                        elif tipo[0] == "Subject":
                            tipo[1] = tipo[1].replace("Re-", "Re:")
                            dato['subject'] = tipo[1].strip()
                        elif tipo[0] == "Date":
                            dato['fecha'] = tipo[1].strip()
                        elif tipo[0] == "Lines":
                            dato['lines'] = tipo[1].strip()         
                        elif tipo[0] == "Message-ID":
                            dato['msg_id'] = tipo[1].strip()                
                        elif tipo[0] == "References":
                            dato['ref'] = tipo[1].strip()    
                        elif tipo[0].startswith("Xref"):
                            msg = "\n"  
                        else:
                            pass
                else:
                    if len(line) > 1:
                        line = line.replace("\n", " ")
                    msg += line
                    # dato['msg'] = tipo[0]

                 
if __name__ == '__main__':
    filename = '/home/aurelio/datos/ehl/ehl.mbox'    
    client = mc('localhost', 27017)
    mydb = client.ehl
    # insertSummary(filename, mydb)
    insertDetails(filename, mydb)
