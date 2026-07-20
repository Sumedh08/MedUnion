from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import logger
from core.database import check_database_connection, run_migrations, SessionLocal
from core.workspace import init_workspaces
from core.event_handlers import register_import_handlers
from connectors import init_connectors
from agents import init_agents
from knowledge_graph.graph import init_knowledge_graph
from routers import auth, health, workspace, hospital, community, intelligence, simulation, knowledge, imports


def bootstrap_canonical_data():
    """Load seed fixture data on first run when tables are empty.

    The fixture file (fixtures/seed_data.sql) was exported from one final
    run of the deterministic demo generators. This replaces the old approach
    which ran ImportManager with demo connectors at startup.
    """
    from seed import is_seeded, seed

    if is_seeded():
        logger.info("Bootstrap: canonical data already present — skipping seed")
        return

    logger.info("Bootstrap: canonical tables empty — loading seed fixture")
    seed()

    from core.database import SessionLocal
    from knowledge_graph.graph import rebuild_from_database
    db = SessionLocal()
    try:
        rebuild_from_database(db)
        logger.info("Bootstrap: knowledge graph rebuilt")
    except Exception as e:
        logger.warning(f"Bootstrap: knowledge graph rebuild failed ({e}) — skipping")
    finally:
        db.close()

    logger.info("Bootstrap: seed finished")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME}")

    db_ok = check_database_connection()
    if not db_ok:
        logger.warning("Database not available — some features may be limited")
    else:
        run_migrations()

    connector_registry = init_connectors()

    register_import_handlers()

    if db_ok:
        bootstrap_canonical_data()

    init_workspaces()

    init_agents()
    init_knowledge_graph()

    logger.info(f"Connectors: {list(connector_registry.list().keys())}")
    logger.info(f"Connector count: {connector_registry.connector_count()}")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Enterprise AI Health Intelligence Platform. "
        "Read-only integrations, multi-agent AI, digital twin simulations."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(workspace.router, prefix=settings.API_V1_STR)
app.include_router(hospital.router, prefix=settings.API_V1_STR)
app.include_router(community.router, prefix=settings.API_V1_STR)
app.include_router(intelligence.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)
app.include_router(knowledge.router, prefix=settings.API_V1_STR)
app.include_router(imports.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "2.0.0",
        "architecture": {
            "integration": "read-only connectors (FHIR, DHIS2)",
            "intelligence": "multi-agent AI system (Phase 4)",
            "knowledge": "healthcare knowledge graph",
            "simulation": "digital twin engine (Phase 4)",
            "presentation": "enterprise dashboard + AI copilot",
        },
        "workspaces": ["hospital", "community"],
        "principles": [
            "Never modify external healthcare systems",
            "Read-only connectors only",
            "AI-augmented decision support",
            "Explainable recommendations",
        ],
    }
