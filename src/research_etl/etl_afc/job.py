import os
import datetime
import tarfile
import shutil
from typing import List

import sqlalchemy as sa

from research_etl.utils.util_rds import DatabaseManager
from research_etl.utils.util_rds import afc_copy
from research_etl.utils.util_logging import ProcessLogger
from research_etl.etl_afc.lookup_tables import deviceclass
from research_etl.etl_afc.lookup_tables import event
from research_etl.etl_afc.lookup_tables import eventgroup
from research_etl.etl_afc.lookup_tables import holiday
from research_etl.etl_afc.lookup_tables import mbta_weekend_service
from research_etl.etl_afc.lookup_tables import routes
from research_etl.etl_afc.lookup_tables import tariffversions
from research_etl.etl_afc.lookup_tables import tickettype
from research_etl.etl_afc.lookup_tables import tvmstation
from research_etl.etl_afc.lookup_tables import tvmtable
from research_etl.etl_afc.lookup_tables import LookupTables
from research_etl.utils.util_aws import file_list_from_s3
from research_etl.utils.util_aws import rename_s3_object
from research_etl.utils.util_aws import delete_object
from research_etl.utils.util_aws import download_file


def verify_partition(date: datetime.date, table: str, db_manager: DatabaseManager) -> None:
    """
    check if table partition exists for afc table and date
    if does not exist, create partition
    """
    partition_table = f"{table}_y{date.strftime('%Y')}m{date.strftime('%m')}"
    check_query = (
        "SELECT EXISTS ( "
        "    SELECT FROM pg_tables WHERE "
        "       schemaname = 'afc' "
        f"       AND tablename = '{partition_table}'"
        ");"
    )
    check_bool = db_manager.select_as_list(sa.text(check_query))[0]["exists"]

    if check_bool:
        # table already exists, do nothing
        return

    # create new partition table
    from_month = datetime.date(date.year, date.month, 1)
    if date.month == 12:
        to_month = datetime.date(date.year + 1, 1, 1)
    else:
        to_month = datetime.date(date.year, date.month + 1, 1)

    create_query = (
        f"CREATE TABLE afc.{partition_table} PARTITION OF afc.{table} "
        f"FOR VALUES FROM ('{from_month}') TO ('{to_month}');"
    )
    db_manager.execute(sa.text(create_query))


def load_ridership(file_path: str, db_manager: DatabaseManager) -> None:
    """
    load ridership csv.gz file into RDS
    """
    file_name = file_path.split("/")[-1]
    service_date = datetime.datetime.strptime(file_name[:8], "%Y%m%d").date()

    verify_partition(service_date, "ridership", db_manager)

    delete_query = f"DELETE FROM afc.ridership WHERE servicedate = '{service_date}';"
    db_manager.execute(sa.text(delete_query))

    headers = [
        "deviceclassid",
        "deviceid",
        "uniquemsid",
        "salestransactionno",
        "sequenceno",
        "trxtime",
        "servicedate",
        "branchlineid",
        "fareoptamount",
        "tariffversion",
        "articleno",
        "card",
        "ticketstocktype",
        "tvmtarifflocationid",
        "movementtype",
        "bookcanc",
        "correctioncounter",
        "correctionflag",
        "tempbooking",
        "testsaleflag",
        "inserted",
    ]

    afc_copy(file_path, "afc.ridership", headers)


def load_faregate(file_path: str, db_manager: DatabaseManager) -> None:
    """
    load faregate csv.gz file into RDS
    """
    file_name = file_path.split("/")[-1]
    service_date = datetime.datetime.strptime(file_name[:8], "%Y%m%d").date()

    verify_partition(service_date, "faregate", db_manager)

    delete_query = f"DELETE FROM afc.faregate WHERE servicedate = '{service_date}';"
    db_manager.execute(sa.text(delete_query))

    headers = [
        "trxtime",
        "servicedate",
        "deviceclassid",
        "deviceid",
        "uniquemsid",
        "eventsequno",
        "tariffversion",
        "tarifflocationid",
        "unplanned",
        "eventcode",
        "inserted",
    ]

    afc_copy(file_path, "afc.faregate", headers)


def load_lookups(file_path: str, db_manager: DatabaseManager) -> None:
    """
    load afc_lookups_.csv.tar.gz file into RDS
    """
    afc_folder = "/tmp/afc_lookups/"
    with tarfile.open(file_path) as afc_tar:
        afc_tar.extractall(afc_folder)

    afc_tables: List[LookupTables] = [
        deviceclass,
        event,
        eventgroup,
        holiday,
        mbta_weekend_service,
        routes,
        tariffversions,
        tickettype,
        tvmstation,
        tvmtable,
    ]

    for table in afc_tables:
        full_path = os.path.join(afc_folder, table["file_name"])
        table_name = f"afc.{table['file_name'].lower().replace('.csv','')}"
        db_manager.truncate_table(table_name, restart_identity=True)
        afc_copy(full_path, table_name, table["columns"])

    shutil.rmtree(afc_folder, ignore_errors=True)


def run() -> None:
    s3_in_path = "afc/in"
    s3_error_path = "afc/error"
    s3_in_bucket = os.getenv("AFC_IN_BUCKET", "")
    temp_download_folder = "/tmp"
    db_manager = DatabaseManager()

    for s3_object in file_list_from_s3(s3_in_bucket, s3_in_path):
        object_name = s3_object.split("/")[-1]
        full_local_path = os.path.join(temp_download_folder, object_name)
        download_file(s3_object, full_local_path)

        afc_log = ProcessLogger("afc_etl_job", s3_object=s3_object, local_path=full_local_path)
        afc_log.log_start()

        try:
            if "_ridership_" in object_name.lower():
                load_ridership(full_local_path, db_manager)
            elif "_faregate_" in object_name.lower():
                load_faregate(full_local_path, db_manager)
            elif "afc_lookups_" in object_name.lower():
                load_lookups(full_local_path, db_manager)

        except Exception as exception:
            rename_s3_object(s3_object, os.path.join(s3_in_bucket, s3_error_path, object_name))
            afc_log.log_failure(exception)
        else:
            delete_object(s3_object)
            afc_log.log_complete()
        finally:
            os.remove(full_local_path)


if __name__ == "__main__":
    run()
