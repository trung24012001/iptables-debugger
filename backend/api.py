from fastapi import APIRouter, Form, HTTPException, status
from iptables.iptables_namespace import IptablesNS
import pathlib
import aiofiles
import uuid


router = APIRouter()
iptablesns = IptablesNS()
FILE_DIR = pathlib.Path(__file__).parent.resolve() / "iptables" / "ruleset"

@router.get("/", response_model=dict)
def test():
    return {
        "env_id": "Hello World"
    }

@router.post("/iptables", response_model=dict)
async def create_iptables(filedata: object = Form(), infs: list = Form()):
    ns = str(uuid.uuid4())[:8]
    out_file = await aiofiles.open(f"{FILE_DIR}/{ns}.iptables", "wb")
    while content := await filedata.read(1024):
        await out_file.write(content)
    try:
        iptablesns.setup(filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create iptables ruleset: {e}",
        )

    return {
        "namespace": ns
    }
    
@router.post("/packet", response_model=dict)
async def handle_packet(packet: dict):
    return {}
