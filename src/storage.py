# ----- STORAGE BACKENDS -----

import json


class SQLiteStorage:
    """
    SQLite storage backend for persisting scraped data
    """

    def __init__(self, db_path="bumi_data.db"):
        """
        Args:
            db_path: path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """establishes database connection"""
        import sqlite3

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        return self

    def _create_tables(self):
        """creates required database tables"""
        cursor = self.conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT,
                bio TEXT,
                profile_image TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT,
                year TEXT,
                director TEXT,
                runtime TEXT,
                genres TEXT,
                average_rating TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                film_slug TEXT,
                rating TEXT,
                watched_date TEXT,
                rewatch INTEGER DEFAULT 0,
                liked INTEGER DEFAULT 0,
                review TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                film_slug TEXT,
                film_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                data_type TEXT,
                data TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_films_slug ON films(slug);
            CREATE INDEX IF NOT EXISTS idx_user_films_user ON user_films(user_id);
        """
        )
        self.conn.commit()

    def save_user(self, user_data):
        """saves user profile data"""
        cursor = self.conn.cursor()
        profile = user_data.get("scraped_data", {}).get("profile", {})
        cursor.execute(
            """
            INSERT OR REPLACE INTO users (username, display_name, bio, profile_image)
            VALUES (?, ?, ?, ?)
        """,
            (
                profile.get("user_data_person"),
                profile.get("user_name"),
                profile.get("user_bio"),
                profile.get("user_profile_image"),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def save_film(self, film_data):
        """saves film details"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO films (slug, title, year, director, runtime, genres, average_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                film_data.get("film_slug"),
                film_data.get("title"),
                film_data.get("year"),
                film_data.get("director"),
                film_data.get("runtime"),
                json.dumps(film_data.get("genres", [])),
                film_data.get("average_rating"),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def save_scrape_result(self, url, data_type, data):
        """saves raw scrape result for history"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO scrape_history (url, data_type, data)
            VALUES (?, ?, ?)
        """,
            (url, data_type, json.dumps(data)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user(self, username):
        """retrieves user by username"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_film(self, slug):
        """retrieves film by slug"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM films WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["genres"] = json.loads(result.get("genres", "[]"))
            return result
        return None

    def query(self, sql, params=()):
        """executes custom SQL query"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """closes database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class PostgreSQLStorage:
    """
    PostgreSQL storage adapter for production-grade data persistence
    Requires psycopg2: pip install psycopg2-binary
    """

    def __init__(
        self, host="localhost", port=5432, database="bumi", user="postgres", password=""
    ):
        """
        Args:
            host: database host
            port: database port
            database: database name
            user: database user
            password: database password
        """
        self.config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.conn = None

    def connect(self):
        """establishes database connection"""
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 required: pip install psycopg2-binary")

        self.conn = psycopg2.connect(**self.config)
        self._create_tables()
        return self

    def _create_tables(self):
        """creates required database tables"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                display_name VARCHAR(255),
                bio TEXT,
                profile_image TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS films (
                id SERIAL PRIMARY KEY,
                slug VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500),
                year VARCHAR(10),
                director VARCHAR(255),
                runtime VARCHAR(50),
                genres JSONB DEFAULT '[]',
                average_rating VARCHAR(20),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_films (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                film_slug VARCHAR(255),
                rating VARCHAR(20),
                watched_date VARCHAR(50),
                rewatch BOOLEAN DEFAULT FALSE,
                liked BOOLEAN DEFAULT FALSE,
                review TEXT
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                film_slug VARCHAR(255),
                film_name VARCHAR(500),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scrape_history (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                data_type VARCHAR(100),
                data JSONB,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_pg_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_pg_films_slug ON films(slug);
            CREATE INDEX IF NOT EXISTS idx_pg_user_films_user ON user_films(user_id);
        """
        )
        self.conn.commit()

    def save_user(self, user_data):
        """saves user profile data"""
        cursor = self.conn.cursor()
        profile = user_data.get("scraped_data", {}).get("profile", {})
        cursor.execute(
            """
            INSERT INTO users (username, display_name, bio, profile_image)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                bio = EXCLUDED.bio,
                profile_image = EXCLUDED.profile_image,
                scraped_at = CURRENT_TIMESTAMP
            RETURNING id
        """,
            (
                profile.get("user_data_person"),
                profile.get("user_name"),
                profile.get("user_bio"),
                profile.get("user_profile_image"),
            ),
        )
        self.conn.commit()
        return cursor.fetchone()[0]

    def save_film(self, film_data):
        """saves film details"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO films (slug, title, year, director, runtime, genres, average_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
                title = EXCLUDED.title,
                year = EXCLUDED.year,
                director = EXCLUDED.director,
                runtime = EXCLUDED.runtime,
                genres = EXCLUDED.genres,
                average_rating = EXCLUDED.average_rating,
                scraped_at = CURRENT_TIMESTAMP
            RETURNING id
        """,
            (
                film_data.get("film_slug"),
                film_data.get("title"),
                film_data.get("year"),
                film_data.get("director"),
                film_data.get("runtime"),
                json.dumps(film_data.get("genres", [])),
                film_data.get("average_rating"),
            ),
        )
        self.conn.commit()
        return cursor.fetchone()[0]

    def save_scrape_result(self, url, data_type, data):
        """saves raw scrape result for history"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO scrape_history (url, data_type, data)
            VALUES (%s, %s, %s)
            RETURNING id
        """,
            (url, data_type, json.dumps(data)),
        )
        self.conn.commit()
        return cursor.fetchone()[0]

    def get_user(self, username):
        """retrieves user by username"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def get_film(self, slug):
        """retrieves film by slug"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM films WHERE slug = %s", (slug,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def query(self, sql, params=()):
        """executes custom SQL query"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self):
        """closes database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
