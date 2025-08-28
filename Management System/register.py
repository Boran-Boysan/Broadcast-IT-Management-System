from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import re

app = Flask(__name__)

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Boran2002@localhost:5432/database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key-here"

app.config.from_object(Config)
db = SQLAlchemy(app)

class Employee(db.Model):
    __tablename__ = 'employee'

    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(50))
    role = db.Column(db.String(10), nullable=False)
    data_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Employee {self.name} {self.surname}>'


@app.route('/')
def index():
    try:
        employees = Employee.query.all()

        # HTML template string
        html_template = """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Çalışan Yönetim Sistemi</title>
            <style>
                * {margin: 0; padding: 0; box-sizing: border-box;}
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {color: #333; text-align: center; margin-bottom: 30px;}
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 500;
                    display: inline-block;
                    transition: all 0.3s ease;
                    margin-bottom: 20px;
                }
                .btn:hover {transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);}
                .btn-delete {
                    background: #dc3545;
                    color: white;
                    padding: 6px 12px;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    font-size: 0.8rem;
                    font-weight: 500;
                    transition: all 0.3s ease;
                }
                .btn-delete:hover {background: #c82333; transform: translateY(-1px);}
                table {width: 100%; border-collapse: collapse; margin-top: 20px;}
                th, td {padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6;}
                th {background: #f8f9fa; font-weight: 600; color: #495057;}
                tr:hover {background: #f8f9fa;}
                .count {background: #e8f4ff; padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #0056b3;}
                .empty {text-align: center; padding: 40px; background: #f8f9fa; border-radius: 10px; color: #6c757d;}
            </style>
        </head>
        <body>
            <div class="container">
                <h1> Çalışan Yönetim Sistemi</h1>

                <a href="/register" class="btn">Yeni Çalışan Ekle</a>

                <div class="count">
                    <strong>Toplam Çalışan Sayısı: """ + str(len(employees)) + """</strong>
                </div>
        """

        if employees:
            html_template += """
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Ad Soyad</th>
                            <th>E-posta</th>
                            <th>Departman</th>
                            <th>Rol</th>
                            <th>Katılım Tarihi</th>
                            <th>İşlem</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for emp in employees:
                date_str = emp.data_joined.strftime('%d.%m.%Y %H:%M') if emp.data_joined else '-'
                dept_str = emp.department if emp.department else '-'

                html_template += f"""
                        <tr>
                            <td>{emp.employee_id}</td>
                            <td>{emp.name} {emp.surname}</td>
                            <td>{emp.email}</td>
                            <td>{dept_str}</td>
                            <td>{emp.role}</td>
                            <td>{date_str}</td>
                            <td><a href="/delete_confirm/{emp.employee_id}" class="btn-delete">Kaldır</a></td>
                        </tr>
                """

            html_template += """
                    </tbody>
                </table>
            """
        else:
            html_template += """
                <div class="empty">
                    <h3>Henüz hiç çalışan kaydı yok</h3>
                </div>
            """

        html_template += """
            </div>
        </body>
        </html>
        """

        return html_template

    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/register')
def register_form():
    return render_template('register.html')  # Buraya bi bak

@app.route('/add_employee', methods=['POST'])
def add_employee():
    try:
        name = request.form.get('name', '').strip()
        surname = request.form.get('surname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        department = request.form.get('department', '').strip()
        role = request.form.get('role', '').strip()

        errors = []

        if not name or len(name) > 30:
            errors.append('Ad alanı zorunludur ve 30 karakter geçmemelidir.')

        if not surname or len(surname) > 30:
            errors.append('Soyad alanı zorunludur ve 30 karakter geçmemelidir.')

        if not email or len(email) > 50:
            errors.append('E-posta alanı zorunludur ve 50 karakter geçmemelidir.')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append('Geçerli bir e-posta adresi girin.')

        if not password or len(password) < 6:  # şifre için daha fazla özellik ekle
            errors.append('Şifre en az 6 karakter olmalıdır.')

        if not role or role not in ['admin', 'user', 'manager']:
            errors.append('Geçerli bir rol seçin.')

        if department and len(department) > 50:
            errors.append('Departman adı 50 karakter geçmemelidir.')

        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
            errors.append('Bu e-posta adresi zaten kullanılıyor.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register_form'))

        hashed_password = generate_password_hash(password)

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

        print("=" * 50)
        print("  YENİ ÇALIŞAN EKLENDİ:")
        print(f"   ID: {new_employee.employee_id}")
        print(f"   Ad Soyad: {name} {surname}")
        print(f"   E-posta: {email}")
        print(f"   Departman: {department or 'Belirtilmedi'}")
        print(f"   Rol: {role}")
        print(f"   Kayıt Tarihi: {new_employee.data_joined}")
        print("=" * 50)

        flash(f'Çalışan {name} {surname} başarıyla PostgreSQL veritabanına eklendi!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        print(f" HATA: {str(e)}")
        flash(f' Hata oluştu: {str(e)}', 'error')
        return redirect(url_for('register_form'))

@app.route('/delete_confirm/<int:employee_id>')
def delete_confirm(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)

        html_template = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Çalışan Sil - Onay</title>
            <style>
                * {{margin: 0; padding: 0; box-sizing: border-box;}}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                }}
                h1 {{color: #dc3545; margin-bottom: 20px;}}
                .employee-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    text-align: left;
                }}
                .employee-info h3 {{color: #333; margin-bottom: 15px;}}
                .employee-info p {{margin: 5px 0; color: #666;}}
                .btn-container {{
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 30px;
                }}
                .btn {{
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    text-decoration: none;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: inline-block;
                }}
                .btn-danger {{
                    background: #dc3545;
                    color: white;
                }}
                .btn-danger:hover {{
                    background: #c82333;
                    transform: translateY(-2px);
                }}
                .btn-secondary {{
                    background: #6c757d;
                    color: white;
                }}
                .btn-secondary:hover {{
                    background: #5a6268;
                    transform: translateY(-2px);
                }}
                .warning {{
                    color: #dc3545;
                    font-weight: 500;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Çalışan Sil</h1>
                <p class="warning">Bu çalışanı kaldırmak istediğinizden emin misiniz?</p>

                <div class="employee-info">
                    <h3>Silinecek Çalışan Bilgileri:</h3>
                    <p><strong>Ad Soyad:</strong> {employee.name} {employee.surname}</p>
                    <p><strong>E-posta:</strong> {employee.email}</p>
                    <p><strong>Departman:</strong> {employee.department or 'Belirtilmedi'}</p>
                    <p><strong>Rol:</strong> {employee.role}</p>
                    <p><strong>Katılım Tarihi:</strong> {employee.data_joined.strftime('%d.%m.%Y %H:%M') if employee.data_joined else '-'}</p>
                </div>

                <p style="color: #666; font-size: 0.9rem;">Bu işlem geri alınamaz!</p>

                <div class="btn-container">
                    <form method="POST" action="/delete_employee/{employee.employee_id}" style="display: inline;">
                        <button type="submit" class="btn btn-danger">Evet, Sil</button>
                    </form>
                    <a href="/" class="btn btn-secondary">İptal</a>
                </div>
            </div>
        </body>
        </html>
        """

        return html_template

    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        employee_name = f"{employee.name} {employee.surname}"

        db.session.delete(employee)
        db.session.commit()

        print("=" * 50)
        print("  ÇALIŞAN SİLİNDİ:")
        print(f"   ID: {employee_id}")
        print(f"   Ad Soyad: {employee_name}")
        print("=" * 50)

        flash(f'Çalışan {employee_name} başarıyla silindi!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        print(f" HATA: {str(e)}")
        flash(f' Silme işlemi sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/employees')
def api_employees():
    try:
        employees = Employee.query.all()
        result = {
            'success': True,
            'count': len(employees),
            'employees': []
        }

        for emp in employees:
            employee_data = {
                'employee_id': emp.employee_id,
                'name': emp.name,
                'surname': emp.surname,
                'email': emp.email,
                'department': emp.department,
                'role': emp.role,
                'data_joined': emp.data_joined.strftime('%Y-%m-%d %H:%M:%S') if emp.data_joined else None
            }
            result['employees'].append(employee_data)

        return result

    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

def init_db():
    try:
        db.create_all()
        print("Veritabanı tabloları başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Veritabanı hatası: {e}")

if __name__ == '__main__':
    with app.app_context():
        init_db()

    print("Flask uygulaması başlatılıyor...")
    print("Ana Sayfa: http://127.0.0.1:5000")
    print("Çalışan Ekle: http://127.0.0.1:5000/register")
    print("API: http://127.0.0.1:5000/api/employees")
    print("-" * 50)

    app.run(debug=True, port=5000)