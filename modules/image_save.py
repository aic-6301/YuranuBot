import sqlite3

# データベースに接続（存在しない場合は作成）
conn = sqlite3.connect('servers.db')
cursor = conn.cursor()

# テーブルの作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL,
    data_blob BLOB NOT NULL
)
''')

# 変更を保存
conn.commit()

# データの挿入関数
def insert_data(server_id, data_blob):
    cursor.execute('''
    INSERT INTO servers (server_id, data_blob) VALUES (?, ?)
    ''', (server_id, data_blob))
    conn.commit()

# データの取得関数
def fetch_data():
    cursor.execute('SELECT server_id, data_blob FROM servers')
    rows = cursor.fetchall()
    for row in rows:
        print(f'Server ID: {row[0]}, Data: {row[1]}')

# 例としてデータを挿入（同じサーバーIDに複数のバイト列を挿入）
insert_data('server_1', b'This is the first binary data example')
insert_data('server_1', b'This is the second binary data example')
insert_data('server_2', b'Another binary data example for server_2')

# データの取得
fetch_data()

# データベース接続の終了
conn.close()
