import sqlite3

conn = sqlite3.connect("wardrobe.sqlite")


cursor = conn.cursor()

sql_query= """ CREATE TABLE wardrobe (
        id integer PRIMARY KEY,
        Article text NOT NULL,
        Color text NOT NULL,
        Size text NOT NULL,
        Material text NOT NULL,
        Season text NOT NULL
    )"""
sql_query= """ CREATE TABLE User_Data (
        User_Id integer PRIMARY KEY,
        Full_Name text NOT NULL,
        Username  text NOT NULL,
        Email text NOT NULL,
        Password text NOT NULL
    )"""

cursor.execute(sql_query)