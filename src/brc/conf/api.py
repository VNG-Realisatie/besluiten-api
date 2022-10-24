import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "1.0.1"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100

DOCUMENTATION_INFO_MODULE = "brc.api.schema"

SPECTACULAR_SETTINGS = BASE_SPECTACULAR_SETTINGS.copy()
SPECTACULAR_SETTINGS.update(
    {
        "SERVERS": [{"url": "https://besluiten-api.test.vng.cloud/api/v1"}],
        # todo remove this line below when deploying to production
        "SORT_OPERATION_PARAMETERS": False,
    }
)

GEMMA_URL_INFORMATIEMODEL_VERSIE = "1.0"

ztc_repo = "vng-Realisatie/gemma-zaaktypecatalogus"
ztc_commit = "b8cc38484ad862b9bbbf975e24718ede3f662e1e"
ZTC_API_SPEC = f"https://raw.githubusercontent.com/{ztc_repo}/{ztc_commit}/src/openapi.yaml"  # noqa

drc_repo = "vng-Realisatie/gemma-documentregistratiecomponent"
drc_commit = "e82802907c24ea6a11a39c77595c29338d55e8c3"
DRC_API_SPEC = f"https://raw.githubusercontent.com/{drc_repo}/{drc_commit}/src/openapi.yaml"  # noqa

zrc_repo = "vng-Realisatie/gemma-zaakregistratiecomponent"
zrc_commit = "8ea1950fe4ec2ad99504d345eba60a175eea3edf"
ZRC_API_SPEC = f"https://raw.githubusercontent.com/{zrc_repo}/{zrc_commit}/src/openapi.yaml"  # noqa

SELF_REPO = "VNG-Realisatie/besluiten-api"
SELF_BRANCH = os.getenv("SELF_BRANCH") or API_VERSION
GITHUB_API_SPEC = f"https://raw.githubusercontent.com/{SELF_REPO}/{SELF_BRANCH}/src/openapi.yaml"  # noqa
