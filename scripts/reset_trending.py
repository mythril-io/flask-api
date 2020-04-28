import sqlalchemy
import os

"""
Reset trending_page_views column for each game
"""

# Connect to Database
engine = sqlalchemy.create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

# Prepare SQL query
sql = 'UPDATE games SET trending_page_views = 0'

# Execute query
with engine.connect() as con:
    rs = con.execute(sql)