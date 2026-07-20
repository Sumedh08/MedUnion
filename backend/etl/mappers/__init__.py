from etl.mappers.hospital_mapper import hospital_mapper
from etl.mappers.community_mapper import community_mapper

MAPPER_REGISTRY = {
    "hospital": hospital_mapper,
    "community": community_mapper,
}


def get_mapper(workspace: str):
    return MAPPER_REGISTRY.get(workspace)
