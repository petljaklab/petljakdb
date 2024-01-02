from petljakapi import connection, q
import petljakapi.dbs
import petljakapi.translate

def describe(db, table):
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    query = f"DESCRIBE {table}"
    cursor.execute(query)
    result = cursor.fetchall()
    return(result)

def simple_select(db, table, filter_column, filter_value):
    ## Initialize
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    ## Sanitize filter_value
    filter_value = q(filter_value)
    ## Build the query
    query = f"SELECT * FROM {table} WHERE {filter_column} = {filter_value}"
    cursor.execute(query)
    result = cursor.fetchall()
    return(result)

def multi_select(db, table, filters):
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    if len(filters.keys()) == 1:
        return(simple_select(db, table, list(filters.keys())[0], list(filters.values())[0]))
    columns = list(filters.keys())
    filters = [f"{k} = {q(v)}" for k,v in filters.items()]
    filterstring = " AND ".join(filters)
    query = f"SELECT * FROM {table} WHERE {filterstring}"
    print(f"Trying {query}")
    cursor.execute(query)
    result = cursor.fetchall()
    return(result)

def parent_ids(in_id, id_dict = {"studies":None, "samples":None, "runs":None}, db = "petljakdb_devel"):
    ## Prefix determines the database table for the ID
    prefix = in_id[:3]
    if prefix == "MPS":
        idtype = "samples"
    elif prefix == "MPR":
        idtype = "runs"
    elif prefix == "MPP":
        idtype = "studies"
    print(prefix)
    id_dict[idtype] = in_id
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