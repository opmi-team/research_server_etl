import os
import pathlib
import shutil
from io import StringIO

import paramiko
import sqlalchemy as sa

from research_etl.utils.util_logging import ProcessLogger
from research_etl.utils.util_rds import DatabaseManager
from research_etl.utils.util_rds import copy_zip_csv_to_db


def download_korbato_files(temp_folder: str) -> None:
    """
    download any available korbato imports from sftp endpoint
    save to temp_folder
    """
    download_logger = ProcessLogger("korbato_download")
    download_logger.log_start()

    # make clean temp_folder
    shutil.rmtree(temp_folder, ignore_errors=True)
    pathlib.Path(temp_folder).mkdir(parents=True, exist_ok=True)

    hostname = os.getenv("KORBATO_HOSTNAME", "")
    username = os.getenv("KORBATO_USERNAME", "")
    env_ssh_key = os.getenv("KORBATO_SSHKEY", "")

    # convert text key paramiko RSAKEY
    ssh_key = paramiko.RSAKey.from_private_key(StringIO(env_ssh_key))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=ssh_key,
        )

        sftp_client = client.open_sftp()
        # files for loading located in 'out' directory
        sftp_client.chdir("out")

        # get all files and save to local temp folder
        for file in sftp_client.listdir():
            sftp_client.get(file, os.path.join(temp_folder, file))

    except Exception as exception:
        download_logger.log_failure(exception)
        raise exception

    finally:
        client.close()

    download_logger.log_complete()


def load_korbato_file(file_path: str, db_manager: DatabaseManager) -> None:
    """
    load one korbato file into rds
    """
    file_name = file_path.split("/")[-1]

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

    copy_zip_csv_to_db(file_path, table)


def run() -> None:
    """
    main job event loop

    load any csv.zip files available in the Korbato SFTP folder
    """
    process_logger = ProcessLogger("etl_korbato")
    process_logger.log_start()

    download_folder = "/tmp/korbato_etl"
    try:
        db_manager = DatabaseManager()
        download_korbato_files(download_folder)

        downloaded_files = os.listdir(download_folder)
        process_logger.add_metadata(file_count=len(downloaded_files))
        for file in downloaded_files:
            load_korbato_file(os.path.join(download_folder, file), db_manager)

        process_logger.log_complete()

    except Exception as exception:
        process_logger.log_failure(exception)

    finally:
        shutil.rmtree(download_folder, ignore_errors=True)


if __name__ == "__main__":
    run()
