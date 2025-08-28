import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Hata handling için try-catch ekleyelim
try:
    import psycopg2
    from sqlalchemy import create_engine, text

    DATABASE_AVAILABLE = True
    print("✅ Database kütüphaneleri yüklü")
except ImportError as e:
    print(f"⚠️ Database kütüphaneleri yüklü değil: {e}")
    print("Demo verilerle çalışılacak...")
    DATABASE_AVAILABLE = False

# Dash uygulamasını başlat
app = dash.Dash(__name__)
app.title = "Broadcast IT - Dashboard"

# Database bağlantısı (PostgreSQL) - Config.py'den alınan URL
DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:Boran2002@localhost:5432/database")


def get_database_connection():
    """PostgreSQL veritabanı bağlantısı - Güvenli versiyon"""
    if not DATABASE_AVAILABLE:
        print("⚠️ Database kütüphaneleri mevcut değil, demo veriler kullanılıyor")
        return None

    try:
        engine = create_engine(DATABASE_URL)
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database bağlantısı başarılı")
        return engine
    except Exception as e:
        print(f"⚠️ Database bağlantı hatası: {e}")
        print("Demo veriler kullanılacak...")
        return None


def fetch_equipment_data():
    """Ekipman verilerini çek - DÜZELTİLMİŞ pandas sorguları"""
    try:
        engine = get_database_connection()
        if engine is None:
            print("📊 Demo ekipman verileri kullanılıyor")
            return create_demo_equipment_data()

        # DÜZELTİLMİŞ SORGU - pandas için doğru format
        query = """
        SELECT 
            eq.equipment_name,
            eq.category,
            eq.brand,
            eq.model,
            eq.status,
            eq.location,
            eq.purchase_date,
            emp.name as assigned_to_name,
            emp.department as assigned_department
        FROM equipment eq
        LEFT JOIN employee emp ON eq.assigned_to = emp.employee_id
        """

        # DÜZELTİLME: pandas.read_sql için engine'i doğru şekilde kullan
        df = pd.read_sql_query(query, engine)
        print(f"✅ Database'den {len(df)} ekipman kaydı çekildi")
        return df
    except Exception as e:
        print(f"⚠️ Ekipman verisi çekme hatası: {e}")
        print("📊 Demo verilere geçiliyor...")
        return create_demo_equipment_data()


def create_demo_equipment_data():
    """Demo ekipman verileri oluştur"""
    return pd.DataFrame({
        'equipment_name': [
            'Server 01', 'Broadcast Camera 01', 'Editing Workstation 01', 'Studio Switch 01',
            'Storage Unit 01', 'Microphone 01', 'Monitor 01', 'Router 01', 'UPS 01', 'Printer 01',
            'Laptop 01', 'Mixer Console 01', 'LED Panel 01', 'Tripod 01', 'Cable Tester 01'
        ],
        'category': [
            'Server', 'Camera', 'PC', 'Network', 'Storage',
            'Audio', 'Display', 'Network', 'Power', 'Office',
            'PC', 'Audio', 'Lighting', 'Support', 'Tools'
        ],
        'brand': [
            'Dell', 'Sony', 'HP', 'Cisco', 'Synology',
            'Shure', 'Samsung', 'Cisco', 'APC', 'Canon',
            'Lenovo', 'Yamaha', 'Arri', 'Manfrotto', 'Fluke'
        ],
        'status': [
            'in_use', 'in_use', 'in_stock', 'under_repair', 'in_use',
            'in_use', 'in_stock', 'in_use', 'in_use', 'under_repair',
            'in_use', 'in_stock', 'in_use', 'in_use', 'under_repair'
        ],
        'location': [
            'Sunucu Odası', 'Stüdyo A', 'Depo', 'Teknik Servis', 'Sunucu Odası',
            'Stüdyo A', 'Depo', 'Sunucu Odası', 'Sunucu Odası', 'Ofis',
            'Ofis', 'Stüdyo B', 'Stüdyo A', 'Depo', 'Teknik Servis'
        ],
        'assigned_department': [
            'IT', 'Yayın', None, 'IT', 'IT',
            'Yayın', None, 'IT', 'IT', 'Yönetim',
            'IT', 'Yayın', 'Yayın', None, 'IT'
        ]
    })


