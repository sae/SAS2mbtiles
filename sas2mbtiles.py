#!/usr/bin/python3
#note XP last version is 3.4.x
import sqlite3
import os
import sys
import re #for translate filename y345.png to 345

dbname = ""
conn=""
cursor=""
zMin=0 
zMax=0 
tileFormat=""
maxZoom=20 #maximum zoomlevel to processing

def main():
    print("sas tiles to mbtiles converter (c)sae762 aka LLIAMAH v0.1 2021")
    print("Usage: "+sys.argv[0]+" <dirname> <maximum zoom>")
    global dbname
    global conn
    global cursor
    global metaData
    if len(sys.argv) < 2:
        exit();
    if len(sys.argv) > 2:
        maxZoom=int(sys.argv[2]) 
    dbname=sys.argv[1]
    if (sys.argv[1] == '.'):
        dbname="db"
    conn = sqlite3.connect(dbname+".mbtiles")
    cursor = conn.cursor()
    createTables()  #create mbtiles database
    fillTiles()     #find and write tiles
    setMetadata()   #add collected metadata (zoomMin, zoomMax, dbname, tileFormat)
    conn.commit()
    conn.close()
    
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def fillTiles1():
    for z in range(1,20):
        fu = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dbname) for f in filenames if
                  os.path.splitext(f)[1].lower() == '.png']
    print(fu)
    
def fillTiles():
    global zMin
    global zMax
    global tileFormat
    for z in range(1,20):
      if(os.path.isdir((dbname+"/z"+str(z)))):
        for dx in listdirs(dbname+"/z"+str(z)):
            for x in listdirs(dbname+"/z"+str(z)+"/"+dx):
                for dy in listdirs(dbname+"/z"+str(z)+"/"+dx+"/"+x):
                    for y in listdirs(dbname+"/z"+str(z)+"/"+dx+"/"+x+"/"+dy):
                        print(dbname+"/z"+str(z)+"/"+dx+"/"+x+"/"+dy+"/"+y)
                        if (tileFormat=="") :
                            if "png" in y:
                                tileFormat="png"
                            else:
                                tileFormat="jpg"
                        if zMin>z:
                            zMin=z
                        if zMax<z:
                            zMax=z
                        yn=re.search(r"\d+",y).group() #numeric part of y345.png
                        xn=re.search(r"\d+",x).group() #numeric part of x0
                        insertBLOB(z,xn,yn,dbname+"/z"+str(z)+"/"+dx+"/"+x+"/"+dy+"/"+y)
                conn.commit() #commit is slow

def listdirs(folder):
    dirlist=[]
    for filename in os.listdir(folder):
        #if os.path.isdir(os.path.join(folder,filename)):
            dirlist.append(filename)
    return dirlist
    
#zoom_level, tile_column, tile_row, tile_data
#row = 2**z-y-1
def insertBLOB(z,x,y,tileFile):
        q = """ INSERT INTO tiles (
            zoom_level ,
            tile_column ,
            tile_row ,
            tile_data)  VALUES (?, ?, ?, ?)"""

        tileBlob = convertToBinaryData(tileFile)
        z=z-1 #tiles started from 1, mbtiles - from 0
        y=2**z-int(y)-1 #z0 y0, z1 y0 y1,
        # Convert data into tuple format
        data_tuple = (str(z),x,str(y),tileBlob)
        #print(q, data_tuple)
        cursor.execute(q, data_tuple)

#common mbtiles 1.3 standart
def createTables(): 
    q="""CREATE TABLE tiles (
            zoom_level integer,
            tile_column integer,
            tile_row integer,
            tile_data blob);
    CREATE TABLE metadata
            (name text, value text);
    CREATE UNIQUE INDEX name on metadata (name);
    CREATE UNIQUE INDEX tile_index on tiles
            (zoom_level, tile_column, tile_row);
    """
    cursor.executescript(q)
    conn.commit()

def setMetadata():
    #
    #[('attribution', ''), ('center', '0,0,2'), ('format', 'png'), ('description', ''), 
    #('bounds', '-180,-85.738076382392,180,84.79842793857'), ('minzoom', '0'), ('maxzoom', '6'), ('name', 'Countries')]
    #
    q="""BEGIN TRANSACTION;
    INSERT INTO "metadata" VALUES('attribution','');
    INSERT INTO "metadata" VALUES('center','0,0,2');
    INSERT INTO "metadata" VALUES('description','');
    INSERT INTO "metadata" VALUES('bounds','-180,-85.738076382392,180,84.79842793857');
    """
    s1="INSERT INTO 'metadata' VALUES('format','"+tileFormat+"');" #png/jpg
    s2="INSERT INTO 'metadata' VALUES('minzoom','"+str(zMin)+"');"
    s3="INSERT INTO 'metadata' VALUES('maxzoom','"+str(zMax)+"');"
    s4="INSERT INTO 'metadata' VALUES('name','"+dbname+"');"
    cursor.executescript(q+s1+s2+s3+s4)
    conn.commit()
    
#call main
if __name__ == '__main__':
    main()
