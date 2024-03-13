import os
import tempfile
from io import StringIO
from typing import List

import paramiko
import sqlalchemy as sa

from research_etl.utils.util_logging import ProcessLogger
from research_etl.utils.util_rds import DatabaseManager
from research_etl.utils.util_rds import copy_zip_csv_to_db


def get_korbato_file_list() -> List[str]:
    """
    get list of any available korbato imports from sftp endpoint
    """
    list_logger = ProcessLogger("get_korbato_file_list")
    list_logger.log_start()

    sftp_folder = "out"
    hostname = os.getenv("KORBATO_HOSTNAME", "")
    username = os.getenv("KORBATO_USERNAME", "")
    env_ssh_key = os.getenv("KORBATO_SSHKEY", "")

    list_logger.add_metadata(
        sftp_folder=sftp_folder,
    )

    # convert text key paramiko RSAKEY
    ssh_key = paramiko.Ed25519Key.from_private_key(StringIO(env_ssh_key))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    return_list = []
    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=ssh_key,
        )

        sftp_client = client.open_sftp()

        # get all files and save to local temp folder
        for file in sftp_client.listdir(sftp_folder):
            return_list.append(os.path.join(sftp_folder, file))

        list_logger.add_metadata(file_count=len(return_list))

    except Exception as exception:
        list_logger.log_failure(exception)
        raise exception

    finally:
        client.close()

    list_logger.log_complete()

    return return_list


def download_sftp_file(sftp_path: str, local_path: str) -> None:
    """
    download an sftp_path to a local_path
    """
    download_logger = ProcessLogger("sftp_download", sftp_path=sftp_path, local_path=local_path)
    download_logger.log_start()

    hostname = os.getenv("KORBATO_HOSTNAME", "")
    username = os.getenv("KORBATO_USERNAME", "")
    env_ssh_key = os.getenv("KORBATO_SSHKEY", "")

    # convert text key paramiko RSAKEY
    ssh_key = paramiko.Ed25519Key.from_private_key(StringIO(env_ssh_key))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=ssh_key,
        )

        sftp_client = client.open_sftp()

        sftp_client.get(sftp_path, local_path)

    except Exception as exception:
        download_logger.log_failure(exception)
        raise exception

    finally:
        client.close()

    download_logger.log_complete()


def load_korbato_file(local_path: str, db_manager: DatabaseManager) -> None:
    """
    load one korbato file into rds

    /tmp/20240309_vehicle_day_20240312-200001.csv.zip_u569z9u
    """
    file_name = local_path.split("/")[-1]

    schema = os.getenv("KORBATO_SCHEMA", "")

    # handle data tables
    if file_name[:8].isnumeric():
        year = file_name[:4]
        month = file_name[4:6]
        day = file_name[6:8]

        table = file_name[9:].rsplit("_", 1)[0]
        table = f"{schema}.{table}"

        del_q = sa.text(f"DELETE FROM {table} WHERE svc_date = '{year}-{month}-{day}'")
        db_manager.execute(del_q)

    # handle lookup tables
    else:
        table = file_name.rsplit("_", 1)[0]
        table = f"{schema}.{table}"

        # for pattern, explicitly truncate it along with pattern_stop (a
        # dependency) rather than cascading, which might truncate other
        # dependent tables that we're not aware of
        if table == "pattern":
            db_manager.truncate_table(f"{schema}.pattern_stop")

        db_manager.truncate_table(table)

    copy_zip_csv_to_db(local_path, table)


def run(db_manager: DatabaseManager) -> None:
    """
    main job event loop

    load any csv.zip files available in the Korbato SFTP folder
    """
    process_logger = ProcessLogger("etl_korbato")
    process_logger.log_start()

    try:
        sftp_paths = get_korbato_file_list()
        process_logger.add_metadata(file_count=len(sftp_paths))
        for sftp_path in sftp_paths:
            sftp_file = sftp_path.split("/")[-1]
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
                temp_file = os.path.join(temp_dir, sftp_file)
                download_sftp_file(sftp_path, temp_file)
                load_korbato_file(temp_file, db_manager)

        process_logger.log_complete()

    except Exception as exception:
        process_logger.log_failure(exception)


if __name__ == "__main__":
    local_db = DatabaseManager()
    run(local_db)
