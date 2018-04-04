from flask import Flask, jsonify, request, abort
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'flask'
app.config['MYSQL_DATABASE_PASSWORD'] = 'flask'
app.config['MYSQL_DATABASE_DB'] = 'flask'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

@app.route('/')
def default():
    return str("User /server/ to gat all server or /server/<id> to get server with id")


@app.route('/server/', methods=['GET'])
def all_servers():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from server")
    rows = cursor.fetchall()

    tasks = []

    for data in rows:
        tasks.append(create_server(data))

    cursor.close()
    conn.close()

    return jsonify(tasks)


@app.route('/server/<string:id>', methods=['GET'])
def server(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT ServerID, Servernaam, CPUcount, MemoryCount, DataDiskCount, OSDiskCount, OS, CreationDate from server where server.ServerID = %s", id)
    data = cursor.fetchone()

    if data is None:
        return jsonify({"Error": "Server not found"})

    task = create_server(data)

    cursor.close()
    conn.close()
    return jsonify(task)


@app.route('/server/', methods=['POST'])
def create_server():
    if not request.json:
        abort(400)

    task = decode_json(request.json)

    # print(task)
    conn = mysql.connect()
    curr = conn.cursor()

    try:
        curr.execute(
            "INSERT INTO server (Servernaam, CPUcount, MemoryCount, DataDiskCount, OSDiskCount, OS, CreationDate) VALUES (%s, %s, %s, %s, %s, %s, curdate())",
            (task['Servernaam'], int(task['CPUcount']), int(task['MemoryCount']), int(task['DataDiskCount']),
             int(task['OSDiskCount']), task['OS']))
        curr.close()
        conn.commit()
    except MySQL.Error as e:
        try:
            print
            "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print
            "MySQL Error: %s" % str(e)
    finally:
        conn.close()

    return jsonify({'task': task}), 201

@app.route('/server/<string:id>', methods=['POST'])
def update_server(id):

    if not request.json:
        abort(400)

    conn = mysql.connect()
    curr = conn.cursor()

    task = decode_json(request.json)

    try:
        curr.execute("UPDATE server SET Servernaam = %s, CPUcount = %s, MemoryCount = %s, DataDiskCount= %s, OSDiskCount = %s, OS = %s WHERE ServerID = %s", (task['Servernaam'], int(task['CPUcount']), int(task['MemoryCount']), int(task['DataDiskCount']), int(task['OSDiskCount']), task['OS'], id))
        curr.close()
        conn.commit()
    finally:
        conn.close()

    return jsonify({'task': task}), 202

def create_server(row):
    server = {
        'ServerID': row[0],
        'Servernaam': row[1],
        'CPUcount': row[2],
        'MemoryCount': row[3],
        'DataDiskCount': row[4],
        'OSDiskCount': row[5],
        'OS': row[6],
        'CreationDate': str(row[7])
    }
    return server

def decode_json(json_file):
    server = {
        'ServerID': json_file['ServerID'],
        'Servernaam': json_file['Servernaam'],
        'CPUcount': json_file['CPUcount'],
        'MemoryCount': json_file['MemoryCount'],
        'DataDiskCount': json_file['DataDiskCount'],
        'OSDiskCount': json_file['OSDiskCount'],
        'OS': json_file['OS'],
        'CreationDate': json_file['CreationDate']
    }
    return server

if __name__ == '__main__':
    app.run(debug=1)