def fetch_license_data():
    """Lisans verilerini çek - DÜZELTİLMİŞ pandas sorguları"""
    try:
        engine = get_database_connection()
        if engine is None:
            print("📊 Demo lisans verileri kullanılıyor")
            return create_demo_license_data()

        # DÜZELTİLMİŞ SORGU - pandas için doğru format
        query = """
        SELECT 
            sl.software_name,
            sl.vendor,
            sl.version,
            sl.status,
            sl.expiration_date,
            sl.license_key,
            COUNT(eq.equipment_id) as assigned_count
        FROM software_license sl
        LEFT JOIN equipment eq ON sl.equipment_id = eq.equipment_id
        GROUP BY sl.license_id, sl.software_name, sl.vendor, sl.version, sl.status, 
                 sl.expiration_date, sl.license_key
        """

        # DÜZELTİLME: pandas.read_sql için engine'i doğru şekilde kullan
        df = pd.read_sql_query(query, engine)
        print(f"✅ Database'den {len(df)} lisans kaydı çekildi")
        return df
    except Exception as e:
        print(f"⚠️ Lisans verisi çekme hatası: {e}")
        print("📊 Demo verilere geçiliyor...")
        return create_demo_license_data()


def create_demo_license_data():
    """Demo lisans verileri oluştur"""
    return pd.DataFrame({
        'software_name': [
            'Adobe Creative Suite', 'Microsoft Office 365', 'Vizrt Trio', 'Avid Media Composer',
            'Windows Server 2022', 'AutoCAD', 'Final Cut Pro', 'Photoshop',
            'Premiere Pro', 'After Effects', 'Maya', 'Unity Pro'
        ],
        'vendor': [
            'Adobe', 'Microsoft', 'Vizrt', 'Avid',
            'Microsoft', 'Autodesk', 'Apple', 'Adobe',
            'Adobe', 'Adobe', 'Autodesk', 'Unity'
        ],
        'status': [
            'active', 'active', 'active', 'expired',
            'active', 'active', 'active', 'expired',
            'active', 'active', 'active', 'expired'
        ],
        'expiration_date': [
            datetime(2024, 12, 31).date(),
            datetime(2025, 6, 30).date(),
            datetime(2025, 8, 15).date(),
            datetime(2024, 8, 1).date(),  # Expired
            None,  # Perpetual
            datetime(2025, 3, 15).date(),
            datetime(2025, 12, 1).date(),
            datetime(2024, 5, 20).date(),  # Expired
            datetime(2025, 2, 28).date(),
            datetime(2025, 4, 15).date(),
            datetime(2025, 7, 10).date(),
            datetime(2024, 9, 30).date()  # Expired
        ],
        'assigned_count': [5, 50, 3, 2, 1, 3, 4, 8, 6, 7, 2, 4]
    })


def fetch_logs_data():
    """Log verilerini çek - DÜZELTİLMİŞ pandas sorguları"""
    try:
        engine = get_database_connection()
        if engine is None:
            print("📊 Demo log verileri kullanılıyor")
            return create_demo_logs_data()

        # DÜZELTİLMİŞ SORGU - pandas için doğru format
        query = """
        SELECT 
            l.action_time,
            l.action_type,
            l.description,
            emp.name as user_name,
            emp.department as user_department
        FROM logs l
        LEFT JOIN employee emp ON l.user_id = emp.employee_id
        WHERE l.action_time >= %s
        ORDER BY l.action_time DESC
        LIMIT 1000
        """

        start_date = datetime.now() - timedelta(days=30)

        # DÜZELTİLME: pandas.read_sql için doğru parametre formatı
        df = pd.read_sql_query(query, engine, params=[start_date])
        print(f"✅ Database'den {len(df)} log kaydı çekildi")
        return df
    except Exception as e:
        print(f"⚠️ Log verisi çekme hatası: {e}")
        print("📊 Demo verilere geçiliyor...")
        return create_demo_logs_data()


