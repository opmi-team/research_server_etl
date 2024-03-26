import os
import tempfile
from io import StringIO

import paramiko
import sqlalchemy as sa

from research_etl.utils.util_logging import ProcessLogger
from research_etl.utils.util_rds import DatabaseManager
from research_etl.utils.util_rds import copy_zip_csv_to_db
from research_etl.utils.util_sftp import walk_sftp_dirs


def connect_ssh_client(hostname: str = "", username: str = "") -> paramiko.SSHClient:
    """
    get/create paramiko sftp client
    """
    logger = ProcessLogger("create_ssh_client")
    logger.log_start()

    if hostname == "":
        hostname = os.getenv("KORBATO_HOSTNAME", "")
    if username == "":
        username = os.getenv("KORBATO_USERNAME", "")

    env_ssh_key = os.getenv("KORBATO_SSHKEY", "")

    ssh_key = paramiko.Ed25519Key.from_private_key(StringIO(env_ssh_key))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=ssh_key,
        )
    except Exception as exception:
        logger.log_failure(exception)
        raise exception

    logger.log_complete()

    return client


def download_sftp_file(sftp_path: str, local_path: str, sftp_client: paramiko.SFTPClient) -> None:
    """
    download an sftp_path to a local_path
    """
    download_logger = ProcessLogger("sftp_download", sftp_path=sftp_path, local_path=local_path)
    download_logger.log_start()

    try:
        sftp_client.get(sftp_path, local_path)

    except Exception as exception:
        download_logger.log_failure(exception)
        raise exception

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
        ssh_client = connect_ssh_client()
        sftp_client = ssh_client.open_sftp()

        sftp_paths = walk_sftp_dirs(sftp_client, "out")

        process_logger.add_metadata(file_count=len(sftp_paths))
        for sftp_path in sftp_paths:
            sftp_file = sftp_path.split("/")[-1]
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
                temp_file = os.path.join(temp_dir, sftp_file)
                download_sftp_file(sftp_path, temp_file, sftp_client)
                load_korbato_file(temp_file, db_manager)

        sftp_client.close()
        ssh_client.close()

        process_logger.log_complete()

    except Exception as exception:
        process_logger.log_failure(exception)


def alt_run(db_manager: DatabaseManager) -> None:
    """
    main job event loop

    load any csv.zip files available in the catch-up Korbato SFTP folder
    """
    process_logger = ProcessLogger("catch_up_korbato")
    process_logger.log_start()

    try:
        ssh_client = connect_ssh_client(
            hostname="sftp.korbato.com",
        )
        sftp_client = ssh_client.open_sftp()

        sftp_paths = walk_sftp_dirs(sftp_client, "out")

        process_logger.add_metadata(file_count=len(sftp_paths))
        for sftp_path in sftp_paths:
            sftp_file = sftp_path.split("/")[-1]
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
                temp_file = os.path.join(temp_dir, sftp_file)
                download_sftp_file(sftp_path, temp_file, sftp_client)
                load_korbato_file(temp_file, db_manager)

        sftp_client.close()
        ssh_client.close()

        process_logger.log_complete()

    except Exception as exception:
        process_logger.log_failure(exception)


if __name__ == "__main__":
    local_db = DatabaseManager()
    run(local_db)
