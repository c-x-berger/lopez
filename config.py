sql_user = "edwan"
# for obvious reasons this should be changed
sql_pass = "johny johny telling lies"
sql_db = "lopez"
sql_host = "localhost"
sql_port = 5432
# changing the below line will void the non-existent warranty Lopez came with
# so please don't
postgresql = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    sql_user, sql_pass, sql_host, sql_port, sql_db
)
