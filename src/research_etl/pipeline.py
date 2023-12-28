import os

from research_etl.etl_gtfs.gtfs_job import run as gtfs_job
from research_etl.etl_korbato.korbato_job import run as odx_job
from research_etl.etl_afc.afc_job import run as afc_job

from research_etl.utils.util_aws import check_for_parallel_tasks


def run_jobs() -> None:
    """
    Run All ETL jobs
    """
    os.environ["SERVICE_NAME"] = "opmi_research_etl"

    check_for_parallel_tasks()

    gtfs_job()
    odx_job()
    afc_job()


if __name__ == "__main__":
    run_jobs()
