from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os

app = Flask(__name__)
CORS(app)

# Data store
rooms = {}

@app.route('/create_room', methods=['POST'])
def create_room():
    room_id = str(uuid.uuid4())
    rooms[room_id] = {"queue": [], "current_student": None, "notifications": 0}
    print({"message": "Room created", "room_id": room_id})
    return jsonify({"message": "Room created", "room_id": room_id})

@app.route('/join_room/<room_id>', methods=['POST'])
def join_room(room_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404

    data = request.get_json()
    student_id = data.get("student_id")
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400

    # Check if the student is already in the queue of the current room
    if student_id in rooms[room_id]['queue']:
        return jsonify({"message": "Student already in the queue", "student_id": student_id})

    # Add student to the queue
    rooms[room_id]['queue'].append(student_id)
    return jsonify({"message": "Joined room", "student_id": student_id})

@app.route('/notify_next/<room_id>', methods=['POST'])
def notify_next(room_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404

    room = rooms[room_id]
    if not room['queue']:
        return jsonify({"message": "No students in the queue"})

    # Move the first student from the queue to current_student
    room['current_student'] = room['queue'].pop(0)
    return jsonify({"message": "Current student updated", "current_student": room['current_student']})

@app.route('/accept_notification/<room_id>/<student_id>', methods=['POST'])
def accept_notification(room_id, student_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404

    room = rooms[room_id]
    if room['current_student'] == student_id:
        room['notifications'] = 0
        return jsonify({"message": "Notification accepted", "current_student": room['current_student']})
    else:
        return jsonify({"error": "Student is not the current student"}), 400

@app.route('/remove_current/<room_id>', methods=['POST'])
def remove_current(room_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404

    room = rooms[room_id]
    if room['current_student']:
        print(f"Removing current student: {room['current_student']} from room {room_id}")
    else:
        print(f"No current student to remove in room {room_id}")

    room['current_student'] = None
    return jsonify({"message": "Current student removed"})


@app.route('/remove_all/<room_id>', methods=['POST'])
def remove_all(room_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404

    rooms[room_id]['queue'] = []
    rooms[room_id]['current_student'] = None
    rooms[room_id]['notifications'] = 0
    return jsonify({"message": "All students removed"})

@app.route('/get_room_status/<room_id>', methods=['GET'])
def get_room_status(room_id):
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404
    
    room = rooms[room_id]
    return jsonify({
        "queue": room['queue'],
        "current_student": room['current_student'],
        "notifications": room['notifications']
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
