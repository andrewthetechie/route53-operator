from pathlib import Path
from sys import argv
from sys import exit

import yaml

from route53_operator.crds import CRDS

if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: python generate_crds_yaml.py <output path>")
        exit(1)

    output_path = Path(argv[1]).expanduser()
    output_path.mkdir(exist_ok=True)
    for crd in CRDS:
        this_crd_path = output_path / f"{crd.__qualname__}.yml"
        with open(this_crd_path, "w") as f:
            f.write(yaml.dump(crd().to_crd()))
    exit(0)