def create_demo_logs_data():
    """Demo log verileri oluştur"""
    import random

    # Gerçekçi tarih aralığı
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Rastgele tarihler oluştur
    date_range = []
    for i in range(300):
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        date_range.append(random_date)

    actions = ['login', 'create', 'update', 'delete', 'view', 'export']
    users = ['Admin User', 'Manager User', 'Regular User', 'Technician', 'Operator', 'Supervisor']
    departments = ['IT', 'Yayın', 'Prodüksiyon', 'Teknik', 'Yönetim', 'İnsan Kaynakları']

    return pd.DataFrame({
        'action_time': date_range,
        'action_type': random.choices(actions, k=300),
        'user_name': random.choices(users, k=300),
        'user_department': random.choices(departments, k=300)
    })


# Veri yükleme - Hata handling ile
print("🚀 Dashboard verileri yükleniyor...")
try:
    equipment_df = fetch_equipment_data()
    license_df = fetch_license_data()
    logs_df = fetch_logs_data()
    print(f"✅ Veriler başarıyla yüklendi: {len(equipment_df)} ekipman, {len(license_df)} lisans, {len(logs_df)} log")
except Exception as e:
    print(f"❌ Veri yükleme hatası: {e}")
    # Fallback olarak boş dataframe'ler oluştur
    equipment_df = create_demo_equipment_data()
    license_df = create_demo_license_data()
    logs_df = create_demo_logs_data()
    print(f"🔄 Fallback veriler kullanılıyor: {len(equipment_df)} ekipman, {len(license_df)} lisans, {len(logs_df)} log")

