# 🏠 Hostel Management System

A complete, production-ready Hostel Management System built with Python Flask, SQL, HTML, and CSS. This system provides comprehensive management features for hostels including student registration, room allocation, complaint management, fee tracking, and more.

## ✨ Features

### Core Functionalities
- ✅ **Student Registration & Secure Login** - User authentication with password hashing
- ✅ **Role-Based Access Control** - Separate dashboards for Admin and Students
- ✅ **Room Allocation** - Real-time room availability tracking with automatic capacity validation
- ✅ **Complaint Management** - Submit, track, and manage complaints with status updates
- ✅ **Fee Management** - Track payments with status (Paid/Due/Overdue)
- ✅ **Room Change Requests** - Students can request room changes with admin approval workflow

### Advanced Features
- 🔍 **Search & Filter** - Search students by name, room number, or status
- 📧 **Email Notification Simulation** - Logs email notifications for complaint updates
- 📊 **Admin Dashboard** - Comprehensive statistics and recent activities
- 🔐 **Secure Authentication** - Password hashing using Werkzeug
- 📝 **Audit Logs** - Track all admin actions with timestamps and IP addresses
- 🎨 **Responsive UI** - Clean, modern design that works on desktop and mobile
- ✅ **Data Validation** - Comprehensive form validation and error handling
- 🔄 **Session Management** - Secure session handling with Flask-Login

## 🛠️ Technology Stack

- **Backend:** Python 3.8+, Flask
- **Database:** SQLite (can be easily switched to MySQL/PostgreSQL)
- **Frontend:** HTML5, CSS3 (Responsive Design)
- **Authentication:** Flask-Login, Werkzeug Security
- **ORM:** SQLAlchemy

## 📋 Prerequisites

- Python 3.8 or higher (Python 3.12+ recommended for best compatibility)
- pip (Python package installer)

## 🚀 Installation & Setup

### 1. Clone or Download the Project

Navigate to the project directory:
```bash
cd "hostel management"
```

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

The database will be created automatically when you run the application for the first time. However, you can manually initialize it by running:

```bash
python app.py
```

This will:
- Create the database tables
- Create a default admin user (username: `admin`, password: `admin123`)
- Create sample rooms for testing

**⚠️ Important:** Change the admin password in production!

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 👤 Default Login Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Change these credentials in production environments!**

### Student Account
Students can register their own accounts through the registration page.

## 📁 Project Structure

```
hostel-management/
│
├── app.py                 # Main Flask application
├── models.py              # Database models (SQLAlchemy)
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   ├── complaints.html
│   ├── fees.html
│   ├── room_change.html
│   ├── admin_students.html
│   ├── admin_rooms.html
│   ├── room_allocation.html
│   ├── admin_room_change.html
│   └── admin_audit_logs.html
│
├── static/
│   └── css/
│       └── style.css     # Main stylesheet
│
└── instance/
    └── hostel.db        # SQLite database (created automatically)
```

## 🎯 Usage Guide

### For Students

1. **Registration**
   - Visit the registration page
   - Fill in your details (username, email, full name, password)
   - Log in with your credentials

2. **Dashboard**
   - View your room allocation
   - Check fee status
   - View recent complaints

3. **Submit Complaints**
   - Go to Complaints section
   - Fill in the complaint form (subject, category, priority, description)
   - Track complaint status (Pending → In Progress → Resolved)

4. **Request Room Change**
   - Navigate to Room Change section
   - Select desired room (if available)
   - Provide reason for change
   - Track request status

5. **View Fees**
   - Check fee records and payment status
   - View due dates and amounts

### For Administrators

1. **Dashboard**
   - View statistics (total students, rooms, pending complaints, etc.)
   - Monitor recent activities
   - Quick access to all management features

2. **Manage Students**
   - View all registered students
   - Search and filter students
   - See allocation status

3. **Manage Rooms**
   - View all rooms with occupancy status
   - Add new rooms
   - See room details and occupants
   - Search and filter rooms

4. **Allocate Rooms**
   - Select unallocated student
   - Choose available room
   - System validates capacity automatically

5. **Manage Complaints**
   - View all student complaints
   - Filter by status and category
   - Update complaint status
   - Add admin responses
   - Email notifications are logged (simulated)

6. **Fee Management**
   - Create fee records for students
   - Update payment status
   - Record payment method and transaction ID
   - Search and filter fees

7. **Room Change Requests**
   - View pending room change requests
   - Approve or reject requests
   - System automatically updates room allocations
   - Add admin responses

8. **Audit Logs**
   - View all admin actions
   - Track changes with timestamps
   - Monitor system activity

## 🔒 Security Features

- Password hashing using Werkzeug (bcrypt-like hashing)
- Session management with Flask-Login
- Role-based access control
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- CSRF protection (can be added with Flask-WTF)

## 🎨 UI/UX Features

- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Modern Interface** - Clean, professional design
- **Intuitive Navigation** - Easy-to-use navigation menu
- **Visual Feedback** - Color-coded status badges and alerts
- **Form Validation** - Client-side and server-side validation
- **User-Friendly Messages** - Clear success/error messages

## 📊 Database Schema

The system uses the following main tables:

- **users** - Students and admin users
- **rooms** - Room information and availability
- **room_allocations** - Student-room assignments
- **complaints** - Student complaints with status tracking
- **fees** - Fee records and payment status
- **room_change_requests** - Room change requests with approval workflow
- **audit_logs** - Admin action history

## 🔧 Configuration

You can modify settings in `config.py`:

- **Database:** Change `SQLALCHEMY_DATABASE_URI` to use MySQL or PostgreSQL
- **Secret Key:** Set environment variable `SECRET_KEY` for production
- **Session Lifetime:** Adjust `PERMANENT_SESSION_LIFETIME`

### Using MySQL

Update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/hostel_db'
```

Install MySQL driver:
```bash
pip install pymysql
```

## 🐛 Troubleshooting

### Database Issues
- Delete `instance/hostel.db` and restart the application to reset the database
- Ensure you have write permissions in the `instance` directory

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

### Module Not Found Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Python 3.13 Compatibility Issues
If you encounter SQLAlchemy compatibility errors with Python 3.13, the requirements.txt has been updated to use SQLAlchemy 2.0.35+ which supports Python 3.13. Ensure you:
1. Have the latest version: `pip install --upgrade SQLAlchemy`
2. Or use Python 3.12 for maximum compatibility

## 🚀 Deployment

For production deployment:

1. Set environment variables:
   ```bash
   export SECRET_KEY='your-secret-key-here'
   export DATABASE_URL='your-database-url'
   ```

2. Disable debug mode in `app.py`:
   ```python
   app.run(debug=False)
   ```

3. Use a production WSGI server (Gunicorn, uWSGI):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. Use a reverse proxy (Nginx) for better performance

## 📝 Future Enhancements

Potential features to add:
- Email notification system (SMTP integration)
- File upload for complaints
- Reports and analytics dashboard
- Messaging system between students and admin
- Maintenance request system
- Visitor management
- Inventory management
- Attendance tracking

## 👨‍💻 Development

This project follows these best practices:
- Modular code structure
- Comprehensive error handling
- Well-commented code
- Industry-standard patterns
- Security best practices
- Responsive design principles

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ for efficient hostel management**

