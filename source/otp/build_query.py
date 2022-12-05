def query_str(data_query):
    str_query = ''
    for key in data_query:
        if isinstance(data_query[key], list):
            for i in data_query[key]:
                if str_query == '':
                    str_query += "{}={}".format(key, i)
                else:
                    str_query += "&{}={}".format(key, i)
        else:
            if str_query == '':
                str_query += "{}={}".format(key, data_query[key])
            else:
                str_query += "&{}={}".format(key, data_query[key])
    return str_query.replace(" ", "")
