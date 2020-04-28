import sqlalchemy
import os

"""
Update rankings for each game
"""

# Connect to Database
engine = sqlalchemy.create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

# Prepare SQL queries
sql_avg_score = """
UPDATE games g
SET    g.score = (SELECT Round(( Avg(score) / 10 ) * 100, 2)
                  FROM   libraries l
                  WHERE  l.game_id = g.id
                         AND l.score IS NOT NULL)  
"""

sql_library_count = """
UPDATE games g
SET    g.library_count = (SELECT Count(id)
                          FROM   libraries l
                          WHERE  l.game_id = g.id)  
"""

sql_score_rank = """
UPDATE games g
SET    g.score_rank = (SELECT rank
                       FROM   (SELECT id,
                                      Row_number() OVER (ORDER BY score DESC, library_count DESC) AS rank
                               FROM   games) r
                       WHERE  r.id = g.id)  
"""

sql_popularity_rank = """
UPDATE games g
SET    g.popularity_rank = (SELECT rank
                            FROM   (SELECT id,
                                           Row_number() OVER (ORDER BY library_count DESC, trending_page_views DESC) AS rank
                                    FROM   games) r
                            WHERE  r.id = g.id)  
"""

# Execute queries
with engine.connect() as con:
    con.execute(sql_avg_score)
    con.execute(sql_library_count)
    con.execute(sql_score_rank)
    con.execute(sql_popularity_rank)