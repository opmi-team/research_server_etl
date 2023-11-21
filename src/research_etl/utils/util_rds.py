import os
import gzip
import platform
import subprocess
import urllib.parse as urlparse
from typing import Any, Dict, List, Tuple, Union

import polars
import boto3
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from research_etl.utils.util_logging import ProcessLogger


def running_in_docker() -> bool:
    """
    return True if running inside of a docker container, else False
    """
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path, encoding="UTF-8"))
    )


def running_in_aws() -> bool:
    """
    return True if running on aws, else False
    """
    return bool(os.getenv("AWS_DEFAULT_REGION"))


def get_db_host() -> str:
    """
    get current db_host string
    """
    db_host = os.environ.get("DB_HOST", "")

    # on mac, when running in docker locally db is accessed by "0.0.0.0" ip
    if db_host == "dmap_local_rds" and "macos" in platform.platform().lower():
        db_host = "0.0.0.0"

    # when running application locally in CLI for configuration
    # and debugging, db is accessed by localhost ip
    if not running_in_docker() and not running_in_aws():
        db_host = "127.0.0.1"

    return db_host


def get_db_password() -> str:
    """
    function to provide rds password

    used to refresh auth token, if required
    """
    db_password = os.environ.get("DB_PASSWORD", None)
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_user = os.environ.get("DB_USER")
    db_region = os.environ.get("DB_REGION", None)

    if db_password is None:
        # generate aws db auth token if in rds
        client = boto3.client("rds")
        return client.generate_db_auth_token(
            DBHostname=db_host,
            Port=db_port,
            DBUsername=db_user,
            Region=db_region,
        )

    return db_password


def create_db_connection_string() -> str:
    """
    produce database connection string from environment
    """
    process_log = ProcessLogger("create_db_connection_string")
    process_log.log_start()

    db_host = get_db_host()
    db_name = os.environ.get("DB_NAME")
    db_password = os.environ.get("DB_PASSWORD", None)
    db_port = os.environ.get("DB_PORT")
    db_user = os.environ.get("DB_USER")
    db_ssl_options = ""

    assert db_host is not None
    assert db_name is not None
    assert db_port is not None
    assert db_user is not None

    process_log.add_metadata(host=db_host, database_name=db_name, user=db_user, port=db_port)

    # use presence of DB_PASSWORD env var as indicator of connection type.
    #
    # if not available, assume cloud database where ssl is used and
    # passwords are generated on the fly
    #
    # if is available, assume local dev usage
    if db_password is None:
        db_password = get_db_password()
        db_password = urlparse.quote_plus(db_password)

        assert db_password is not None
        assert db_password != ""

        # set the ssl cert path to the file that should be added to the
        # lambda function at deploy time
        db_ssl_cert = os.path.abspath(os.path.join("/", "usr", "local", "share", "amazon-certs.pem"))

        assert os.path.isfile(db_ssl_cert)

        # update the ssl options string to add to the database url
        db_ssl_options = f"?sslmode=verify-full&sslrootcert={db_ssl_cert}"

    process_log.log_complete()

    return f"{db_user}:{db_password}@{db_host}:{db_port}/{db_name}{db_ssl_options}"


def postgres_event_update_db_password(
    _: sa.engine.interfaces.Dialect,
    __: Any,
    ___: Tuple[Any, ...],
    cparams: Dict[str, Any],
) -> None:
    """
    update database passord on every new connection attempt
    this will refresh db auth token passwords
    """
    process_logger = ProcessLogger("password_refresh")
    process_logger.log_start()
    cparams["password"] = get_db_password()
    process_logger.log_complete()


def get_local_engine(
    echo: bool = False,
) -> sa.future.engine.Engine:
    """
    Get an SQL Alchemy engine that connects to a locally Postgres RDS stood up
    via docker using env variables
    """
    process_logger = ProcessLogger("create_sql_engine")
    process_logger.log_start()
    try:
        database_url = f"postgresql+psycopg2://{create_db_connection_string()}"

        engine = sa.create_engine(
            database_url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
            pool_use_lifo=True,
            pool_size=3,
            max_overflow=2,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 60,
                "keepalives_interval": 60,
            },
        )

        process_logger.log_complete()
        return engine
    except Exception as exception:
        process_logger.log_failure(exception)
        raise exception


# Setup the base class that all of the SQL objects will inherit from.
#
# Note that the typing hint is required to be set at Any for mypy to be cool
# with it being a base class. This should be fixed with SQLAlchemy2.0
#
# For more context:
# https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html
# https://github.com/python/mypy/issues/2477


