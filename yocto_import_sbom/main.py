from . import global_values
from . import config
from .RecipeListClass import RecipeList
from .SBOMClass import SBOM
from .BOMClass import BOM
from .OEClass import OE
import logging
import sys


def main():
    config.check_args()

    logging.info(f"Processing files '{global_values.license_manifest}' and '{global_values.bitbake_layers}' ...")
    reclist = RecipeList(global_values.license_manifest, global_values.bitbake_layers)
    # reclist.print_recipes()

    if global_values.get_oe_data:
        oe_class = OE()
        reclist.check_recipes_in_oe(oe_class)
        logging.info("Done")
    else:
        logging.info("Skipping connection to OE APIs to verify origin layers and revisions")

    sbom = SBOM(global_values.bd_project, global_values.bd_version)
    sbom.process_recipes(reclist.recipes)
    sbomfile = sbom.output(global_values.output_file)

    if global_values.output_file != '':
        sys.exit(2)

    bom = BOM(global_values.bd_project, global_values.bd_version)

    if bom.upload_sbom(bom.bd, sbomfile):
        logging.info(f"Uploaded SBOM file '{sbomfile}' to create project {global_values.bd_project}/{global_values.bd_version}")
    else:
        sys.exit(2)

    if global_values.cve_check_file != '':
        bom.get_proj()
        if not bom.wait_for_bom_completion():
            logging.error("Error waiting for project scan completion")
            sys.exit(2)

        bom.get_data()
        bom.process_cve_file(global_values.cve_check_file, reclist)
        bom.process_patched_cves()
    else:
        logging.info("Skipping CVE processing as no cve_check output file supplied")

    logging.info("Done")


if __name__ == '__main__':
    main()