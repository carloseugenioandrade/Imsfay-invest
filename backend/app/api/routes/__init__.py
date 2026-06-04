from fastapi import APIRouter

from app.api.routes import ativos, carteira, fiscal, market, proventos, transacoes, valuation

api_router = APIRouter()
api_router.include_router(ativos.router)
api_router.include_router(transacoes.router)
api_router.include_router(proventos.router)
api_router.include_router(valuation.router)
api_router.include_router(carteira.router)
api_router.include_router(fiscal.router)
api_router.include_router(market.router)
