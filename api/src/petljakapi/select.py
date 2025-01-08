from petljakapi import q
from petljakapi.connection import connection
import petljakapi.dbs
import petljakapi.translate
import re
import time
import sys

def describe(db, table):
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    query = f"DESCRIBE {table}"
    cursor.execute(query)
    result = cursor.fetchall()
    return(result)

def simple_select(db, table, filter_column, filter_value, headers = False, bench = False):
    if bench:
        t1 = time.time()
    ## Initialize
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    ## Sanitize filter_value
    filter_value = q(filter_value)
    ## Build the query
    query = f"SELECT * FROM {table} WHERE {filter_column} = {filter_value}"
    cursor.execute(query)
    if headers:
        cols = [cursor.column_names]
    else:
        cols = []
    cols.extend(cursor.fetchall())
    if bench:
        t2 = time.time()
        print(f"SIMPLE_SELECT time = {t2 - t1}", file = sys.stderr)
    return(cols)

def multi_select(db, table, filters, headers = False, bench = False):
    if bench:
        t1 = time.time()
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    if not filters:
        ## No filters - dump whole table
        query = f"SELECT * FROM {table}"
    elif len(filters.keys()) == 1:
        return(simple_select(db, table, list(filters.keys())[0], list(filters.values())[0], headers))
    else:
        columns = list(filters.keys())
        filters = [f"{k} = {q(v)}" for k,v in filters.items()]
        ## Check if there's any NULL values, in which case we replace = with "is"
        filters = [re.sub("= NULL", "IS NULL", f) for f in filters]
        filterstring = " AND ".join(filters)
        query = f"SELECT * FROM {table} WHERE {filterstring}"
        #print(f"Trying {query}")
    cursor.execute(query)
    if headers:
        cols = [cursor.column_names]
    else:
        cols = []
    cols.extend(cursor.fetchall())
    if bench:
        t2 = time.time()
        print(f"SIMPLE_SELECT time = {t2 - t1}", file = sys.stderr)
    return(cols)

def parent_ids(in_id, db = "petljakdb_devel"):
    ## Prefix determines the database table for the ID
    prefix = in_id[:3]
    if prefix == "MPS":
        idtype = "samples"
    elif prefix == "MPR":
        idtype = "runs"
    elif prefix == "MPP":
        idtype = "studies"
    #print(id_dict)
    #print(prefix)
    #print(idtype)
    id_dict = {"studies":None, "samples":None, "runs":None}
    id_dict[idtype] = in_id
    #print(id_dict)
    ## End recursiveness
    if idtype == "studies":
        return(id_dict)
    ## Numeric ID
    num = int(in_id[3:])
    result = petljakapi.select.simple_select(db, idtype, "id", num)
    if not result:
        raise ValueError("Supplied ID {in_id} has no match in database")
    result = result[0]
    table_descr = petljakapi.select.describe(db, idtype)
    table_descr = [element[0] for element in table_descr]
    result = dict(zip(table_descr, result))
    id_dict["studies"] = petljakapi.translate.idtostring(result["study_id"], "MPP")
    if idtype == "runs":
        id_dict["samples"] = petljakapi.translate.idtostring(result["sample_id"], "MPS")
    return(id_dict)


def select_join_2(db, tbl1, tbl1_fkey, tbl2, tbl2_fkey, tbl1_cols = None, tbl2_cols = None, filters = None, headers = False):
    ## Open connection and set db
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    ## Handle table column selects
    if tbl1_cols == None:
        ## We want all columns
        select1 = f"{tbl1}.*"
    else:
        ## We want a subset of columns
        if isinstance(tbl1_cols, str):
            ## Handles the case of a single string column name
            tbl1_cols = [tbl1_cols]
        ## Concatenates to a comma-separated list
        select1 = ", ".join([f"{tbl1}.{elem}" for elem in tbl2_cols])
    ## Do the same for tbl2 and tbl2_cols
    if tbl2_cols == None:
        select2 = f"{tbl2}.*"
    else:
        if isinstance(tbl2_cols, str):
            tbl2_cols = [tbl2_cols]
        select2 = ", ".join([f"{tbl2}.{elem}" for elem in tbl2_cols])
    ## If we filter the rows at all
    if filters:
        ## Handle differently if there's one filter or multiple filters
        if len(filters.keys()) == 1:
            ## This is a mess, I know. It just unpacks the one-element dict and gives key=value
            filterstring = f"{list(filters.keys())[0]}={filters[list(filters.keys())[0]]}"
        else:
            ## Unpack dictionary and concatenates
            filters = [f"{k} = {q(v)}" for k,v in filters.items()]
            filterstring = " AND ".join(filters)
        ## Prefix for the WHERE statement
        filterstring = f" WHERE {filterstring}"
    else:
        ## Otherwise don't append anything to the query
        filterstring = ""
    ## Build query
    query = f"SELECT {select1}, {select2} FROM {tbl1} JOIN {tbl2} ON {tbl1}.{tbl1_fkey}={tbl2}.{tbl2_fkey}{filterstring}"
    cursor.execute(query)
    if headers:
        cols = [cursor.column_names]
    else:
        cols = []
    cols.extend(cursor.fetchall())
    return(cols)