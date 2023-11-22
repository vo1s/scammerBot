import sqlite3 as sq
db = sq.connect("main_db.db")
cursor = db.cursor()

async def db_start():
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS scammer
                   (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   tg_scammer_id INTEGER,
                   tg_scammer_nick TEXT,
                   scam_caption TEXT,
                   photo_scam BLOB,
                   tg_victim_id INTEGER,
                   tg_victim_nick TEXT,
                   not_scammer INTEGER DEFAULT 0
                   );
                   ''')


    cursor.execute('''
                       CREATE TABLE IF NOT EXISTS temp_storage
                       (
                       id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       tg_scammer_id INTEGER,
                       tg_scammer_nick TEXT,
                       scam_caption TEXT,
                       photo_scam BLOB,
                       tg_victim_id INTEGER,
                       tg_victim_nick TEXT,
                       not_scammer INTEGER DEFAULT 0
                       );
                       ''')

    db.commit()