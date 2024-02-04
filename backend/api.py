from fastapi import APIRouter, Form, HTTPException, status, UploadFile
from fastapi.responses import PlainTextResponse
from iptables.iptables_namespace import IptablesNS
from iptables.iptables_handler import IptablesHandler
from nsenter import Namespace
from jinja2 import Environment, FileSystemLoader
import pathlib
import aiofiles
import uuid
import os
import json


router = APIRouter()
iptablesns = IptablesNS()
filedir = pathlib.Path(__file__).parent.resolve() / "iptables"
template_env = Environment(loader=FileSystemLoader(f"{filedir}/scripts"))
url = "http://10.100.10.182:8000/api"
result_url = "http://127.0.0.1:3000"


@router.get("/setup", response_model=str)
def get_setup():
    template = template_env.get_template("all-in-one.sh")
    content = template.render(url=url, result_url=result_url)
    return PlainTextResponse(content)


@router.post("/iptables", response_model=str)
async def create_iptables(rules: str = Form()):
    netns = str(uuid.uuid4())[:8]

    filepath = filedir / "ruleset" / f"{netns}.iptables"
    async with aiofiles.open(filepath, "w") as f:
        rules = rules.replace("\r\n", "\n")
        await f.write(rules)
    try:
        iptablesns.addns(netns)
        iptablesns.init_iptables(filepath, netns)
    except Exception as e:
        iptablesns.delns(netns)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create iptables ruleset: {e}",
        )

    return PlainTextResponse(netns)


@router.get("/{namespace}", response_model=dict)
async def get_namespace_data(namespace: str):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )
    rules = iptablesns.get_iptables(namespace)
    interfaces = iptablesns.get_interfaces(namespace)
    return {"rules": rules, "interfaces": interfaces}


@router.get("/{namespace}/interfaces", response_model=str)
async def get_interfaces_script(namespace: str):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )
    template = template_env.get_template("interfaces.sh")
    content = template.render(url=url, netns=namespace)
    return PlainTextResponse(content)


@router.post("/{namespace}/interfaces", response_model=bool)
async def create_interfaces(namespace: str, interfaces: str = Form()):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )
    try:
        iptablesns.init_interfaces(json.loads(interfaces), namespace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create interfaces: {e}",
        )
    return True


@router.get("/{namespace}/ipset", response_model=str)
async def get_ipset_script(namespace: str):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )
    template = template_env.get_template("ipset.sh")
    content = template.render(url=url, netns=namespace)
    return PlainTextResponse(content)


@router.post("/{namespace}/ipset", response_model=bool)
async def create_ipset(namespace: str, ipset: str = Form()):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )

    filepath = filedir / "ruleset" / f"{namespace}.ipset"
    async with aiofiles.open(filepath, "w") as f:
        ipset = ipset.replace("\r\n", "\n")
        await f.write(ipset)

    try:
        iptablesns.init_ipset(filepath, namespace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not import ipset: {e}",
        )
    finally:
        os.remove(filepath)

    return True


@router.post("/{namespace}/packet", response_model=list)
async def create_import_packet(namespace: str, packet: dict):
    is_ns = iptablesns.findns(namespace)
    if not is_ns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Namespace not found"
        )
    with Namespace(f"/var/run/netns/{namespace}", "net"):
        iptables = IptablesHandler(namespace)
        results = iptables.import_packet(packet)
    return results
