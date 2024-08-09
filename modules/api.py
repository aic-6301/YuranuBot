from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from pydantic import BaseModel
from typing import Optional

from modules.db_settings import get_server_all_setting, db_load, save_server_setting
from modules.db_vc_dictionary import dictionary_load


class posttdata(BaseModel):
    welcome_server: Optional[int]
    speak_channel: Optional[int]
    auto_connect: Optional[int]
    speak_speed: Optional[int]
    length_limit: Optional[int]
    vc_join_message: Optional[int]
    vc_exit_message: Optional[int]
    vc_connect_message: Optional[int]
    vc_speaker: Optional[int]

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_headers=["*"])

db_load("database.db")
dictionary_load("dictionary.db")

@app.get("/")
def root():
    return {"message": "Hello World"}

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
                "vc_join_message": result[6],
                "vc_exit_message": result[7],
                "vc_connect_message": result[8],
                "vc_speaker": result[9]
            }
            return JSONResponse(content=data)
        else:
            return JSONResponse(content={"message": "No data found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": "Internal Server Error", "error": str(e)}, status_code=500)


@app.post("/guild/{guild_id}/settings")
async def post_guild_settings(guild_id: int, data: posttdata):
    try:
        result = get_server_all_setting(guild_id)
        if result:
            for key, value in data.dict().items():
                if value is not None:
                    save_server_setting(guild_id, key, value)
            return JSONResponse(content={"message": "OK"})
        else:
            return JSONResponse(content={"message": "Data not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": "Internal Server Error", "error": str(e)}, status_code=500)

uvicorn.run(app, host="localhost", port=8000)