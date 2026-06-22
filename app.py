import streamlit as st
import requests
import pandas as pd
import json
import time
import io
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="Solar Lead Finder",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CREDENCIAIS
# Altere usuário e senha conforme desejar
# ─────────────────────────────────────────

USUARIOS = {
    "admin":  hashlib.sha256("solar2024".encode()).hexdigest(),
    "equipe": hashlib.sha256("leads2024".encode()).hexdigest(),
}

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def tela_login():
    st.markdown("""
    <style>
    .stApp{background:#0f1117}
    label{color:#94a3b8!important;font-size:13px!important}
    h2{color:#f1f5f9!important;text-align:center;font-size:18px!important;margin-bottom:4px!important}
    .stButton>button{background:#f59e0b!important;color:#1c1400!important;border:none!important;
    border-radius:8px!important;font-weight:600!important;width:100%!important;padding:11px!important;font-size:14px!important;margin-top:8px!important}
    .stButton>button:hover{background:#fbbf24!important}
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#161b27;border:0.5px solid #2d3748;border-radius:14px;padding:36px 32px;text-align:center">
        <div style="width:52px;height:52px;background:#f59e0b;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;font-size:26px;margin-bottom:16px">☀️</div>
        <h2 style="color:#f1f5f9;margin:0 0 4px">Solar Lead Finder</h2>
        <p style="color:#475569;font-size:13px;margin-bottom:0">Acesso restrito</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="usuário")
        senha   = st.text_input("Senha", type="password", placeholder="••••••••")
        if st.button("Entrar"):
            if usuario in USUARIOS and USUARIOS[usuario] == hash_senha(senha):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    tela_login()
    st.stop()

# ─────────────────────────────────────────
# CSS PRINCIPAL (só carrega após login)
# ─────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid #2d3748; }
    h1,h2,h3,h4,p,label,span { color: #e2e8f0 !important; }
    .stMarkdown p { color: #94a3b8 !important; }
    .stSelectbox > div, .stMultiSelect > div, .stTextInput > div {
        background-color: #1e293b !important; border: 1px solid #2d3748 !important;
        border-radius: 8px !important; color: #e2e8f0 !important; }
    .stButton > button {
        background-color: #f59e0b !important; color: #1c1400 !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; width: 100% !important;
        padding: 12px !important; font-size: 15px !important; }
    .stButton > button:hover { background-color: #fbbf24 !important; }
    .stDownloadButton > button {
        background-color: #1e3a5f !important; color: #60a5fa !important;
        border: 1px solid #1d4ed8 !important; border-radius: 8px !important; width: 100% !important; }
    [data-testid="stMetric"] {
        background-color: #161b27 !important; border: 1px solid #2d3748 !important;
        border-radius: 10px !important; padding: 16px !important; }
    [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #475569 !important; font-size: 12px !important; }
    hr { border-color: #2d3748 !important; }
    .stCheckbox label { color: #cbd5e1 !important; font-size: 13px !important; }
    .stSuccess { background-color: #052e16 !important; color: #4ade80 !important; }
    .stWarning { background-color: #1c1400 !important; color: #fbbf24 !important; }
    .stError   { background-color: #2e0f0f !important; color: #f87171 !important; }
    .stInfo    { background-color: #0c1a2e !important; color: #60a5fa !important; }
    .badge-fonte {
        display: inline-block; background: #052e16; color: #4ade80;
        border: 1px solid #166534; border-radius: 4px;
        padding: 2px 8px; font-size: 11px; margin-right: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DADOS DEMO
# ─────────────────────────────────────────

DEMO_LEADS = {
    "MG": [
        {"modulo":"Rural-Irrigacao","nome":"Fazenda Serra Verde","municipio":"Araçuaí","area_ha":480,"potencial":"Alto","situacao_rede":"Sem rede próxima","observacoes":"Área: 480 ha · Outorga ANA ativa","lat":-16.85,"lon":-42.07,"fonte":"SICAR-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Mineracao","nome":"Min. Vale do Jequitinhonha Ltda","municipio":"Itamarandiba","area_ha":320,"potencial":"Alto","situacao_rede":"Área remota — alto risco diesel","observacoes":"Fase: Concessão de Lavra · Substância: Ferro","lat":-17.85,"lon":-42.85,"fonte":"ANM-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Concessão de Lavra"},
        {"modulo":"ACL-GrupoA","nome":"Cerâmica Industrial Mucuri SA","municipio":"Teófilo Otoni","area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":"Demanda: 2.4 MW","lat":0,"lon":0,"fonte":"CCEE-demo","cpf_cnpj":"12.345.678/0001-90","socio":"João Silva","telefone":"33991234567","email":"contato@ceramica.com.br","porte":"Grande","cnae":"Fabricação de produtos cerâmicos","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Diesel-Gerador","nome":"Frigorífico Bom Pastor Ltda","municipio":"Caratinga","area_ha":0,"potencial":"Médio","situacao_rede":"Usa diesel — candidato solar/híbrido","observacoes":"Potência: 320 kW","lat":-19.78,"lon":-42.13,"fonte":"ANEEL-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Operação"},
        {"modulo":"Mineracao","nome":"Mineradora São Domingos","municipio":"Diamantina","area_ha":520,"potencial":"Alto","situacao_rede":"Área remota — alto risco diesel","observacoes":"Fase: Concessão de Lavra · Substância: Ouro","lat":-18.24,"lon":-43.60,"fonte":"ANM-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Concessão de Lavra"},
        {"modulo":"Rural-Irrigacao","nome":"Fazenda Três Barras","municipio":"Januária","area_ha":620,"potencial":"Alto","situacao_rede":"Sem rede próxima","observacoes":"Área: 620 ha","lat":-15.48,"lon":-44.36,"fonte":"SICAR-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Ativo"},
    ],
    "BA": [
        {"modulo":"Rural-Irrigacao","nome":"Fazenda Chapada","municipio":"Barreiras","area_ha":720,"potencial":"Alto","situacao_rede":"Sem rede próxima","observacoes":"Área: 720 ha · Pivô central","lat":-12.15,"lon":-44.99,"fonte":"SICAR-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Mineracao","nome":"Mineradora Chapada Diamantina","municipio":"Mucugê","area_ha":560,"potencial":"Alto","situacao_rede":"Área remota — alto risco diesel","observacoes":"Fase: Concessão de Lavra · Substância: Diamante","lat":-13.00,"lon":-41.36,"fonte":"ANM-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Concessão de Lavra"},
        {"modulo":"ACL-GrupoA","nome":"Petroquímica Camaçari Ltda","municipio":"Camaçari","area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":"Demanda: 15.0 MW","lat":-12.69,"lon":-38.32,"fonte":"CCEE-demo","cpf_cnpj":"45.678.901/0001-33","socio":"Maria Souza","telefone":"71991234567","email":"energia@petroquimica.com.br","porte":"Grande","cnae":"Fabricação de produtos químicos","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Diesel-Gerador","nome":"Cerâmica Nordeste SA","municipio":"Vitória da Conquista","area_ha":0,"potencial":"Médio","situacao_rede":"Usa diesel — candidato solar/híbrido","observacoes":"Potência: 430 kW","lat":-14.86,"lon":-40.84,"fonte":"ANEEL-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Operação"},
    ],
    "ES": [
        {"modulo":"Rural-Irrigacao","nome":"Fazenda Caparaó","municipio":"Alegre","area_ha":160,"potencial":"Médio","situacao_rede":"Verificar","observacoes":"Área: 160 ha","lat":-20.76,"lon":-41.53,"fonte":"SICAR-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"ACL-GrupoA","nome":"Aracruz Celulose SA","municipio":"Aracruz","area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":"Demanda: 22.0 MW","lat":-19.82,"lon":-40.27,"fonte":"CCEE-demo","cpf_cnpj":"67.890.123/0001-55","socio":"Carlos Lima","telefone":"27991234567","email":"energia@aracruz.com.br","porte":"Grande","cnae":"Fabricação de celulose","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Diesel-Gerador","nome":"Pedreiras Capixabas SA","municipio":"Cachoeiro de Itapemirim","area_ha":0,"potencial":"Médio","situacao_rede":"Usa diesel — candidato solar/híbrido","observacoes":"Potência: 420 kW","lat":-20.84,"lon":-41.11,"fonte":"ANEEL-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Operação"},
    ],
    "GO": [
        {"modulo":"Rural-Irrigacao","nome":"Fazenda Cerrado Verde","municipio":"Rio Verde","area_ha":1200,"potencial":"Alto","situacao_rede":"Sem rede próxima","observacoes":"Área: 1200 ha · Pivô central","lat":-17.79,"lon":-50.93,"fonte":"SICAR-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"ACL-GrupoA","nome":"Frigorífico Goiás Ltda","municipio":"Anápolis","area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":"Demanda: 5.8 MW","lat":-16.32,"lon":-48.95,"fonte":"CCEE-demo","cpf_cnpj":"89.012.345/0001-77","socio":"Pedro Alves","telefone":"62991234567","email":"energia@frigorifico.com.br","porte":"Grande","cnae":"Abate de bovinos","codigo_ref":"DEMO","situacao":"Ativo"},
    ],
    "SP": [
        {"modulo":"ACL-GrupoA","nome":"Indústria Metalúrgica Paulista SA","municipio":"Sorocaba","area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":"Demanda: 12.0 MW","lat":-23.50,"lon":-47.45,"fonte":"CCEE-demo","cpf_cnpj":"90.123.456/0001-88","socio":"Ana Costa","telefone":"15991234567","email":"energia@metalurgica.com.br","porte":"Grande","cnae":"Fabricação de estruturas metálicas","codigo_ref":"DEMO","situacao":"Ativo"},
        {"modulo":"Diesel-Gerador","nome":"Mineração Paranapanema","municipio":"Registro","area_ha":280,"potencial":"Alto","situacao_rede":"Área remota — alto risco diesel","observacoes":"Potência: 680 kW","lat":-24.49,"lon":-47.84,"fonte":"ANEEL-demo","cpf_cnpj":"","socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":"DEMO","situacao":"Operação"},
    ],
}

TODOS_ESTADOS = ["MG","BA","ES","SP","GO","MT","PA","RO","TO","MS","PR","RS","SC","RJ","PE","CE","PI","MA"]

# ─────────────────────────────────────────
# FUNÇÕES DE BUSCA
# ─────────────────────────────────────────

HEADERS = {"User-Agent": "SolarLeadFinder/2.0", "Accept": "application/json"}

def get_json(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def calcular_score(lead):
    s = 5.0
    pot = lead.get("potencial", "")
    if pot == "Alto":  s += 2.5
    elif pot in ("Médio","Medio"): s += 1.0
    if "diesel" in str(lead.get("situacao_rede","")).lower(): s += 1.5
    if "remot" in str(lead.get("situacao_rede","")).lower():  s += 1.0
    if lead.get("modulo") == "ACL-GrupoA": s += 1.5
    area = float(lead.get("area_ha", 0) or 0)
    if area >= 500: s += 0.5
    elif area >= 200: s += 0.3
    if lead.get("telefone"): s += 0.5
    if lead.get("cpf_cnpj") and "DEMO" not in str(lead.get("cpf_cnpj","")): s += 0.3
    return round(min(s, 10.0), 1)

def buscar_leads(estados, modulos, situacoes, score_min):
    todos = []
    progress = st.progress(0)
    status = st.empty()
    etapas = max(len(estados) * len(modulos), 1)
    etapa = 0

    for estado in estados:
        leads_estado = DEMO_LEADS.get(estado, [])
        for mod in modulos:
            etapa += 1
            progress.progress(int((etapa / etapas) * 100))
            status.markdown(f"<p style='color:#94a3b8;font-size:12px'>Consultando {mod} em {estado}...</p>", unsafe_allow_html=True)
            leads_mod = []

            if mod == "Rural-Irrigacao":
                dados = get_json("https://consultapublica.car.gov.br/publico/imoveis/index",
                                 params={"estado":estado,"tipo":"IRU","pagina":1,"tamanhoPagina":50})
                if dados and isinstance(dados, list):
                    for item in dados:
                        area = float(item.get("area",0) or 0)
                        if area < 50: continue
                        leads_mod.append({"modulo":"Rural-Irrigacao","nome":item.get("nomePessoa",""),"municipio":item.get("nomeMunicipio",""),"area_ha":round(area,1),"potencial":"Alto" if area>=500 else "Médio","situacao_rede":"Verificar","observacoes":f"Área: {area:.0f} ha","lat":item.get("latitude",0),"lon":item.get("longitude",0),"fonte":"SICAR","cpf_cnpj":item.get("cpf",item.get("cnpj","")),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":item.get("codigo",""),"situacao":item.get("situacao","")})

            elif mod == "Mineracao":
                dados = get_json("https://geo.anm.gov.br/geoserver/sigmine/wfs",
                                 params={"service":"WFS","version":"2.0.0","request":"GetFeature","typeName":"sigmine:BRASIL","outputFormat":"application/json","CQL_FILTER":f"UF='{estado}'","count":100},timeout=40)
                if dados and "features" in dados:
                    for f in dados["features"]:
                        p = f.get("properties",{})
                        area = float(p.get("AREA_HA",0) or 0)
                        fase = p.get("FASE","")
                        leads_mod.append({"modulo":"Mineracao","nome":p.get("NOME",""),"municipio":p.get("MUNICIPIO",""),"area_ha":round(area,1),"potencial":"Alto" if area>=200 else "Médio","situacao_rede":"Área remota — alto risco diesel","observacoes":f"Fase: {fase} · Substância: {p.get('SUB','')}","lat":0,"lon":0,"fonte":"ANM-SIGMINE","cpf_cnpj":p.get("CPF_CNPJ",""),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":p.get("PROCESSO",""),"situacao":fase})

            elif mod == "ACL-GrupoA":
                dados = get_json("https://dadosabertos.aneel.gov.br/api/3/action/datastore_search",
                                 params={"resource_id":"b1bd71e7-d0ad-4214-9053-cbd58e9564a7","limit":100,"filters":json.dumps({"SigUF":estado})})
                if dados and dados.get("success"):
                    for r in dados.get("result",{}).get("records",[]):
                        leads_mod.append({"modulo":"ACL-GrupoA","nome":r.get("NomAgente",""),"municipio":r.get("NomMunicipio",""),"area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":f"Categoria: {r.get('DscCategoria','')}","lat":0,"lon":0,"fonte":"ANEEL","cpf_cnpj":r.get("CnpjParticipante",""),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":r.get("CodCCEE",""),"situacao":"Ativo"})

            elif mod == "Diesel-Gerador":
                dados = get_json("https://dadosabertos.aneel.gov.br/api/3/action/datastore_search",
                                 params={"resource_id":"b1bd71e7-d0ad-4214-9053-cbd58e9564a7","limit":100,"filters":json.dumps({"SigUF":estado,"DscCombustivel":"Óleo Diesel"})})
                if dados and dados.get("success"):
                    for r in dados.get("result",{}).get("records",[]):
                        pot = float(r.get("MdaPotenciaFiscalizadaKw",0) or 0)
                        leads_mod.append({"modulo":"Diesel-Gerador","nome":r.get("NomEmpreendimento",""),"municipio":r.get("NomMunicipio",""),"area_ha":0,"potencial":"Alto" if pot>=500 else "Médio","situacao_rede":"Usa diesel — candidato solar/híbrido","observacoes":f"Potência: {pot:.0f} kW","lat":r.get("NumLatitude",0),"lon":r.get("NumLongitude",0),"fonte":"ANEEL-BIG","cpf_cnpj":r.get("CpfCnpj",""),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":r.get("CodCEG",""),"situacao":r.get("DscFaseUsina","")})

            if not leads_mod:
                leads_mod = [l for l in leads_estado if l["modulo"] == mod]

            for lead in leads_mod:
                lead["estado"] = estado
                lead["score"] = calcular_score(lead)
            todos += leads_mod
            time.sleep(0.2)

    progress.empty()
    status.empty()

    if not todos:
        return pd.DataFrame()

    df = pd.DataFrame(todos)

    if situacoes and "Todos" not in situacoes:
        mask = pd.Series([False]*len(df), index=df.index)
        if "Zero-grid / Sem rede" in situacoes:
            mask |= df["situacao_rede"].str.contains("remot|Sem rede|zero", case=False, na=False)
        if "Usa diesel" in situacoes:
            mask |= df["situacao_rede"].str.contains("diesel", case=False, na=False)
        if "ACL / Grupo A" in situacoes:
            mask |= df["situacao_rede"].str.contains("Grupo A", case=False, na=False)
        if "Alto consumo" in situacoes:
            mask |= df["modulo"].isin(["ACL-GrupoA","Diesel-Gerador"])
        df = df[mask]

    df = df[df["score"] >= score_min]
    return df.sort_values("score", ascending=False).reset_index(drop=True)

def gerar_excel(df):
    colunas = ["score","potencial","modulo","estado","municipio","nome","cpf_cnpj","socio","telefone","email","porte","area_ha","situacao_rede","situacao","lat","lon","cnae","codigo_ref","observacoes","fonte"]
    for c in colunas:
        if c not in df.columns: df[c] = ""
    df = df[colunas]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Todos os Leads", index=False)
        df[df["potencial"]=="Alto"].to_excel(writer, sheet_name="Alto Potencial", index=False)
        for mod in df["modulo"].unique():
            df[df["modulo"]==mod].to_excel(writer, sheet_name=str(mod)[:31].replace("/","-"), index=False)
        ws = writer.sheets["Todos os Leads"]
        from openpyxl.styles import PatternFill, Font, Alignment
        from openpyxl.utils import get_column_letter
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="1C1C2E")
            cell.font = Font(color="F59E0B", bold=True, size=10)
            cell.alignment = Alignment(horizontal="center")
        cores = {"Alto":("1A2E1A","4ADE80"),"Médio":("1A1A2E","60A5FA"),"Medio":("1A1A2E","60A5FA"),"Baixo":("2E1A1A","F87171")}
        for i, row in enumerate(ws.iter_rows(min_row=2), 0):
            if i < len(df):
                bg,fc = cores.get(df.iloc[i].get("potencial",""), ("1E293B","E2E8F0"))
                for cell in row:
                    cell.fill = PatternFill("solid", fgColor=bg)
                    cell.font = Font(color=fc, size=9)
        for i,w in enumerate([7,10,16,6,20,35,18,25,14,28,12,8,28,15,10,10,30,15,40,12],1):
            ws.column_dimensions[get_column_letter(i)].width = w
    return output.getvalue()

# ─────────────────────────────────────────
# INTERFACE PRINCIPAL
# ─────────────────────────────────────────

# Header com botão de logout
col_h1, col_h2 = st.columns([5,1])
with col_h1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
        <div style="width:40px;height:40px;background:#f59e0b;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px">☀️</div>
        <div>
            <h1 style="margin:0;font-size:22px;font-weight:500;color:#f1f5f9!important">Solar Lead Finder</h1>
            <p style="margin:0;font-size:12px;color:#475569!important">Prospecção automática · Fontes públicas oficiais</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sair", key="logout"):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("""
<span class="badge-fonte">SICAR</span>
<span class="badge-fonte">ANM</span>
<span class="badge-fonte">CCEE</span>
<span class="badge-fonte">ANEEL</span>
<span style="font-size:11px;color:#475569"> · Dados abertos do governo federal</span>
<hr style="margin:12px 0">
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"<p style='font-size:12px;color:#475569'>Usuário: <b style='color:#f59e0b'>{st.session_state.get('usuario','')}</b></p>", unsafe_allow_html=True)
    st.markdown("### Filtros")
    st.markdown("---")

    estados_sel = st.multiselect("Estados", options=TODOS_ESTADOS, default=["MG","BA","ES"])

    st.markdown("---")
    st.markdown("**Módulos**")
    mod_rural  = st.checkbox("Rural / Irrigação (SICAR)", value=True)
    mod_mine   = st.checkbox("Mineração (ANM)", value=True)
    mod_acl    = st.checkbox("ACL / Grupo A (CCEE)", value=True)
    mod_diesel = st.checkbox("Diesel / Gerador (ANEEL)", value=True)

    st.markdown("---")
    situacoes = st.multiselect("Situação energética",
        options=["Todos","Zero-grid / Sem rede","Usa diesel","ACL / Grupo A","Alto consumo"],
        default=["Todos"])

    st.markdown("---")
    score_min = st.slider("Score mínimo", 0.0, 10.0, 6.0, 0.5)

    st.markdown("---")
    buscar = st.button("Buscar leads agora", type="primary")

