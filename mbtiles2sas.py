#!/usr/bin/python3
#note XP last version is 3.4.x
import sqlite3
import os
import sys

def main():
        
    print("mbtiles to sas tiles converter (c)sae762 aka LLIAMAH v0.1 2021")
    print("Usage: "+sys.argv[0]+" <filename>")


    result = dumpTable(sys.argv[1],"metadata")
    print(result)
    dirtop=sys.argv[1]+".d"
    os.makedirs(dirtop, exist_ok=True)
    with open(dirtop+"/metadata.sql", 'w') as file:
        file.write(result)

    #get tiles from db and place them to folders
    conn = sqlite3.connect(sys.argv[1]);
    cur = conn.cursor()
    cur.execute("SELECT * FROM tiles;")
    for rs in cur.fetchall():
        print("z=",rs[0],",x=",rs[1],"y=",rs[2])
        dirname=dirtop+"/z"+str(rs[0]+1)+"/"+str(rs[1]//1000)+"/x"+str(rs[1])+"/"+str(rs[2]//1000)+"/"
        y=(2**rs[0])-rs[2]-1
        filename="y"+str(y)+".png" ##TODO - use format from metadata
        os.makedirs(dirname, exist_ok=True)
        writeToFileBin(rs[3], dirname+filename)
        print(dirname+filename)
        #if (rs[0] >= 2):
            #exit()

def writeToFileBin(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

#dump metadata table via memory table trick
def dumpTable(db_file, table_to_dump):
    conn = sqlite3.connect(':memory:')    
    cu = conn.cursor()
    cu.execute("attach database '" + db_file + "' as attached_db")
    cu.execute("select sql from attached_db.sqlite_master "
               "where type='table' and name='" + table_to_dump + "'")
    sql_create_table = cu.fetchone()[0]
    cu.execute(sql_create_table);
    cu.execute("insert into " + table_to_dump +
               " select * from attached_db." + table_to_dump)
    conn.commit()
    cu.execute("detach database attached_db")
    return "\n".join(conn.iterdump())
    
def dumpTables(db_file):
    dump=""
    conn = sqlite3.connect(':memory:')    
    cu = conn.cursor()
    cu.execute("attach database '" + db_file + "' as attached_db")
    #dump database structure wit indexes (standart)
    cu.execute("select sql from attached_db.sqlite_master ")
    for ss in cu.fetchall():
        t="".join(ss)  #make string from tuple
        if "sqlite_stat1" not in t:  #check for reserved word
            dump=dump+t+";\n"
    #print (dump)
    conn.commit()
    #dump metadata table
    cu.execute("CREATE TABLE metadata (name text, value text);")
    conn.commit()
    cu.execute("insert into metadata select * from attached_db.metadata")
    conn.commit()    
    cu.execute("detach database attached_db")
    dump = dump+"\n".join(conn.iterdump())
    print (dump)
    return dump
    
#call main
if __name__ == '__main__':
    main()