# Layout tasarımı (aynı kalacak - değişiklik yok)
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1(" Broadcast IT", className="header-title"),
            html.P("Dashboard & Analytics", className="header-subtitle")
        ], className="header-content"),
        html.Div([
            html.Span(f"Son güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                      className="last-update")
        ], className="header-info")
    ], className="header"),

    # Metrics Row
    html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-desktop metric-icon"),
                html.Div([
                    html.H3(str(len(equipment_df)), className="metric-number"),
                    html.P("Toplam Ekipman", className="metric-label")
                ])
            ], className="metric-content"),
            html.Div([
                html.Span(
                    f"Kullanımda: {len(equipment_df[equipment_df['status'] == 'in_use']) if len(equipment_df) > 0 else 0}",
                    className="metric-detail")
            ])
        ], className="metric-card equipment"),

        html.Div([
            html.Div([
                html.I(className="fas fa-key metric-icon"),
                html.Div([
                    html.H3(str(len(license_df)), className="metric-number"),
                    html.P("Yazılım Lisansı", className="metric-label")
                ])
            ], className="metric-content"),
            html.Div([
                html.Span(f"Aktif: {len(license_df[license_df['status'] == 'active']) if len(license_df) > 0 else 0}",
                          className="metric-detail")
            ])
        ], className="metric-card licenses"),

        html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle metric-icon"),
                html.Div([
                    html.H3(str(len(license_df[license_df['status'] == 'expired']) if len(license_df) > 0 else 0),
                            className="metric-number"),
                    html.P("Süresi Dolmuş", className="metric-label")
                ])
            ], className="metric-content"),
            html.Div([
                html.Span(
                    "Acil İşlem Gerekli" if len(license_df[license_df['status'] == 'expired']) > 0 else "Sorun Yok",
                    className="metric-detail alert" if len(
                        license_df[license_df['status'] == 'expired']) > 0 else "metric-detail")
            ])
        ], className="metric-card alerts"),

        html.Div([
            html.Div([
                html.I(className="fas fa-chart-line metric-icon"),
                html.Div([
                    html.H3(f"{len(logs_df)}", className="metric-number"),
                    html.P("30 Günlük Aktivite", className="metric-label")
                ])
            ], className="metric-content"),
            html.Div([
                html.Span(f"Günlük ortalama: {len(logs_df) // 30 if len(logs_df) > 0 else 0}",
                          className="metric-detail")
            ])
        ], className="metric-card activity")
    ], className="metrics-row"),

    # Charts Section
    html.Div([
        # Sol Kolon
        html.Div([
            # Ekipman Durumu Pie Chart
            html.Div([
                html.H3("Donanım Envanteri Durumu", className="chart-title"),
                dcc.Graph(
                    id='equipment-status-pie',
                    config={'displayModeBar': False}
                )
            ], className="chart-container"),

            # Departman Bazlı Dağılım
            html.Div([
                html.H3("Departman Bazlı Ekipman Dağılımı", className="chart-title"),
                dcc.Graph(
                    id='department-distribution',
                    config={'displayModeBar': False}
                )
            ], className="chart-container")
        ], className="chart-column"),

        # Sağ Kolon
        html.Div([
            # Kategori Bazlı Bar Chart
            html.Div([
                html.H3("Ekipman Türlerine Göre Dağılım", className="chart-title"),
                dcc.Graph(
                    id='category-bar-chart',
                    config={'displayModeBar': False}
                )
            ], className="chart-container"),

            # Yazılım Durumu Chart
            html.Div([
                html.H3("Yazılım Lisans Durumu", className="chart-title"),
                dcc.Graph(
                    id='license-status-chart',
                    config={'displayModeBar': False}
                )
            ], className="chart-container")
        ], className="chart-column")
    ], className="charts-row"),

    # Alt Bölüm - Aktivite Timeline ve Lisans Tablosu
    html.Div([
        # Aktivite Zaman Serisi
        html.Div([
            html.H3("Sistem Aktivite Geçmişi (Son 30 Gün)", className="chart-title"),
            dcc.Graph(
                id='activity-timeline',
                config={'displayModeBar': True}
            )
        ], className="full-width-chart"),

        # Lisans Süresi Tablosu
        html.Div([
            html.H3("Lisans Süresi Takibi", className="chart-title"),
            html.Div([
                dcc.Tabs(id="license-tabs", value='expiring', children=[
                    dcc.Tab(label='Süresi Yaklaşanlar', value='expiring'),
                    dcc.Tab(label='Aktif Lisanslar', value='active'),
                    dcc.Tab(label='Süresi Dolmuşlar', value='expired')
                ]),
                html.Div(id='license-tab-content')
            ])
        ], className="full-width-chart")
    ], className="bottom-section"),

    # Refresh Button
    html.Div([
        html.Button('🔄 Verileri Yenile', id='refresh-button', className='refresh-btn'),
        html.Div(id='refresh-output', style={'margin-top': '10px'})
    ], className="refresh-section")

], className="dashboard-container")


