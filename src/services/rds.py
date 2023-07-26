import argparse
import pymysql


class RDS:
    def __init__(
            self,
            host: str = 'database-superofertas-master.cooi236cxxsr.sa-east-1.rds.amazonaws.com',
            port: int = 3306,
            db: str = 'database-superofertas-master',
            user: str = 'admin',
            password: str = '****'  # Fill Manually in production
    ):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.conn = None

    def _connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db
        )

    def execute_query(self, query):
        if self.conn is None:
            self._connect()

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)

                # if the query is a select statement
                if query.lstrip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    return result
                # if the query is insert, update or delete statement
                self.conn.commit()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--query', type=str, help='SQL Query to execute')
    args = parser.parse_args()

    rds = RDS()
    print('Executing this query:')
    print(args.query)
    query_result = rds.execute_query(f'{args.query};')
    if query_result is not None:
        print('Query result:')
        print(query_result)

    rds.disconnect()
