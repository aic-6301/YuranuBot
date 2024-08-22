from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

import uvicorn
import os

from pydantic import BaseModel
from typing import Optional, Union

from db_settings import (
    get_server_all_setting,
    db_load,
    save_server_setting,
    get_user_all_settings,
    save_user_setting,
)
from db_vc_dictionary import dictionary_load, get_dictionary, save_dictionary
from dotenv import load_dotenv


class posttdata(BaseModel):
    welcome_server: Optional[int] = None
    speak_channel: Optional[int] = None
    auto_connect: Optional[int] = None
    speak_speed: Optional[int] = None
    length_limit: Optional[int] = None
    vc_join_message: Optional[str] = None
    vc_exit_message: Optional[str] = None
    connect_message: Optional[str] = None
    vc_speaker: Optional[int] = None


class user_posttdata(BaseModel):
    vc_speaker: Optional[int] = None
    vc_join_message: Optional[str] = None
    vc_exit_message: Optional[str] = None
    speak_speed: Optional[float] = None


class dictionary_post(BaseModel):
    word: str
    reading: str
    user: int


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# .envから設定値を取得
load_dotenv()
DIC_DIR = os.getenv("DIC_DIR")

# データベースの読み込み
db_load("database.db")

# サーバー辞書共有用
# ディレクトリが設定されている場合はその場所を指定
if type(DIC_DIR) is str:
    dic_data = dictionary_load(os.path.join(DIC_DIR, "dictionary.db"))
# ディレクトリが設定されていない場合はデフォルトの場所
else:
    dic_data = dictionary_load("dictionary.db")


@app.get("/")
def root():
    return {"message": "Hello World"}


# Server settings


@app.get("/guild/{guild_id}/settings")
async def get_guild_settings(guild_id: int, type: str = None):
    try:
        result = get_server_all_setting(guild_id)
        print(result)
        if result:
            data = {
                "guild_id": str(result[0]),
                "welcome_server": f"{result[1]}",
                "speak_channel": f"{result[2]}",
                "auto_connect": f"{result[3]}",
                "speak_speed": f"{result[4]}",
                "length_limit": result[5],
                "join_message": result[6],
                "exit_message": result[7],
                "connect_message": result[8],
                "vc_speaker": result[9],
                "user_announce": result[10],
            }
            return JSONResponse(content=data)
        else:
            return JSONResponse(content={"message": "Server Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


@app.post("/guild/{guild_id}/settings")
async def post_guild_settings(guild_id: int, data: posttdata):
    try:
        if all(value is None for value in data.model_dump().values()):
            return JSONResponse(content={"message": "Bad Request"},
                                status_code=400)
        result = get_server_all_setting(guild_id)
        if result:
            for key, value in data.model_dump().items():
                if value is not None:
                    save_server_setting(guild_id, key, value)
            return JSONResponse(content={"message": "OK"})
        else:
            return JSONResponse(content={"message": "Server Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


# Dictionary


@app.get("/guild/{guild_id}/dictionary")
async def get_guild_dictionary(guild_id: int, limit: int = 10):
    try:
        result = get_dictionary(guild_id)
        if limit == 0:
            limit = 10000
        elif type(limit) is not int:
            return JSONResponse(content={"message": "Bad Request"},
                                status_code=400)
        else:
            limit = int(limit)
        if result:
            data = []
            for page in result:
                data.append({
                    "word": page[0],
                    "reading": page[1],
                    "user": page[2]
                })
            return JSONResponse(content={"message": "OK", "data": data})
        else:
            return JSONResponse(content={"message": "Server Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


@app.post("/guild/{server_id}/dictionary")
async def post_guild_settings(server_id: int, data: dictionary_post):
    try:
        result = get_dictionary(server_id)
        if result:
            save_dictionary(server_id, data.word, data.reading, data.user)
            return JSONResponse(content={"message": "OK"})
        else:
            return JSONResponse(content={"message": "Server Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


# User settings


@app.get("/user/{user_id}/settings")
async def get_guild_settings(user_id: int, type: str = None):
    try:
        result = get_user_all_settings(user_id)
        print(result)
        if result:
            data = {
                "user_id": str(result[0]),
                "vc_speaker": f"{result[1]}",
                "join_message": f"{result[2]}",
                "exit_message": f"{result[3]}",
                "speak_speed": f"{result[4]}",
            }
            return JSONResponse(content=data)
        else:
            return JSONResponse(content={"message": "User Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


@app.post("/user/{user_id}/settings")
async def post_guild_settings(user_id: int, data: user_posttdata):
    try:
        if all(value is None for value in data.model_dump().values()):
            return JSONResponse(content={"message": "Bad Request"},
                                status_code=400)
        result = get_user_all_settings(user_id)
        if result:
            for key, value in data.model_dump().items():
                if value is not None:
                    save_user_setting(user_id, key, value)
            return JSONResponse(content={"message": "OK"})
        else:
            return JSONResponse(content={"message": "User Not found"},
                                status_code=404)
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal Server Error",
                "error": str(e)
            },
            status_code=500,
        )


# Teapot


@app.get("/418")
def teapot():
    return Response(content="I'm a teapot", status_code=418)


uvicorn.run(app, host="localhost", port=8000)
