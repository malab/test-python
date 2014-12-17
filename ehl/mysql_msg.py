'''
Created on 15/12/2014

@author: aurelio
'''
import re
import mysql.connector as my
from datetime import datetime
from pprint import pprint

con_data = {'user':'root','password':'agm','host':'localhost', \
'database':'ehl','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

def insertSummary(filename):
    cur = con.cursor()
    with open(filename, 'rt', encoding='UTF-8') as mes:
        lines = mes.readlines() 
        num = 0  
        lista = []
        for line in lines:
            line = line.replace("=?ISO-8859-1?Q?", "")
            line = line.replace("\\", "")
            if num == 0:
                num +=1
                continue
            datos = line.strip().split('\t')
            dato = {}
            #dato['num'] = num
            fecha = datos[0]
            dato['date'] = fecha[0:4] + '-' + fecha[4:6] + '-' + fecha[6:8] #+ ' ' + fecha[8:10] + ':' + fecha[10:12]
            dato['id'] = datos[1]
            from_ = datos[2].replace('"', '').split()
            # if len(from_) == 1:
            #    from_.append(from_[0])
            dato['user'] =  from_[0].replace("\'", "\\'").strip()
            # dato['fr_email'] =  from_[1]
            # dato['ngroup'] = datos[3]
            dato['subject'] = datos[4].replace("\'", "\\'").strip()
            if datos[5]:
                dato['parent'] = datos[5].split()[-1]
            else:
                dato['parent'] = ''
            #dato['length'] = datos[7]
            #campos = list(dato.keys())
            #valores = list(dato.values())
            t = "Insert ignore into resumen (`id`, `date`, `user`, `parent`, `subject`) values('%s', '%s', '%s', '%s', '%s');" \
            % (dato['id'], dato['date'], dato['user'], dato['parent'], dato['subject'])
            try:
                cur.execute(t)
            except my.Error as err:
                print("Error ...", err, "\n", t)
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
    filename = '/home/aurelio/datos/ehl/ehl.mbox.csv'    
    insertSummary(filename)
    #insertDetails(filename)
