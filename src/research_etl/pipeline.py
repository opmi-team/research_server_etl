from research_etl.etl_gtfs.job import run as gtfs_job
from research_etl.etl_korbato.job import run as odx_job
from research_etl.etl_afc.job import run as afc_job


def run_jobs() -> None:
    """
    Run All ETL jobs
    """
    gtfs_job()
    odx_job()
    afc_job()


if __name__ == "__main__":
    run_jobs()