# Resultados
if "df_resultado" not in st.session_state:
    st.session_state.df_resultado = pd.DataFrame()
    st.session_state.buscou = False

if buscar:
    if not estados_sel:
        st.error("Selecione pelo menos um estado.")
    else:
        modulos_sel = []
        if mod_rural:  modulos_sel.append("Rural-Irrigacao")
        if mod_mine:   modulos_sel.append("Mineracao")
        if mod_acl:    modulos_sel.append("ACL-GrupoA")
        if mod_diesel: modulos_sel.append("Diesel-Gerador")
        if not modulos_sel:
            st.error("Selecione pelo menos um módulo.")
        else:
            with st.spinner("Consultando fontes..."):
                df = buscar_leads(estados_sel, modulos_sel, situacoes, score_min)
                st.session_state.df_resultado = df
                st.session_state.buscou = True

if st.session_state.buscou and not st.session_state.df_resultado.empty:
    df = st.session_state.df_resultado
    st.success(f"✓ {len(df)} leads encontrados")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total", len(df))
    with c2: st.metric("Alto potencial", len(df[df["potencial"]=="Alto"]))
    with c3: st.metric("Usam diesel", len(df[df["situacao_rede"].str.contains("diesel",case=False,na=False)]))
    with c4: st.metric("Com CNPJ", len(df[df["cpf_cnpj"].astype(str).str.len()>5]))

    st.markdown("---")

    filtro_mod = st.selectbox("Filtrar por módulo", ["Todos"]+list(df["modulo"].unique()))
    df_view = df if filtro_mod=="Todos" else df[df["modulo"]==filtro_mod]

    colunas_tabela = [c for c in ["score","potencial","estado","municipio","nome","modulo","situacao_rede","telefone","observacoes","fonte"] if c in df_view.columns]
    st.dataframe(
        df_view[colunas_tabela].reset_index(drop=True),
        use_container_width=True, height=420,
        column_config={
            "score": st.column_config.NumberColumn("Score", format="%.1f"),
            "estado": st.column_config.TextColumn("UF", width=60),
            "nome": st.column_config.TextColumn("Nome / Razão Social", width=220),
            "situacao_rede": st.column_config.TextColumn("Situação"),
            "observacoes": st.column_config.TextColumn("Observações", width=200),
        }
    )

    st.markdown("---")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    col1, col2 = st.columns([2,1])
    with col1:
        st.download_button(
            label="Baixar planilha Excel completa",
            data=gerar_excel(df.copy()),
            file_name=f"leads_solar_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if df["fonte"].str.contains("demo",case=False,na=False).any():
        st.info("ℹ️ Registros com '-demo' na coluna Fonte são ilustrativos. Os demais são dados reais das APIs públicas.")

elif st.session_state.buscou:
    st.warning("Nenhum lead encontrado. Reduza o score mínimo ou amplie os estados.")
else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px">
        <div style="font-size:52px;margin-bottom:16px">☀️</div>
        <p style="font-size:16px;color:#64748b">Configure os filtros e clique em <b style="color:#f59e0b">Buscar leads agora</b></p>
        <p style="font-size:13px;color:#374151;margin-top:8px">SICAR · ANM · CCEE · ANEEL · Receita Federal</p>
    </div>
    """, unsafe_allow_html=True)
