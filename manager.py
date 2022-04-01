import sqlite3
from datetime import datetime


def create_table():
    db = sqlite3.connect('.database.db')
    statement = '''CREATE TABLE if not exists MANAGER
	(ID INTEGER PRIMARY KEY AUTOINCREMENT,
	WEBSITE TEXT NOT NULL,
	PASSWORD TEXT NOT NULL,
	DATECREATED DATETIME NOT NULL
	);'''
    cur = db.cursor()
    cur.execute(statement)
    db.close()


def register_password(website, password):
    db = sqlite3.connect('.database.db')
    statement = '''INSERT INTO MANAGER(WEBSITE, PASSWORD, DATECREATED)
	VALUES (?,?,?)
	'''
    cur = db.cursor()
    date = datetime.utcnow()
    cur.execute(statement, (website, password, date))
    db.commit()
    db.close()
    return retrieve_password(website, date)


def search_website(website):
    db = sqlite3.connect('.database.db')
    statement = 'SELECT website,password,id FROM MANAGER where WEBSITE LIKE ? ORDER BY datecreated DESC'
    cur = db.cursor()
    items = cur.execute(statement, (str(website)+'%',))
    password_list = [i for i in items]
    return password_list


def all_website():
    db = sqlite3.connect('.database.db')
    statement = 'SELECT website,password,id  FROM MANAGER ORDER BY datecreated DESC'
    cur = db.cursor()
    items = cur.execute(statement)
    password_list = [i for i in items]
    # if callback:
    #     for p in password_list:
    #         callback(p)
    return password_list


def delete_website(id):
    db = sqlite3.connect('.database.db')
    statement = 'DELETE FROM MANAGER WHERE id = ?'
    cur = db.cursor()
    cur.execute(statement, (id,))
    db.commit()
    db.close()


def retrieve_password(website, date):
    db = sqlite3.connect('.database.db')
    statement = 'SELECT website,password,id FROM MANAGER where (WEBSITE, DATECREATED) = (?,?)'
    cur = db.cursor()
    items = cur.execute(statement, (website, date))
    password_list = [i for i in items]
    return password_list[0]


def update_password_entry(wbs, pwrd, id):
    db = sqlite3.connect('.database.db')
    statement = 'UPDATE MANAGER SET (WEBSITE, PASSWORD) = (?,?) WHERE id = {}'.format(
        id)
    cur = db.cursor()
    cur.execute(statement, (wbs, pwrd))
    db.commit()
    db.close()


# if __name__ == '__main__':
#     update_password_entry('new', 'newfdasf', 4)