# Callbacks - Güvenli versiyonlar (aynı kalacak - değişiklik yok)
@app.callback(
    Output('equipment-status-pie', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_equipment_status_pie(n_clicks):
    try:
        if len(equipment_df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Ekipman verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=300)
            return fig

        status_counts = equipment_df['status'].value_counts()

        colors = {
            'in_use': '#28a745',
            'in_stock': '#17a2b8',
            'under_repair': '#ffc107',
            'scrap': '#dc3545'
        }

        status_labels = {
            'in_use': 'Kullanımda',
            'in_stock': 'Stokta',
            'under_repair': 'Tamirde',
            'scrap': 'Hurda'
        }

        fig = go.Figure(data=[go.Pie(
            labels=[status_labels.get(status, status) for status in status_counts.index],
            values=status_counts.values,
            hole=0.4,
            marker_colors=[colors.get(status, '#6c757d') for status in status_counts.index],
            textinfo='label+percent+value',
            textfont_size=12
        )])

        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            font=dict(family="Arial", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        return fig
    except Exception as e:
        print(f"Equipment pie chart hatası: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Chart oluşturulamadı",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
        return fig


@app.callback(
    Output('category-bar-chart', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_category_bar_chart(n_clicks):
    try:
        if len(equipment_df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Ekipman verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=300)
            return fig

        category_counts = equipment_df['category'].value_counts()

        fig = go.Figure(data=[go.Bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            marker_color='#667eea',
            text=category_counts.values,
            textposition='auto'
        )])

        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=100, r=20),
            xaxis_title="Adet",
            yaxis_title="Kategori",
            font=dict(family="Arial", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )

        return fig
    except Exception as e:
        print(f"Category bar chart hatası: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Chart oluşturulamadı",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
        return fig


@app.callback(
    Output('department-distribution', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_department_distribution(n_clicks):
    try:
        if len(equipment_df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Ekipman verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=300)
            return fig

        dept_counts = equipment_df['assigned_department'].fillna('Atanmamış').value_counts()

        fig = go.Figure(data=[go.Bar(
            x=dept_counts.index,
            y=dept_counts.values,
            marker_color=['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14'][:len(dept_counts)],
            text=dept_counts.values,
            textposition='auto'
        )])

        fig.update_layout(
            height=300,
            margin=dict(t=20, b=40, l=40, r=20),
            xaxis_title="Departman",
            yaxis_title="Ekipman Sayısı",
            font=dict(family="Arial", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )

        return fig
    except Exception as e:
        print(f"Department distribution hatası: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Chart oluşturulamadı",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
        return fig


@app.callback(
    Output('license-status-chart', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_license_status_chart(n_clicks):
    try:
        if len(license_df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Lisans verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=300)
            return fig

        status_counts = license_df['status'].value_counts()

        colors = {'active': '#28a745', 'expired': '#dc3545', 'inactive': '#6c757d'}

        fig = go.Figure(data=[go.Bar(
            x=status_counts.index,
            y=status_counts.values,
            marker_color=[colors.get(status, '#6c757d') for status in status_counts.index],
            text=status_counts.values,
            textposition='auto'
        )])

        fig.update_layout(
            height=300,
            margin=dict(t=20, b=40, l=40, r=20),
            xaxis_title="Lisans Durumu",
            yaxis_title="Adet",
            font=dict(family="Arial", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )

        return fig
    except Exception as e:
        print(f"License status chart hatası: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Chart oluşturulamadı",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
        return fig


@app.callback(
    Output('activity-timeline', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_activity_timeline(n_clicks):
    try:
        if len(logs_df) == 0 or 'action_time' not in logs_df.columns:
            fig = go.Figure()
            fig.add_annotation(text="Aktivite verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=400)
            return fig

        # Tarih sütununu datetime'a çevir
        logs_df_copy = logs_df.copy()
        logs_df_copy['action_time'] = pd.to_datetime(logs_df_copy['action_time'])
        logs_df_copy['date'] = logs_df_copy['action_time'].dt.date

        # Günlük aktivite sayıları
        daily_activities = logs_df_copy.groupby(['date', 'action_type']).size().reset_index(name='count')

        if len(daily_activities) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Günlük aktivite verisi bulunamadı",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=400)
            return fig

        fig = px.line(daily_activities, x='date', y='count', color='action_type',
                      title="Günlük Aktivite Dağılımı",
                      labels={'count': 'Aktivite Sayısı', 'date': 'Tarih', 'action_type': 'İşlem Türü'})

        fig.update_layout(
            height=400,
            margin=dict(t=40, b=40, l=40, r=40),
            font=dict(family="Arial", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )

        return fig
    except Exception as e:
        print(f"Activity timeline hatası: {e}")
        fig = go.Figure()
        fig.add_annotation(text="Timeline oluşturulamadı",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=400)
        return fig


@app.callback(
    Output('license-tab-content', 'children'),
    Input('license-tabs', 'value')
)
def update_license_tab_content(active_tab):
    try:
        if len(license_df) == 0:
            return html.Div([
                html.P("Lisans verisi bulunamadı.", className="no-data")
            ])

        if active_tab == 'expiring':
            # Süresi yaklaşan lisanslar (30 gün içinde)
            today = datetime.now().date()

            if 'expiration_date' in license_df.columns:
                license_df_copy = license_df.copy()
                license_df_copy['expiration_date'] = pd.to_datetime(license_df_copy['expiration_date'],
                                                                    errors='coerce').dt.date
                expiring = license_df_copy[
                    (license_df_copy['expiration_date'] >= today) &
                    (license_df_copy['expiration_date'] <= today + timedelta(days=30)) &
                    (license_df_copy['status'] == 'active')
                    ].sort_values('expiration_date')

                if len(expiring) > 0:
                    return html.Div([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th("Yazılım"),
                                    html.Th("Sağlayıcı"),
                                    html.Th("Bitiş Tarihi"),
                                    html.Th("Kalan Gün"),
                                    html.Th("Durum")
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row['software_name']),
                                    html.Td(row['vendor']),
                                    html.Td(row['expiration_date'].strftime('%d.%m.%Y') if pd.notnull(
                                        row['expiration_date']) else '-'),
                                    html.Td(f"{(row['expiration_date'] - today).days} gün" if pd.notnull(
                                        row['expiration_date']) else '-'),
                                    html.Td(html.Span("⚠️ Yaklaşan", className="status-warning"))
                                ]) for _, row in expiring.iterrows()
                            ])
                        ], className="license-table")
                    ])
                else:
                    return html.Div([
                        html.P("✅ 30 gün içinde süresi dolacak lisans bulunmuyor.", className="no-data")
                    ])
            else:
                return html.Div([html.P("Tarih verisi bulunamadı.", className="no-data")])

        elif active_tab == 'active':
            active_licenses = license_df[license_df['status'] == 'active']
            return html.Div([
                html.P(f"Toplam {len(active_licenses)} aktif lisans bulunuyor.", className="info-text"),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Yazılım"),
                            html.Th("Sağlayıcı"),
                            html.Th("Versiyon"),
                            html.Th("Atanan Sayı"),
                            html.Th("Bitiş Tarihi")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['software_name']),
                            html.Td(row['vendor']),
                            html.Td(row['version'] if 'version' in row and pd.notnull(row['version']) else '-'),
                            html.Td(row['assigned_count'] if 'assigned_count' in row else '-'),
                            html.Td(
                                row['expiration_date'].strftime('%d.%m.%Y') if 'expiration_date' in row and pd.notnull(
                                    row['expiration_date']) else 'Süresiz')
                        ]) for _, row in active_licenses.iterrows()
                    ])
                ], className="license-table")
            ])

        elif active_tab == 'expired':
            expired_licenses = license_df[license_df['status'] == 'expired']
            if len(expired_licenses) > 0:
                return html.Div([
                    html.P(f"⚠️ {len(expired_licenses)} lisansın süresi dolmuş!", className="alert-text"),
                    html.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Yazılım"),
                                html.Th("Sağlayıcı"),
                                html.Th("Bitiş Tarihi"),
                                html.Th("Durum")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(row['software_name']),
                                html.Td(row['vendor']),
                                html.Td(row['expiration_date'].strftime(
                                    '%d.%m.%Y') if 'expiration_date' in row and pd.notnull(
                                    row['expiration_date']) else '-'),
                                html.Td(html.Span("❌ Süresi Dolmuş", className="status-expired"))
                            ]) for _, row in expired_licenses.iterrows()
                        ])
                    ], className="license-table")
                ])
            else:
                return html.Div([
                    html.P("✅ Süresi dolmuş lisans bulunmuyor.", className="no-data")
                ])

    except Exception as e:
        print(f"License tab content hatası: {e}")
        return html.Div([
            html.P(f"Lisans tablosu oluşturulamadı: {str(e)}", className="no-data")
        ])


