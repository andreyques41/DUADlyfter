import psycopg2


class PgManager:
    def __init__(self, db_name, user, password, host, port=5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.connection = self.create_connection(db_name, user, password, host, port)
        if self.connection:
            self.cursor = self.connection.cursor()
        print("[INFO] Database cursor created successfully")

    def create_connection(self, db_name, user, password, host, port):
        try:
            connection = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port,
            )

            # Set the search path after connecting
            cursor = connection.cursor()
            cursor.execute("SET search_path TO lyfter_car_rental, public;")
            connection.commit()
            cursor.close()

            print("[INFO] Database connection established")

            return connection
        except Exception as error:
            print("[ERROR] Error connecting to the database:", error)
            return None

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("[INFO] Database connection closed")

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.connection.commit()
            print(f"[INFO] {self.cursor.statusmessage}")

            if self.cursor.description:
                result = self.cursor.fetchall()
                return result
        except Exception as error:
            print("[Error] Error executing query:", error)
            self.connection.rollback()
            return None
