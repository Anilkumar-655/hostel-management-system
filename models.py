"""
Database Models for Hostel Management System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for students and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    allocations = db.relationship('RoomAllocation', backref='student', lazy=True, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='student', lazy=True)
    fees = db.relationship('Fee', backref='student', lazy=True)
    room_change_requests = db.relationship('RoomChangeRequest', backref='student', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Room(db.Model):
    """Room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    floor = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    current_occupancy = db.Column(db.Integer, default=0)
    room_type = db.Column(db.String(50), default='standard')  # 'standard', 'deluxe', 'premium'
    amenities = db.Column(db.Text)  # JSON string or comma-separated
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('RoomAllocation', backref='room', lazy=True, cascade='all, delete-orphan')
    room_change_requests = db.relationship('RoomChangeRequest', foreign_keys='RoomChangeRequest.new_room_id', backref='new_room', lazy=True)
    
    def is_full(self):
        """Check if room is full"""
        return self.current_occupancy >= self.capacity
    
    def has_space(self):
        """Check if room has available space"""
        return self.current_occupancy < self.capacity
    
    def __repr__(self):
        return f'<Room {self.room_number}>'


class RoomAllocation(db.Model):
    """Room allocation model"""
    __tablename__ = 'room_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    allocated_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'transferred', 'vacated'
    
    def __repr__(self):
        return f'<RoomAllocation Student:{self.student_id} Room:{self.room_id}>'


class Complaint(db.Model):
    """Complaint model"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')  # 'maintenance', 'food', 'security', 'general'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'in_progress', 'resolved', 'rejected'
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_response = db.Column(db.Text)
    resolved_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Complaint {self.id} - {self.subject}>'


class Fee(db.Model):
    """Fee management model"""
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    payment_status = db.Column(db.String(20), default='due')  # 'paid', 'due', 'overdue'
    payment_method = db.Column(db.String(50))  # 'cash', 'online', 'bank_transfer'
    transaction_id = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Fee {self.id} - Student:{self.student_id} Amount:{self.amount}>'


class RoomChangeRequest(db.Model):
    """Room change request model"""
    __tablename__ = 'room_change_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    new_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    admin_response = db.Column(db.Text)
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    
    # Relationships
    current_room = db.relationship('Room', foreign_keys=[current_room_id], backref='outgoing_requests')
    
    def __repr__(self):
        return f'<RoomChangeRequest {self.id} - Student:{self.student_id}>'


class AuditLog(db.Model):
    """Audit log for admin actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'room_allocated', 'complaint_updated', etc.
    target_type = db.Column(db.String(50))  # 'student', 'room', 'complaint', etc.
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON string with action details
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    admin = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'

