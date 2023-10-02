from fastapi import APIRouter, Form, HTTPException, status, UploadFile
from iptables.iptables_namespace import IptablesNS
from iptables.iptables_handler import IptablesHandler
from nsenter import Namespace
import pathlib
import aiofiles
import uuid
import os


router = APIRouter()
iptablesns = IptablesNS()
FILE_DIR = pathlib.Path(__file__).parent.resolve() / "iptables" / "ruleset"


@router.get("/", response_model=dict)
def test():
    return {
        "env_id": "Hello World"
    }

@router.post("/iptables", response_model=dict)
async def create_iptables(filedata: UploadFile = Form()):
    ns = str(uuid.uuid4())[:8]
    filename = f"{ns}.iptables"
    filepath = f"{FILE_DIR}/{filename}"
    async with aiofiles.open(filepath, "wb") as out_file:
        while content := await filedata.read(1024):
            await out_file.write(content)
    try:
        iptablesns.addns(ns)
        iptablesns.init_iptables(filename, ns)
    except Exception as e:
        iptablesns.delns(ns)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create iptables ruleset: {e}",
        )
    finally:
        os.remove(filepath)

    return {
        "netns": ns
    }


@router.get("/{namespace}", response_model=bool)
async def get_iptables(namespace: str):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found"
        )
    #ruleset = iptablesns.get_iptables(namespace)
    #return ruleset  
    return True


@router.post("/{namespace}/ipset", response_model=bool)
async def create_ipset(namespace: str):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found"
        )
    return True


@router.post("/{namespace}/packet", response_model=list)
async def create_import_packet(namespace: str, packet: dict):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Namespace not found"
        )

    packet["ininf"] = None
    packet["outinf"] = None

    with Namespace(f"/var/run/netns/{namespace}", "net"):
        iptables = IptablesHandler()
        results = iptables.import_packet(packet)
    return results
