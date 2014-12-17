import os
import sys
import ftplib
import mysql.connector as my

from config import *
'''
Created on 24/04/2013

@author: aurelio
'''

def copia_tablas():
    exporta = ['not_clasif', 'noticias', 'not_relacion', 'not_nombres_relaciones', \
               'not_importancia_noticias', 'not_importancia_ners', 'not_imagenes', 'ners'];
    try:
        con = my.connect(**con_data)
    except my.Error as err:
        print(format(err))
    cur = con.cursor()
    for tabla in exporta:
        copia = "/var/www/noticias"+DIR_LOCAL+tabla+".sql"
        if os.path.exists(copia):
            try:
                os.remove(copia)
            except OSError as err:
                print(format(err))
                sys.exit()
    
        q = "SELECT * INTO OUTFILE '%s' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' \
            LINES TERMINATED BY '\n' FROM %s" % (copia, tabla)
        try:
            cur.execute(q)
        except my.Error as err:
            print(format(err))
            sys.exit()
        print("%s copiada con exito a %s" % (tabla, copia))

def exporta_tablas():
    tablas = ['noticias.sql', 'not_clasif.sql', 'not_relacion.sql', 'not_nombres_relaciones.sql', \
              'not_importancia_noticias.sql', 'not_importancia_ners.sql', 'not_imagenes.sql', 'ners.sql']
    dirOrigen = '/var/www/noticias'+DIR_LOCAL
    ftpServidor = 'ftp.noticias123.es'
    ftpUsuario = 'noti8980' #trim('noti8980'); 
    ftpContra = 'Malabo@123' #trim('Malabo@123');
    try:
        ftp = ftplib.FTP(host=ftpServidor)
        ftp.login(user=ftpUsuario, passwd=ftpContra)
    except:
        print("Error conectando ftp a remoto")
    ftp.cwd(DIR_REMOTO)
    # ftp.login(ftpUsuario, ftpContra)
    print(ftp.pwd())
    for tabla in tablas:
        if os.path.exists(tabla):
            os.remove(tabla)
        try:
            ftp.storbinary("STOR " + tabla, open(dirOrigen+tabla, 'rb'))
        except ftplib.Error as e:
            print(format(e))
            sys.exit()
        print("%s exportada con exito a %s" % (tabla, ftpServidor))
    ftp.quit()  
# Programa
'''
copia_tablas()
exporta_tablas()
'''

