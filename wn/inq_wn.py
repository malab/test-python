'''
Created on 23/10/2014

@author: aurelio
'''
import mysql.connector as my
from pprint import pprint


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)



class MySQLCursorDict(my.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None
    
def selectRecords(offset, lexname):
    cur = con.cursor(cursor_class=MySQLCursorDict)
    t = "select distinct l.offset, l.lexname, c.new from lexname l inner join inquirer i \
    on l.offset = LEFT(i.wn, 8) inner join inq_cats c on i.cat = c.cat where \
    l.offset = %s and l.lexname = %s;"
    values = (offset, lexname)
    cur.execute(t, values)
    return cur.fetchall()

def selectOffsets():
    cur = con.cursor(cursor_class=MySQLCursorDict)
    t = "select distinct l.offset, l.lexname from lexname l inner join inquirer i on \
    l.offset = LEFT(i.wn, 8) inner join inq_cats c on i.cat = c.cat;"
    cur.execute(t)
    return cur.fetchall()

def updateRecord(offset, lexname, cambio):
    cur = con.cursor()
    t = "update lexname set inquirer = %s where offset = %s and lexname = %s;"
    values = (cambio, offset, lexname)
    try:
        cur.execute(t, values)
    except my.Error as err:
        print("ERROR: ", err, t, values)


if __name__ == '__main__':
    offsets = selectOffsets()
    for offs in offsets:
        offset = offs['offset']
        lexname = offs['lexname']
        cambio = []
        all = selectRecords(offset, lexname)
        for cada in all:
            cambio.append(cada['new'])
        cambio = ", ".join(cambio)
        updateRecord(offset, lexname, cambio)
                
    
        