from Project import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask import request
import os


class Employee(UserMixin, db.Model):
    __tablename__ = 'employee'

    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(50))
    role = db.Column(db.String(10), nullable=False)
    data_joined = db.Column(db.DateTime, server_default=db.func.now())

    # İlişkiler - envanter modülleri için
    assigned_equipment = db.relationship('Equipment', backref='assigned_employee', lazy=True)
    assigned_licenses = db.relationship('SoftwareLicense', backref='assigned_employee', lazy=True)
    uploaded_documents = db.relationship('KnowledgeBase', backref='uploader', lazy=True)
    action_logs = db.relationship('Logs', backref='user', lazy=True)

    def get_id(self):
        return str(self.employee_id)

    def __repr__(self):
        return f'<Employee {self.name} {self.surname}>'

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"

    @property
    def initials(self):
        return f"{self.name[0]}{self.surname[0]}"

    def get_equipment_count(self):
        """Çalışana atanan ekipman sayısı"""
        return len(self.assigned_equipment)

    def get_license_count(self):
        """Çalışana atanan lisans sayısı"""
        return len(self.assigned_licenses)

    def get_uploaded_documents_count(self):
        """Çalışanın yüklediği doküman sayısı"""
        return len(self.uploaded_documents)


class Equipment(db.Model):
    __tablename__ = 'equipment'

    equipment_id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(30), nullable=False)  # Server, Switch, Camera, PC, etc.
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial_number = db.Column(db.String(50), unique=True)
    purchase_date = db.Column(db.Date)
    status = db.Column(db.String(15), nullable=False)  # in_stock, in_use, under_repair, scrap
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=True)
    location = db.Column(db.String(50))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    licenses = db.relationship('SoftwareLicense', backref='installed_equipment', lazy=True)

    def __repr__(self):
        return f'<Equipment {self.equipment_name}>'

    @property
    def status_display(self):
        """Status değerlerini Türkçe göster"""
        status_map = {
            'in_stock': 'Stokta',
            'in_use': 'Kullanımda',
            'under_repair': 'Tamirde',
            'scrap': 'Hurdaya Çıkarıldı'
        }
        return status_map.get(self.status, self.status)

    @property
    def status_color(self):
        """Status için renk kodu"""
        color_map = {
            'in_stock': '#ffc107',  # sarı
            'in_use': '#28a745',  # yeşil
            'under_repair': '#dc3545',  # kırmızı
            'scrap': '#6c757d'  # gri
        }
        return color_map.get(self.status, '#6c757d')

    @property
    def category_display(self):
        """Kategori değerlerini Türkçe göster"""
        category_map = {
            'Server': 'Sunucu',
            'Switch': 'Ağ Anahtarı',
            'Camera': 'Kamera',
            'PC': 'Bilgisayar',
            'Laptop': 'Laptop',
            'Monitor': 'Monitör',
            'Storage': 'Depolama',
            'Network': 'Ağ Ekipmanı',
            'Audio': 'Ses Ekipmanı',
            'Video': 'Video Ekipmanı',
            'Printer': 'Yazıcı',
            'Scanner': 'Tarayıcı',
            'Router': 'Yönlendirici',
            'Firewall': 'Güvenlik Duvarı',
            'UPS': 'Kesintisiz Güç Kaynağı',
            'Other': 'Diğer'
        }
        return category_map.get(self.category, self.category)

    @property
    def category_icon(self):
        """Kategori için ikon"""
        icon_map = {
            'Server': 'fas fa-server',
            'Switch': 'fas fa-network-wired',
            'Camera': 'fas fa-video',
            'PC': 'fas fa-desktop',
            'Laptop': 'fas fa-laptop',
            'Monitor': 'fas fa-tv',
            'Storage': 'fas fa-hdd',
            'Network': 'fas fa-wifi',
            'Audio': 'fas fa-volume-up',
            'Video': 'fas fa-film',
            'Printer': 'fas fa-print',
            'Scanner': 'fas fa-scanner',
            'Router': 'fas fa-route',
            'Firewall': 'fas fa-shield-alt',
            'UPS': 'fas fa-battery-full',
            'Other': 'fas fa-cube'
        }
        return icon_map.get(self.category, 'fas fa-cube')

    def get_age_days(self):
        """Ekipmanın yaşını gün olarak hesapla"""
        if self.purchase_date:
            return (datetime.now().date() - self.purchase_date).days
        return None

    def get_age_display(self):
        """Yaşı okunabilir formatta göster"""
        days = self.get_age_days()
        if days is None:
            return 'Bilinmiyor'

        if days < 30:
            return f'{days} gün'
        elif days < 365:
            months = days // 30
            return f'{months} ay'
        else:
            years = days // 365
            months = (days % 365) // 30
            if months > 0:
                return f'{years} yıl {months} ay'
            return f'{years} yıl'

    def is_warranty_expired(self, warranty_years=3):
        """Garanti süresi dolmuş mu? (Varsayılan 3 yıl)"""
        if self.purchase_date:
            warranty_end = datetime(
                self.purchase_date.year + warranty_years,
                self.purchase_date.month,
                self.purchase_date.day
            ).date()
            return datetime.now().date() > warranty_end
        return None

    def get_warranty_status(self, warranty_years=3):
        """Garanti durumunu string olarak döndür"""
        warranty_expired = self.is_warranty_expired(warranty_years)
        if warranty_expired is None:
            return 'unknown'
        return 'expired' if warranty_expired else 'valid'

    def get_warranty_color(self, warranty_years=3):
        """Garanti durumu için renk"""
        status = self.get_warranty_status(warranty_years)
        if status == 'valid':
            return '#28a745'  # yeşil
        elif status == 'expired':
            return '#dc3545'  # kırmızı
        return '#6c757d'  # gri

    @property
    def assigned_to_display(self):
        """Atanan kişi bilgisi"""
        if self.assigned_employee:
            return f"{self.assigned_employee.name} {self.assigned_employee.surname}"
        return 'Atanmamış'


