from petljakapi import connection, q
import petljakapi.dbs
import petljakapi.select

def generic_insert(insert_keys, table, db = "petljakdb_devel"):
    ## Initialize
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    ## Check types
    if not isinstance(insert_keys, dict):
        raise(TypeError("insert_keys must be a dict"))
    if "rname" not in insert_keys.keys():
        raise(ValueError("rname must be a key in insert_keys"))
    ## unpack rname
    rname = insert_keys["rname"]
    ## Check if what we're inserting already exists
    result = petljakapi.select.simple_select(db = db, table = table, filter_column = "rname", filter_value = rname)
    ## If not, then do the insert
    if result:
        print(f"Value {rname} in column rname already exists. Skipping this add.")
    else:
        ## Create the colnames/values strings
        ## Need to keep things sorted so we do it this way
        ## Convert everything to a string, things that were strings before get quoted to play nice with mySQL
        colkeys = list(insert_keys.keys())
        colvals = [str(q(insert_keys[k])) for k in colkeys]
        colkeys = ", ".join(colkeys)
        colvals = ", ".join(colvals)
        ## Create the query and add the line
        query = f"INSERT INTO {table}({colkeys}) VALUES ({colvals})"
        print(f"Performing operation:\n{query};")
        cursor.execute(query)
        connection.commit()
        ## Now get the result of what we just inserted
        result = petljakapi.select.simple_select(db = db, table = table, filter_column = "rname", filter_value = rname)
    return(result)