from petljakapi import q
from petljakapi.connection import connection
import petljakapi.dbs

def update(db, table, filters, update_col, update_val):
    connection.reconnect(attempts=10, delay = 10)
    cursor = connection.cursor(buffered = True)
    petljakapi.dbs.chdb(db, cursor)
    filtlist = [f"`{k}`={q(v)}" for k, v in filters.items()]
    if len(filters.keys()) == 1:
        filtstring = filtlist[0]
    else:
        filtstring = " AND ".join(filtlist)
    query = f"UPDATE {table} SET `{update_col}`={q(update_val)} WHERE {filtstring}"
    print(f"executing:\n{query}")
    cursor.execute(query)
    connection.commit()
    return(None)