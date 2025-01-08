from petljakapi import q
from petljakapi.connection import connection
import petljakapi.dbs
import petljakapi.select
import petljakapi.translate

def daughter_cells(id, db = "petljakdb_devel"):
    ## Initialize
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    ## Check if id is numeric, if so, use it, if not, try to convert
    ### First type check
    if isinstance(id, int):
        pass
    ## Next we process the ID (if correctly formatted)
    elif isinstance(id, str):
        if not id.startswith("MPS"):
            raise ValueError(f"id does not appear to be an MPS id")
        else:
            id = petljakapi.translate.stringtoid(id)
    else:
        raise TypeError(f"id is neither int or str: {id}")
    result = petljakapi.select.multi_select(db = db, table = "samples", filters = {"sample_parent_id":id}) 
    return(result)