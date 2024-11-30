from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

#data
users = {
    "boss": {"password": "123", "role": "boss"},
    "employee1": {"password": "123", "role": "employee"},
    "employee2": {"password": "123", "role": "employee"},
}
tasks = {}

#authentication
def authenticate(username: str, password: str):
    user = users.get(username)
    if user and user["password"] == password:
        return user
    return None

#login page
@app.get("/", response_class=HTMLResponse)
def login_page():
    return """
    <html>
        <body>
            <h1>Login</h1>
            <form method="post" action="/login">
                <label>Username:</label>
                <input type="text" name="username" required><br>
                <label>Password:</label>
                <input type="password" name="password" required><br>
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """

#handle login
@app.post("/login", response_class=HTMLResponse)
def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate(username, password)
    if not user:
        return """
        <html>
            <body>
                <h1>Login</h1>
                <p style="color:red;">Invalid credentials!</p>
                <form method="post" action="/login">
                    <label>Username:</label>
                    <input type="text" name="username" required><br>
                    <label>Password:</label>
                    <input type="password" name="password" required><br>
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """
    if user["role"] == "boss":
        return RedirectResponse(url=f"/boss?username={username}", status_code=302)
    return RedirectResponse(url=f"/employee?username={username}", status_code=302)

#boss dashboard
@app.get("/boss", response_class=HTMLResponse)
def boss_dashboard(username: str):
    task_list = ""
    for employee, employee_tasks in tasks.items():
        task_list += f"<h3>Tasks for {employee}</h3><ul>"
        for task in employee_tasks:
            task_list += f"<li>{task['id']}: {task['description']} - {task['progress']}</li>"
        task_list += "</ul>"

    return f"""
    <html>
        <body>
            <h1>Welcome, {username}!</h1>
            <h2>Assign Task</h2>
            <form method="post" action="/assign-task">
                <label>Employee Username:</label>
                <input type="text" name="username" required><br>
                <label>Task Description:</label>
                <input type="text" name="task_desc" required><br>
                <button type="submit">Assign Task</button>
            </form>
            <h2>All Tasks</h2>
            {task_list}
        </body>
    </html>
    """

#assign task
@app.post("/assign-task", response_class=HTMLResponse)
def assign_task(username: str = Form(...), task_desc: str = Form(...)):
    username= username.lower()
    if username not in users or users[username]["role"] != "employee":
        return RedirectResponse(url="/boss?username=boss", status_code=302)

    task_id = len(tasks.get(username, [])) + 1
    tasks.setdefault(username, []).append({"id": task_id, "description": task_desc, "progress": "Not Started"})
    return RedirectResponse(url="/boss?username=boss", status_code=302)

#employee dashboard
@app.get("/employee", response_class=HTMLResponse)
def employee_dashboard(username: str):
    user_tasks = tasks.get(username, [])
    task_list = "<ul>"
    for task in user_tasks:
        task_list += f"<li>{task['id']}: {task['description']} - {task['progress']}</li>"
    task_list += "</ul>"

    return f"""
    <html>
        <body>
            <h1>Welcome, {username}!</h1>
            <h2>Your Tasks</h2>
            {task_list}
            <h3>Update Task Progress</h3>
            <form method="post" action="/update-task">
                <label>Task ID:</label>
                <input type="number" name="task_id" required><br>
                <label>Progress:</label>
                <select name="progress" required>
                    <option value="Not Started">Not Started</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                </select><br>
                <input type="hidden" name="username" value="{username}">
                <button type="submit">Update Task</button>
            </form>
        </body>
    </html>
    """

#update task progress
@app.post("/update-task", response_class=HTMLResponse)
def update_task(username: str = Form(...), task_id: int = Form(...), progress: str = Form(...)):
    user_tasks = tasks.get(username, [])
    for task in user_tasks:
        if task["id"] == task_id:
            task["progress"] = progress
            break
    return RedirectResponse(url=f"/employee?username={username}", status_code=302)
