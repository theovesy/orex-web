import sqlite3 as lite

# Connect to a db and return Connect and Cursor objects
def db_connect(db_name):
	
	con = lite.connect(db_name)
	con.row_factory = lite.Row
	cur = con.cursor()
	
	return con, cur
	
# Execute a querry and return resulting lines
def getFromQuerry(cur, querry):
	
	cur.execute(querry)
	lines = cur.fetchall()
	
	return lines
	
# Create a SELECT querry from a list of arguments
def querryFromSelect(args, table):
	
	querry = "SELECT " + ", ".join(args) + " from " + table
	
	return querry	

# Create a SELECT querry with JOIN(S)
# table_list : list of tables
# join_dic : join dictionny --> ex : {"table1.id": "table2.num"} => table1.id = table2.num
def querryFromJoin(args, table_list, join_dic):
	
	querry = "SELECT " + ", ".join(args) + " from " + table_list[0]
		
	for i in range(len(table_list)-1):
		key = list(join_dic.keys())[i]
		value = list(join_dic.values())[i]
		querry += " JOIN " + table_list[i] + " ON " + key + " = " + value
		
	return querry
	
# Add a WHERE condition to the querry
def addWhereCondition(querry, condition):
	
	querry += " WHERE " + condition
	
	return querry

# Add an ORDER BY condition to the querry
def addOrderByCondition(querry, condition, direction="DESC"):
	
	querry += " ORDER BY " + condition + " " + direction
	
	return querry
	
#querry = ""
#querry = querryFromJoin(["commande.numero", "commande.date_rec", "piece.ref", "contient.quantite"], ["commande", "piece", "contient"], {"commande.numero": "contient.commande", "contient.ref": "piece.ref"})
#print(querry)
