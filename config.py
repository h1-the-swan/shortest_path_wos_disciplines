import os
from pathlib import Path
# from dotenv import load_dotenv, find_dotenv, DotEnv
from dotenv import load_dotenv, find_dotenv, dotenv_values
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
# dotenv_vals = load_dotenv(dotenv_path)

import logging
logger = logging.getLogger('__main__').getChild(__name__)

REQUIRED_VARS = [
]

OPTIONAL_VARS = [
]

# default logging levels
LOGGING_LEVELS = {
}

class Config(object):

    def __init__(self, 
                spark_mem='80g', 
                logging_levels=LOGGING_LEVELS,
                datadir=None):
        """
        Configuration object for the project.

        spark_mem: amount of memory allocated to spark 
        datadir: base directory for data

        """
        self.PROJECT_DIR = os.environ.get('PROJECT_DIR') or Path(__file__).resolve().parents[1]

        if datadir is None:
            self.datadir = os.environ.get('DATADIR')
        else:
            self.datadir = datadir


        for var in REQUIRED_VARS:
            setattr(self, var, os.environ[var])

        for var in OPTIONAL_VARS:
            setattr(self, var, os.environ.get(var, default=None))

        # self._mysql_db = None
        self._spark = None
        self.spark_mem = spark_mem

        # self._dask_client = None

        self.logging_levels = logging_levels
        self.set_logging_levels()

    def get(self, x, default=None):
        return getattr(self, x, default)

    # @property
    # def mysql_db(self):
    #     """database object used for connecting to MySQL"""
    #     # if not hasattr(self, '_mysql') or self._mysql_db is None:
    #     if self.get('_mysql_db') is None:
    #         db_name = self.MYSQL_DEFAULT_DB or None
    #         self._mysql_db = self._get_mysql_connection(db_name=db_name)
    #     return self._mysql_db

    # @mysql_db.deleter
    # def mysql_db(self):
    #     del self._mysql_db

    @property
    def spark(self):
        if self.get('_spark') is None:
            self._spark = self.load_spark_session(mem=self.spark_mem)
        return self._spark

    @spark.deleter
    def spark(self):
        if self.get('_spark') is not None:
            self._spark.stop()
        del self._spark

    def restart_spark(self):
        del self.spark
        return self.spark

    def load_spark_session(self, appName="sparkApp", mem='80g', showConsoleProgress=False, additional_conf=[], logLevel=None):
        # import findspark
        # findspark.init()

        import pyspark
        conf = pyspark.SparkConf().setAll([
            ('spark.executor.memory', mem), 
            ('spark.driver.memory', mem),
            ('spark.ui.showConsoleProgress', showConsoleProgress),
            ('spark.driver.maxResultSize', '0'),
            ('spark.reducer.maxSizeInFlight', '5g'),
            ("spark.sql.execution.arrow.enabled", "true"),
            ("spark.driver.extraJavaOptions", "-Duser.timezone=UTC"),  # https://stackoverflow.com/a/48767250
            ("spark.executor.extraJavaOptions", "-Duser.timezone=UTC"),
            ('spark.jars.packages', 'graphframes:graphframes:0.7.0-spark2.4-s_2.11'),
        ])
        for k,v in additional_conf:
            conf.set(k, v)

        sc = pyspark.SparkContext(appName=appName, conf=conf)
        if logLevel:
            sc.setLogLevel(logLevel)
        spark = pyspark.sql.SparkSession(sc)
        return spark

    def set_logging_levels(self, logging_levels=None):
        # if `logging_levels` is specified, it will change self.logging_levels
        if logging_levels is None:
            logging_levels = self.logging_levels
        else:
            self.logging_levels = logging_levels
        for k, v in logging_levels.items():
            lgr = logging.getLogger(k)
            lgr.setLevel(v)

    def update_logging_levels(self, **kwargs):
        """
        example usage: `config.update_logging_levels(snowflake='WARN')
        example usage: `config.update_logging_levels(botocore=logging.INFO)
        """
        self.logging_levels.update(kwargs)
        self.set_logging_levels()

    def teardown(self):
        del self.spark
        # del self.mysql_db
        # del self.dask_client
        
