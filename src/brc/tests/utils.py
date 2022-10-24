import os

from django.conf import settings


def get_oas_spec(service):
    spec_dirs = settings.TEST_SPEC_DIRS

    try:
        filepath = next((os.path.join(path, f"{service}.yaml") for path in spec_dirs))
    except StopIteration:
        raise IOError(f"OAS for {service} not found")

    with open(filepath, "rb") as oas_spec:
        return oas_spec.read()
