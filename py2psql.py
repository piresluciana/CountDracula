#!/usr/bin/env python

""""THIS FILE DOES ALL THE INTERACTION WITH PSQL !!
"""

import psycopg2 #Imported library(external) to interact with psql

__author__ = "Varun Kohli, San Francisco County Transportation Authority"
__license__= "GPL"
__email__  = "modeling@sfcta.org"
__date__   = "Jul 1 2011" 

def upload_mainline (commandslist,db,user):	    #uploads counts to mainline table
    
    conn2db = psycopg2.connect("dbname="+db+" user="+user)
    cur2db = conn2db.cursor()
    
    #________________THIS IS ONLY FOR TESTING !!!
    
    cur2db.execute("DELETE from counts_ml;")
    
    for command in commandslist:
        #send command to server
        #cur2db.execute("INSERT INTO counts_ml (count,starttime,period,vtype, onstreet,ondir,fromstreet,tostreet,refpos,sourcefile,project) Values (%s, %s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s )",
        cur2db.execute("INSERT INTO counts_ml (count,starttime,period,vtype, onstreet,ondir,fromstreet,tostreet,refpos,sourcefile,project) Values (%s, %s, %s ,%s ,UPPER(%s) ,%s ,UPPER(%s) ,UPPER(%s) ,%s ,%s ,%s )",
                       tuple(command))
        
    conn2db.commit()
    cur2db.close()
    conn2db.close()

def upload_turns (commandslist,db,user):	#uploads counts to turns table
    
    conn2db = psycopg2.connect("dbname="+db+" user="+user)
    cur2db = conn2db.cursor()
    
    #________________THIS IS ONLY FOR TESTING !!!
    
    cur2db.execute("DELETE from counts_turns;")
    
    for command in commandslist:
        #send command to server
        cur2db.execute("SELECT int_id from intersection_ids WHERE ((street1=UPPER(%s) AND street2=UPPER(%s)) OR (street1=UPPER(%s) AND street2=UPPER(%s)));",(command[4],command[8],command[8],command[4]))
        intid = -1 
        intid = cur2db.fetchone()
        if intid == None:
            print "F"
        else:
        #cur2db.execute("INSERT INTO counts_turns (count,starttime,period,vtype,fromstreet,fromdir,tostreet,todir,intstreet,intid,sourcefile,project) Values (%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s )",
            cur2db.execute("INSERT INTO counts_turns (count,starttime,period,vtype,fromstreet,fromdir,tostreet,todir,intstreet,intid,sourcefile,project) Values (%s ,%s ,%s ,%s ,UPPER(%s) ,%s ,UPPER(%s) ,%s ,UPPER(%s) ,%s ,%s ,%s )",
                            (command[0],command[1],command[2],command[3],command[4],command[5],command[6],command[7],command[8],intid,command[10],command[11],))
        
    conn2db.commit()
    cur2db.close()
    conn2db.close()

def street_names (commandslist,db,user):    #uploads street names to  table
    
    conn2db = psycopg2.connect("dbname="+db+" user="+user)
    cur2db = conn2db.cursor()
    
    #________________THIS IS ONLY FOR TESTING !!!
    cur2db.execute("DELETE from intersection_ids;")
    cur2db.execute("DELETE from street_names;")
    
    for command in commandslist:
        #send command to server
        #cur2db.execute("INSERT INTO counts_turns (count,starttime,period,vtype,fromstreet,fromdir,tostreet,todir,intstreet,intid,sourcefile,project) Values (%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s )",
        cur2db.execute("INSERT INTO street_names VALUES (%s)",
                       [command])
        
    conn2db.commit()
    cur2db.close()
    conn2db.close()

def int_ids (commandslist,db,user):    #uploads intersection ids table
    
    conn2db = psycopg2.connect("dbname="+db+" user="+user)
    cur2db = conn2db.cursor()
    
    #________________THIS IS ONLY FOR TESTING !!!
    cur2db.execute("DELETE from intersection_ids;")
    
    
    for command in commandslist:
        #send command to server
        #cur2db.execute("INSERT INTO intersection_ids VALUES (%s, %s, %s)",
        #=======================================================================
        # ONLY IF PAIR DOESNT EXIST
        #=======================================================================
        cur2db.execute("INSERT INTO intersection_ids (street1, street2, int_id) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT street1, street2 FROM intersection_ids WHERE street1 = %s AND street2 = %s);",
                           (command[0],command[1],command[2],command[0],command[1]))
            
    conn2db.commit()
    cur2db.close()
    conn2db.close()


           
def retrieve_table (filepath,table,db,user):        #save a table as csv (used for testing primarily) 
    
    myfile = open(filepath + '\\' + db + '_' + table + '.csv', 'wb') #Create CSV filename
    
    conn2db = psycopg2.connect("dbname="+db+" user="+user)
    cur2db = conn2db.cursor()
    
    cur2db.copy_to(myfile, table, sep="|")
    
    conn2db.commit()
    cur2db.close()
    conn2db.close()

if __name__ == '__main__':
    
    retrieve_table("C:\\Documents and Settings\\Varun\\Desktop\\Docs\\Samples","counts_ml","postgres", "postgres")