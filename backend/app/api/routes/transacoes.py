from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.get("")
async def listar_transacoes():
    # TODO: listar transações
    return {"detail": "stub", "items": []}


@router.post("", status_code=201)
async def criar_transacao():
    # TODO: registrar compra/venda
    return {"detail": "stub"}


@router.post("/importar")
async def importar_extrato(file: UploadFile):
    # TODO: parsear extrato B3/corretora (XLSX/PDF) e injetar transações
    return {"detail": "stub", "filename": file.filename}
