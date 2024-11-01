import mysql.connector as mariadb
import datetime as datetime

mariadb_connection = mariadb.connect(user= 'sqluser', password = '123',database="DuckTape", host = 'localhost')
create_cusor = mariadb_connection.cursor()

class DTdatabase:
    def __init__(self):
        self.mariadb_connection = mariadb.connect(
            user= 'sqluser',
            password = '123',
            database="DuckTape",
            host = 'localhost'
        )
        self.create_cusor = mariadb_connection.cursor()
        self.histdict = {}
    # this function sorts the databass my date (most recent 5) and takes each date which is index[-1] in the databass and stores those results as keys in a new dictionary, histdict{}
    def history(self):
        sql_statement = "SELECT * FROM pics ORDER BY date DESC LIMIT 5;"
        self.create_cusor.execute(sql_statement)
        result = self.create_cusor.fetchall()
        for i in result:
            key = str(i[-1])
            value = 2
            self.histdict[key] = value
        return self.histdict.keys()
        
    # this function takes in a arguement (date) which will be retrived from the dictionary keys in the history() function above and will retrive the filename(filepath), response from gemini(description), and the date as a list in that order
    def record(self,date):
        
        sql_statement = "SELECT * FROM pics WHERE date = %s;"
        self.create_cusor.execute(sql_statement,(date,))
        return self.create_cusor.fetchall()
    # this function takes the latest row in the database and returns the filename(filepath), response from gimini(description), and date as a list in that order
    def last(self):
        sql_statement = "SELECT * FROM pics ORDER BY date DESC LIMIT 1;"
        self.create_cusor.execute(sql_statement)
        return self.create_cusor.fetchall()
    



############# MAIN (testing) ######################################
db = DTdatabase()
#print(db.history())
rec_var = list(db.history())
rec_var = str(rec_var[0])
#print (rec_var)
#print (type(db.record(rec_var)))
print(type(db.last()))
