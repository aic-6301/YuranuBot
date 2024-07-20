import requests

VC_PORT = 50021
VC_HOST = "127.0.0.1"

spk_req = requests.get(url=f"http://{VC_HOST}:{VC_PORT}/speakers")
des_spks = spk_req.json()

for des_spk in des_spks:
    for style in des_spk["styles"]:
        if style["name"] in ("ノーマル","ふつう") :
            name=des_spk["name"]
            spk_id=style["id"]
            print(f"{name}, {spk_id}")
