# Quick Setup Guide

## Step-by-Step Installation

### 1. Verify Python Installation
```bash
python --version
```
Should show Python 3.8 or higher.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

The application will:
- Automatically create the database
- Create default admin user (username: `admin`, password: `admin123`)
- Create sample rooms
- Start the server on `http://localhost:5000`

### 4. Access the Application
- Open your browser and go to: `http://localhost:5000`
- Login with admin credentials or register as a new student

## Default Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the admin password in production!

## Troubleshooting

### If port 5000 is already in use:
Edit `app.py` line 825 and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### If database errors occur:
Delete the `instance` folder and restart the application to recreate the database.

### If module import errors:
1. Ensure virtual environment is activated
2. Run: `pip install -r requirements.txt`
3. Check Python version: `python --version`