class SoftwareLicense(db.Model):
    __tablename__ = 'software_license'

    license_id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(50), nullable=False)
    license_key = db.Column(db.String(255), unique=True, nullable=False)
    version = db.Column(db.String(50))
    vendor = db.Column(db.String(50))  # Adobe, Microsoft, Vizrt, etc.
    expiration_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False)  # active, expired, cancelled
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SoftwareLicense {self.software_name}>'

    @property
    def status_display(self):
        """Status değerlerini Türkçe göster"""
        status_map = {
            'active': 'Aktif',
            'expired': 'Süresi Dolmuş',
            'cancelled': 'İptal Edilmiş'
        }
        return status_map.get(self.status, self.status)

    @property
    def status_color(self):
        """Status için renk kodu"""
        color_map = {
            'active': '#28a745',  # yeşil
            'expired': '#dc3545',  # kırmızı
            'cancelled': '#6c757d'  # gri
        }
        return color_map.get(self.status, '#6c757d')

    @property
    def days_until_expiry(self):
        """Süresi dolmasına kaç gün kaldığını hesapla"""
        if self.expiration_date:
            delta = self.expiration_date - datetime.now().date()
            return delta.days
        return None

    @property
    def is_expiring_soon(self, days=30):
        """30 gün içinde süresi dolacak mı?"""
        if self.expiration_date and self.status == 'active':
            days_left = self.days_until_expiry
            return days_left is not None and 0 <= days_left <= days
        return False

    @property
    def is_expired(self):
        """Lisansın süresi dolmuş mu?"""
        if self.expiration_date:
            return datetime.now().date() > self.expiration_date
        return False

    def get_expiry_status(self):
        """Süre durumunu string olarak döndür"""
        if self.is_expired:
            return 'expired'
        elif self.is_expiring_soon:
            return 'expiring_soon'
        else:
            return 'active'

    def get_expiry_color(self):
        """Süre durumu için renk"""
        status = self.get_expiry_status()
        if status == 'active':
            return '#28a745'  # yeşil
        elif status == 'expiring_soon':
            return '#ffc107'  # sarı
        else:
            return '#dc3545'  # kırmızı

    def get_vendor_icon_class(self):
        """Vendor'a göre CSS class döndür"""
        if not self.vendor:
            return 'other'

        vendor_lower = self.vendor.lower()
        if 'adobe' in vendor_lower:
            return 'adobe'
        elif 'microsoft' in vendor_lower:
            return 'microsoft'
        elif 'vizrt' in vendor_lower:
            return 'vizrt'
        elif 'avid' in vendor_lower:
            return 'avid'
        elif 'apple' in vendor_lower:
            return 'apple'
        elif 'google' in vendor_lower:
            return 'google'
        else:
            return 'other'

    @property
    def assigned_to_display(self):
        """Atanan kişi bilgisi"""
        if self.assigned_employee:
            return f"{self.assigned_employee.name} {self.assigned_employee.surname}"
        return 'Atanmamış'

    @property
    def equipment_display(self):
        """Kurulduğu ekipman bilgisi"""
        if self.installed_equipment:
            return self.installed_equipment.equipment_name
        return 'Belirtilmemiş'


