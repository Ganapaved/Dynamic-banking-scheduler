from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import heapq

app = Flask(__name__)

# Global variables
customer_queue = []  # For Round Robin Scheduler
priority_queue = []  # For Priority Queue
time_quantum = 5     # Time quantum for Round Robin in seconds

# Counter to ensure unique priorities
unique_priority_counter = 0

def calculate_priority(action, age, amount):
    global unique_priority_counter

    # Base priority for action
    if action == "deposit":
        priority = 1
    elif action == "withdrawal":
        priority = 2
    else:  # loan application
        priority = 3

    # Adjust priority for senior citizens
    if age >= 60:
        priority -= 1  # Higher priority for senior citizens

    # Ensure uniqueness with a counter
    priority = max(priority, 1)  # Priority should be at least 1
    unique_priority_counter += 1
    final_priority = priority + unique_priority_counter

    return final_priority

# Route to add customers (Priority Queue)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        age = int(request.form['age'])
        amount = float(request.form['amount'])

        # Calculate priority
        index = len(priority_queue)  # Use current queue size as unique index
        priority = calculate_priority(action, age, amount)


        # Add customer to both queues
        customer = {
            "action": action,
            "age": age,
            "amount": amount,
            "priority": priority
        }
        heapq.heappush(priority_queue, (priority,len(priority_queue), customer))
        customer_queue.append(customer)

        return redirect(url_for('queue'))
    return render_template('bankindex.html')

# Route to display priority queue
@app.route('/queue')
def queue():
    sorted_queue = sorted(priority_queue, key=lambda x: x[0])
    return render_template('queue.html', queue=sorted_queue)

# Round Robin scheduler simulation
@app.route('/round_robin', methods=['GET'])
def round_robin():
    if not customer_queue:
        return "No customers in queue!"

    sorted_queue = sorted(customer_queue, key=lambda x: x['priority'], reverse=True)
    results = []
    start_time = time.time()

    for customer in sorted_queue:
        operation_time = min(time_quantum, 3)  # Simulated time for operation
        time.sleep(operation_time)  # Simulate processing time
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        results.append({
            "action": customer['action'],
            "amount": customer['amount'],
            "priority": customer['priority'],
            "elapsed_time": elapsed_time
        })
        start_time = end_time

    return jsonify(results)

# Route for the execution page (Round Robin)
@app.route('/execute', methods=['GET'])
def execute():
    if not customer_queue:
        return render_template('execute.html', results=[], message="No customers in queue!")

    # Simulate Round Robin execution
    sorted_queue = sorted(priority_queue, key=lambda x: x[0])
    results = []
    current_time = time.time()

    for _,_, customer in sorted_queue:
        start_time =current_time  # Simulated time for operation
        duration=customer["amount"]/10  # Simulate processing time
        end_time = start_time+duration

        results.append({
            "action": customer["action"],
            "priority": customer["priority"],
            "age": customer["age"],
            "amount": customer["amount"],
            "start_time": time.strftime("%H:%M:%S", time.localtime(start_time)),
            "end_time": time.strftime("%H:%M:%S", time.localtime(end_time)),
            "duration": round(duration, 2),
        })
        current_time = end_time

    return render_template('execute.html', results=results, message=None)


if __name__ == '__main__':
    app.run(debug=True)
