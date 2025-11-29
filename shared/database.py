import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class Database:
    """
    Helper class to manage database connections with basic pooling.
    """
    def __init__(self):
        self.engine = None
        self.conn = None
        self.session = None

    def conectar(
        self,
        db_name,
        user,
        password,
        host,
        port,
        pool_size: int = 5,
        max_overflow: int = 5,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
    ):
        """
        Estabelece conexao com o banco de dados usando SQLAlchemy engine pooling.
        """
        try:
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
            self.engine = create_engine(
                connection_string,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,
                future=True,
            )
            self.conn = self.engine.connect()

            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            logger.info("Database: conexao estabelecida com sucesso")
            return True, "Conectado com sucesso!"
        except Exception as e:
            logger.exception("Database: erro ao conectar")
            return False, str(e)

    def desconectar(self):
        """Fecha a conexao e a sessao com o banco de dados."""
        if self.session:
            self.session.close()
        if self.conn:
            self.conn.close()
        self.engine = None
        logger.info("Database: conexao fechada")
