from petljakapi import connection, q
import petljakapi.dbs

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