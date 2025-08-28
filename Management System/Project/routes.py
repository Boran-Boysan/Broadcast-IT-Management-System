from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from Project.models import Employee, Equipment, SoftwareLicense, Logs, log_user_action, KnowledgeBase, Logs
from Project import db
from datetime import datetime, timedelta
import re
from werkzeug.utils import secure_filename
import os

main = Blueprint("main", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads', 'knowledge_base')


# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == 'manager':
            return redirect(url_for('main.manager'))
        else:
            return redirect(url_for('main.user'))
    else:
        return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Employee.query.filter(
            (Employee.email == username) | (Employee.name == username)
        ).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session['role'] = user.role
            session['user_id'] = user.employee_id

            # Log giriş
            log_user_action(user.employee_id, 'login', 'employee', user.employee_id)

            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'manager':
                return redirect(url_for('main.manager'))
            else:
                return redirect(url_for('main.user_dashboard'))
        else:
            flash('Hatalı giriş bilgisi! Lütfen e-posta/kullanıcı adı ve şifrenizi kontrol edin.', 'danger')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    log_user_action(current_user.employee_id, 'logout', 'employee', current_user.employee_id)
    logout_user()
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.login'))


# ===========================
# ADMIN PANEL ROUTES
# ===========================

@main.route('/admin')
@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # İstatistikler
    stats = {
        'total_employees': Employee.query.count(),
        'admin_count': Employee.query.filter_by(role='admin').count(),
        'manager_count': Employee.query.filter_by(role='manager').count(),
        'user_count': Employee.query.filter_by(role='user').count(),
        'departments': db.session.query(Employee.department, db.func.count(Employee.employee_id)).group_by(
            Employee.department).all(),
        'total_equipment': Equipment.query.count(),
        'equipment_in_use': Equipment.query.filter_by(status='in_use').count(),
        'total_licenses': SoftwareLicense.query.count(),
        'active_licenses': SoftwareLicense.query.filter_by(status='active').count()
    }

    # Son eklenen çalışanlar
    recent_employees = Employee.query.order_by(Employee.data_joined.desc()).limit(5).all()

    return render_template('admin/admin_dashboard.html', stats=stats, recent_employees=recent_employees)


@main.route('/admin/employees')
@login_required
def admin_employees():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Arama ve filtreleme
    search = request.args.get('search', '')
    department_filter = request.args.get('department', '')
    role_filter = request.args.get('role', '')

    query = Employee.query

    if search:
        query = query.filter(
            (Employee.name.ilike(f'%{search}%')) |
            (Employee.surname.ilike(f'%{search}%')) |
            (Employee.email.ilike(f'%{search}%'))
        )

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    if role_filter:
        query = query.filter(Employee.role == role_filter)

    employees = query.order_by(Employee.data_joined.desc()).all()

    # Departman listesi filtre için
    departments = db.session.query(Employee.department).distinct().filter(Employee.department.isnot(None)).all()
    departments = [dept[0] for dept in departments]

    return render_template('admin/employees.html',
                           employees=employees,
                           departments=departments,
                           search=search,
                           department_filter=department_filter,
                           role_filter=role_filter)


@main.route('/admin/employees/add', methods=['GET', 'POST'])
@login_required
def admin_add_employee():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            surname = request.form.get('surname', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            department = request.form.get('department', '').strip()
            role = request.form.get('role', '').strip()

            errors = []

            # Validasyonlar
            if not name or len(name) > 30:
                errors.append('Ad alanı zorunludur ve 30 karakter geçmemelidir.')

            if not surname or len(surname) > 30:
                errors.append('Soyad alanı zorunludur ve 30 karakter geçmemelidir.')

            if not email or len(email) > 50:
                errors.append('E-posta alanı zorunludur ve 50 karakter geçmemelidir.')
            elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors.append('Geçerli bir e-posta adresi girin.')

            if not password or len(password) < 6:
                errors.append('Şifre en az 6 karakter olmalıdır.')

            if not role or role not in ['admin', 'user', 'manager']:
                errors.append('Geçerli bir rol seçin.')

            if department and len(department) > 50:
                errors.append('Departman adı 50 karakter geçmemelidir.')

            # E-posta kontrolü
            existing_employee = Employee.query.filter_by(email=email).first()
            if existing_employee:
                errors.append('Bu e-posta adresi zaten kullanılıyor.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/add_employee.html')

            # Şifreyi hashle
            hashed_password = generate_password_hash(password)

            # Yeni çalışan oluştur
            new_employee = Employee(
                name=name,
                surname=surname,
                email=email,
                password=hashed_password,
                department=department if department else None,
                role=role
            )

            db.session.add(new_employee)
            db.session.commit()

            # Log kaydı
            log_user_action(current_user.employee_id, 'add', 'employee', new_employee.employee_id,
                            f'{name} {surname} çalışanı eklendi')

            flash(f'Çalışan {name} {surname} başarıyla eklendi!', 'success')
            return redirect(url_for('main.admin_employees'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')
            return render_template('admin/add_employee.html')

    return render_template('admin/add_employee.html')


@main.route('/admin/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_employee(employee_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            employee.name = request.form.get('name', '').strip()
            employee.surname = request.form.get('surname', '').strip()
            email = request.form.get('email', '').strip().lower()
            department = request.form.get('department', '').strip()
            role = request.form.get('role', '').strip()

            # E-posta değiştiriliyorsa kontrol et
            if email != employee.email:
                existing = Employee.query.filter_by(email=email).first()
                if existing:
                    flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
                    return render_template('admin/edit_employee.html', employee=employee)
                employee.email = email

            employee.department = department if department else None
            employee.role = role

            # Şifre değiştirilmek isteniyorsa
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                if len(new_password) < 6:
                    flash('Yeni şifre en az 6 karakter olmalıdır.', 'error')
                    return render_template('admin/edit_employee.html', employee=employee)
                employee.password = generate_password_hash(new_password)

            db.session.commit()

            # Log kaydı
            log_user_action(current_user.employee_id, 'edit', 'employee', employee.employee_id,
                            f'{employee.name} {employee.surname} çalışanı güncellendi')

            flash(f'Çalışan {employee.name} {employee.surname} başarıyla güncellendi!', 'success')
            return redirect(url_for('main.admin_employees'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')

    return render_template('admin/edit_employee.html', employee=employee)


@main.route('/admin/employees/delete/<int:employee_id>', methods=['POST'])
@login_required
def admin_delete_employee(employee_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    try:
        employee = Employee.query.get_or_404(employee_id)

        # Kendi hesabını silmesin
        if employee.employee_id == current_user.employee_id:
            flash('Kendi hesabınızı silemezsiniz!', 'error')
            return redirect(url_for('main.admin_employees'))

        employee_name = f"{employee.name} {employee.surname}"

        # Log kaydı
        log_user_action(current_user.employee_id, 'delete', 'employee', employee.employee_id,
                        f'{employee_name} çalışanı silindi')

        db.session.delete(employee)
        db.session.commit()

        flash(f'Çalışan {employee_name} başarıyla silindi!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Silme işlemi sırasında hata oluştu: {str(e)}', 'error')

    return redirect(url_for('main.admin_employees'))


@main.route('/admin/employees/view/<int:employee_id>')
@login_required
def admin_view_employee(employee_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    employee = Employee.query.get_or_404(employee_id)

    # Log kaydı
    log_user_action(current_user.employee_id, 'view', 'employee', employee.employee_id,
                    f'{employee.name} {employee.surname} profili görüntülendi')

    return render_template('admin/view_employee.html', employee=employee)


# ===========================
# INVENTORY MANAGEMENT ROUTES - DÜZELTİLMİŞ
# ===========================

# Ana Envanter Dashboard'u
@main.route('/admin/inventory')
@login_required
def admin_inventory_dashboard():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    from datetime import timedelta

    # Ekipman istatistikleri
    equipment_stats = {
        'total_equipment': Equipment.query.count(),
        'in_use': Equipment.query.filter_by(status='in_use').count(),
        'in_stock': Equipment.query.filter_by(status='in_stock').count(),
        'under_repair': Equipment.query.filter_by(status='under_repair').count()
    }

    # Lisans istatistikleri
    license_stats = {
        'total_licenses': SoftwareLicense.query.count(),
        'active_licenses': SoftwareLicense.query.filter_by(status='active').count(),
        'expired_licenses': SoftwareLicense.query.filter_by(status='expired').count(),
        'expiring_soon': SoftwareLicense.query.filter(
            SoftwareLicense.expiration_date <= datetime.now().date() + timedelta(days=30),
            SoftwareLicense.expiration_date >= datetime.now().date(),
            SoftwareLicense.status == 'active'
        ).count() if SoftwareLicense.query.count() > 0 else 0
    }

    # Kombine istatistikler
    stats = {**equipment_stats, **license_stats}

    # Son eklenen ekipmanlar
    recent_equipment = Equipment.query.order_by(Equipment.last_updated.desc()).limit(5).all()

    # Son eklenen lisanslar
    recent_licenses = SoftwareLicense.query.order_by(SoftwareLicense.license_id.desc()).limit(5).all()

    # Süresi yaklaşan lisanslar
    expiring_licenses = SoftwareLicense.query.filter(
        SoftwareLicense.expiration_date <= datetime.now().date() + timedelta(days=30),
        SoftwareLicense.expiration_date >= datetime.now().date(),
        SoftwareLicense.status == 'active'
    ).limit(5).all()

    # Kategori bazlı dağılım
    equipment_by_category = db.session.query(
        Equipment.category,
        db.func.count(Equipment.equipment_id)
    ).group_by(Equipment.category).all()

    # Her lisansın kalan gün sayısını hesapla
    for license in expiring_licenses:
        if license.expiration_date:
            days_left = (license.expiration_date - datetime.now().date()).days
            license.days_until_expiry = days_left

    return render_template('admin/inventory/inventory_dashboard.html',
                           stats=stats,
                           recent_equipment=recent_equipment,
                           recent_licenses=recent_licenses,
                           expiring_licenses=expiring_licenses,
                           equipment_by_category=equipment_by_category)


# Ekipman Listesi Sayfası - URL değiştirildi
@main.route('/admin/inventory/equipment/list')
@login_required
def admin_inventory_equipment():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Filtreleme
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    assigned_filter = request.args.get('assigned', '')

    query = Equipment.query

    if search:
        query = query.filter(
            (Equipment.equipment_name.ilike(f'%{search}%')) |
            (Equipment.brand.ilike(f'%{search}%')) |
            (Equipment.model.ilike(f'%{search}%')) |
            (Equipment.serial_number.ilike(f'%{search}%'))
        )

    if category_filter:
        query = query.filter(Equipment.category == category_filter)

    if status_filter:
        query = query.filter(Equipment.status == status_filter)

    if assigned_filter == 'assigned':
        query = query.filter(Equipment.assigned_to.isnot(None))
    elif assigned_filter == 'unassigned':
        query = query.filter(Equipment.assigned_to.is_(None))

    equipment_list = query.order_by(Equipment.last_updated.desc()).all()

    # Kategori ve durum listesi filtre için
    categories = db.session.query(Equipment.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]

    return render_template('admin/inventory/equipment_list.html',
                           equipment_list=equipment_list,
                           categories=categories,
                           search=search,
                           category_filter=category_filter,
                           status_filter=status_filter,
                           assigned_filter=assigned_filter)


# Ekipman Ekleme
@main.route('/admin/inventory/equipment/add', methods=['GET', 'POST'])
@login_required
def admin_add_equipment():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            equipment_name = request.form.get('equipment_name', '').strip()
            category = request.form.get('category', '').strip()
            brand = request.form.get('brand', '').strip()
            model = request.form.get('model', '').strip()
            serial_number = request.form.get('serial_number', '').strip()
            location = request.form.get('location', '').strip()
            purchase_date = request.form.get('purchase_date', '')
            status = request.form.get('status', 'in_stock')
            assigned_to = request.form.get('assigned_to', '')

            errors = []

            if not equipment_name or len(equipment_name) > 100:
                errors.append('Ekipman adı zorunludur ve 100 karakter geçmemelidir.')

            if not category or len(category) > 50:
                errors.append('Kategori zorunludur ve 50 karakter geçmemelidir.')

            if serial_number:
                if len(serial_number) > 100:
                    errors.append('Seri numarası 100 karakter geçmemelidir.')
                existing = Equipment.query.filter_by(serial_number=serial_number).first()
                if existing:
                    errors.append('Bu seri numarası zaten kullanılıyor.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                return render_template('admin/inventory/add_equipment.html', employees=employees)

            # Tarih dönüşümü
            parsed_purchase_date = None
            if purchase_date:
                try:
                    parsed_purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Geçersiz tarih formatı.', 'error')
                    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                    return render_template('admin/inventory/add_equipment.html', employees=employees)

            # Çalışan kontrolü
            assigned_employee_id = None
            if assigned_to and assigned_to.isdigit():
                employee = Employee.query.get(int(assigned_to))
                assigned_employee_id = employee.employee_id if employee else None

            equipment = Equipment(
                equipment_name=equipment_name,
                category=category,
                brand=brand or None,
                model=model or None,
                serial_number=serial_number or None,
                location=location or None,
                purchase_date=parsed_purchase_date,
                status=status,
                assigned_to=assigned_employee_id,

            )

            db.session.add(equipment)
            db.session.commit()

            log_user_action(current_user.employee_id, 'add', 'equipment', equipment.equipment_id,
                            f'{equipment.equipment_name} ekipmanı eklendi')

            flash(f'Ekipman {equipment.equipment_name} başarıyla eklendi!', 'success')
            return redirect(url_for('main.admin_inventory_equipment'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')

    # Çalışan listesi atama için
    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
    return render_template('admin/inventory/add_equipment.html', employees=employees)


# Lisans Listesi
@main.route('/admin/inventory/licenses/list')
@login_required
def admin_licenses():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Filtreleme
    search = request.args.get('search', '')
    vendor_filter = request.args.get('vendor', '')
    status_filter = request.args.get('status', '')

    query = SoftwareLicense.query

    if search:
        query = query.filter(
            (SoftwareLicense.software_name.ilike(f'%{search}%')) |
            (SoftwareLicense.license_key.ilike(f'%{search}%')) |
            (SoftwareLicense.version.ilike(f'%{search}%'))
        )

    if vendor_filter:
        query = query.filter(SoftwareLicense.vendor == vendor_filter)

    if status_filter:
        query = query.filter(SoftwareLicense.status == status_filter)

    licenses = query.order_by(SoftwareLicense.last_updated.desc()).all()

    # Vendor listesi filtre için
    vendors = db.session.query(SoftwareLicense.vendor).distinct().all()
    vendors = [vendor[0] for vendor in vendors if vendor[0]]

    return render_template('admin/inventory/license_list.html',
                           licenses=licenses,
                           vendors=vendors,
                           search=search,
                           vendor_filter=vendor_filter,
                           status_filter=status_filter)


# Lisans Ekleme
@main.route('/admin/inventory/licenses/add', methods=['GET', 'POST'])
@login_required
def admin_add_license():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            software_name = request.form.get('software_name', '').strip()
            license_key = request.form.get('license_key', '').strip()
            version = request.form.get('version', '').strip()
            vendor = request.form.get('vendor', '').strip()
            expiration_date = request.form.get('expiration_date', '')
            status = request.form.get('status', 'active')
            assigned_to = request.form.get('assigned_to', '')
            equipment_id = request.form.get('equipment_id', '')

            errors = []

            if not software_name or len(software_name) > 50:
                errors.append('Yazılım adı zorunludur ve 50 karakter geçmemelidir.')

            if not license_key or len(license_key) > 255:
                errors.append('Lisans anahtarı zorunludur ve 255 karakter geçmemelidir.')

            # Lisans anahtarı kontrolü
            existing = SoftwareLicense.query.filter_by(license_key=license_key).first()
            if existing:
                errors.append('Bu lisans anahtarı zaten kullanılıyor.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                equipment_list = Equipment.query.order_by(Equipment.equipment_name).all()
                return render_template('admin/inventory/add_license.html',
                                       employees=employees, equipment_list=equipment_list)

            # Tarih dönüşümü
            parsed_expiry_date = None
            if expiration_date:
                try:
                    parsed_expiry_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Geçersiz tarih formatı.', 'error')
                    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                    equipment_list = Equipment.query.order_by(Equipment.equipment_name).all()
                    return render_template('admin/inventory/add_license.html',
                                           employees=employees, equipment_list=equipment_list)

            # Çalışan ve ekipman kontrolü
            assigned_employee_id = None
            if assigned_to and assigned_to.isdigit():
                employee = Employee.query.get(int(assigned_to))
                assigned_employee_id = employee.employee_id if employee else None

            assigned_equipment_id = None
            if equipment_id and equipment_id.isdigit():
                equipment = Equipment.query.get(int(equipment_id))
                assigned_equipment_id = equipment.equipment_id if equipment else None

            license = SoftwareLicense(
                software_name=software_name,
                license_key=license_key,
                version=version or None,
                vendor=vendor or None,
                expiration_date=parsed_expiry_date,
                status=status,
                assigned_to=assigned_employee_id,
                equipment_id=assigned_equipment_id,

            )

            db.session.add(license)
            db.session.commit()

            log_user_action(current_user.employee_id, 'add', 'license', license.license_id,
                            f'{license.software_name} lisansı eklendi')

            flash(f'Lisans {license.software_name} başarıyla eklendi!', 'success')
            return redirect(url_for('main.admin_licenses'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')

    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
    equipment_list = Equipment.query.order_by(Equipment.equipment_name).all()
    return render_template('admin/inventory/add_license.html',
                           employees=employees, equipment_list=equipment_list)

# API Endpoints for AJAX calls
@main.route('/api/admin/employees')
@login_required
def api_admin_employees():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    employees = Employee.query.all()
    result = []

    for emp in employees:
        result.append({
            'employee_id': emp.employee_id,
            'name': emp.name,
            'surname': emp.surname,
            'email': emp.email,
            'department': emp.department,
            'role': emp.role,
            'data_joined': emp.data_joined.strftime('%Y-%m-%d %H:%M:%S') if emp.data_joined else None
        })

    return jsonify({'employees': result})


@main.route('/api/admin/stats')
@login_required
def api_admin_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    stats = {
        'total_employees': Employee.query.count(),
        'roles': {
            'admin': Employee.query.filter_by(role='admin').count(),
            'manager': Employee.query.filter_by(role='manager').count(),
            'user': Employee.query.filter_by(role='user').count()
        },
        'departments': {},
        'equipment': {
            'total': Equipment.query.count(),
            'in_use': Equipment.query.filter_by(status='in_use').count(),
            'in_stock': Equipment.query.filter_by(status='in_stock').count(),
            'under_repair': Equipment.query.filter_by(status='under_repair').count()
        },
        'licenses': {
            'total': SoftwareLicense.query.count(),
            'active': SoftwareLicense.query.filter_by(status='active').count(),
            'expired': SoftwareLicense.query.filter_by(status='expired').count()
        }
    }

    # Departman bazlı sayılar
    dept_counts = db.session.query(Employee.department, db.func.count(Employee.employee_id)).group_by(
        Employee.department).all()
    for dept, count in dept_counts:
        stats['departments'][dept or 'Belirtilmemiş'] = count

    return jsonify(stats)


# ===========================
# MANAGER VE USER ROUTES
# ===========================

@main.route('/manager')
@login_required
def manager():
    if current_user.role != 'manager':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    user_info = f"""
    <h2>Manager Paneli</h2>
    <p><strong>Hoş geldiniz:</strong> {current_user.name} {current_user.surname}</p>
    <p><strong>E-posta:</strong> {current_user.email}</p>
    <p><strong>Rol:</strong> {current_user.role}</p>
    <p><strong>Departman:</strong> {current_user.department or 'Belirtilmemiş'}</p>
    <br>
    <a href="{url_for('main.logout')}" style="background:#dc3545; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">Çıkış Yap</a>
    """
    return user_info


@main.route('/user')
@login_required
def user():
    if current_user.role != 'user':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    user_info = f"""
    <h2>Kullanıcı Paneli</h2>
    <p><strong>Hoş geldiniz:</strong> {current_user.name} {current_user.surname}</p>
    <p><strong>E-posta:</strong> {current_user.email}</p>
    <p><strong>Rol:</strong> {current_user.role}</p>
    <p><strong>Departman:</strong> {current_user.department or 'Belirtilmemiş'}</p>
    <br>
    <a href="{url_for('main.logout')}" style="background:#dc3545; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">Çıkış Yap</a>
    """
    return user_info


# ===========================
# ADDITIONAL UTILITY ROUTES
# ===========================




@main.route('/admin/search')
@login_required
def admin_search():
    """Global arama fonksiyonu"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'results': []})

    results = []

    # Çalışan araması
    employees = Employee.query.filter(
        (Employee.name.ilike(f'%{query}%')) |
        (Employee.surname.ilike(f'%{query}%')) |
        (Employee.email.ilike(f'%{query}%'))
    ).limit(5).all()

    for emp in employees:
        results.append({
            'type': 'employee',
            'id': emp.employee_id,
            'title': f"{emp.name} {emp.surname}",
            'subtitle': emp.email,
            'url': url_for('main.admin_view_employee', employee_id=emp.employee_id)
        })

    # Ekipman araması
    equipment = Equipment.query.filter(
        (Equipment.equipment_name.ilike(f'%{query}%')) |
        (Equipment.brand.ilike(f'%{query}%')) |
        (Equipment.model.ilike(f'%{query}%')) |
        (Equipment.serial_number.ilike(f'%{query}%'))
    ).limit(5).all()

    for eq in equipment:
        results.append({
            'type': 'equipment',
            'id': eq.equipment_id,
            'title': eq.equipment_name,
            'subtitle': f"{eq.brand} {eq.model}" if eq.brand else eq.category,
            'url': url_for('main.admin_view_equipment', equipment_id=eq.equipment_id)
        })

    # Lisans araması
    licenses = SoftwareLicense.query.filter(
        (SoftwareLicense.software_name.ilike(f'%{query}%')) |
        (SoftwareLicense.vendor.ilike(f'%{query}%'))
    ).limit(5).all()

    for lic in licenses:
        results.append({
            'type': 'license',
            'id': lic.license_id,
            'title': lic.software_name,
            'subtitle': lic.vendor or 'Vendor belirtilmemiş',
            'url': f"/admin/inventory/licenses/{lic.license_id}"  # Bu route henüz yok ama eklenebilir
        })

    return jsonify({'results': results})


# ===========================
# ERROR HANDLERS
# ===========================

@main.errorhandler(404)
def not_found(error):
    """404 hata sayfası"""
    return render_template('errors/404.html'), 404


@main.errorhandler(403)
def forbidden(error):
    """403 hata sayfası"""
    return render_template('errors/403.html'), 403


@main.errorhandler(500)
def internal_error(error):
    """500 hata sayfası"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ===========================
# DASHBOARD DATA ENDPOINTS
# ===========================

@main.route('/api/admin/dashboard-data')
@login_required
def api_dashboard_data():
    """Dashboard için gerçek zamanlı veri"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Son aktiviteler
        recent_activities = Logs.query.order_by(Logs.action_time.desc()).limit(10).all()

        activities = []
        for log in recent_activities:
            activities.append({
                'id': log.log_id,
                'user': f"{log.user.name} {log.user.surname}" if log.user else 'Sistem',
                'action': log.action_display,
                'target': log.target_display,
                'time': log.time_ago,
                'description': log.description
            })

        # Sistem durumu
        system_health = {
            'database': 'healthy',
            'storage': 'healthy',
            'network': 'healthy',
            'services': 'healthy'
        }

        # Uyarılar
        warnings = []

        # Süresi yaklaşan lisanslar
        from datetime import timedelta
        expiring_licenses = SoftwareLicense.query.filter(
            SoftwareLicense.expiration_date <= datetime.now().date() + timedelta(days=30),
            SoftwareLicense.expiration_date >= datetime.now().date(),
            SoftwareLicense.status == 'active'
        ).count()

        if expiring_licenses > 0:
            warnings.append({
                'type': 'license_expiry',
                'message': f'{expiring_licenses} lisansın süresi 30 gün içinde dolacak',
                'count': expiring_licenses,
                'priority': 'medium'
            })

        # Tamirde olan ekipmanlar
        under_repair = Equipment.query.filter_by(status='under_repair').count()
        if under_repair > 0:
            warnings.append({
                'type': 'equipment_repair',
                'message': f'{under_repair} ekipman tamirde',
                'count': under_repair,
                'priority': 'low'
            })

        return jsonify({
            'success': True,
            'data': {
                'recent_activities': activities,
                'system_health': system_health,
                'warnings': warnings,
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===========================
# BULK OPERATIONS
# ===========================

@main.route('/admin/employees/bulk-delete', methods=['POST'])
@login_required
def admin_bulk_delete_employees():
    """Toplu çalışan silme"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        employee_ids = request.json.get('employee_ids', [])
        if not employee_ids:
            return jsonify({'error': 'No employees selected'}), 400

        deleted_count = 0
        errors = []

        for emp_id in employee_ids:
            try:
                employee = Employee.query.get(emp_id)
                if employee:
                    if employee.employee_id == current_user.employee_id:
                        errors.append(f"Kendi hesabınızı silemezsiniz")
                        continue

                    # Log kaydı
                    log_user_action(current_user.employee_id, 'delete', 'employee',
                                    employee.employee_id, f'{employee.name} {employee.surname} toplu silmede silindi')

                    db.session.delete(employee)
                    deleted_count += 1
            except Exception as e:
                errors.append(f"ID {emp_id}: {str(e)}")

        db.session.commit()

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'errors': errors
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main.route('/admin/equipment/bulk-update-status', methods=['POST'])
@login_required
def admin_bulk_update_equipment_status():
    """Toplu ekipman durum güncelleme"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        equipment_ids = request.json.get('equipment_ids', [])
        new_status = request.json.get('status', '')

        if not equipment_ids or not new_status:
            return jsonify({'error': 'Missing required data'}), 400

        if new_status not in ['in_stock', 'in_use', 'under_repair', 'scrap']:
            return jsonify({'error': 'Invalid status'}), 400

        updated_count = 0

        for eq_id in equipment_ids:
            equipment = Equipment.query.get(eq_id)
            if equipment:
                old_status = equipment.status
                equipment.status = new_status

                # Log kaydı
                log_user_action(current_user.employee_id, 'edit', 'equipment',
                                equipment.equipment_id,
                                f'{equipment.equipment_name} durumu {old_status} -> {new_status}')
                updated_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'updated_count': updated_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===========================
# EXPORT OPERATIONS
# ===========================

@main.route('/admin/export/employees')
@login_required
def admin_export_employees():
    """Çalışan listesini CSV olarak dışa aktar"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    try:
        import csv
        from io import StringIO
        from flask import make_response

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['ID', 'Ad', 'Soyad', 'E-posta', 'Departman', 'Rol', 'Katılım Tarihi'])

        # Data
        employees = Employee.query.order_by(Employee.employee_id).all()
        for emp in employees:
            writer.writerow([
                emp.employee_id,
                emp.name,
                emp.surname,
                emp.email,
                emp.department or '',
                emp.role,
                emp.data_joined.strftime('%Y-%m-%d %H:%M:%S') if emp.data_joined else ''
            ])

        output.seek(0)

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers[
            'Content-Disposition'] = f'attachment; filename=employees_{datetime.now().strftime("%Y%m%d")}.csv'

        # Log kaydı
        log_user_action(current_user.employee_id, 'export', 'employee', None,
                        'Çalışan listesi CSV olarak dışa aktarıldı')

        return response

    except Exception as e:
        flash(f'Dışa aktarma sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.admin_employees'))


@main.route('/admin/export/equipment')
@login_required
def admin_export_equipment():
    """Ekipman listesini CSV olarak dışa aktar"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    try:
        import csv
        from io import StringIO
        from flask import make_response

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['ID', 'Ekipman Adı', 'Kategori', 'Marka', 'Model', 'Seri No',
                         'Durum', 'Atanan Kişi', 'Konum', 'Satın Alma Tarihi'])

        # Data
        equipment_list = Equipment.query.order_by(Equipment.equipment_id).all()
        for eq in equipment_list:
            assigned_person = ''
            if eq.assigned_employee:
                assigned_person = f"{eq.assigned_employee.name} {eq.assigned_employee.surname}"

            writer.writerow([
                eq.equipment_id,
                eq.equipment_name,
                eq.category,
                eq.brand or '',
                eq.model or '',
                eq.serial_number or '',
                eq.status_display,
                assigned_person,
                eq.location or '',
                eq.purchase_date.strftime('%Y-%m-%d') if eq.purchase_date else ''
            ])

        output.seek(0)

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers[
            'Content-Disposition'] = f'attachment; filename=equipment_{datetime.now().strftime("%Y%m%d")}.csv'

        # Log kaydı
        log_user_action(current_user.employee_id, 'export', 'equipment', None,
                        'Ekipman listesi CSV olarak dışa aktarıldı')

        return response

    except Exception as e:
        flash(f'Dışa aktarma sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.admin_inventory_equipment'))
        id = employee.employee_id

        new_equipment = Equipment(
            equipment_name=equipment_name,
            category=category,
            brand=brand if brand else None,
            model=model if model else None,
            serial_number=serial_number if serial_number else None,
            purchase_date=parsed_date,
            status=status,
            assigned_to=assigned_employee_id,
            location=location if location else None
        )

        db.session.add(new_equipment)
        db.session.commit()

        # Log kaydı
        log_user_action(current_user.employee_id, 'add', 'equipment', new_equipment.equipment_id,
                        f'{equipment_name} ekipmanı eklendi')

        flash(f'Ekipman {equipment_name} başarıyla eklendi!', 'success')
        return redirect(url_for('main.admin_inventory_equipment'))

    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'error')


# Çalışan listesi atama için
    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
    return render_template('admin/inventory/add_equipment.html', employees=employees)


@main.route('/admin/inventory/edit/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_equipment(equipment_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    equipment = Equipment.query.get_or_404(equipment_id)

    if request.method == 'POST':
        try:
            equipment.equipment_name = request.form.get('equipment_name', '').strip()
            equipment.category = request.form.get('category', '').strip()
            equipment.brand = request.form.get('brand', '').strip() or None
            equipment.model = request.form.get('model', '').strip() or None
            equipment.location = request.form.get('location', '').strip() or None

            serial_number = request.form.get('serial_number', '').strip()
            purchase_date = request.form.get('purchase_date', '')
            status = request.form.get('status', '')
            assigned_to = request.form.get('assigned_to', '')

            if serial_number and serial_number != equipment.serial_number:
                existing = Equipment.query.filter_by(serial_number=serial_number).first()
                if existing:
                    flash('Bu seri numarası zaten kullanılıyor.', 'error')
                    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                    return render_template('admin/inventory/edit_equipment.html',
                                           equipment=equipment, employees=employees)

            equipment.serial_number = serial_number or None

            if purchase_date:
                try:
                    equipment.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Geçersiz tarih formatı.', 'error')
                    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
                    return render_template('admin/inventory/edit_equipment.html',
                                           equipment=equipment, employees=employees)
            else:
                equipment.purchase_date = None

            equipment.status = status

            if assigned_to and assigned_to.isdigit():
                employee = Employee.query.get(int(assigned_to))
                equipment.assigned_to = employee.employee_id if employee else None
            else:
                equipment.assigned_to = None

            db.session.commit()

            log_user_action(current_user.employee_id, 'edit', 'equipment', equipment.equipment_id,
                            f'{equipment.equipment_name} ekipmanı güncellendi')

            flash(f'Ekipman {equipment.equipment_name} başarıyla güncellendi!', 'success')
            return redirect(url_for('main.admin_inventory_equipment'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')

    employees = Employee.query.order_by(Employee.name, Employee.surname).all()
    return render_template('admin/inventory/edit_equipment.html', equipment=equipment, employees=employees)


@main.route('/admin/inventory/view/<int:equipment_id>')
@login_required
def admin_view_equipment(equipment_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    equipment = Equipment.query.get_or_404(equipment_id)

    # Atanan çalışan bilgisi
    assigned_employee = None
    if equipment.assigned_to:
        assigned_employee = Employee.query.get(equipment.assigned_to)

    return render_template('admin/inventory/view_equipment.html',
                           equipment=equipment,
                           assigned_employee=assigned_employee)


@main.route('/admin/inventory/delete/<int:equipment_id>', methods=['POST'])
@login_required
def admin_delete_equipment(equipment_id):
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        equipment_name = equipment.equipment_name

        # Log kaydı
        log_user_action(current_user.employee_id, 'delete', 'equipment', equipment.equipment_id,
                        f'{equipment_name} ekipmanı silindi')

        db.session.delete(equipment)
        db.session.commit()

        flash(f'Ekipman {equipment_name} başarıyla silindi!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Silme işlemi sırasında hata oluştu: {str(e)}', 'error')

    return redirect(url_for('main.admin_inventory_equipment'))





# ===========================
# KNOWLEDGE BASE ROUTES
# ===========================

@main.route('/admin/knowledge-base')
@login_required
def admin_knowledge_base():
    if current_user.role not in ['admin', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Arama ve filtreleme
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    department_filter = request.args.get('department', '')

    query = KnowledgeBase.query

    if search:
        query = query.filter(
            (KnowledgeBase.title.ilike(f'%{search}%')) |
            (KnowledgeBase.description.ilike(f'%{search}%'))
        )

    if category_filter:
        query = query.filter(KnowledgeBase.category == category_filter)

    if department_filter:
        query = query.filter(KnowledgeBase.department == department_filter)

    documents = query.order_by(KnowledgeBase.upload_date.desc()).all()

    # Filtre seçenekleri
    categories = db.session.query(KnowledgeBase.category).distinct().filter(KnowledgeBase.category.isnot(None)).all()
    categories = [cat[0] for cat in categories]

    departments = db.session.query(KnowledgeBase.department).distinct().filter(
        KnowledgeBase.department.isnot(None)).all()
    departments = [dept[0] for dept in departments]

    return render_template('admin/knowledge_base/documents.html',
                           documents=documents,
                           categories=categories,
                           departments=departments,
                           search=search,
                           category_filter=category_filter,
                           department_filter=department_filter)


@main.route('/admin/knowledge-base/upload', methods=['GET', 'POST'])
@login_required
def admin_upload_document():
    if current_user.role not in ['admin', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            department = request.form.get('department', '').strip()

            # Validation
            if not title or len(title) > 50:
                flash('Başlık zorunludur ve 50 karakter geçmemelidir.', 'error')
                return render_template('admin/knowledge_base/upload.html')

            # File upload handling
            file = request.files.get('file')
            file_path = None

            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename

                    # DOĞRU UPLOAD KLASÖRÜ (Project içinde)
                    upload_dir = r'C:\Users\boran\OneDrive\Masaüstü\my_project4\Project\uploads\knowledge_base'
                    print(f"Kullanılan upload klasörü: {upload_dir}")

                    # Ensure upload directory exists
                    os.makedirs(upload_dir, exist_ok=True)

                    # Full file path
                    full_file_path = os.path.join(upload_dir, filename)
                    print(f"Dosya kaydedilecek yer: {full_file_path}")

                    # Save file
                    file.save(full_file_path)
                    print(f"Dosya kaydedildi: {os.path.exists(full_file_path)}")

                    # Store relative path in database (from Project root)
                    file_path = os.path.join('uploads', 'knowledge_base', filename).replace('\\', '/')
                    print(f"Veritabanına kaydedilecek yol: {file_path}")

                else:
                    flash('Desteklenmeyen dosya formatı!', 'error')
                    return render_template('admin/knowledge_base/upload.html')

            # Create new document
            new_document = KnowledgeBase(
                title=title,
                description=description if description else None,
                category=category if category else None,
                department=department if department else None,
                file_path=file_path,
                uploaded_by=current_user.employee_id
            )

            db.session.add(new_document)
            db.session.commit()

            # Log action
            log_action(current_user.employee_id, 'add', 'knowledge_base', new_document.document_id,
                       f'Doküman yüklendi: {title}')

            flash(f'Doküman "{title}" başarıyla yüklendi!', 'success')
            return redirect(url_for('main.admin_knowledge_base'))

        except Exception as e:
            db.session.rollback()
            print(f"Upload hatası: {e}")
            flash(f'Hata oluştu: {str(e)}', 'error')

    return render_template('admin/knowledge_base/upload.html')


# Preview ve download route'larını da güncelleyin:
@main.route('/admin/knowledge-base/preview/<int:document_id>')
@login_required
def admin_preview_document(document_id):
    if current_user.role not in ['admin', 'manager', 'user']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    document = KnowledgeBase.query.get_or_404(document_id)

    if not document.file_path:
        flash('Dosya yolu bulunamadı!', 'error')
        return redirect(url_for('main.admin_knowledge_base'))

    # Mutlak dosya yolu oluştur
    if os.path.isabs(document.file_path):
        file_path = document.file_path
    else:
        # Göreceli yolsa, project root ile birleştir
        project_root = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_root, document.file_path.replace('/', os.sep))

    file_path = os.path.normpath(file_path)

    print(f"Preview - Aranan dosya: {file_path}")
    print(f"Preview - Dosya var mı: {os.path.exists(file_path)}")

    if not os.path.exists(file_path):
        flash(f'Dosya bulunamadı: {file_path}', 'error')
        return redirect(url_for('main.admin_knowledge_base'))

    log_action(current_user.employee_id, 'preview', 'knowledge_base', document.document_id,
               f'Doküman önizlendi: {document.title}')

    return send_file(file_path, as_attachment=False)


@main.route('/admin/knowledge-base/view/<int:document_id>')
@login_required
def admin_view_document(document_id):
    if current_user.role not in ['admin', 'manager', 'user']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    document = KnowledgeBase.query.get_or_404(document_id)

    # Log view action
    log_action(current_user.employee_id, 'view', 'knowledge_base', document.document_id,
               f'Doküman görüntülendi: {document.title}')

    return render_template('admin/knowledge_base/view.html', document=document)


@main.route('/admin/knowledge-base/download/<int:document_id>')
@login_required
def admin_download_document(document_id):
    if current_user.role not in ['admin', 'manager', 'user']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    document = KnowledgeBase.query.get_or_404(document_id)

    if not document.file_path:
        flash('Dosya yolu bulunamadı!', 'error')
        return redirect(url_for('main.admin_knowledge_base'))

    # Mutlak dosya yolu oluştur
    if os.path.isabs(document.file_path):
        file_path = document.file_path
    else:
        # Göreceli yolsa, project root ile birleştir
        project_root = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_root, document.file_path.replace('/', os.sep))

    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        flash(f'Dosya bulunamadı: {file_path}', 'error')
        return redirect(url_for('main.admin_knowledge_base'))

    log_action(current_user.employee_id, 'download', 'knowledge_base', document.document_id,
               f'Doküman indirildi: {document.title}')

    return send_file(file_path, as_attachment=True)


@main.route('/admin/knowledge-base/edit/<int:document_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_document(document_id):
    if current_user.role not in ['admin', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    document = KnowledgeBase.query.get_or_404(document_id)

    if request.method == 'POST':
        try:
            document.title = request.form.get('title', '').strip()
            document.description = request.form.get('description', '').strip() or None
            document.category = request.form.get('category', '').strip() or None
            document.department = request.form.get('department', '').strip() or None

            # Handle file replacement
            file = request.files.get('file')
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Delete old file if exists
                    if document.file_path and os.path.exists(document.file_path):
                        os.remove(document.file_path)

                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename

                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    document.file_path = file_path
                else:
                    flash('Desteklenmeyen dosya formatı!', 'error')
                    return render_template('admin/knowledge_base/edit.html', document=document)

            db.session.commit()

            # Log action
            log_action(current_user.employee_id, 'edit', 'knowledge_base', document.document_id,
                       f'Doküman güncellendi: {document.title}')

            flash(f'Doküman "{document.title}" başarıyla güncellendi!', 'success')
            return redirect(url_for('main.admin_knowledge_base'))

        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'error')

    return render_template('admin/knowledge_base/edit.html', document=document)


@main.route('/admin/knowledge-base/delete/<int:document_id>', methods=['GET', 'POST'])
@login_required
def admin_delete_document(document_id):
    if current_user.role != 'admin':
        flash('Bu işlem için yetkiniz yok!', 'danger')
        return redirect(url_for('main.admin_knowledge_base'))

    # GET ile confirm parametresi kontrolü
    if request.method == 'GET' and request.args.get('confirm') == 'true':
        try:
            document = KnowledgeBase.query.get_or_404(document_id)
            document_title = document.title

            # Fiziksel dosyayı sil
            if document.file_path:
                project_root = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(project_root, document.file_path.replace('/', os.sep))
                file_path = os.path.normpath(file_path)

                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Dosya silindi: {file_path}")

            # Veritabanından sil
            db.session.delete(document)
            db.session.commit()

            flash(f'Doküman "{document_title}" başarıyla silindi!', 'success')

        except Exception as e:
            db.session.rollback()
            print(f"Silme hatası: {e}")
            flash(f'Silme işlemi sırasında hata oluştu: {str(e)}', 'error')

    return redirect(url_for('main.admin_knowledge_base'))
# Bu route'u routes.py dosyasına admin_download_document'in altına ekleyin




# ===========================
# LOGS ROUTES
# ===========================
@main.route('/admin/logs')
@login_required
def admin_logs():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Filtering parameters
    action_filter = request.args.get('action', '')
    table_filter = request.args.get('table', '')
    user_filter = request.args.get('user', '')
    date_filter = request.args.get('date', '')

    # Log this view action
    log_user_action(current_user.employee_id, 'view', 'logs', None,
                    'Sistem logları görüntülendi')

    # Base query with employee join
    query = Logs.query.outerjoin(Employee, Logs.user_id == Employee.employee_id)

    # Apply filters
    if action_filter:
        query = query.filter(Logs.action_type == action_filter)

    if table_filter:
        query = query.filter(Logs.target_table == table_filter)

    if user_filter:
        try:
            query = query.filter(Logs.user_id == int(user_filter))
        except ValueError:
            flash('Geçersiz kullanıcı ID!', 'warning')

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Logs.action_time) == filter_date)
        except ValueError:
            flash('Geçersiz tarih formatı!', 'warning')

    # Get logs ordered by time (most recent first)
    logs = query.order_by(Logs.action_time.desc()).limit(500).all()

    # Get unique values for filter dropdowns
    actions = db.session.query(Logs.action_type.distinct()).filter(
        Logs.action_type.isnot(None)
    ).all()
    actions = sorted([action[0] for action in actions if action[0]])

    tables = db.session.query(Logs.target_table.distinct()).filter(
        Logs.target_table.isnot(None)
    ).all()
    tables = sorted([table[0] for table in tables if table[0]])

    # Get all users who have log entries
    users = db.session.query(Employee).join(Logs).distinct().order_by(
        Employee.name, Employee.surname
    ).all()

    return render_template('admin/knowledge_base/system_logs.html',
                           logs=logs,
                           actions=actions,
                           tables=tables,
                           users=users,
                           action_filter=action_filter,
                           table_filter=table_filter,
                           user_filter=user_filter,
                           date_filter=date_filter)


@main.route('/admin/logs/export')
@login_required
def admin_logs_export():
    """Export log data"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Get export format from query parameter
        export_format = request.args.get('format', 'csv')

        # Apply same filters as main logs page
        action_filter = request.args.get('action', '')
        table_filter = request.args.get('table', '')
        user_filter = request.args.get('user', '')
        date_filter = request.args.get('date', '')

        query = Logs.query.outerjoin(Employee, Logs.user_id == Employee.employee_id)

        if action_filter:
            query = query.filter(Logs.action_type == action_filter)
        if table_filter:
            query = query.filter(Logs.target_table == table_filter)
        if user_filter:
            query = query.filter(Logs.user_id == int(user_filter))
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Logs.action_time) == filter_date)

        logs = query.order_by(Logs.action_time.desc()).all()

        # Log the export action
        log_user_action(current_user.employee_id, 'export', 'logs', None,
                        f'Sistem logları {export_format.upper()} formatında export edildi ({len(logs)} kayıt)')

        if export_format == 'json':
            return jsonify({
                'logs': [log.to_dict() for log in logs],
                'total': len(logs),
                'exported_at': datetime.now().isoformat()
            })
        else:
            # For CSV export, you can implement CSV generation here
            return jsonify({
                'status': 'success',
                'message': f'{len(logs)} log kaydı {export_format.upper()} formatında hazırlandı',
                'count': len(logs)
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Export hatası: {str(e)}'
        }), 500


@main.route('/admin/logs/statistics')
@login_required
def admin_logs_statistics():
    """Get log statistics"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Get date range for statistics
        days = request.args.get('days', 30, type=int)
        date_from = datetime.now() - timedelta(days=days)

        # Total counts
        total_logs = Logs.query.count()
        recent_logs = Logs.query.filter(Logs.action_time >= date_from).count()

        # Action type statistics
        action_stats = db.session.query(
            Logs.action_type,
            db.func.count(Logs.log_id).label('count')
        ).filter(
            Logs.action_time >= date_from
        ).group_by(Logs.action_type).all()

        # Table statistics
        table_stats = db.session.query(
            Logs.target_table,
            db.func.count(Logs.log_id).label('count')
        ).filter(
            Logs.action_time >= date_from,
            Logs.target_table.isnot(None)
        ).group_by(Logs.target_table).all()

        # User activity statistics
        user_stats = db.session.query(
            Employee.name,
            Employee.surname,
            Employee.role,
            db.func.count(Logs.log_id).label('count')
        ).join(Logs, Employee.employee_id == Logs.user_id) \
            .filter(Logs.action_time >= date_from) \
            .group_by(Employee.employee_id, Employee.name, Employee.surname, Employee.role) \
            .order_by(db.func.count(Logs.log_id).desc()).limit(10).all()

        # Recent activity
        recent_activity = Logs.query.outerjoin(Employee) \
            .order_by(Logs.action_time.desc()) \
            .limit(10).all()

        stats = {
            'total_logs': total_logs,
            'recent_logs': recent_logs,
            'date_range_days': days,
            'actions': {action: count for action, count in action_stats},
            'tables': {table: count for table, count in table_stats if table},
            'top_users': [
                {
                    'name': f"{name} {surname}",
                    'role': role,
                    'count': count
                } for name, surname, role, count in user_stats
            ],
            'recent_activity': [
                {
                    'time': log.action_time.strftime('%H:%M'),
                    'date': log.action_time.strftime('%d.%m.%Y'),
                    'user': f"{log.employee.name} {log.employee.surname}" if log.employee else "System",
                    'action': Logs.get_action_display_name(log.action_type),
                    'table': Logs.get_table_display_name(log.target_table),
                    'description': log.description
                } for log in recent_activity
            ]
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': f'İstatistik hatası: {str(e)}'}), 500


@main.route('/admin/logs/clear', methods=['POST'])
@login_required
def admin_logs_clear():
    """Clear old logs"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Get days parameter (default 90 days)
        days = request.json.get('days', 90) if request.is_json else 90
        cutoff_date = datetime.now() - timedelta(days=days)

        # Count logs to be deleted
        old_logs_query = Logs.query.filter(Logs.action_time < cutoff_date)
        count = old_logs_query.count()

        # Delete old logs
        old_logs_query.delete()

        # Log this action
        log_user_action(current_user.employee_id, 'delete', 'logs', None,
                        f'{count} adet {days} günden eski log kaydı temizlendi')

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'{count} adet eski log kaydı silindi',
            'deleted_count': count,
            'cutoff_days': days
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Log temizleme hatası: {str(e)}'
        }), 500
# ===========================
# HELPER FUNCTIONS
# ===========================

def log_user_action(user_id, action_type, target_table=None, target_id=None, description=None):
    """
    Log user action according to actual table structure
    """
    try:
        new_log = Logs(
            user_id=user_id,
            action_type=action_type,
            target_table=target_table,
            target_id=target_id,
            description=description,
            action_time=datetime.now()
        )

        db.session.add(new_log)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Log kaydetme hatası: {e}")
        return False

def log_action(user_id, action_type, target_table=None, target_id=None, description=None):
    """Backward compatibility wrapper"""
    return log_user_action(user_id, action_type, target_table, target_id, description)


def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        stats = {
            'total_documents': KnowledgeBase.query.count(),
            'recent_uploads': KnowledgeBase.query.filter(
                KnowledgeBase.upload_date >= datetime.now() - timedelta(days=7)
            ).count()
        }

        # Category stats
        categories = db.session.query(
            KnowledgeBase.category,
            db.func.count(KnowledgeBase.document_id)
        ).group_by(KnowledgeBase.category).all()
        stats['by_category'] = {cat: count for cat, count in categories if cat}

        # Department stats
        departments = db.session.query(
            KnowledgeBase.department,
            db.func.count(KnowledgeBase.document_id)
        ).group_by(KnowledgeBase.department).all()
        stats['by_department'] = {dept: count for dept, count in departments if dept}

        return stats
    except Exception as e:
        print(f"Knowledge base stats error: {e}")
        return {'total_documents': 0, 'recent_uploads': 0, 'by_category': {}, 'by_department': {}}


# routes.py dosyanızın sonuna bu route'ları ekleyin:

import subprocess
import requests
import threading
import time
import os
import signal
import json
import sys
import socket
from datetime import datetime

# Global değişkenler
dash_process = None
DASH_PROCESS_FILE = 'dash_process.json'


def save_dash_process_info(pid, start_time):
    """Dash process bilgilerini kaydet"""
    try:
        with open(DASH_PROCESS_FILE, 'w') as f:
            json.dump({
                'pid': pid,
                'start_time': start_time,
                'status': 'running'
            }, f)
    except Exception as e:
        print(f"Process info kaydetme hatası: {e}")


def load_dash_process_info():
    """Dash process bilgilerini yükle"""
    try:
        if os.path.exists(DASH_PROCESS_FILE):
            with open(DASH_PROCESS_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception:
        return None


def clear_dash_process_info():
    """Dash process bilgilerini temizle"""
    try:
        if os.path.exists(DASH_PROCESS_FILE):
            os.remove(DASH_PROCESS_FILE)
    except Exception:
        pass


def is_dash_running():
    """Dash sunucusunun çalışıp çalışmadığını kontrol et"""
    try:
        response = requests.get('http://localhost:8050', timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def is_port_in_use(port):
    """Port kullanımda mı kontrol et"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0



@main.route('/admin/analytics-dashboard')
@login_required
def admin_analytics_dashboard():
    """Analytics Dashboard with REAL data from database"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    from datetime import timedelta
    from sqlalchemy import func

    try:
        # REAL Equipment Statistics from actual database
        equipment_stats = {
            'total': Equipment.query.count(),
            'in_use': Equipment.query.filter_by(status='in_use').count(),
            'in_stock': Equipment.query.filter_by(status='in_stock').count(),
            'under_repair': Equipment.query.filter_by(status='under_repair').count(),
            'scrap': Equipment.query.filter_by(status='scrap').count()
        }

        # REAL License Statistics from actual database
        license_stats = {
            'total': SoftwareLicense.query.count(),
            'active': SoftwareLicense.query.filter_by(status='active').count(),
            'expired': SoftwareLicense.query.filter_by(status='expired').count(),
            'cancelled': SoftwareLicense.query.filter_by(status='cancelled').count()
        }

        # Calculate REAL expiring soon licenses (30 days)
        expiring_soon = SoftwareLicense.query.filter(
            SoftwareLicense.expiration_date.isnot(None),
            SoftwareLicense.expiration_date <= datetime.now().date() + timedelta(days=30),
            SoftwareLicense.expiration_date >= datetime.now().date(),
            SoftwareLicense.status == 'active'
        ).count()
        license_stats['expiring_soon'] = expiring_soon

        # REAL Employee Statistics
        employee_stats = {
            'total': Employee.query.count(),
            'admin': Employee.query.filter_by(role='admin').count(),
            'manager': Employee.query.filter_by(role='manager').count(),
            'user': Employee.query.filter_by(role='user').count()
        }

        # REAL Equipment Categories (only if equipment exists)
        equipment_categories = []
        if equipment_stats['total'] > 0:
            equipment_categories = db.session.query(
                Equipment.category,
                func.count(Equipment.equipment_id)
            ).group_by(Equipment.category).order_by(func.count(Equipment.equipment_id).desc()).all()

        # REAL Department Statistics (only if data exists)
        department_stats = []
        if equipment_stats['total'] > 0:
            department_query = db.session.query(
                func.coalesce(Employee.department, 'Atanmamış').label('department'),
                func.count(Equipment.equipment_id).label('count')
            ).select_from(Equipment) \
                .outerjoin(Employee, Equipment.assigned_to == Employee.employee_id) \
                .group_by(Employee.department) \
                .order_by(func.count(Equipment.equipment_id).desc())

            department_stats = department_query.all()

        # REAL License Vendor Statistics (only if licenses exist)
        license_vendors = []
        if license_stats['total'] > 0:
            license_vendors = db.session.query(
                func.coalesce(SoftwareLicense.vendor, 'Belirtilmemiş').label('vendor'),
                func.count(SoftwareLicense.license_id)
            ).group_by(SoftwareLicense.vendor) \
                .order_by(func.count(SoftwareLicense.license_id).desc()).all()

        # REAL Expiring Licenses with calculated days left
        expiring_licenses = []
        if license_stats['total'] > 0:
            expiring_licenses = SoftwareLicense.query.filter(
                SoftwareLicense.expiration_date.isnot(None)
            ).order_by(SoftwareLicense.expiration_date.asc()).limit(10).all()

            # Calculate days left for each license
            for license in expiring_licenses:
                if license.expiration_date:
                    days_left = (license.expiration_date - datetime.now().date()).days
                    license.days_left = days_left
                else:
                    license.days_left = None

        # REAL Activity Logs (last 30 days) - only if logs exist
        recent_logs = []
        logs_count = Logs.query.count()
        if logs_count > 0:
            recent_logs = Logs.query.filter(
                Logs.action_time >= datetime.now() - timedelta(days=30)
            ).order_by(Logs.action_time.desc()).limit(10).all()

        # REAL Activity by day (for timeline chart)
        activity_by_day = []
        if logs_count > 0:
            activity_by_day = db.session.query(
                func.date(Logs.action_time).label('date'),
                func.count(Logs.log_id).label('count')
            ).filter(
                Logs.action_time >= datetime.now() - timedelta(days=30)
            ).group_by(func.date(Logs.action_time)) \
                .order_by(func.date(Logs.action_time)).all()

        # System Health Metrics (simulated but realistic)
        system_health = {
            'database_health': 95 if equipment_stats['total'] > 0 or license_stats['total'] > 0 else 85,
            'storage_usage': min(70, max(30, (equipment_stats['total'] + license_stats['total']) * 5)),
            'network_status': 88,
            'security_score': 92 if employee_stats['admin'] > 0 else 75,
            'overall_status': 'healthy' if equipment_stats['total'] + license_stats['total'] > 0 else 'warning'
        }

        # REAL Risk Assessment based on actual data
        risk_factors = []

        # Check for expired licenses
        if license_stats['expired'] > 0:
            risk_factors.append({
                'type': 'expired_licenses',
                'severity': 'high',
                'count': license_stats['expired'],
                'message': f"{license_stats['expired']} lisansın süresi dolmuş"
            })

        # Check for equipment under repair
        if equipment_stats['under_repair'] > 0:
            risk_factors.append({
                'type': 'equipment_repair',
                'severity': 'medium',
                'count': equipment_stats['under_repair'],
                'message': f"{equipment_stats['under_repair']} ekipman tamirde"
            })

        # Check for expiring licenses
        if license_stats['expiring_soon'] > 0:
            risk_factors.append({
                'type': 'expiring_licenses',
                'severity': 'medium',
                'count': license_stats['expiring_soon'],
                'message': f"{license_stats['expiring_soon']} lisansın süresi 30 gün içinde dolacak"
            })

        # Add warning if no data exists
        if equipment_stats['total'] == 0 and license_stats['total'] == 0:
            risk_factors.append({
                'type': 'no_data',
                'severity': 'low',
                'count': 0,
                'message': 'Henüz ekipman veya lisans verisi bulunmuyor'
            })

        print(
            f"📊 Analytics data loaded: {equipment_stats['total']} equipment, {license_stats['total']} licenses, {employee_stats['total']} employees")

        return render_template('admin/analytics_dashboard.html',
                               equipment_stats=equipment_stats,
                               license_stats=license_stats,
                               employee_stats=employee_stats,
                               equipment_categories=equipment_categories,
                               department_stats=department_stats,
                               license_vendors=license_vendors,
                               expiring_licenses=expiring_licenses,
                               recent_logs=recent_logs,
                               activity_by_day=activity_by_day,
                               system_health=system_health,
                               risk_factors=risk_factors)

    except Exception as e:
        flash(f'Analytics dashboard yüklenirken hata oluştu: {str(e)}', 'error')
        print(f"Analytics dashboard error: {e}")

        # Fallback with ZERO data to show actual state
        return render_template('admin/analytics_dashboard.html',
                               equipment_stats={'total': 0, 'in_use': 0, 'in_stock': 0, 'under_repair': 0, 'scrap': 0},
                               license_stats={'total': 0, 'active': 0, 'expired': 0, 'cancelled': 0,
                                              'expiring_soon': 0},
                               employee_stats={'total': 0, 'admin': 0, 'manager': 0, 'user': 0},
                               equipment_categories=[],
                               department_stats=[],
                               license_vendors=[],
                               expiring_licenses=[],
                               recent_logs=[],
                               activity_by_day=[],
                               system_health={'database_health': 50, 'storage_usage': 20, 'network_status': 70,
                                              'security_score': 60},
                               risk_factors=[{
                                   'type': 'no_data',
                                   'severity': 'info',
                                   'count': 0,
                                   'message': 'Veri yüklenemedi veya henüz veri bulunmuyor'
                               }])


@main.route('/admin/check-dash-status')
@login_required
def admin_check_dash_status():
    """Dash sunucusunun durumunu kontrol et"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        if is_dash_running():
            # Process bilgilerini al
            process_info = load_dash_process_info()
            uptime = None

            if process_info:
                try:
                    start_time = datetime.fromisoformat(process_info['start_time'])
                    uptime_seconds = (datetime.now() - start_time).total_seconds()

                    if uptime_seconds < 60:
                        uptime = f"{int(uptime_seconds)} saniye"
                    elif uptime_seconds < 3600:
                        uptime = f"{int(uptime_seconds / 60)} dakika"
                    else:
                        hours = int(uptime_seconds / 3600)
                        minutes = int((uptime_seconds % 3600) / 60)
                        uptime = f"{hours} saat {minutes} dakika"
                except Exception:
                    uptime = "Bilinmiyor"

            return jsonify({
                'status': 'running',
                'message': 'Dashboard çalışıyor',
                'uptime': uptime,
                'url': 'http://localhost:8050'
            })
        else:
            # Çalışmıyorsa process bilgilerini temizle
            clear_dash_process_info()
            return jsonify({
                'status': 'not_running',
                'message': 'Dashboard çalışmıyor'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Durum kontrolü hatası: {str(e)}'
        })


@main.route('/admin/start-dash-server', methods=['POST'])
@login_required
def admin_start_dash_server():
    """Dash sunucusunu başlat - Debug sürümü"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    global dash_process

    try:
        # Önce çalışıp çalışmadığını kontrol et
        if is_dash_running():
            return jsonify({
                'status': 'already_running',
                'message': 'Dashboard zaten çalışıyor'
            })

        # Dosya kontrolü
        dash_file_path = os.path.join(os.getcwd(), 'dash_dashboard.py')
        if not os.path.exists(dash_file_path):
            return jsonify({
                'status': 'error',
                'message': f'dash_dashboard.py dosyası bulunamadı. Aranan konum: {dash_file_path}'
            })

        # Python executable kontrolü
        python_executable = sys.executable
        if not os.path.exists(python_executable):
            python_executable = 'python'

        try:
            # Process'i başlat - Detaylı hata yakalama ile
            dash_process = subprocess.Popen([
                python_executable, dash_file_path
            ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                text=True
            )

            # Process bilgilerini kaydet
            start_time = datetime.now().isoformat()
            save_dash_process_info(dash_process.pid, start_time)

            print(f"✅ Dash process başlatıldı. PID: {dash_process.pid}")

            # Dash sunucusunun başlaması için bekle ve detaylı kontrol yap
            max_wait_time = 20  # 20 saniye maksimum bekleme
            wait_interval = 1  # 1 saniye aralıklarla kontrol

            for i in range(max_wait_time):
                time.sleep(wait_interval)

                # Process durumunu kontrol et
                poll_result = dash_process.poll()
                if poll_result is not None:
                    # Process durdu, hata mesajlarını al
                    try:
                        stdout, stderr = dash_process.communicate(timeout=2)
                        error_details = f"STDOUT: {stdout}\n\nSTDERR: {stderr}"
                        print(f"❌ Dash process durdu: {error_details}")
                    except subprocess.TimeoutExpired:
                        error_details = "Process durdu ama çıktı alınamadı"

                    clear_dash_process_info()
                    return jsonify({
                        'status': 'error',
                        'message': f'Dashboard process durdu (exit code: {poll_result})',
                        'details': error_details[:500] + '...' if len(error_details) > 500 else error_details
                    })

                # Dash sunucusuna bağlanmayı dene
                if is_dash_running():
                    log_user_action(current_user.employee_id, 'start', 'dashboard', None,
                                    'Analytics Dashboard başlatıldı')

                    print(f"✅ Dashboard başarıyla başlatıldı! ({i + 1} saniye beklendi)")

                    return jsonify({
                        'status': 'started',
                        'message': f'Dashboard başarıyla başlatıldı ({i + 1} saniye beklendi)',
                        'url': 'http://localhost:8050',
                        'pid': dash_process.pid
                    })

                print(f"⏳ Dash bekleniyor... {i + 1}/{max_wait_time}")

            # Timeout durumu
            poll_result = dash_process.poll()
            if poll_result is None:
                # Hala çalışıyor ama port'a cevap vermiyor
                print("⚠️ Dashboard process çalışıyor ama bağlantı yok")
                return jsonify({
                    'status': 'timeout',
                    'message': 'Dashboard process çalışıyor ama bağlantı kurulamıyor. Lütfen manuel kontrol edin: python dash_dashboard.py',
                    'suggestion': 'Port 8050 engellenmiş olabilir veya başka bir uygulama tarafından kullanılıyor olabilir.'
                })
            else:
                # Process durdu
                try:
                    stdout, stderr = dash_process.communicate()
                    error_details = f"Exit Code: {poll_result}\nSTDOUT: {stdout}\nSTDERR: {stderr}"
                    print(f"❌ Dashboard process beklerken durdu: {error_details}")
                except:
                    error_details = f"Process durdu (exit code: {poll_result}) ama detaylar alınamadı"

                clear_dash_process_info()
                return jsonify({
                    'status': 'error',
                    'message': 'Dashboard process beklerken durdu',
                    'details': error_details
                })

        except FileNotFoundError as e:
            return jsonify({
                'status': 'error',
                'message': f'Python yorumlayıcısı bulunamadı: {e}',
                'suggestion': 'Python\'un PATH\'de olduğundan emin olun'
            })
        except Exception as e:
            clear_dash_process_info()
            return jsonify({
                'status': 'error',
                'message': f'Process başlatma hatası: {str(e)}',
                'type': type(e).__name__
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Genel hata: {str(e)}',
            'type': type(e).__name__
        })


@main.route('/admin/stop-dash-server', methods=['POST'])
@login_required
def admin_stop_dash_server():
    """Dash sunucusunu durdur"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    global dash_process

    try:
        # Process bilgilerini al
        process_info = load_dash_process_info()

        if process_info and 'pid' in process_info:
            pid = process_info['pid']

            try:
                # Process'i nazikçe durdur
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)

                # Hala çalışıyorsa zorla durdur
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process zaten durmuş

            except ProcessLookupError:
                pass  # Process zaten yok
            except PermissionError:
                return jsonify({
                    'status': 'error',
                    'message': 'Process durdurulamadı (yetki hatası)'
                })

        # Global process'i temizle
        if dash_process:
            try:
                dash_process.terminate()
                dash_process = None
            except Exception:
                pass

        # Process bilgilerini temizle
        clear_dash_process_info()

        # Log kaydı
        log_user_action(current_user.employee_id, 'stop', 'dashboard', None,
                        'Analytics Dashboard durduruldu')

        return jsonify({
            'status': 'stopped',
            'message': 'Dashboard başarıyla durduruldu'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Durdurma hatası: {str(e)}'
        })


# Debug için environment kontrolü
@main.route('/admin/debug-dash-environment')
@login_required
def admin_debug_dash_environment():
    """Dashboard environment'ını debug et"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    import platform

    debug_info = {
        'python_version': platform.python_version(),
        'python_executable': sys.executable,
        'current_directory': os.getcwd(),
        'dash_file_exists': os.path.exists('dash_dashboard.py'),
        'dash_file_path': os.path.abspath('dash_dashboard.py') if os.path.exists('dash_dashboard.py') else 'Not found',
        'port_8050_available': not is_port_in_use(8050),
        'port_8051_available': not is_port_in_use(8051),
        'required_packages': {},
        'database_info': {}
    }

    # Gerekli paketleri kontrol et
    required_packages = ['dash', 'plotly', 'pandas', 'psycopg2', 'sqlalchemy', 'requests']
    for package in required_packages:
        try:
            __import__(package)
            debug_info['required_packages'][package] = '✅ Yüklü'
        except ImportError:
            debug_info['required_packages'][package] = '❌ Yüklü değil'

    # Database connection test
    try:
        from Project import db
        db.session.execute('SELECT 1')
        debug_info['database_info']['connection'] = '✅ Bağlantı OK'

        # Tablo kontrolü
        tables = ['employee', 'equipment', 'software_license', 'logs']
        for table in tables:
            try:
                result = db.session.execute(f'SELECT COUNT(*) FROM {table}')
                count = result.fetchone()[0]
                debug_info['database_info'][f'{table}_count'] = f'✅ {count} kayıt'
            except Exception as e:
                debug_info['database_info'][f'{table}_count'] = f'❌ Hata: {str(e)}'
    except Exception as e:
        debug_info['database_info']['connection'] = f'❌ Hata: {str(e)}'

    # Process durumu
    debug_info['current_dash_status'] = 'Çalışıyor' if is_dash_running() else 'Durmuş'
    debug_info['process_info'] = load_dash_process_info()

    return jsonify(debug_info)


# Uygulama kapatılırken dash process'ini temizle
import atexit


def cleanup_dash_process():
    """Uygulama kapatılırken dash process'ini temizle"""
    global dash_process

    try:
        # Global process'i temizle
        if dash_process and dash_process.poll() is None:
            dash_process.terminate()
            time.sleep(1)
            if dash_process.poll() is None:
                dash_process.kill()

        # Kaydedilen process bilgilerini kontrol et ve temizle
        process_info = load_dash_process_info()
        if process_info and 'pid' in process_info:
            try:
                os.kill(process_info['pid'], signal.SIGTERM)
                time.sleep(1)
                try:
                    os.kill(process_info['pid'], signal.SIGKILL)
                except ProcessLookupError:
                    pass
            except (ProcessLookupError, PermissionError):
                pass

        clear_dash_process_info()

    except Exception as e:
        print(f"Cleanup hatası: {e}")

# ===========================
# SETTINGS ROUTES
# ===========================

@main.route('/admin/settings')
@login_required
def admin_settings():
    """Admin ayarlar sayfası"""
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    log_user_action(current_user.employee_id, 'view', 'settings', None,
                    'Admin ayarlar sayfası görüntülendi')

    # Admin dashboard URL'ini template'e gönder
    dashboard_url = url_for('main.admin_dashboard')  # Bu '/admin' olarak resolve edilecek

    return render_template('admin/settings.html', dashboard_url=dashboard_url)


@main.route('/manager/settings')
@login_required
def manager_settings():
    """Manager ayarlar sayfası"""
    if current_user.role != 'manager':
        flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
        return redirect(url_for('main.index'))

    # Log kaydı
    log_user_action(current_user.employee_id, 'view', 'settings', None,
                    'Manager ayarlar sayfası görüntülendi')

    return render_template('manager/settings.html')

@main.route('/api/settings/save', methods=['POST'])
@login_required
def api_save_settings():
    """Kullanıcı ayarlarını kaydet - API endpoint"""
    try:
        settings_data = request.get_json()

        if not settings_data:
            return jsonify({'success': False, 'error': 'Veri gönderilmedi'}), 400

        # Ayarları session'a kaydet (isterseniz database'e de kaydedebilirsiniz)
        session['user_settings'] = {
            'theme': settings_data.get('theme', 'light'),
            'language': settings_data.get('language', 'tr'),
            'notifications': settings_data.get('notifications', True),
            'animations': settings_data.get('animations', True),
            'autosave': settings_data.get('autosave', True)
        }

        # Log kaydı
        log_user_action(current_user.employee_id, 'edit', 'settings', None,
                        f'Kullanıcı ayarları güncellendi: {current_user.name} {current_user.surname}')

        return jsonify({
            'success': True,
            'message': 'Ayarlar başarıyla kaydedildi'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Kaydetme hatası: {str(e)}'
        }), 500


@main.route('/api/settings/load')
@login_required
def api_load_settings():
    """Kullanıcı ayarlarını yükle - API endpoint"""
    try:
        # Session'dan ayarları al
        user_settings = session.get('user_settings', {
            'theme': 'light',
            'language': 'tr',
            'notifications': True,
            'animations': True,
            'autosave': True
        })

        return jsonify({
            'success': True,
            'settings': user_settings
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Yükleme hatası: {str(e)}'
        }), 500

@main.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('user/user_dashboard.html')  # user/ ekle

@main.route('/user/employees')
@login_required
def user_employees():
    if current_user.role != 'user':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('user/user_employees.html')  # user/ ekle

@main.route('/user/inventory')
@login_required
def user_inventory():
    if current_user.role != 'user':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('user/user_inventory.html')  # user/ ekle

@main.route('/user/knowledge-base')
@login_required
def user_knowledge_base():
    if current_user.role != 'user':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('user/user_knowledge_base.html')  # user/ ekle

@main.route('/user/settings')
@login_required
def user_settings():
    if current_user.role != 'user':
        return redirect(url_for('main.admin_dashboard'))
    return render_template('user/user_settings.html')  # user/ ekle
