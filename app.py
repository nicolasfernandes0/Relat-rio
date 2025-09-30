# app.py - VERSÃO COMPLETA COM TODAS AS FUNÇÕES
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(
    page_title="Gestão de Frotas",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TEMA ESCURO COMPLETO
st.markdown("""
<style>
    /* TEMA ESCURO COMPLETO */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: #60A5FA;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #334155;
    }
    
    .card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #475569;
        margin-bottom: 1rem;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #374151 0%, #1F2937 100%);
        color: #F9FAFB;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #4B5563;
    }
    
    .success-box {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #10B981;
        font-weight: bold;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #F59E0B;
    }
    
    .error-box {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #EF4444;
    }
    
    /* Botões personalizados */
    .stButton button {
        background: linear-gradient(45deg, #6366F1, #8B5CF6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(45deg, #8B5CF6, #7C3AED);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
    }
    
    /* Sidebar personalizada */
    .css-1d391kg {
        background-color: #1E293B !important;
    }
    
    .css-1d391kg .stRadio label {
        color: #E2E8F0 !important;
    }
    
    /* Métricas com tema escuro */
    [data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
        color: #E2E8F0;
    }
    
    [data-testid="metric-label"] {
        color: #94A3B8 !important;
    }
    
    [data-testid="metric-value"] {
        color: #F1F5F9 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class GestaoFrotasStreamlit:
    def __init__(self):
        self.vehicles = None
        self.vehicle_uses = None
        self.users = None
        self.point_records = None
        self.maintenances = None
        
        # Inicializar session state
        if 'dados_carregados' not in st.session_state:
            st.session_state.dados_carregados = False

    def processar_upload(self, vehicles_file, uses_file, maintenances_file, users_file, points_file):
        """Processa os arquivos enviados"""
        arquivos = {
            "Veículos": vehicles_file,
            "Utilizações": uses_file,
            "Manutenções": maintenances_file,
            "Usuários": users_file,
            "Registros de Ponto": points_file
        }
        
        # Verificar se todos os arquivos foram enviados
        arquivos_faltantes = [nome for nome, arquivo in arquivos.items() if arquivo is None]
        
        if arquivos_faltantes:
            st.error(f"❌ Arquivos faltantes: {', '.join(arquivos_faltantes)}")
            return
        
        # Processar cada arquivo
        try:
            with st.spinner("📥 Processando arquivos..."):
                self.vehicles = pd.read_csv(vehicles_file)
                self.vehicle_uses = pd.read_csv(uses_file)
                self.maintenances = pd.read_csv(maintenances_file)
                self.users = pd.read_csv(users_file)
                self.point_records = pd.read_csv(points_file)
            
            # Converter datas
            self._converter_datas()
            
            # Marcar como carregado
            st.session_state.dados_carregados = True
            st.session_state.dados_veiculos = self.vehicles
            st.session_state.dados_utilizacoes = self.vehicle_uses
            st.session_state.dados_manutencoes = self.maintenances
            st.session_state.dados_usuarios = self.users
            st.session_state.dados_ponto = self.point_records
            
            st.success("✅ Todos os dados foram carregados com sucesso!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivos: {e}")

    def carregar_dados_exemplo(self):
        """Carrega dados de exemplo diretamente no código"""
        try:
            with st.spinner("📥 Carregando dados de exemplo..."):
                # Dados de Veículos
                vehicles_data = """id,created_at,foto,placa,marca,modelo,status,tipo
1301a649-42d0-4f83-b64e-c735bd928c5f,2025-09-02 16:12:07.327105+00,https://placehold.co/50x50/e0e0e0/ffffff?text=Sem+foto,BBB1234,TESTE,TESTE,DISPONÍVEL,CARRO
445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-08-26 16:42:54.064125+00,https://kelzcwwdntxuplvqgjdg.supabase.co/storage/v1/object/sign/fotos/celta.jpg?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV9kNzJiODg0ZS1hNTNiLTQzYjMtYjlhYi1mMGFlZDBiNTQ4NTQi,ASG2345,CELTA,CHEVROLET,DISPONÍVEL,CARRO
b4214b15-550f-4299-a9dd-f1eb68693084,2025-09-02 16:34:46.23207+00,https://placehold.co/50x50/e0e0e0/ffffff?text=Sem+foto,EDS1234,TESTE,TESTE,DISPONÍVEL,CARRO
c986b737-6364-4ffe-98d6-1c34c122cc17,2025-09-02 16:11:45.039057+00,https://placehold.co/50x50/e0e0e0/ffffff?text=Sem+foto,ABC1234,TESTE,TESTE,DISPONÍVEL,CARRO"""
                
                # Dados de Utilizações
                uses_data = """id,created_at,data_inicio,data_fim,utilizador,quilometragem,finalidade,status,vehicle_id
182557f0-73fa-401c-b78b-4dab7b8aba27,2025-09-01 22:44:16.037633+00,01/09/2025 19:44:15,01/09/2025 19:44:33,Rosemeire,12345 / 123456,teste,CONCLUÍDO,445f97a3-6f3e-4326-83ed-e0049ba933ed
27159787-4422-4a68-a781-b2b0e737ecdf,2025-09-01 21:19:20.046921+00,2025-09-01,01/09/2025 18:19:56,Nicolas Fernandes Oliveira,20000 / 30000,inicio,CONCLUÍDO,445f97a3-6f3e-4326-83ed-e0049ba933ed
70bcba6a-fbdc-4c09-aeb4-c629f5a81bca,2025-09-05 21:23:27.163282+00,05/09/2025 18:23:26,05/09/2025 18:24:32,Nicolas Fernandes Oliveira,20000 / 25000,transcafrw,CONCLUÍDO,445f97a3-6f3e-4326-83ed-e0049ba933ed
7c089cb9-cf6b-490c-9f58-d5b449a84e54,2025-09-25 20:15:38.406336+00,25/09/2025 17:15:38,25/09/2025 17:16:06,Nicolas Fernandes Oliveira,400000 / 500000,yuik,CONCLUÍDO,445f97a3-6f3e-4326-83ed-e0049ba933ed
b0729004-8322-42f6-b47a-eca60854082b,2025-08-30 02:57:38.545834+00,2025-08-29,29/08/2025 23:58:06,Nicolas Fernandes Oliveira,20000 / 3000,inicio,CONCLUÍDO,445f97a3-6f3e-4326-83ed-e0049ba933ed"""
                
                # Dados de Manutenções
                maintenances_data = """id,created_at,vehicle_id,data_manutencao,descricao,custo,status
1de56229-337e-41f6-90cd-d03bb15c38c4,2025-09-01 22:27:43.885494+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,teste,235.00,Concluído
389cffba-7624-4af0-b24d-149dfcaadba2,2025-09-01 22:27:30.055662+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,teste,1234.00,Concluído
4ce52708-1837-432d-8307-7b8a4de87020,2025-09-01 22:53:03.461019+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-11,1231,41243.00,Concluído
77cea694-99ba-4461-be12-024b5e700bb9,2025-09-01 21:20:34.12544+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,pneu,1000.00,Concluído
794f4ffa-43e0-4aef-8c27-931a8d8280c9,2025-09-05 21:20:59.877258+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-05,alinhamento,12000.00,Concluído
b3e5bd80-2c1e-4cb4-9b8d-cfe7b41964fa,2025-09-01 22:52:45.634506+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,et,123.00,Concluído
c5d4fe29-e756-4d96-9557-1643f8f53cef,2025-09-01 21:21:13.689242+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,embreagem,1000.00,Concluído
d19d76fa-a790-4be3-a578-c0ce6026afc9,2025-09-01 22:39:18.668552+00,445f97a3-6f3e-4326-83ed-e0049ba933ed,2025-09-01,teste,1242.00,Concluído"""
                
                # Dados de Usuários
                users_data = """id,created_at,nome,email,funcao,acesso
2db6198e-86ea-44a2-99cc-17a6b1921e99,2025-08-14 21:33:50.514768+00,Nicolas Fernandes Oliveira,nicolasfernandes789@gmail.com,DBA,master
650b51ba-dfa2-47ee-a2e7-44ae0f92c736,2025-09-02 13:58:19.289312+00,tester,nicolasfernandeso@outlook.com,tester,user"""
                
                # Dados de Ponto
                points_data = """id,created_at,tipo,utilizador,data,latitude,longitude
048bdc49-a1b2-4d5c-a755-294b806aa9ba,2025-09-04 12:43:47.413589+00,ENTRADA,nicolasfernandeso@outlook.com,2025-09-04 09:43:47,-23.5791541523325,-46.5913287501795
0c61ef02-be7e-4ade-ad7b-fb829a509d93,2025-09-05 21:26:34.807594+00,ENTRADA,nicolasfernandeso@outlook.com,2025-09-05 18:26:34,,
122874cf-7468-4808-82dd-98d7a7c3d2f2,2025-08-30 02:56:12.07045+00,ENTRADA,nicolasfernandes789@gmail.com,2025-08-29 23:56:11,,
148bc842-c451-476f-9167-e65d5a6102ea,2025-08-20 01:06:02.840647+00,SAÍDA,nicolasfernandes789@gmail.com,2025-08-19 22:05:23,,
19291b77-2729-49c5-971f-0b9f8515e3c7,2025-09-01 22:52:32.913521+00,SAÍDA,nicolasfernandes789@gmail.com,2025-09-01 19:52:32,,"""
                
                # Converter para DataFrames
                self.vehicles = pd.read_csv(io.StringIO(vehicles_data))
                self.vehicle_uses = pd.read_csv(io.StringIO(uses_data))
                self.maintenances = pd.read_csv(io.StringIO(maintenances_data))
                self.users = pd.read_csv(io.StringIO(users_data))
                self.point_records = pd.read_csv(io.StringIO(points_data))
                
                # Converter datas
                self._converter_datas()
                
                # Salvar no session state
                st.session_state.dados_carregados = True
                st.session_state.dados_veiculos = self.vehicles
                st.session_state.dados_utilizacoes = self.vehicle_uses
                st.session_state.dados_manutencoes = self.maintenances
                st.session_state.dados_usuarios = self.users
                st.session_state.dados_ponto = self.point_records
                
                st.success("✅ Dados de exemplo carregados com sucesso!")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados de exemplo: {e}")

    def _converter_datas(self):
        """Converte colunas de data"""
        try:
            # Vehicles
            if 'created_at' in self.vehicles.columns:
                self.vehicles['created_at'] = pd.to_datetime(self.vehicles['created_at'], errors='coerce')
            
            # Vehicle Uses
            if 'created_at' in self.vehicle_uses.columns:
                self.vehicle_uses['created_at'] = pd.to_datetime(self.vehicle_uses['created_at'], errors='coerce')
            if 'data_inicio' in self.vehicle_uses.columns:
                self.vehicle_uses['data_inicio'] = pd.to_datetime(self.vehicle_uses['data_inicio'], format='mixed', errors='coerce')
            if 'data_fim' in self.vehicle_uses.columns:
                self.vehicle_uses['data_fim'] = pd.to_datetime(self.vehicle_uses['data_fim'], format='mixed', errors='coerce')
            
            # Point Records
            if 'created_at' in self.point_records.columns:
                self.point_records['created_at'] = pd.to_datetime(self.point_records['created_at'], errors='coerce')
            if 'data' in self.point_records.columns:
                self.point_records['data'] = pd.to_datetime(self.point_records['data'], errors='coerce')
            
            # Maintenances
            if 'created_at' in self.maintenances.columns:
                self.maintenances['created_at'] = pd.to_datetime(self.maintenances['created_at'], errors='coerce')
            if 'data_manutencao' in self.maintenances.columns:
                self.maintenances['data_manutencao'] = pd.to_datetime(self.maintenances['data_manutencao'], errors='coerce')
                
        except Exception as e:
            st.warning(f"Aviso na conversão de datas: {e}")

    def interface_upload(self):
        """Interface para upload de arquivos"""
        st.markdown('<h1 class="main-header">📤 Upload de Dados - Gestão de Frotas</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="upload-section">
            <h3>📁 Faça upload dos arquivos CSV</h3>
            <p>Selecione os 5 arquivos necessários para carregar o dashboard:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload de múltiplos arquivos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚗 Veículos")
            uploaded_vehicles = st.file_uploader("vehicles_rows.csv", type="csv", key="vehicles")
            
            st.subheader("📈 Utilizações")
            uploaded_vehicle_uses = st.file_uploader("vehicle_uses_rows.csv", type="csv", key="uses")
        
        with col2:
            st.subheader("🔧 Manutenções")
            uploaded_maintenances = st.file_uploader("maintenances_rows.csv", type="csv", key="maintenances")
            
            st.subheader("👥 Controle")
            uploaded_users = st.file_uploader("users_rows.csv", type="csv", key="users")
            uploaded_point_records = st.file_uploader("point_records_rows.csv", type="csv", key="points")
        
        # Botão para processar
        if st.button("🚀 Processar Dados", type="primary", use_container_width=True):
            self.processar_upload(
                uploaded_vehicles, uploaded_vehicle_uses, uploaded_maintenances,
                uploaded_users, uploaded_point_records
            )
        
        # Opção para usar dados de exemplo
        st.markdown("---")
        st.subheader("🎯 Opção Rápida")
        
        if st.button("📊 Carregar Dados de Exemplo", use_container_width=True):
            self.carregar_dados_exemplo()

    def mostrar_header(self):
        """Cabeçalho do dashboard"""
        st.markdown('<h1 class="main-header">🚗 Dashboard de Gestão de Frotas</h1>', unsafe_allow_html=True)
        
        # Carregar dados do session state
        self.vehicles = st.session_state.dados_veiculos
        self.vehicle_uses = st.session_state.dados_utilizacoes
        self.maintenances = st.session_state.dados_manutencoes
        self.users = st.session_state.dados_usuarios
        self.point_records = st.session_state.dados_ponto
        
        # Métricas principais
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Veículos", len(self.vehicles))
        with col2:
            st.metric("Utilizações", len(self.vehicle_uses))
        with col3:
            st.metric("Manutenções", len(self.maintenances))
        with col4:
            st.metric("Registros Ponto", len(self.point_records))
        with col5:
            if not self.maintenances.empty and 'custo' in self.maintenances.columns:
                custo_total = self.maintenances['custo'].sum()
                st.metric("Custo Manutenções", f"R$ {custo_total:,.2f}")
            else:
                st.metric("Custo Manutenções", "R$ 0,00")

    def calcular_horas_trabalhadas(self):
        """Calcula horas trabalhadas por dia e mês para cada usuário"""
        if self.point_records is None or self.point_records.empty:
            return None
            
        try:
            # Garantir que a coluna data é datetime
            if 'data' in self.point_records.columns:
                if not pd.api.types.is_datetime64_any_dtype(self.point_records['data']):
                    self.point_records['data'] = pd.to_datetime(self.point_records['data'], errors='coerce')
            
            # Ordenar por usuário e data
            df_ponto = self.point_records.sort_values(['utilizador', 'data']).copy()
            
            # Criar colunas para dia e mês
            df_ponto['dia'] = df_ponto['data'].dt.date
            df_ponto['mes'] = df_ponto['data'].dt.to_period('M')
            
            horas_trabalhadas = []
            
            # Para cada usuário, calcular horas trabalhadas
            for usuario in df_ponto['utilizador'].unique():
                user_data = df_ponto[df_ponto['utilizador'] == usuario].copy()
                
                # Calcular por dia
                for dia in user_data['dia'].unique():
                    dia_data = user_data[user_data['dia'] == dia].sort_values('data')
                    
                    # Encontrar pares de ENTRADA/SAÍDA
                    entradas = dia_data[dia_data['tipo'] == 'ENTRADA']
                    saidas = dia_data[dia_data['tipo'] == 'SAÍDA']
                    
                    total_horas_dia = 0
                    
                    for _, entrada in entradas.iterrows():
                        # Encontrar saída correspondente (próxima saída após a entrada)
                        saida_correspondente = saidas[saidas['data'] > entrada['data']].head(1)
                        
                        if not saida_correspondente.empty:
                            horas_trabalhadas_dia = (saida_correspondente.iloc[0]['data'] - entrada['data']).total_seconds() / 3600
                            total_horas_dia += max(0, horas_trabalhadas_dia)  # Evitar valores negativos
                    
                    if total_horas_dia > 0:
                        horas_trabalhadas.append({
                            'utilizador': usuario,
                            'periodo': dia,
                            'tipo_periodo': 'Dia',
                            'horas_trabalhadas': round(total_horas_dia, 2)
                        })
                
                # Calcular por mês
                for mes in user_data['mes'].unique():
                    mes_data = user_data[user_data['mes'] == mes]
                    total_horas_mes = mes_data.groupby('utilizador')['horas_trabalhadas'].sum().iloc[0] if 'horas_trabalhadas' in mes_data.columns else 0
                    
                    horas_trabalhadas.append({
                        'utilizador': usuario,
                        'periodo': mes,
                        'tipo_periodo': 'Mês',
                        'horas_trabalhadas': round(total_horas_mes, 2)
                    })
            
            return pd.DataFrame(horas_trabalhadas) if horas_trabalhadas else None
            
        except Exception as e:
            st.error(f"Erro ao calcular horas trabalhadas: {e}")
            return None

    def aba_visao_geral(self):
        """Aba com visão geral"""
        st.header("📊 Visão Geral")
        
        # Gráficos principais
        col1, col2 = st.columns(2)
        
        with col1:
            # Status dos veículos
            if 'status' in self.vehicles.columns:
                status_count = self.vehicles['status'].value_counts()
                fig = px.pie(values=status_count.values, names=status_count.index, 
                            title="Status dos Veículos",
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tipo de veículo
            if 'tipo' in self.vehicles.columns:
                tipo_count = self.vehicles['tipo'].value_counts()
                fig = px.bar(x=tipo_count.index, y=tipo_count.values,
                            title="Distribuição por Tipo de Veículo",
                            labels={'x': 'Tipo', 'y': 'Quantidade'},
                            color_discrete_sequence=['#6366F1'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Segunda linha de gráficos
        col3, col4 = st.columns(2)
        
        with col3:
            # Utilizações por veículo (top 5)
            if not self.vehicle_uses.empty and 'vehicle_id' in self.vehicle_uses.columns:
                vehicle_usage = self.vehicle_uses['vehicle_id'].value_counts().head(5)
                if not vehicle_usage.empty:
                    vehicle_labels = []
                    for vid in vehicle_usage.index:
                        veiculo = self.vehicles[self.vehicles['id'] == vid]
                        if not veiculo.empty and 'placa' in veiculo.columns:
                            vehicle_labels.append(f"{veiculo.iloc[0]['placa']}")
                        else:
                            vehicle_labels.append(str(vid)[:8])
                    
                    fig = px.bar(x=vehicle_labels, y=vehicle_usage.values,
                                title="Top 5 Veículos Mais Utilizados",
                                labels={'x': 'Veículo', 'y': 'Utilizações'},
                                color_discrete_sequence=['#10B981'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Custo de manutenção por veículo
            if not self.maintenances.empty and 'vehicle_id' in self.maintenances.columns:
                maint_costs = self.maintenances.groupby('vehicle_id')['custo'].sum().nlargest(5)
                if not maint_costs.empty:
                    fig = px.bar(x=maint_costs.index.astype(str), y=maint_costs.values,
                                title="Top 5 Veículos - Custos de Manutenção",
                                labels={'x': 'Veículo', 'y': 'Custo (R$)'},
                                color_discrete_sequence=['#F59E0B'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

    def aba_veiculos(self):
        """Aba detalhada de veículos"""
        st.header("🚗 Gestão de Veículos")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            if 'status' in self.vehicles.columns:
                status_options = self.vehicles['status'].unique()
                status_filter = st.multiselect("Filtrar por Status:", 
                                             status_options,
                                             default=status_options)
        
        with col2:
            if 'tipo' in self.vehicles.columns:
                tipo_options = self.vehicles['tipo'].unique()
                tipo_filter = st.multiselect("Filtrar por Tipo:",
                                           tipo_options,
                                           default=tipo_options)
        
        # Aplicar filtros
        filtered_vehicles = self.vehicles.copy()
        if 'status' in self.vehicles.columns and status_filter:
            filtered_vehicles = filtered_vehicles[filtered_vehicles['status'].isin(status_filter)]
        if 'tipo' in self.vehicles.columns and tipo_filter:
            filtered_vehicles = filtered_vehicles[filtered_vehicles['tipo'].isin(tipo_filter)]
        
        # Mostrar tabela
        st.subheader("Lista de Veículos")
        colunas_mostrar = []
        for col in ['placa', 'marca', 'modelo', 'status', 'tipo']:
            if col in filtered_vehicles.columns:
                colunas_mostrar.append(col)
        
        if colunas_mostrar:
            st.dataframe(filtered_vehicles[colunas_mostrar], use_container_width=True)
        
        # Estatísticas
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Veículos Filtrados", len(filtered_vehicles))
        with col4:
            if 'status' in filtered_vehicles.columns:
                disponiveis = len(filtered_vehicles[filtered_vehicles['status'] == 'DISPONÍVEL'])
                st.metric("Disponíveis", disponiveis)
        with col5:
            if 'status' in filtered_vehicles.columns:
                em_uso = len(filtered_vehicles[filtered_vehicles['status'] == 'EM USO'])
                st.metric("Em Uso", em_uso)

    def aba_utilizacao(self):
        """Aba de utilização de veículos"""
        st.header("📈 Análise de Utilização")
        
        # Calcular duração se possível
        if all(col in self.vehicle_uses.columns for col in ['data_inicio', 'data_fim']):
            # VERIFICAR SE AS DATAS SÃO VÁLIDAS ANTES DE CALCULAR
            if self.vehicle_uses['data_inicio'].notna().any() and self.vehicle_uses['data_fim'].notna().any():
                self.vehicle_uses['duracao_horas'] = (
                    self.vehicle_uses['data_fim'] - self.vehicle_uses['data_inicio']
                ).dt.total_seconds() / 3600
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top motoristas
            if 'utilizador' in self.vehicle_uses.columns:
                top_motoristas = self.vehicle_uses['utilizador'].value_counts().head(10)
                if not top_motoristas.empty:
                    fig = px.bar(x=top_motoristas.index, y=top_motoristas.values,
                                title="Top 10 Motoristas",
                                labels={'x': 'Motorista', 'y': 'Quantidade de Utilizações'},
                                color_discrete_sequence=['#8B5CF6'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Duração média por motorista
            if 'duracao_horas' in self.vehicle_uses.columns and 'utilizador' in self.vehicle_uses.columns:
                duracao_media = self.vehicle_uses.groupby('utilizador')['duracao_horas'].mean().nlargest(10)
                if not duracao_media.empty:
                    fig = px.bar(x=duracao_media.index, y=duracao_media.values,
                                title="Duração Média por Motorista (Horas)",
                                labels={'x': 'Motorista', 'y': 'Horas'},
                                color_discrete_sequence=['#EC4899'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas de utilização
        st.subheader("📊 Estatísticas de Utilização")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            if 'duracao_horas' in self.vehicle_uses.columns:
                total_horas = self.vehicle_uses['duracao_horas'].sum()
                st.metric("Total Horas Utilizadas", f"{total_horas:.1f}h")
        
        with col4:
            if 'duracao_horas' in self.vehicle_uses.columns:
                media_horas = self.vehicle_uses['duracao_horas'].mean()
                st.metric("Duração Média", f"{media_horas:.1f}h")
        
        with col5:
            if 'vehicle_id' in self.vehicle_uses.columns and not self.vehicle_uses.empty:
                veiculo_mais_usado = self.vehicle_uses['vehicle_id'].value_counts().idxmax()
                veiculo_info = self.vehicles[self.vehicles['id'] == veiculo_mais_usado]
                if not veiculo_info.empty and 'placa' in veiculo_info.columns:
                    st.metric("Veículo Mais Usado", f"{veiculo_info.iloc[0]['placa']}")
        
        with col6:
            total_utilizacoes = len(self.vehicle_uses)
            st.metric("Total Utilizações", total_utilizacoes)

    def aba_manutencoes(self):
        """Aba de manutenções"""
        st.header("🔧 Gestão de Manutenções")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Custos totais por veículo
            if 'vehicle_id' in self.maintenances.columns and 'custo' in self.maintenances.columns:
                custos_veiculo = self.maintenances.groupby('vehicle_id')['custo'].sum().nlargest(10)
                if not custos_veiculo.empty:
                    fig = px.bar(x=custos_veiculo.index.astype(str), y=custos_veiculo.values,
                                title="Custos de Manutenção por Veículo",
                                labels={'x': 'Veículo', 'y': 'Custo Total (R$)'},
                                color_discrete_sequence=['#EF4444'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Evolução temporal dos custos
            if 'data_manutencao' in self.maintenances.columns and 'custo' in self.maintenances.columns:
                try:
                    # VERIFICAR SE AS DATAS SÃO VÁLIDAS
                    if self.maintenances['data_manutencao'].notna().any():
                        custos_mensais = self.maintenances.groupby(
                            self.maintenances['data_manutencao'].dt.to_period('M')
                        )['custo'].sum()
                        if not custos_mensais.empty:
                            custos_mensais.index = custos_mensais.index.astype(str)
                            fig = px.line(x=custos_mensais.index, y=custos_mensais.values,
                                         title="Evolução Mensal dos Custos",
                                         labels={'x': 'Mês', 'y': 'Custo (R$)'},
                                         color_discrete_sequence=['#F59E0B'])
                            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        
        # Métricas de custos
        st.subheader("💰 Métricas Financeiras")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            if 'custo' in self.maintenances.columns:
                custo_total = self.maintenances['custo'].sum()
                st.metric("Custo Total", f"R$ {custo_total:,.2f}")
        
        with col4:
            if 'custo' in self.maintenances.columns:
                custo_medio = self.maintenances['custo'].mean()
                st.metric("Custo Médio", f"R$ {custo_medio:,.2f}")
        
        with col5:
            total_manutencoes = len(self.maintenances)
            st.metric("Total Manutenções", total_manutencoes)
        
        with col6:
            if 'custo' in self.maintenances.columns and not self.maintenances.empty:
                manut_mais_cara = self.maintenances['custo'].max()
                st.metric("Manutenção Mais Cara", f"R$ {manut_mais_cara:,.2f}")
        
        # Tabela de manutenções
        st.subheader("📋 Detalhes das Manutenções")
        colunas_mostrar = []
        for col in ['data_manutencao', 'descricao', 'custo', 'status']:
            if col in self.maintenances.columns:
                colunas_mostrar.append(col)
        
        if colunas_mostrar:
            st.dataframe(self.maintenances[colunas_mostrar], use_container_width=True)

    def aba_controle_ponto(self):
        """Aba de controle de ponto"""
        st.header("⏰ Controle de Ponto")
        
        # CORREÇÃO: Verificar se a coluna 'data' existe e é datetime
        if 'data' in self.point_records.columns:
            # Verificar se já é datetime, se não, converter
            if not pd.api.types.is_datetime64_any_dtype(self.point_records['data']):
                self.point_records['data'] = pd.to_datetime(self.point_records['data'], errors='coerce')
            
            # Só criar a coluna 'hora' se as datas forem válidas
            if self.point_records['data'].notna().any():
                self.point_records['hora'] = self.point_records['data'].dt.hour
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por tipo
            if 'tipo' in self.point_records.columns:
                tipo_ponto = self.point_records['tipo'].value_counts()
                if not tipo_ponto.empty:
                    fig = px.pie(values=tipo_ponto.values, names=tipo_ponto.index,
                                title="Distribuição de Tipos de Registro",
                                color_discrete_sequence=px.colors.sequential.Plasma)
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Registros por hora - SÓ SE A COLUNA HORA EXISTIR
            if 'hora' in self.point_records.columns and self.point_records['hora'].notna().any():
                registros_hora = self.point_records['hora'].value_counts().sort_index()
                if not registros_hora.empty:
                    fig = px.bar(x=registros_hora.index, y=registros_hora.values,
                                title="Registros por Hora do Dia",
                                labels={'x': 'Hora', 'y': 'Quantidade'},
                                color_discrete_sequence=['#06B6D4'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚠️ Dados de hora não disponíveis para análise")
        
        # Top usuários
        st.subheader("👥 Atividade por Usuário")
        if 'utilizador' in self.point_records.columns:
            usuarios_ativos = self.point_records['utilizador'].value_counts().head(10)
            if not usuarios_ativos.empty:
                fig = px.bar(x=usuarios_ativos.index, y=usuarios_ativos.values,
                            title="Top 10 Usuários - Registros de Ponto",
                            labels={'x': 'Usuário', 'y': 'Registros'},
                            color_discrete_sequence=['#84CC16'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    def aba_manutencoes_detalhadas(self):
        """Aba detalhada de manutenções por veículo"""
        st.header("🔧 Manutenções por Veículo")
        
        if self.maintenances is None or self.maintenances.empty:
            st.error("Dados de manutenções não disponíveis!")
            return
        
        # Selecionar veículo
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Lista de veículos com manutenções
            veiculos_com_manutencao = self.maintenances['vehicle_id'].unique()
            veiculos_info = []
            
            for vehicle_id in veiculos_com_manutencao:
                veiculo = self.vehicles[self.vehicles['id'] == vehicle_id]
                if not veiculo.empty:
                    veiculos_info.append({
                        'id': vehicle_id,
                        'label': f"{veiculo.iloc[0]['placa']} - {veiculo.iloc[0]['marca']} {veiculo.iloc[0]['modelo']}"
                    })
            
            if veiculos_info:
                veiculo_selecionado = st.selectbox(
                    "Selecione o Veículo:",
                    options=[v['id'] for v in veiculos_info],
                    format_func=lambda x: next((v['label'] for v in veiculos_info if v['id'] == x), x)
                )
            else:
                st.warning("Nenhum veículo com manutenção encontrado")
                return
        
        with col2:
            # Estatísticas do veículo selecionado
            veiculo_info = self.vehicles[self.vehicles['id'] == veiculo_selecionado].iloc[0]
            manutencoes_veiculo = self.maintenances[self.maintenances['vehicle_id'] == veiculo_selecionado]
            
            st.metric("Total Manutenções", len(manutencoes_veiculo))
            st.metric("Custo Total", f"R$ {manutencoes_veiculo['custo'].sum():,.2f}")
            st.metric("Custo Médio", f"R$ {manutencoes_veiculo['custo'].mean():,.2f}")
        
        # Detalhes das manutenções do veículo selecionado
        st.subheader(f"📋 Histórico de Manutenções - {veiculo_info['placa']}")
        
        colunas_mostrar = ['data_manutencao', 'descricao', 'custo', 'status']
        colunas_disponiveis = [col for col in colunas_mostrar if col in manutencoes_veiculo.columns]
        
        if colunas_disponiveis:
            # Ordenar por data
            manutencoes_veiculo = manutencoes_veiculo.sort_values('data_manutencao', ascending=False)
            st.dataframe(manutencoes_veiculo[colunas_disponiveis], use_container_width=True)
        
        # Gráfico de custos ao longo do tempo
        if 'data_manutencao' in manutencoes_veiculo.columns and 'custo' in manutencoes_veiculo.columns:
            st.subheader("📈 Evolução dos Custos")
            
            # Agrupar por mês
            try:
                manutencoes_veiculo['mes'] = manutencoes_veiculo['data_manutencao'].dt.to_period('M')
                custos_mensais = manutencoes_veiculo.groupby('mes')['custo'].sum()
                
                if not custos_mensais.empty:
                    custos_mensais.index = custos_mensais.index.astype(str)
                    fig = px.line(
                        x=custos_mensais.index, 
                        y=custos_mensais.values,
                        title=f"Evolução Mensal dos Custos - {veiculo_info['placa']}",
                        labels={'x': 'Mês', 'y': 'Custo (R$)'},
                        color_discrete_sequence=['#F59E0B']
                    )
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível gerar gráfico temporal: {e}")

    def aba_controle_ponto_detalhado(self):
        """Aba detalhada de controle de ponto por usuário"""
        st.header("⏰ Controle de Ponto por Usuário")
        
        if self.point_records is None or self.point_records.empty:
            st.error("Dados de ponto não disponíveis!")
            return
        
        # Calcular horas trabalhadas
        horas_trabalhadas = self.calcular_horas_trabalhadas()
        
        # Selecionar usuário
        usuarios = self.point_records['utilizador'].unique()
        usuario_selecionado = st.selectbox("Selecione o Usuário:", usuarios)
        
        # Filtrar dados do usuário selecionado
        user_data = self.point_records[self.point_records['utilizador'] == usuario_selecionado].copy()
        
        # Ordenar por data
        user_data = user_data.sort_values('data')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Estatísticas - {usuario_selecionado}")
            
            # Métricas básicas
            total_registros = len(user_data)
            entradas = len(user_data[user_data['tipo'] == 'ENTRADA'])
            saidas = len(user_data[user_data['tipo'] == 'SAÍDA'])
            
            st.metric("Total Registros", total_registros)
            st.metric("Entradas", entradas)
            st.metric("Saídas", saidas)
            
            # Horas trabalhadas (se disponível)
            if horas_trabalhadas is not None:
                horas_usuario = horas_trabalhadas[horas_trabalhadas['utilizador'] == usuario_selecionado]
                if not horas_usuario.empty:
                    horas_hoje = horas_usuario[
                        (horas_usuario['tipo_periodo'] == 'Dia') & 
                        (horas_usuario['periodo'] == datetime.now().date())
                    ]
                    horas_mes_atual = horas_usuario[
                        (horas_usuario['tipo_periodo'] == 'Mês') & 
                        (horas_usuario['periodo'] == pd.Period(datetime.now(), 'M'))
                    ]
                    
                    if not horas_hoje.empty:
                        st.metric("Horas Hoje", f"{horas_hoje.iloc[0]['horas_trabalhadas']}h")
                    if not horas_mes_atual.empty:
                        st.metric("Horas Este Mês", f"{horas_mes_atual.iloc[0]['horas_trabalhadas']}h")
        
        with col2:
            st.subheader("📅 Distribuição por Tipo")
            tipo_ponto = user_data['tipo'].value_counts()
            
            if not tipo_ponto.empty:
                fig = px.pie(
                    values=tipo_ponto.values, 
                    names=tipo_ponto.index,
                    title=f"Tipos de Registro - {usuario_selecionado}",
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Histórico de registros
        st.subheader("📋 Histórico de Registros")
        
        colunas_mostrar = ['data', 'tipo']
        if 'latitude' in user_data.columns and 'longitude' in user_data.columns:
            colunas_mostrar.extend(['latitude', 'longitude'])
        
        colunas_disponiveis = [col for col in colunas_mostrar if col in user_data.columns]
        
        if colunas_disponiveis:
            st.dataframe(user_data[colunas_disponiveis], use_container_width=True)
        
        # Gráfico de horas trabalhadas (se disponível)
        if horas_trabalhadas is not None:
            horas_usuario = horas_trabalhadas[horas_trabalhadas['utilizador'] == usuario_selecionado]
            
            if not horas_usuario.empty:
                st.subheader("⏱️ Horas Trabalhadas")
                
                # Horas por dia (últimos 30 dias)
                horas_dia = horas_usuario[horas_usuario['tipo_periodo'] == 'Dia'].tail(30)
                
                if not horas_dia.empty:
                    fig = px.bar(
                        x=horas_dia['periodo'].astype(str),
                        y=horas_dia['horas_trabalhadas'],
                        title=f"Horas Trabalhadas por Dia - {usuario_selecionado}",
                        labels={'x': 'Data', 'y': 'Horas Trabalhadas'},
                        color_discrete_sequence=['#10B981']
                    )
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Horas por mês
                horas_mes = horas_usuario[horas_usuario['tipo_periodo'] == 'Mês']
                
                if not horas_mes.empty:
                    fig = px.bar(
                        x=horas_mes['periodo'].astype(str),
                        y=horas_mes['horas_trabalhadas'],
                        title=f"Horas Trabalhadas por Mês - {usuario_selecionado}",
                        labels={'x': 'Mês', 'y': 'Horas Trabalhadas'},
                        color_discrete_sequence=['#6366F1']
                    )
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

    def aba_relatorio_horas(self):
        """Aba com relatório completo de horas trabalhadas"""
        st.header("📊 Relatório de Horas Trabalhadas")
        
        horas_trabalhadas = self.calcular_horas_trabalhadas()
        
        if horas_trabalhadas is None or horas_trabalhadas.empty:
            st.warning("Não foi possível calcular horas trabalhadas. Verifique os dados de ponto.")
            return
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            periodo_selecionado = st.selectbox(
                "Tipo de Período:",
                ['Dia', 'Mês', 'Todos']
            )
        
        with col2:
            usuarios_selecionados = st.multiselect(
                "Usuários:",
                options=horas_trabalhadas['utilizador'].unique(),
                default=horas_trabalhadas['utilizador'].unique()
            )
        
        # Aplicar filtros
        dados_filtrados = horas_trabalhadas[horas_trabalhadas['utilizador'].isin(usuarios_selecionados)]
        
        if periodo_selecionado != 'Todos':
            dados_filtrados = dados_filtrados[dados_filtrados['tipo_periodo'] == periodo_selecionado]
        
        # Métricas gerais
        st.subheader("📈 Métricas Gerais")
        
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            total_horas = dados_filtrados['horas_trabalhadas'].sum()
            st.metric("Total Horas", f"{total_horas:.1f}h")
        
        with col4:
            media_horas = dados_filtrados['horas_trabalhadas'].mean()
            st.metric("Média por Período", f"{media_horas:.1f}h")
        
        with col5:
            total_usuarios = dados_filtrados['utilizador'].nunique()
            st.metric("Usuários", total_usuarios)
        
        with col6:
            total_periodos = dados_filtrados['periodo'].nunique()
            st.metric("Períodos", total_periodos)
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento por Usuário")
        st.dataframe(dados_filtrados, use_container_width=True)
        
        # Gráficos
        col7, col8 = st.columns(2)
        
        with col7:
            # Top usuários por horas totais
            horas_por_usuario = dados_filtrados.groupby('utilizador')['horas_trabalhadas'].sum().sort_values(ascending=False)
            
            if not horas_por_usuario.empty:
                fig = px.bar(
                    x=horas_por_usuario.index,
                    y=horas_por_usuario.values,
                    title="Total de Horas por Usuário",
                    labels={'x': 'Usuário', 'y': 'Horas Trabalhadas'},
                    color_discrete_sequence=['#8B5CF6']
                )
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col8:
            # Evolução temporal (apenas para dias)
            if periodo_selecionado == 'Dia':
                evolucao_diaria = dados_filtrados.groupby('periodo')['horas_trabalhadas'].sum().sort_index()
                
                if not evolucao_diaria.empty:
                    fig = px.line(
                        x=evolucao_diaria.index.astype(str),
                        y=evolucao_diaria.values,
                        title="Evolução Diária de Horas Trabalhadas",
                        labels={'x': 'Data', 'y': 'Horas Trabalhadas'},
                        color_discrete_sequence=['#EC4899']
                    )
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)

    def executar_dashboard(self):
        """Executa o dashboard completo"""
        # Verificar se dados foram carregados
        if not st.session_state.get('dados_carregados', False):
            self.interface_upload()
            return
        
        self.mostrar_header()
        
        # Sidebar com navegação
        st.sidebar.title("🌙 Navegação")
        aba_selecionada = st.sidebar.radio(
            "Selecione a Aba:",
            [
                "Visão Geral", 
                "Veículos", 
                "Utilização", 
                "Manutenções",
                "Manutenções por Veículo",
                "Controle de Ponto",
                "Ponto por Usuário",
                "Relatório de Horas"
            ]
        )
        
        # Botão para recarregar dados
        if st.sidebar.button("🔄 Carregar Novos Dados", use_container_width=True):
            st.session_state.dados_carregados = False
            st.rerun()
        
        # Navegação entre abas
        if aba_selecionada == "Visão Geral":
            self.aba_visao_geral()
        elif aba_selecionada == "Veículos":
            self.aba_veiculos()
        elif aba_selecionada == "Utilização":
            self.aba_utilizacao()
        elif aba_selecionada == "Manutenções":
            self.aba_manutencoes()
        elif aba_selecionada == "Manutenções por Veículo":
            self.aba_manutencoes_detalhadas()
        elif aba_selecionada == "Controle de Ponto":
            self.aba_controle_ponto()
        elif aba_selecionada == "Ponto por Usuário":
            self.aba_controle_ponto_detalhado()
        elif aba_selecionada == "Relatório de Horas":
            self.aba_relatorio_horas()
        
        # Informações na sidebar
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **💡 Novas Funcionalidades:**
        - 🔧 Manutenções detalhadas por veículo
        - 👤 Controle de ponto por usuário  
        - ⏱️ Cálculo de horas trabalhadas
        - 📊 Relatórios completos de horas
        """)

# Executar a aplicação
if __name__ == "__main__":
    app = GestaoFrotasStreamlit()
    app.executar_dashboard()