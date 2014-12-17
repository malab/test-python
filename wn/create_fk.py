'''
Created on 19/10/2014

@author: aurelio
'''
import mysql.connector as my
import sys

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

def checkFk(fk):
    continuamos(fk)
    t = "Select bd, tabla, field from tablas.tablas where fk = %s;" % fk
    cur = con.cursor()
    try:
        cur.execute(t)
        return cur.fetchall()
    except my.Error as err:
        print("error - ", err)
        
def checkBd(bd):
    continuamos(bd)
    t = "Select bd from tablas.tablas where bd = '%s' limit 1;" % bd
    cur = con.cursor()
    try:
        cur.execute(t)
        if cur._rowcount == 1:
            return True
        else:
            return False
    except my.Error as err:
        print("error - ", err)    
        
def checkTabla(bd, tabla):
    continuamos(tabla)
    t = "Select tabla from tablas.tablas where bd = '%s' and tabla = '%s' limit 1;" % (bd,tabla)
    cur = con.cursor()
    try:
        cur.execute(t)
        if cur._rowcount == 1:
            return True
        else:
            return False
    except my.Error as err:
        print("error - ", err)  

def checkCol(bd, tabla, col):
    continuamos(col)
    t = "Select field from tablas.tablas where bd = '%s' and tabla = '%s' and field = '%s' limit 1;" % (bd, tabla, col)
    cur = con.cursor()
    try:
        cur.execute(t)
        if cur._rowcount == 1:
            return True
        else:
            return False
    except my.Error as err:
        print("error - ", err)  
        
def continuamos(pal):
    if pal.lower() == 's':
        pal = input("Realmente deseas salir? (s para confirmar): ")
        if pal.lower() == 's':
            print("SESION FINALIZADA")
            sys.exit()

def dataInput():
    valido = True
    while valido:
        valido2 = True
        valido3 = True
        valido4 = True
        valido5 = True
        while valido2:
            fk = input("fk: ")
            datos = checkFk(fk)
            print(fk, ", ".join(datos[0]))
            if isinstance(datos, list):
                valido2 = False
        while valido3:
            bd2 = input("bd2: ")
            ret = checkBd(bd2)
            if ret:
                valido3 = False   
        while valido4:
            tabla2 = input("tabla2: ")
            ret = checkTabla(bd2, tabla2)
            if ret:  
                valido4 = False           
        while valido5:
            col2 = input("col2: ")
            ret = checkCol(bd2, tabla2, col2)
            if ret:
                valido5 = False 
        bd1 = datos[0][0]
        tabla1 = datos[0][1]
        col1 = datos[0][2]
        print(fk, bd1, tabla1, col1, bd2, tabla2, col2)

        

if __name__ == '__main__':
    print("""para cada fila hay que inroducir la siguiente información:
    fk: la clave de foreign key (fk) que corresponde al primer campo. De la tabla "tablas"
    (al introducir fk automáticamente se recuperan los datos de bd1, tabla1 y col1.
    Solo hay que rellenar el resto:
    bd2 (nombre de base de datos del segundo campo)")
    tabla2 (nombre de la tabla del segundo campo)
    col2 (nombre del campo del segundo campo)
    
    para salir entre "s"
    """)
    
    dataInput()
    