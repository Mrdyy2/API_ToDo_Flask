from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.done
        }

# Créer la base de données et les tables
with app.app_context():
    db.create_all()



# Route pour obtenir toutes les tâches
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify({'tasks': [task.to_json() for task in tasks]})

# Route pour créer une nouvelle tâche
@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.form['title']
    description = request.form['description']
    data = {'title':title,
            'description':description
            }
    response = requests.post("http://127.0.0.1:5000/tasks", json=data)
    new_task = Task(title=data['title'], description=data.get('description', ''), done=data.get('done', False))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_json()), 201

# Route pour obtenir une seule tâche par son ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify(task.to_json())
    else:
        return jsonify({'error': 'Tâche introuvable'}), 404

# Route pour mettre à jour une tâche par son ID
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task:
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = data.get('done', task.done)
        db.session.commit()
        return jsonify(task.to_json())
    else:
        return jsonify({'error': 'Tâche introuvable'}), 404

# Route pour supprimer une tâche par son ID
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'result': 'Tâche supprimée'})
    else:
        return jsonify({'error': 'Tâche introuvable'}), 404
    


@app.route('/form', methods=['GET', 'POST'])
def show_form():
    return render_template('index.html')


# Exécute l'application Flask
if __name__ == '__main__':
    app.run(debug=True)

# Affiche un message de succès
print("Fin d'exécution API Flask avec base de données SQLite pour la gestion des tâches .")