class DatabaseManager:
    """
    manager class for rds application operations
    """

    def __init__(self, verbose: bool = False):
        """
        initialize db manager object, creates engine and sessionmaker
        """
        self.engine = get_local_engine(echo=verbose)

        sa.event.listen(
            self.engine,
            "do_connect",
            postgres_event_update_db_password,
        )

        self.session = sessionmaker(bind=self.engine)

    def _get_schema_table(self, table: Any) -> sa.sql.schema.Table:
        if isinstance(table, sa.sql.schema.Table):
            return table
        if isinstance(
            table,
            (
                sa.orm.decl_api.DeclarativeMeta,
                sa.orm.decl_api.DeclarativeAttributeIntercept,
            ),
        ):
            # mypy error: "DeclarativeMeta" has no attribute "__table__"
            return table.__table__  # type: ignore

        raise TypeError(f"can not pull schema table from {type(table)} type")

    def get_session(self) -> sessionmaker:
        """
        get db session for performing actions
        """
        return self.session

    def execute(
        self,
        statement: Union[
            sa.sql.selectable.Select,
            sa.sql.dml.Update,
            sa.sql.dml.Delete,
            sa.sql.dml.Insert,
            sa.sql.elements.TextClause,
        ],
    ) -> sa.engine.CursorResult:
        """
        execute db action WITHOUT data
        """
        with self.session.begin() as cursor:
            result = cursor.execute(statement)
        return result  # type: ignore

    def insert_dataframe(self, dataframe: polars.DataFrame, insert_table: Any) -> None:
        """
        insert data into db table from polars dataframe
        """
        insert_as = self._get_schema_table(insert_table)

        with self.session.begin() as cursor:
            cursor.execute(
                sa.insert(insert_as),
                dataframe.to_dicts(),
            )

    def select_as_list(self, select_query: sa.sql.selectable.Select) -> Union[List[Any], List[Dict[str, Any]]]:
        """
        select data from db table and return list
        """
        with self.session.begin() as cursor:
            return [row._asdict() for row in cursor.execute(select_query)]

    def vaccuum_analyze(self, table: Any) -> None:
        """RUN VACUUM (ANALYZE) on table"""
        table_as = self._get_schema_table(table)

        with self.session.begin() as cursor:
            cursor.execute(sa.text("END TRANSACTION;"))
            cursor.execute(sa.text(f"VACUUM (ANALYZE) {table_as};"))

    def truncate_table(
        self,
        table_to_truncate: Any,
        restart_identity: bool = False,
        cascade: bool = False,
    ) -> None:
        """
        truncate db table

        restart_identity: Automatically restart sequences owned by columns of the truncated table(s).
        cascade: Automatically truncate all tables that have foreign-key references to any of the named tables, or to any tables added to the group due to CASCADE.
        """
        truncat_as = self._get_schema_table(table_to_truncate)

        truncate_query = f"TRUNCATE {truncat_as}"

        if restart_identity:
            truncate_query = f"{truncate_query} RESTART IDENTITY"

        if cascade:
            truncate_query = f"{truncate_query} CASCADE"

        self.execute(sa.text(f"{truncate_query};"))

        # Execute VACUUM to avoid non-deterministic behavior during testing
        self.vaccuum_analyze(table_to_truncate)


def copy_local_to_db(local_path: str, destination_table: DeclarativeBase) -> None:
    """
    Load local file into DB using psql COPY command
    will throw if psql command does not exit with code 0

    :param local_path: path to local file that will be loaded
    :param destination_table: SQLAlchemy table object for COPY destination
    """
    copy_log = ProcessLogger(
        "psql_copy",
        destination_table=str(destination_table.__table__),
    )
    copy_log.log_start()

    with gzip.open(local_path, "rt") as gzip_file:
        local_columns = gzip_file.readline().strip().lower().split(",")

    copy_command = (
        f"\\COPY {destination_table.__table__} "
        f"({','.join(local_columns)}) "
        "FROM PROGRAM "
        f"'gzip -dc {local_path}' "
        "WITH CSV HEADER"
    )

    psql = [
        "psql",
        f"postgresql://{create_db_connection_string()}",
        "-c",
        f"{copy_command}",
    ]

    process_result = subprocess.run(psql, check=True)

    copy_log.add_metadata(exit_code=process_result.returncode)
    copy_log.log_complete()
