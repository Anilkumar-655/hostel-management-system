"""
Hostel Management System - Main Application
A complete production-ready system for managing hostel operations
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
import os

from config import Config
from models import db, User, Room, RoomAllocation, Complaint, Fee, RoomChangeRequest, AuditLog

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def log_audit(action, target_type=None, target_id=None, details=None):
    """Log admin action to audit log"""
    if current_user.is_authenticated and current_user.is_admin():
        log = AuditLog(
            admin_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return render_template('login.html')
            
            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        errors = []
        if not all([username, email, password, full_name]):
            errors.append('Please fill in all required fields.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role='student'
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ==================== STUDENT DASHBOARD ROUTES ====================

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    # Get student's room allocation
    allocation = RoomAllocation.query.filter_by(student_id=current_user.id, status='active').first()
    room = allocation.room if allocation else None
    
    # Get student's complaints
    complaints = Complaint.query.filter_by(student_id=current_user.id).order_by(Complaint.created_at.desc()).limit(5).all()
    
    # Get fee status
    fee = Fee.query.filter_by(student_id=current_user.id).order_by(Fee.created_at.desc()).first()
    
    # Get room change request
    room_change_request = RoomChangeRequest.query.filter_by(student_id=current_user.id, status='pending').first()
    
    return render_template('student_dashboard.html', 
                         room=room, 
                         allocation=allocation,
                         complaints=complaints,
                         fee=fee,
                         room_change_request=room_change_request)


@app.route('/student/complaints', methods=['GET', 'POST'])
@login_required
def student_complaints():
    """Student complaints page"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'general')
        priority = request.form.get('priority', 'medium')
        
        if not subject or not description:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('student_complaints'))
        
        complaint = Complaint(
            student_id=current_user.id,
            subject=subject,
            description=description,
            category=category,
            priority=priority
        )
        
        try:
            db.session.add(complaint)
            db.session.commit()
            flash('Complaint submitted successfully!', 'success')
            return redirect(url_for('student_complaints'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to submit complaint. Please try again.', 'danger')
    
    # Get all complaints for current student
    complaints = Complaint.query.filter_by(student_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    return render_template('complaints.html', complaints=complaints, is_student=True)


@app.route('/student/fees')
@login_required
def student_fees():
    """Student fee status page"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    fees = Fee.query.filter_by(student_id=current_user.id).order_by(Fee.created_at.desc()).all()
    return render_template('fees.html', fees=fees, is_student=True)


@app.route('/student/room-change', methods=['GET', 'POST'])
@login_required
def student_room_change():
    """Student room change request"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    # Check if student has a room
    allocation = RoomAllocation.query.filter_by(student_id=current_user.id, status='active').first()
    if not allocation:
        flash('You are not allocated to any room.', 'warning')
        return redirect(url_for('student_dashboard'))
    
    # Get available rooms
    available_rooms = Room.query.filter(
        Room.is_available == True,
        Room.id != allocation.room_id,
        Room.current_occupancy < Room.capacity
    ).all()
    
    if request.method == 'POST':
        new_room_id = request.form.get('new_room_id')
        reason = request.form.get('reason', '').strip()
        
        if not new_room_id or not reason:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('student_room_change'))
        
        # Check if pending request exists
        existing_request = RoomChangeRequest.query.filter_by(
            student_id=current_user.id, 
            status='pending'
        ).first()
        
        if existing_request:
            flash('You already have a pending room change request.', 'warning')
            return redirect(url_for('student_room_change'))
        
        # Create room change request
        room_change = RoomChangeRequest(
            student_id=current_user.id,
            current_room_id=allocation.room_id,
            new_room_id=new_room_id,
            reason=reason
        )
        
        try:
            db.session.add(room_change)
            db.session.commit()
            flash('Room change request submitted successfully!', 'success')
            return redirect(url_for('student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to submit request. Please try again.', 'danger')
    
    # Get existing requests
    requests = RoomChangeRequest.query.filter_by(student_id=current_user.id).order_by(RoomChangeRequest.requested_date.desc()).all()
    
    return render_template('room_change.html', 
                         allocation=allocation,
                         available_rooms=available_rooms,
                         requests=requests)


# ==================== ADMIN DASHBOARD ROUTES ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Statistics
    total_students = User.query.filter_by(role='student').count()
    total_rooms = Room.query.count()
    occupied_rooms = RoomAllocation.query.filter_by(status='active').count()
    available_rooms = Room.query.filter(Room.current_occupancy < Room.capacity).count()
    
    # Pending complaints
    pending_complaints = Complaint.query.filter_by(status='pending').count()
    
    # Pending room change requests
    pending_room_changes = RoomChangeRequest.query.filter_by(status='pending').count()
    
    # Fees due
    fees_due = Fee.query.filter_by(payment_status='due').count()
    
    # Recent activities
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    recent_allocations = RoomAllocation.query.order_by(RoomAllocation.allocated_date.desc()).limit(5).all()
    
    stats = {
        'total_students': total_students,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'pending_complaints': pending_complaints,
        'pending_room_changes': pending_room_changes,
        'fees_due': fees_due
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         recent_complaints=recent_complaints,
                         recent_allocations=recent_allocations)


@app.route('/admin/students')
@admin_required
def admin_students():
    """Admin - Manage students"""
    # Search and filter
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    
    query = User.query.filter_by(role='student')
    
    if search:
        query = query.filter(
            (User.full_name.contains(search)) |
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    
    if status_filter == 'allocated':
        query = query.join(RoomAllocation).filter(RoomAllocation.status == 'active')
    elif status_filter == 'unallocated':
        subquery = db.session.query(RoomAllocation.student_id).filter(RoomAllocation.status == 'active')
        query = query.filter(~User.id.in_(subquery))
    
    students = query.all()
    
    # Get allocation info for each student
    student_data = []
    for student in students:
        allocation = RoomAllocation.query.filter_by(student_id=student.id, status='active').first()
        student_data.append({
            'student': student,
            'allocation': allocation,
            'room': allocation.room if allocation else None
        })
    
    return render_template('admin_students.html', students_data=student_data, search=search, status_filter=status_filter)


@app.route('/admin/rooms')
@admin_required
def admin_rooms():
    """Admin - Manage rooms"""
    search = request.args.get('search', '').strip()
    availability_filter = request.args.get('availability', 'all')
    
    query = Room.query
    
    if search:
        query = query.filter(Room.room_number.contains(search))
    
    if availability_filter == 'available':
        query = query.filter(Room.current_occupancy < Room.capacity)
    elif availability_filter == 'full':
        query = query.filter(Room.current_occupancy >= Room.capacity)
    
    rooms = query.order_by(Room.room_number).all()
    
    # Get students in each room
    room_data = []
    for room in rooms:
        allocations = RoomAllocation.query.filter_by(room_id=room.id, status='active').all()
        students = [alloc.student for alloc in allocations]
        room_data.append({
            'room': room,
            'students': students
        })
    
    return render_template('admin_rooms.html', rooms_data=room_data, search=search, availability_filter=availability_filter)


@app.route('/admin/allocate-room', methods=['GET', 'POST'])
@admin_required
def admin_allocate_room():
    """Admin - Allocate room to student"""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        room_id = request.form.get('room_id')
        
        if not student_id or not room_id:
            flash('Please select both student and room.', 'danger')
            return redirect(url_for('admin_allocate_room'))
        
        student = User.query.get(student_id)
        room = Room.query.get(room_id)
        
        if not student or student.role != 'student':
            flash('Invalid student selected.', 'danger')
            return redirect(url_for('admin_allocate_room'))
        
        if not room:
            flash('Invalid room selected.', 'danger')
            return redirect(url_for('admin_allocate_room'))
        
        # Check if student already has a room
        existing_allocation = RoomAllocation.query.filter_by(student_id=student_id, status='active').first()
        if existing_allocation:
            flash(f'Student is already allocated to room {existing_allocation.room.room_number}.', 'warning')
            return redirect(url_for('admin_allocate_room'))
        
        # Check room availability
        if room.is_full():
            flash('Selected room is full.', 'danger')
            return redirect(url_for('admin_allocate_room'))
        
        # Create allocation
        allocation = RoomAllocation(
            student_id=student_id,
            room_id=room_id
        )
        
        # Update room occupancy
        room.current_occupancy += 1
        if room.current_occupancy >= room.capacity:
            room.is_available = False
        
        try:
            db.session.add(allocation)
            db.session.commit()
            log_audit('room_allocated', 'student', student_id, f'Room {room.room_number} allocated to {student.full_name}')
            flash(f'Room {room.room_number} allocated to {student.full_name} successfully!', 'success')
            return redirect(url_for('admin_rooms'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to allocate room. Please try again.', 'danger')
    
    # Get unallocated students
    allocated_student_ids = db.session.query(RoomAllocation.student_id).filter(RoomAllocation.status == 'active')
    unallocated_students = User.query.filter_by(role='student').filter(~User.id.in_(allocated_student_ids)).all()
    
    # Get available rooms
    available_rooms = Room.query.filter(Room.current_occupancy < Room.capacity).all()
    
    return render_template('room_allocation.html', 
                         unallocated_students=unallocated_students,
                         available_rooms=available_rooms)


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    """Admin - Manage complaints"""
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    query = Complaint.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    
    return render_template('complaints.html', complaints=complaints, is_student=False, status_filter=status_filter, category_filter=category_filter)


@app.route('/admin/complaint/<int:complaint_id>/update', methods=['POST'])
@admin_required
def admin_update_complaint(complaint_id):
    """Admin - Update complaint status"""
    complaint = Complaint.query.get_or_404(complaint_id)
    status = request.form.get('status')
    admin_response = request.form.get('admin_response', '').strip()
    
    if status not in ['pending', 'in_progress', 'resolved', 'rejected']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin_complaints'))
    
    complaint.status = status
    complaint.updated_at = datetime.utcnow()
    
    if admin_response:
        complaint.admin_response = admin_response
    
    if status == 'resolved':
        complaint.resolved_date = datetime.utcnow()
    
    try:
        db.session.commit()
        log_audit('complaint_updated', 'complaint', complaint_id, f'Status changed to {status}')
        flash('Complaint status updated successfully!', 'success')
        
        # Simulate email notification
        # In production, you would send actual email here
        app.logger.info(f'Email notification sent to {complaint.student.email} - Complaint #{complaint.id} status: {status}')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update complaint. Please try again.', 'danger')
    
    return redirect(url_for('admin_complaints'))


@app.route('/admin/fees')
@admin_required
def admin_fees():
    """Admin - Manage fees"""
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    
    query = Fee.query.join(User)
    
    if search:
        query = query.filter(
            (User.full_name.contains(search)) |
            (User.username.contains(search))
        )
    
    if status_filter != 'all':
        query = query.filter_by(payment_status=status_filter)
    
    fees = query.order_by(Fee.created_at.desc()).all()
    
    # Get all students for fee creation form
    all_students = User.query.filter_by(role='student').order_by(User.full_name).all()
    
    return render_template('fees.html', fees=fees, all_students=all_students, is_student=False, search=search, status_filter=status_filter)


@app.route('/admin/fee/create', methods=['POST'])
@admin_required
def admin_create_fee():
    """Admin - Create fee record"""
    student_id = request.form.get('student_id')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
    
    if not all([student_id, amount, due_date]):
        flash('Please fill in all fields.', 'danger')
        return redirect(url_for('admin_fees'))
    
    try:
        amount = float(amount)
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        fee = Fee(
            student_id=student_id,
            amount=amount,
            due_date=due_date,
            payment_status='due'
        )
        
        db.session.add(fee)
        db.session.commit()
        log_audit('fee_created', 'fee', fee.id, f'Fee {amount} created for student {student_id}')
        flash('Fee record created successfully!', 'success')
    except ValueError:
        flash('Invalid amount or date format.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash('Failed to create fee record. Please try again.', 'danger')
    
    return redirect(url_for('admin_fees'))


@app.route('/admin/fee/<int:fee_id>/update', methods=['POST'])
@admin_required
def admin_update_fee(fee_id):
    """Admin - Update fee payment status"""
    fee = Fee.query.get_or_404(fee_id)
    payment_status = request.form.get('payment_status')
    payment_method = request.form.get('payment_method', '').strip()
    transaction_id = request.form.get('transaction_id', '').strip()
    
    if payment_status not in ['paid', 'due', 'overdue']:
        flash('Invalid payment status.', 'danger')
        return redirect(url_for('admin_fees'))
    
    fee.payment_status = payment_status
    fee.updated_at = datetime.utcnow()
    
    if payment_status == 'paid':
        fee.paid_date = date.today()
        fee.payment_method = payment_method if payment_method else None
        fee.transaction_id = transaction_id if transaction_id else None
    
    try:
        db.session.commit()
        log_audit('fee_updated', 'fee', fee_id, f'Payment status changed to {payment_status}')
        flash('Fee payment status updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update fee. Please try again.', 'danger')
    
    return redirect(url_for('admin_fees'))


@app.route('/admin/room-change-requests')
@admin_required
def admin_room_change_requests():
    """Admin - Manage room change requests"""
    status_filter = request.args.get('status', 'pending')
    
    query = RoomChangeRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(RoomChangeRequest.requested_date.desc()).all()
    
    return render_template('admin_room_change.html', requests=requests, status_filter=status_filter)


@app.route('/admin/room-change/<int:request_id>/process', methods=['POST'])
@admin_required
def admin_process_room_change(request_id):
    """Admin - Process room change request"""
    room_change = RoomChangeRequest.query.get_or_404(request_id)
    action = request.form.get('action')  # 'approve' or 'reject'
    admin_response = request.form.get('admin_response', '').strip()
    
    if action not in ['approve', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('admin_room_change_requests'))
    
    if action == 'approve':
        # Check if new room has space
        new_room = Room.query.get(room_change.new_room_id)
        if new_room.is_full():
            flash('The requested room is now full. Cannot approve request.', 'danger')
            return redirect(url_for('admin_room_change_requests'))
        
        # Update old room occupancy
        old_room = Room.query.get(room_change.current_room_id)
        old_room.current_occupancy -= 1
        if old_room.current_occupancy < old_room.capacity:
            old_room.is_available = True
        
        # Update new room occupancy
        new_room.current_occupancy += 1
        if new_room.current_occupancy >= new_room.capacity:
            new_room.is_available = False
        
        # Update allocation
        allocation = RoomAllocation.query.filter_by(student_id=room_change.student_id, status='active').first()
        if allocation:
            allocation.room_id = room_change.new_room_id
        
        room_change.status = 'approved'
        
    else:  # reject
        room_change.status = 'rejected'
    
    room_change.admin_response = admin_response
    room_change.processed_date = datetime.utcnow()
    
    try:
        db.session.commit()
        log_audit('room_change_processed', 'room_change_request', request_id, f'Request {action}ed')
        flash(f'Room change request {action}d successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to process request. Please try again.', 'danger')
    
    return redirect(url_for('admin_room_change_requests'))


@app.route('/admin/room/create', methods=['POST'])
@admin_required
def admin_create_room():
    """Admin - Create new room"""
    room_number = request.form.get('room_number', '').strip()
    floor = request.form.get('floor')
    capacity = request.form.get('capacity')
    room_type = request.form.get('room_type', 'standard')
    amenities = request.form.get('amenities', '').strip()
    
    if not all([room_number, floor, capacity]):
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('admin_rooms'))
    
    # Check if room number already exists
    if Room.query.filter_by(room_number=room_number).first():
        flash('Room number already exists.', 'danger')
        return redirect(url_for('admin_rooms'))
    
    try:
        floor = int(floor)
        capacity = int(capacity)
        
        room = Room(
            room_number=room_number,
            floor=floor,
            capacity=capacity,
            room_type=room_type,
            amenities=amenities,
            current_occupancy=0,
            is_available=True
        )
        
        db.session.add(room)
        db.session.commit()
        log_audit('room_created', 'room', room.id, f'Room {room_number} created')
        flash(f'Room {room_number} created successfully!', 'success')
    except ValueError:
        flash('Invalid floor or capacity. Please enter numbers.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash('Failed to create room. Please try again.', 'danger')
    
    return redirect(url_for('admin_rooms'))


@app.route('/admin/audit-logs')
@admin_required
def admin_audit_logs():
    """Admin - View audit logs"""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin_audit_logs.html', logs=logs)


# ==================== INITIALIZATION ====================

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def create_admin_user():
    """Create default admin user"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@hostel.com',
                full_name='System Administrator',
                role='admin'
            )
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created!")
            print("Username: admin, Password: admin123")
        else:
            print("Admin user already exists.")


def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        # Create sample rooms
        if Room.query.count() == 0:
            rooms_data = [
                {'room_number': '101', 'floor': 1, 'capacity': 2, 'room_type': 'standard'},
                {'room_number': '102', 'floor': 1, 'capacity': 2, 'room_type': 'standard'},
                {'room_number': '201', 'floor': 2, 'capacity': 3, 'room_type': 'deluxe'},
                {'room_number': '202', 'floor': 2, 'capacity': 3, 'room_type': 'deluxe'},
                {'room_number': '301', 'floor': 3, 'capacity': 2, 'room_type': 'premium'},
            ]
            
            for room_data in rooms_data:
                room = Room(**room_data)
                db.session.add(room)
            
            db.session.commit()
            print("Sample rooms created!")


if __name__ == '__main__':
    # Create instance directory for SQLite database
    os.makedirs('instance', exist_ok=True)
    
    # Initialize database
    create_tables()
    create_admin_user()
    create_sample_data()
    
    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)