@app.callback(
    Output('refresh-output', 'children'),
    Input('refresh-button', 'n_clicks')
)
def refresh_data(n_clicks):
    if n_clicks:
        return html.Span(f"✅ Veriler güncellendi - {datetime.now().strftime('%H:%M:%S')}",
                         className="refresh-success")
    return ""


# CSS Styles - Komplet ve modern tasarım
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }

        .dashboard-container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }

        .header-title {
            font-size: 32px;
            color: #2d3748;
            margin-bottom: 5px;
            font-weight: 700;
        }

        .header-subtitle {
            color: #718096;
            font-size: 16px;
            font-weight: 400;
        }

        .last-update {
            color: #718096;
            font-size: 14px;
            font-style: italic;
        }

        .metrics-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }

        .metric-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.5);
        }

        .metric-card.equipment { border-left-color: #667eea; }
        .metric-card.licenses { border-left-color: #fcb69f; }
        .metric-card.alerts { border-left-color: #ff9a9e; }
        .metric-card.activity { border-left-color: #a8edea; }

        .metric-content {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        .metric-icon {
            font-size: 32px;
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }

        .equipment .metric-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
        .licenses .metric-icon { background: linear-gradient(135deg, #ffecd2, #fcb69f); color: #8b4513; }
        .alerts .metric-icon { background: linear-gradient(135deg, #ff9a9e, #fecfef); color: #742a2a; }
        .activity .metric-icon { background: linear-gradient(135deg, #a8edea, #fed6e3); color: #2d3748; }

        .metric-number {
            font-size: 36px;
            font-weight: 700;
            color: #2d3748;
            margin: 0;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .metric-label {
            color: #718096;
            font-size: 14px;
            margin: 0;
            font-weight: 600;
        }

        .metric-detail {
            color: #4a5568;
            font-size: 12px;
            padding: 4px 8px;
            background: #f7fafc;
            border-radius: 6px;
            font-weight: 500;
        }

        .metric-detail.alert {
            background: #fed7d7;
            color: #e53e3e;
            font-weight: 600;
        }

        .charts-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .chart-column {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }

        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.45);
        }

        .chart-title {
            color: #2d3748;
            font-size: 18px;
            margin-bottom: 20px;
            font-weight: 600;
            text-align: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        .bottom-section {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .full-width-chart {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }

        .full-width-chart:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.45);
        }

        .license-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }

        .license-table th,
        .license-table td {
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        .license-table th {
            background: linear-gradient(135deg, #f7fafc, #edf2f7);
            font-weight: 600;
            color: #4a5568;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }

        .license-table tbody tr {
            transition: all 0.2s ease;
        }

        .license-table tbody tr:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
            transform: scale(1.01);
        }

        .license-table tbody tr:nth-child(even) {
            background: rgba(247, 250, 252, 0.5);
        }

        .status-warning {
            background: linear-gradient(135deg, #fed7aa, #faf089);
            color: #744210;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .status-expired {
            background: linear-gradient(135deg, #fed7d7, #fbb6ce);
            color: #742a2a;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .no-data {
            text-align: center;
            color: #718096;
            font-style: italic;
            padding: 40px 20px;
            font-size: 16px;
        }

        .info-text {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 14px;
            font-weight: 500;
        }

        .alert-text {
            color: #e53e3e;
            margin-bottom: 15px;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            padding: 10px;
            background: #fed7d7;
            border-radius: 8px;
            border-left: 4px solid #e53e3e;
        }

        .refresh-section {
            text-align: center;
            margin-top: 30px;
        }

        .refresh-btn {
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .refresh-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
            background: linear-gradient(90deg, #5a6fd8, #6a4190);
        }

        .refresh-btn:active {
            transform: translateY(-1px);
        }

        .refresh-success {
            color: #28a745;
            font-weight: 600;
            font-size: 14px;
            margin-top: 10px;
            padding: 8px 16px;
            background: #d4edda;
            border-radius: 20px;
            display: inline-block;
        }

        /* Tab Styles */
        .tab-content {
            background: white;
            border-radius: 0 0 10px 10px;
        }

        .tab {
            background: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            color: #495057 !important;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .tab:hover {
            background: #e9ecef !important;
        }

        .tab--selected {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            border-color: #667eea !important;
            font-weight: 600;
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .charts-row {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .dashboard-container {
                padding: 15px;
            }

            .header {
                flex-direction: column;
                text-align: center;
                gap: 15px;
                padding: 20px;
            }

            .header-title {
                font-size: 24px;
            }

            .metrics-row {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }

            .metric-card {
                padding: 20px;
            }

            .metric-number {
                font-size: 28px;
            }

            .chart-container,
            .full-width-chart {
                padding: 20px;
            }

            .license-table {
                font-size: 12px;
            }

            .license-table th,
            .license-table td {
                padding: 8px 4px;
            }

            .refresh-btn {
                padding: 12px 24px;
                font-size: 14px;
            }
        }

        @media (max-width: 480px) {
            .dashboard-container {
                padding: 10px;
            }

            .metrics-row {
                grid-template-columns: 1fr;
            }

            .metric-card {
                padding: 15px;
            }

            .metric-content {
                flex-direction: column;
                text-align: center;
                gap: 10px;
            }
        }

        /* Animations */
        .metric-card,
        .chart-container,
        .full-width-chart {
            animation: fadeInUp 0.6s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Plotly Graph Customizations */
        .js-plotly-plot .plotly .modebar {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 6px;
        }

        .js-plotly-plot .plotly .modebar-btn {
            color: #4a5568 !important;
        }

        .js-plotly-plot .plotly .modebar-btn:hover {
            background: rgba(102, 126, 234, 0.1) !important;
            color: #667eea !important;
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a6fd8, #6a4190);
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

if __name__ == '__main__':
    print("Broadcast IT Dashboard başlatılıyor...")

    # Port kontrolü
    import socket


    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0


    port = 8050
    if is_port_in_use(port):
        print(f"⚠️ Port {port} zaten kullanımda, {port + 1} portu deneniyor...")
        port = port + 1
        if is_port_in_use(port):
            print(f"⚠️ Port {port} da kullanımda, {port + 1} portu deneniyor...")
            port = port + 1

    try:
        print(f"🌐 Dashboard http://localhost:{port} adresinde başlatılıyor...")
        print("✅ Dashboard hazır! Tarayıcınızda açmak için Ctrl+Click yapın:")
        print(f"   👉 http://localhost:{port}")
        print("\n📊 Özellikler:")
        print("   • İnteraktif grafikler")
        print("   • Gerçek zamanlı veriler")
        print("   • Responsive tasarım")
        print("   • Modern UI/UX")
        print("\n🔄 Durdurmak için Ctrl+C tuşlarına basın")
        print("-" * 50)

        # DÜZELTİLME: app.run_server yerine app.run kullan
        app.run(
            debug=False,  # Production için False
            host='0.0.0.0',
            port=port,
            dev_tools_ui=False,
            dev_tools_hot_reload=False
        )
    except KeyboardInterrupt:
        print(f"\n👋 Dashboard kapatıldı.")
    except Exception as e:
        print(f"\n❌ HATA: Dash sunucu başlatılamadı!")
        print(f"📋 Hata detayı: {e}")
        print(f"🔧 Hata türü: {type(e).__name__}")
        print(f"\n🔍 Sorun giderme önerileri:")
        print(f"1. 🔌 Port çakışması: Başka bir uygulama {port} portunu kullanıyor olabilir")
        print(f"2. 📦 Eksik paketler: pip install dash plotly pandas")
        print(f"3. 🗄️ Database: PostgreSQL bağlantısı kontrol edin (demo verilerle çalışabilir)")
        print(f"4. 🐍 Python: Python 3.7+ gerekli")
        print(f"\n🧪 Manuel test için:")
        print(f"   python dash_dashboard.py")
        print(f"\n💡 Yardım için: https://dash.plotly.com/")
        sys.exit(1)