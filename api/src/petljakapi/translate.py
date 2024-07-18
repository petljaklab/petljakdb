def idtostring(id, prefix):
    string = prefix + format(int(id), "06d")
    return(string)

def stringtoid(string):
    num = int(string[3:])
    return(num)
