import sqlite3
import logging
###データベース関連の処理###

##設定リストの管理
server_settings = [
    ("server_id", "INTEGER"),
    ("speak_channel", "INTEGER"),
    ("auto_connect", "INTEGER DEFAULT 0"),
    ("speak_speed", "REAL DEFAULT 1"),
    ("length_limit", "INTEGER DEFAULT 50"),
    ("vc_join_message", "TEXT DEFAULT がさんかしたのだ！"),
    ("vc_exit_message", "TEXT DEFAULT がたいせきしたのだ！"),
    ("vc_connect_message", "TEXT DEFAULT せつぞくしたのだ！")
]


# グローバル変数としてcursorとconnを定義
cursor: sqlite3.Cursor
conn: sqlite3.Connection

##データベースに接続
def db_load(file):
    """
    データベースに接続します

    Args:
        file: ファイル名

    Returns:
        true: 正常  false:異常
    """
    try:
        global cursor, conn

        conn = sqlite3.connect(file)
        cursor = conn.cursor()

        conn.autocommit = True

        return True
    except:
        return False

def db_init():
    """
    データベースを準備します(更新も含む)

    Returns:
        true: 正常  false:異常
    """
    try:
        ##初期処理しちゃいますね(テーブルがないときに作成する)
        cursor.execute('CREATE TABLE IF NOT EXISTS "server_settings" (server_id INTEGER)')


        ##追加した名前のオブジェクトがなかった場合に新しく作成(server_settings)
        ##server_settingの状態を取得
        cursor.execute("PRAGMA table_info(server_settings)")

        ##不足している設定の追加
        columns = [column[1] for column in cursor.fetchall()]
        for name, type in server_settings:
            if name not in columns:
                cursor.execute(f'ALTER TABLE server_settings ADD COLUMN {name} {type}')

    except:
        return False

##データベースから設定を読み出し、返すやつ
def get_setting(server_id, type):
    """
    データベースの設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのサーバーID
        type: 設定内容

    Returns:
        Result or None
    """


    cursor.execute(f'SELECT {type} FROM server_settings WHERE server_id = {server_id}')
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO server_settings (server_id) VALUES (?)', (server_id,))
    
##設定を上書きするやつ
def save_setting(server_id, type, new_value):
    """
    データベースの設定を更新します

    Args:
        server_id: discordのサーバーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: Exception
    """
    try:
        result = cursor.execute(f'SELECT "{type}" FROM server_settings WHERE server_id = {server_id}').fetchone()
        if result is None:
            cursor.execute(f'INSERT INTO server_settings (server_id, "{type}") VALUES ({server_id}, {new_value})')
            logging.debug(f"Server '{server_id}' Setting was created ({type}: {new_value})")
            return
    
        cursor.execute(f'UPDATE server_settings SET "{type}" = "{new_value}" WHERE server_id = {server_id}')
        logging.debug(f"Server '{server_id}' Setting was updated ({type}: {new_value})")
        return
    
    except Exception as e:
        return e

