from flask import Blueprint, request, jsonify
from psycopg2 import errors
from ..services.conn import finalizar_conn_cur, conn_cur
from datetime import datetime

bp = Blueprint('example_blueprint', __name__)

# @bp.route('/animes', methods=["GET"])
# def get_create():
#     return "This is an example app"

@bp.route('/animes', methods=["POST", "GET"])
def get_create():

    conn, cur = conn_cur()

    if request.method == 'POST':

        data = request.json

    
    
        data['anime'] = data['anime'].title()
        try:
            cur.execute(
                """
                    CREATE TABLE IF NOT EXISTS anime
                        (
                            id BIGSERIAL PRIMARY KEY,
                            anime VARCHAR(100) NOT NULL UNIQUE,
                            released_date DATE NOT NULL,
                            seasons INTEGER NOT NULL
                        );
                    
                    INSERT INTO anime
                        (anime, released_date, seasons)
                    VALUES
                        (%(anime)s, %(released_date)s, %(seasons)s)
                    RETURNING *;
                    
                """,
                data,
            )
        except errors.UniqueViolation:
            return {"error": "anime is already exists"}, 422
        except KeyError as e:
            return {"available_keys": ["anime", "released_date", "seasons"], "wrong_keys_sended": [e.args[0]]}, 422

        query = cur.fetchone()

        table = ["id", "anime", "released_date", "seasons"]
        response = dict(zip(table, query))
        
        response['released_date'] = response['released_date'].strftime("%d/%m/%y")
        finalizar_conn_cur(conn, cur)
  
        return jsonify(response), 201

    else:

        cur.execute("SELECT * FROM anime")
        query = cur.fetchall()
        table = ["id", "anime", "released_date", "seasons"]
        
        # response = {"data": [dict(zip(table, data)) for data in query]}
        

        response = [dict(zip(table, data)) for data in query]
        


        finalizar_conn_cur(conn, cur)


        return jsonify(response)

@bp.route('/animes/<int:anime_id>', methods=["GET"])
def filter(anime_id: str) -> dict:
    data = dict(zip(["id"], [anime_id]))
    conn, cur = conn_cur()
    
    cur.execute("""SELECT * FROM anime WHERE id = %(id)s""", data)
    query = cur.fetchall()
    finalizar_conn_cur(conn, cur)
    if not query or not anime_id:
        return {"error": "Not found"}
    table = ["id", "anime", "released_date", "seasons"]
    response = [dict(zip(table, data)) for data in query]
    response[0]['released_date'] = response[0]['released_date'].strftime("%d/%m/%y")
    response = {"data": response}
    return jsonify(response)


@bp.route('/animes/<int:anime_id>', methods=["DELETE"])
def delete(anime_id: int) -> dict:
    data = dict(zip(["id"], [anime_id]))
    conn, cur = conn_cur()
    try:
        cur.execute("""SELECT * FROM anime WHERE id = %(id)s""", data)
        query = cur.fetchall()
        if not query:
            return {"error": "Not found"},404

        cur.execute("""DELETE FROM anime WHERE id = %(id)s;""", data)
        finalizar_conn_cur(conn, cur)
        return ('',204)
    except:
        return errors

@bp.route('/animes/<int:anime_id>', methods=["PATCH"])
def update(anime_id: int) -> dict:
    data = request.json
    data['id'] = anime_id
    conn, cur = conn_cur()
    
    cur.execute("""SELECT * FROM anime WHERE id = %(id)s""", data)
    query = cur.fetchall()

    if data.get('seasons'):
        data['seasons'] = data.get('seasons')
    if data.get('anime'):
        data['anime'] = data.get('anime')


    print(data)

    if not query:
        return {"error": "Not found"},404

    try:
        cur.execute(
            """
                UPDATE anime SET anime=%(anime)s, seasons=%(seasons)s, released_date=%(released_date)s WHERE id = %(id)s
                RETURNING *;
            """,
            data
        )
        query = cur.fetchall()        
        finalizar_conn_cur(conn, cur)


        table = ["id", "anime", "released_date", "seasons"]
        response = dict(zip(table, data))
        return jsonify(response)

    except KeyError as e:
        print(KeyError)
        return {"available_keys": ["anime", "released_date", "seasons"], "wrong_keys_sended": [e.args[0]]}, 422    





        
