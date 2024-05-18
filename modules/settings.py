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
    ("vc_join_message", "TEXT DEFAULT がさんかしました！"),
    ("vc_exit_message", "TEXT DEFAULT がたいせきしました！"),
    ("vc_connect_message", "TEXT DEFAULT せつぞくしました！"),
    ("vc_speaker", "INTEGER DEFAULT 3")
]

user_settings = [
    ("user_id", "INTEGER"),
    ("vc_speaker", "INTEGER DEFAULT -1")
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
        cursor.execute('CREATE TABLE IF NOT EXISTS "user_settings" (user_id INTEGER)')

        ##追加した名前のオブジェクトがなかった場合に新しく作成(server_settings)
        ##server_settingの状態を取得
        cursor.execute("PRAGMA table_info(server_settings)")

        ##不足している設定の追加
        columns = [column[1] for column in cursor.fetchall()]
        for name, type in server_settings:
            if name not in columns:
                cursor.execute(f'ALTER TABLE server_settings ADD COLUMN {name} {type}')
    

        ##追加した名前のオブジェクトがなかった場合に新しく作成(user_settings)
        ##user_settingの状態を取得
        cursor.execute("PRAGMA table_info(user_settings)")

        ##不足している設定の追加
        columns = [column[1] for column in cursor.fetchall()]
        for name, type in user_settings:
            if name not in columns:
                cursor.execute(f'ALTER TABLE user_settings ADD COLUMN {name} {type}')
    
        conn.commit()
        return True
    
    except:
        return False

##データベースから設定を読み出し、返すやつ
def get_server_setting(id, type):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのサーバーID
        type: 設定内容

    Returns:
        Result or None
    """

    list_type = "server_settings"
    id_type = "server_id"

    cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))
    
##設定を上書きするやつ
def save_server_setting(id, type, new_value):
    """
    データベースのサーバー設定を更新します

    Args:
        server_id: discordのユーザーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: Exception
    """
    list_type = "server_settings"
    id_type = "server_id"

    try:
        result = cursor.execute(f'SELECT "{type}" FROM {list_type} WHERE {id_type} = {id}').fetchone()
        if result is None:
            cursor.execute(f'INSERT INTO {list_type} ({id_type}, "{type}") VALUES ({id}, {new_value})')
            conn.commit()
            
            logging.info(f"{list_type} '{id}' was created ({type}: {new_value})")
            return
    
        cursor.execute(f'UPDATE {list_type} SET "{type}" = "{new_value}" WHERE {id_type} = {id}')
        conn.commit()

        logging.info(f"{list_type} '{id}' was updated ({type}: {new_value})")
        return
    
    
    except Exception as e:
        return e

##データベースから設定を読み出し、返すやつ
def get_user_setting(id, type):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのユーザーID
        type: 設定内容

    Returns:
        Result or None
    """

    list_type = "user_settings"
    id_type = "user_id"

    cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))
    
##設定を上書きするやつ
def save_user_setting(id, type, new_value):
    """
    データベースのサーバー設定を更新します

    Args:
        server_id: discordのユーザーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: Exception
    """
    list_type = "user_settings"
    id_type = "user_id"

    try:
        result = cursor.execute(f'SELECT "{type}" FROM {list_type} WHERE {id_type} = {id}').fetchone()
        if result is None:
            cursor.execute(f'INSERT INTO {list_type} ({id_type}, "{type}") VALUES ({id}, {new_value})')
            conn.commit()
            
            logging.debug(f"{list_type} '{id}' was created ({type}: {new_value})")
            return
    
        cursor.execute(f'UPDATE {list_type} SET "{type}" = "{new_value}" WHERE {id_type} = {id}')
        conn.commit()

        logging.debug(f"{list_type} '{id}' was updated ({type}: {new_value})")
        return
    
    
    except Exception as e:
        return e
