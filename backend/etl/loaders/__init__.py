from etl.loaders.hospital_loader import HospitalLoader
from etl.loaders.community_loader import CommunityLoader

LOADER_REGISTRY = {
    "hospital": HospitalLoader,
    "community": CommunityLoader,
}


def get_loader(workspace: str):
    loader_cls = LOADER_REGISTRY.get(workspace)
    if not loader_cls:
        return None
    return loader_cls
