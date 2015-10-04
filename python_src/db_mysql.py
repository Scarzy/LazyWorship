import MySQLdb as mysql

class Database():
    def __init__(self):
        self.connect()
    
    def connect(self):
        self.db_conn = mysql.connect(host="localhost", db="lazyworship", user='root')
        self.db = self.db_conn.cursor()
        self.create_unknown()
    
    def create_unknown(self):
        # Prevents a crash by creating a dummy dataset
        self.db.execute("CREATE TABLE IF NOT EXISTS unknown (verse int, part int, lyric varchar(255))")
        self.db.execute("INSERT INTO unknown VALUES (0, 0, '')")
    
    def get_lyrics(self, song, verse, part):
        res = self.db.execute("SELECT * FROM %s WHERE verse=%d AND part=%d" % (song, verse, part))
        for (verse, part, lyric) in self.db:
            return lyric


if __name__ == "__main__":
    db = Database()
    print db.get_lyrics("amazing_grace", 0, 0)