class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'

    document_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Network, Storage, RAID, iNews
    file_path = db.Column(db.String(100))
    department = db.Column(db.String(50))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=True)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<KnowledgeBase {self.title}>'

    @property
    def file_extension(self):
        """Dosya uzantısını döndür"""
        if self.file_path:
            return self.file_path.split('.')[-1].lower()
        return None

    @property
    def file_icon(self):
        """Dosya tipine göre ikon döndür"""
        ext = self.file_extension
        if ext in ['pdf']:
            return 'fas fa-file-pdf'
        elif ext in ['doc', 'docx']:
            return 'fas fa-file-word'
        elif ext in ['xls', 'xlsx']:
            return 'fas fa-file-excel'
        elif ext in ['ppt', 'pptx']:
            return 'fas fa-file-powerpoint'
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'fas fa-file-image'
        elif ext in ['mp4', 'avi', 'mov']:
            return 'fas fa-file-video'
        elif ext in ['txt']:
            return 'fas fa-file-alt'
        else:
            return 'fas fa-file'

    @property
    def category_color(self):
        """Kategori rengini döndür"""
        color_map = {
            'Network': '#17a2b8',  # info blue
            'Storage': '#28a745',  # success green
            'RAID': '#ffc107',  # warning yellow
            'iNews': '#dc3545',  # danger red
            'Broadcast': '#6f42c1',  # purple
            'Technical': '#fd7e14',  # orange
            'Manual': '#20c997',  # teal
            'Other': '#6c757d'  # secondary gray
        }
        return color_map.get(self.category, '#6c757d')

    @property
    def upload_time_ago(self):
        """Yükleme zamanını göreceli olarak döndür"""
        if not self.upload_date:
            return 'Bilinmiyor'

        now = datetime.utcnow()
        diff = now - self.upload_date

        if diff.days > 0:
            return f"{diff.days} gün önce"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} saat önce"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} dakika önce"
        else:
            return "Az önce"

    def get_file_size(self):
        """Dosya boyutunu döndür (eğer mevcut ise)"""
        if self.file_path and os.path.exists(self.file_path):
            size = os.path.getsize(self.file_path)
            # Convert bytes to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return 'Bilinmiyor'

    @classmethod
    def get_categories(cls):
        """Mevcut kategorileri döndür"""
        categories = db.session.query(cls.category).distinct().filter(cls.category.isnot(None)).all()
        return [cat[0] for cat in categories if cat[0]]

    @classmethod
    def get_departments(cls):
        """Mevcut departmanları döndür"""
        departments = db.session.query(cls.department).distinct().filter(cls.department.isnot(None)).all()
        return [dept[0] for dept in departments if dept[0]]

    @classmethod
    def search_documents(cls, query, category=None, department=None):
        """Doküman arama fonksiyonu"""
        search_query = cls.query

        if query:
            search_query = search_query.filter(
                db.or_(
                    cls.title.ilike(f'%{query}%'),
                    cls.description.ilike(f'%{query}%')
                )
            )

        if category:
            search_query = search_query.filter(cls.category == category)

        if department:
            search_query = search_query.filter(cls.department == department)

        return search_query.order_by(cls.upload_date.desc()).all()


class Logs(db.Model):
    __tablename__ = 'logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id', ondelete='SET NULL'), nullable=True)
    action_type = db.Column(db.String(30), nullable=False)  # add, delete, view gibi
    target_table = db.Column(db.String(20), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    action_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Relationship
    employee = db.relationship('Employee', backref='logs', lazy='joined')

    def __repr__(self):
        return f'<Log {self.log_id}: {self.employee.name if self.employee else "System"} - {self.action_type}>'

    def to_dict(self):
        """Convert log to dictionary for API responses"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'user_name': f"{self.employee.name} {self.employee.surname}" if self.employee else "System",
            'user_role': self.employee.role if self.employee else None,
            'action_type': self.action_type,
            'target_table': self.target_table,
            'target_id': self.target_id,
            'description': self.description,
            'action_time': self.action_time.isoformat(),
            'action_time_formatted': self.action_time.strftime('%d.%m.%Y %H:%M:%S')
        }

    @staticmethod
    def get_action_display_name(action_type):
        """Get Turkish display name for action types"""
        action_names = {
            'add': 'Ekleme',
            'delete': 'Silme',
            'view': 'Görüntüleme',
            'update': 'Güncelleme',
            'login': 'Giriş',
            'logout': 'Çıkış',
            'assign': 'Atama',
            'unassign': 'Atama Kaldırma',
            'download': 'İndirme',
            'upload': 'Yükleme',
            'start': 'Başlatma',
            'stop': 'Durdurma',
            'export': 'Dışa Aktarma',
            'create': 'Oluşturma'
        }
        return action_names.get(action_type, action_type.title())

    @staticmethod
    def get_table_display_name(table_name):
        """Get Turkish display name for table names"""
        if not table_name:
            return 'Sistem'

        table_names = {
            'employee': 'Çalışanlar',
            'equipment': 'Donanım',
            'software_license': 'Lisanslar',
            'knowledge_base': 'Bilgi Bankası',
            'dashboard': 'Dashboard',
            'logs': 'Sistem Logları'
        }
        return table_names.get(table_name, table_name.title())


# Yardımcı fonksiyonlar
def log_user_action(user_id, action_type, target_table, target_id=None, description=None):
    """
    Log user action to database according to the actual table structure

    Args:
        user_id: ID of the user performing the action
        action_type: Type of action (add, delete, view, update, etc.)
        target_table: Name of the affected table/module (optional)
        target_id: ID of the affected record (optional)
        description: Human readable description (optional)
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

def log_action(user_id, action_type, target_table, target_id=None, description=None):
    """Backward compatibility wrapper"""
    return log_user_action(user_id, action_type, target_table, target_id, description)

def get_equipment_stats():
    """Ekipman istatistiklerini döndür"""
    try:
        stats = {
            'total': Equipment.query.count(),
            'in_use': Equipment.query.filter_by(status='in_use').count(),
            'in_stock': Equipment.query.filter_by(status='in_stock').count(),
            'under_repair': Equipment.query.filter_by(status='under_repair').count(),
            'scrap': Equipment.query.filter_by(status='scrap').count()
        }

        # Kategori bazlı istatistikler
        categories = db.session.query(Equipment.category, db.func.count(Equipment.equipment_id)).group_by(
            Equipment.category).all()
        stats['by_category'] = {cat: count for cat, count in categories}

        return stats
    except Exception as e:
        print(f"Ekipman istatistik hatası: {e}")
        return {'total': 0, 'in_use': 0, 'in_stock': 0, 'under_repair': 0, 'scrap': 0, 'by_category': {}}


def get_license_stats():
    """Lisans istatistiklerini döndür"""
    try:
        stats = {
            'total': SoftwareLicense.query.count(),
            'active': SoftwareLicense.query.filter_by(status='active').count(),
            'expired': SoftwareLicense.query.filter_by(status='expired').count(),
            'cancelled': SoftwareLicense.query.filter_by(status='cancelled').count()
        }

        # Yakında süresı dolacaklar (30 gün içinde)
        expiring_soon = SoftwareLicense.query.filter(
            SoftwareLicense.expiration_date <= datetime.now().date() + timedelta(days=30),
            SoftwareLicense.expiration_date >= datetime.now().date(),
            SoftwareLicense.status == 'active'
        ).count()
        stats['expiring_soon'] = expiring_soon

        # Vendor bazlı istatistikler
        vendors = db.session.query(SoftwareLicense.vendor, db.func.count(SoftwareLicense.license_id)).group_by(
            SoftwareLicense.vendor).all()
        stats['by_vendor'] = {vendor: count for vendor, count in vendors if vendor}

        return stats
    except Exception as e:
        print(f"Lisans istatistik hatası: {e}")
        return {'total': 0, 'active': 0, 'expired': 0, 'cancelled': 0, 'expiring_soon': 0, 'by_vendor': {}}


def get_knowledge_base_stats():
    """Bilgi bankası istatistiklerini döndür"""
    try:
        stats = {
            'total_documents': KnowledgeBase.query.count(),
            'recent_uploads': KnowledgeBase.query.filter(
                KnowledgeBase.upload_date >= datetime.now() - timedelta(days=7)
            ).count()
        }

        # Kategori bazlı istatistikler
        categories = db.session.query(
            KnowledgeBase.category,
            db.func.count(KnowledgeBase.document_id)
        ).group_by(KnowledgeBase.category).all()
        stats['by_category'] = {cat: count for cat, count in categories if cat}

        # Departman bazlı istatistikler
        departments = db.session.query(
            KnowledgeBase.department,
            db.func.count(KnowledgeBase.document_id)
        ).group_by(KnowledgeBase.department).all()
        stats['by_department'] = {dept: count for dept, count in departments if dept}

        return stats
    except Exception as e:
        print(f"Bilgi bankası istatistik hatası: {e}")
        return {'total_documents': 0, 'recent_uploads': 0, 'by_category': {}, 'by_department': {}}


def get_recent_logs(limit=10):
    """Son aktiviteleri getir"""
    try:
        return Logs.query.order_by(Logs.action_time.desc()).limit(limit).all()
    except Exception as e:
        print(f"Log getirme hatası: {e}")
        return []


# Database helper functions
def init_database():
    """Veritabanını başlat ve test verisi ekle"""
    try:
        db.create_all()
        print("✅ Database tabloları oluşturuldu!")

        # Test verisi var mı kontrol et
        if Employee.query.count() == 0:
            print("📝 Test verileri ekleniyor...")
            create_test_data()

        return True
    except Exception as e:
        print(f"❌ Database initialization hatası: {e}")
        return False


def create_test_data():
    """Test verileri oluştur"""
    try:
        from werkzeug.security import generate_password_hash

        # Test admin kullanıcısı
        admin_user = Employee(
            name="Admin",
            surname="User",
            email="admin@trt.gov.tr",
            password=generate_password_hash("admin123"),
            department="IT",
            role="admin"
        )
        db.session.add(admin_user)

        # Test manager kullanıcısı
        manager_user = Employee(
            name="Manager",
            surname="User",
            email="manager@trt.gov.tr",
            password=generate_password_hash("manager123"),
            department="Broadcast",
            role="manager"
        )
        db.session.add(manager_user)

        # Test normal kullanıcı
        normal_user = Employee(
            name="Normal",
            surname="User",
            email="user@trt.gov.tr",
            password=generate_password_hash("user123"),
            department="Production",
            role="user"
        )
        db.session.add(normal_user)

        db.session.commit()

        # Test ekipman ve lisans verileri
        create_sample_inventory()
        create_sample_knowledge_base()

        print("✅ Test kullanıcıları oluşturuldu!")
        print("📧 Admin: admin@trt.gov.tr / admin123")
        print("📧 Manager: manager@trt.gov.tr / manager123")
        print("📧 User: user@trt.gov.tr / user123")

        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Test verisi oluşturma hatası: {e}")
        return False


def create_sample_inventory():
    """Örnek envanter verileri oluştur"""
    try:
        # Örnek ekipmanlar
        sample_equipment = [
            {
                'equipment_name': 'TRT Server 01',
                'category': 'Server',
                'brand': 'Dell',
                'model': 'PowerEdge R740',
                'serial_number': 'DEL001',
                'status': 'in_use',
                'location': 'Sunucu Odası'
            },
            {
                'equipment_name': 'Broadcast Camera 01',
                'category': 'Camera',
                'brand': 'Sony',
                'model': 'PXW-X320',
                'serial_number': 'SON001',
                'status': 'in_use',
                'location': 'Stüdyo A'
            },
            {
                'equipment_name': 'Editing Workstation 01',
                'category': 'PC',
                'brand': 'HP',
                'model': 'Z8 G4',
                'serial_number': 'HP001',
                'status': 'in_stock',
                'location': 'Depo'
            }
        ]

        for eq_data in sample_equipment:
            equipment = Equipment(**eq_data)
            db.session.add(equipment)

        # Örnek lisanslar
        sample_licenses = [
            {
                'software_name': 'Adobe Creative Suite',
                'license_key': 'ADOBE-2024-001',
                'version': '2024',
                'vendor': 'Adobe',
                'status': 'active',
                'expiration_date': datetime(2024, 12, 31).date()
            },
            {
                'software_name': 'Microsoft Office 365',
                'license_key': 'MS365-2024-001',
                'version': '365',
                'vendor': 'Microsoft',
                'status': 'active',
                'expiration_date': datetime(2025, 6, 30).date()
            },
            {
                'software_name': 'Vizrt Trio',
                'license_key': 'VIZRT-TRIO-001',
                'version': '3.0',
                'vendor': 'Vizrt',
                'status': 'active'
            }
        ]

        for lic_data in sample_licenses:
            license = SoftwareLicense(**lic_data)
            db.session.add(license)

        db.session.commit()
        print("✅ Örnek envanter verileri oluşturuldu!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Örnek envanter verisi oluşturma hatası: {e}")


def create_sample_knowledge_base():
    """Örnek bilgi bankası verileri oluştur"""
    try:
        # Örnek dokümanlar
        sample_docs = [
            {
                'title': 'iNews Kullanım Kılavuzu',
                'description': 'iNews haber sistemi kullanım rehberi ve best practices',
                'category': 'iNews',
                'department': 'News',
                'uploaded_by': 1  # Admin user
            },
            {
                'title': 'Network Switch Konfigürasyonu',
                'description': 'Cisco ve HP switch\'lerin temel konfigürasyon ayarları',
                'category': 'Network',
                'department': 'IT',
                'uploaded_by': 1
            },
            {
                'title': 'RAID Konfigürasyon Rehberi',
                'description': 'RAID seviyelerinin karşılaştırması ve kurulum rehberi',
                'category': 'RAID',
                'department': 'IT',
                'uploaded_by': 2  # Manager user
            },
            {
                'title': 'Broadcast System Şeması',
                'description': 'Ana yayın sisteminin teknik şeması ve bağlantı diyagramları',
                'category': 'Broadcast',
                'department': 'Technical',
                'uploaded_by': 2
            }
        ]

        for doc_data in sample_docs:
            document = KnowledgeBase(**doc_data)
            db.session.add(document)

        db.session.commit()
        print("✅ Örnek bilgi bankası verileri oluşturuldu!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Örnek bilgi bankası verisi oluşturma hatası: {e}")