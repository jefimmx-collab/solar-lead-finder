import streamlit as st
import requests
import pandas as pd
import json
import time
import io
import hashlib
import math
from datetime import datetime

st.set_page_config(
    page_title="Solar Lead Finder",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CREDENCIAIS
# ─────────────────────────────────────────
USUARIOS = {
    "admin":  hashlib.sha256("solar2024".encode()).hexdigest(),
    "equipe": hashlib.sha256("leads2024".encode()).hexdigest(),
}
def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
.stApp{background:#0f1117}
section[data-testid="stSidebar"]{background:#161b27;border-right:1px solid #2d3748}
h1,h2,h3,h4{color:#f1f5f9!important}
p,label,span{color:#e2e8f0!important}
.stMarkdown p{color:#94a3b8!important}
.stSelectbox>div,.stMultiSelect>div,.stTextInput>div,.stNumberInput>div{
  background:#1e293b!important;border:1px solid #2d3748!important;
  border-radius:8px!important;color:#e2e8f0!important}
.stButton>button{background:#f59e0b!important;color:#1c1400!important;
  border:none!important;border-radius:8px!important;font-weight:600!important;
  width:100%!important;padding:12px!important;font-size:14px!important}
.stButton>button:hover{background:#fbbf24!important}
.stDownloadButton>button{background:#1e3a5f!important;color:#60a5fa!important;
  border:1px solid #1d4ed8!important;border-radius:8px!important;width:100%!important}
[data-testid="stMetric"]{background:#161b27!important;border:1px solid #2d3748!important;
  border-radius:10px!important;padding:16px!important}
[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:28px!important}
[data-testid="stMetricLabel"]{color:#475569!important;font-size:12px!important}
hr{border-color:#2d3748!important}
.stCheckbox label{color:#cbd5e1!important;font-size:13px!important}
.stSuccess{background:#052e16!important;color:#4ade80!important}
.stWarning{background:#1c1400!important;color:#fbbf24!important}
.stError{background:#2e0f0f!important;color:#f87171!important}
.stInfo{background:#0c1a2e!important;color:#60a5fa!important}
.badge-fonte{display:inline-block;background:#052e16;color:#4ade80;
  border:1px solid #166534;border-radius:4px;padding:2px 8px;font-size:11px;margin-right:4px}
.badge-demo{display:inline-block;background:#1c1400;color:#f59e0b;
  border:1px solid #92400e;border-radius:4px;padding:2px 8px;font-size:11px}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
def tela_login():
    col1,col2,col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#161b27;border:0.5px solid #2d3748;border-radius:14px;padding:36px 32px;text-align:center">
        <div style="width:52px;height:52px;background:#f59e0b;border-radius:12px;display:inline-flex;
        align-items:center;justify-content:center;font-size:26px;margin-bottom:16px">☀️</div>
        <h2 style="color:#f1f5f9;margin:0 0 4px">Solar Lead Finder</h2>
        <p style="color:#475569;font-size:13px;margin-bottom:0">Acesso restrito</p></div>
        """,unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
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
# REGIÕES DE MG / BA / ES
# ─────────────────────────────────────────
REGIOES = {
    "MG": {
        "Todas as regiões": [],
        "Vale do Jequitinhonha": ["Araçuaí","Diamantina","Itamarandiba","Pedra Azul","Turmalina","Capelinha","Minas Novas","Virgem da Lapa","Coronel Murta","Berilo"],
        "Norte de Minas": ["Montes Claros","Januária","Pirapora","Bocaiúva","Janaúba","Porteirinha","Unaí","Manga","São Francisco","Brasília de Minas"],
        "Vale do Mucuri": ["Teófilo Otoni","Nanuque","Ladainha","Carlos Chagas","Novo Oriente de Minas","Poté","Malacacheta","Itambacuri","Ataléia","Franciscópolis"],
        "Triângulo Mineiro": ["Uberlândia","Uberaba","Araguari","Ituiutaba","Patos de Minas","Frutal","Iturama","Araxá","Patrocínio","Monte Carmelo"],
        "Zona da Mata": ["Juiz de Fora","Viçosa","Muriaé","Caratinga","Governador Valadares","Manhuaçu","Ipatinga","Coronel Fabriciano","Timóteo","Ubá"],
        "Sul de Minas": ["Poços de Caldas","Varginha","Pouso Alegre","Itajubá","Lavras","Alfenas","Passos","São Sebastião do Paraíso","Três Corações","Guaxupé"],
        "Central / Metropolitana": ["Belo Horizonte","Contagem","Betim","Sete Lagoas","Divinópolis","Conselheiro Lafaiete","Ouro Preto","Mariana","Itabira","João Monlevade"],
    },
    "BA": {
        "Todas as regiões": [],
        "Oeste Baiano": ["Barreiras","Luís Eduardo Magalhães","Bom Jesus da Lapa","Ibotirama","Santa Maria da Vitória","Correntina","São Desidério","Cocos","Coribe","Jaborandi"],
        "Chapada Diamantina": ["Mucugê","Lençóis","Palmeiras","Seabra","Iraquara","Andaraí","Ibicoara","Piatã","Rio de Contas","Boninal"],
        "Sertão Baiano": ["Juazeiro","Paulo Afonso","Senhor do Bonfim","Jacobina","Irecê","Xique-Xique","Barra","Morro do Chapéu","Campo Formoso","Itaberaba"],
        "Litoral Norte / Metropolitana": ["Salvador","Camaçari","Lauro de Freitas","Simões Filho","Feira de Santana","Santo Antônio de Jesus","Cruz das Almas","Alagoinhas","Candeias","São Francisco do Conde"],
        "Sul da Bahia": ["Ilhéus","Itabuna","Eunápolis","Porto Seguro","Teixeira de Freitas","Vitória da Conquista","Jequié","Ipiaú","Gandu","Valença"],
    },
    "ES": {
        "Todas as regiões": [],
        "Norte do ES": ["São Mateus","Linhares","Colatina","Nova Venécia","Barra de São Francisco","Boa Esperança","Pinheiros","Jaguaré","Pedro Canário","Montanha"],
        "Metropolitana": ["Vitória","Vila Velha","Serra","Cariacica","Viana","Guarapari","Domingos Martins","Santa Leopoldina","Marechal Floriano","Alfredo Chaves"],
        "Sul do ES": ["Cachoeiro de Itapemirim","Alegre","Guaçuí","Muniz Freire","Iúna","Castelo","Venda Nova do Imigrante","Ibatiba","Bom Jesus do Norte","Presidente Kennedy"],
    },
    "GO": {"Todas as regiões": [],"Sul de Goiás": ["Rio Verde","Jataí","Itumbiara","Catalão","Caldas Novas","Morrinhos","Quirinópolis","Mineiros","Itajá","Caçu"],"Centro": ["Goiânia","Anápolis","Aparecida de Goiânia","Senador Canedo","Trindade","Goianira","Hidrolândia","Abadia de Goiás","Aragoiânia","Bela Vista de Goiás"]},
    "MT": {"Todas as regiões": [],"Norte": ["Sinop","Alta Floresta","Sorriso","Lucas do Rio Verde","Nova Mutum","Guarantã do Norte","Peixoto de Azevedo","Nova Canaã do Norte","Terra Nova do Norte","Colíder"],"Sul": ["Cuiabá","Várzea Grande","Rondonópolis","Tangará da Serra","Cáceres","Barra do Garças","Primavera do Leste","Campo Verde","Juína","Juara"]},
    "PA": {"Todas as regiões": [],"Pará": ["Belém","Ananindeua","Santarém","Marabá","Parauapebas","Altamira","Redenção","Tucuruí","Castanhal","Barcarena"]},
}

TODOS_ESTADOS = list(REGIOES.keys()) + ["SP","RJ","PE","CE","RS","PR","SC","MS","RO","TO","PI","MA","RN","PB","AL","SE","AC","AM","RR","AP","DF"]

# ─────────────────────────────────────────
# GEOCODING — converter cidade em lat/lon
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def geocodificar_cidade(cidade, estado):
    """Usa Nominatim (OpenStreetMap) para obter coordenadas da cidade."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{cidade}, {estado}, Brasil",
            "format": "json",
            "limit": 1,
            "countrycodes": "br",
        }
        headers = {"User-Agent": "SolarLeadFinder/2.0"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None

def distancia_km(lat1, lon1, lat2, lon2):
    """Haversine — distância entre dois pontos em km."""
    try:
        R = 6371
        d_lat = math.radians(float(lat2) - float(lat1))
        d_lon = math.radians(float(lon2) - float(lon1))
        a = math.sin(d_lat/2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(d_lon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    except:
        return 9999

@st.cache_data(ttl=3600)
def get_coords_municipios_estado(estado):
    """Busca coordenadas de todos os municípios do estado via IBGE + Nominatim."""
    try:
        cod = {"MG":"31","BA":"29","ES":"32","GO":"52","MT":"51","PA":"15","SP":"35","RJ":"33","PR":"41","RS":"43","SC":"42","PE":"26","CE":"23","PI":"22","MA":"21","MS":"50","RO":"11","TO":"17","RN":"24","PB":"25"}
        cod_estado = cod.get(estado,"")
        if not cod_estado:
            return {}
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{cod_estado}/municipios"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return {}
        municipios = r.json()
        coords = {}
        for m in municipios[:500]:
            nome = m.get("nome","")
            coords[nome.upper()] = None
        return coords
    except:
        return {}

# ─────────────────────────────────────────
# DADOS DEMO EXPANDIDOS
# ─────────────────────────────────────────
def gerar_demo_estado(estado):
    """Gera conjunto rico de leads demo para qualquer estado."""
    base = {
        "MG": [
            ("Rural-Irrigacao","Fazenda Serra Verde","Araçuaí",480,-16.85,-42.07,"Alto","Sem rede próxima","Área: 480 ha · Outorga ANA ativa"),
            ("Rural-Irrigacao","Fazenda Três Barras","Januária",620,-15.48,-44.36,"Alto","Sem rede próxima","Área: 620 ha · Pivô central"),
            ("Rural-Irrigacao","Agropecuária Jequitinhonha","Diamantina",340,-18.24,-43.60,"Alto","Sem rede próxima","Área: 340 ha"),
            ("Rural-Irrigacao","Sítio Boa Esperança","Montes Claros",210,-16.72,-43.86,"Médio","Verificar","Área: 210 ha"),
            ("Rural-Irrigacao","Fazenda do Cerrado","Unaí",890,-16.36,-46.90,"Alto","Sem rede próxima","Área: 890 ha · Pivô central"),
            ("Rural-Irrigacao","Fazenda Santa Luzia","Porteirinha",430,-15.74,-43.02,"Alto","Sem rede próxima","Área: 430 ha"),
            ("Rural-Irrigacao","Grupo Rural Mucuri","Teófilo Otoni",180,-17.86,-41.50,"Médio","Verificar","Área: 180 ha"),
            ("Rural-Irrigacao","Fazenda Vale Verde","Nanuque",260,-17.83,-40.35,"Médio","Sem rede próxima","Área: 260 ha"),
            ("Mineracao","Min. Vale do Jequitinhonha Ltda","Itamarandiba",320,-17.85,-42.85,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Ferro"),
            ("Mineracao","Mineradora São Domingos","Diamantina",520,-18.24,-43.60,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Ouro"),
            ("Mineracao","Granitos MG Extração Ltda","Pedra Azul",85,-16.00,-41.27,"Médio","Área remota — alto risco diesel","Fase: Licenciamento · Substância: Granito"),
            ("Mineracao","Mineração Capelinha","Capelinha",210,-17.69,-42.52,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Nióbio"),
            ("Mineracao","Extratora Norte MG","Bocaiúva",145,-17.11,-43.81,"Médio","Área remota — alto risco diesel","Fase: Licenciamento · Substância: Calcário"),
            ("ACL-GrupoA","Cerâmica Industrial Mucuri SA","Teófilo Otoni",0,-17.86,-41.50,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 2.4 MW","12.345.678/0001-90","João Silva","33991234567"),
            ("ACL-GrupoA","Siderúrgica Vale do Aço Ltda","Ipatinga",0,-19.47,-42.54,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 8.1 MW","23.456.789/0001-11","Maria Santos","31991234567"),
            ("ACL-GrupoA","Frigorífico Central MG SA","Uberlândia",0,-18.91,-48.27,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 1.2 MW","34.567.890/0001-22","Pedro Alves","34991234567"),
            ("ACL-GrupoA","Cimento Norte MG Ltda","Montes Claros",0,-16.72,-43.86,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 5.5 MW","45.678.901/0001-33","Ana Lima","38991234567"),
            ("Diesel-Gerador","Frigorífico Bom Pastor Ltda","Caratinga",0,-19.78,-42.13,"Médio","Usa diesel — candidato solar/híbrido","Potência: 320 kW"),
            ("Diesel-Gerador","Mineração São Domingos Ltda","Diamantina",0,-18.24,-43.60,"Alto","Usa diesel — candidato solar/híbrido","Potência: 850 kW"),
            ("Diesel-Gerador","Fazenda Industrial MG","Montes Claros",0,-16.72,-43.86,"Médio","Usa diesel — candidato solar/híbrido","Potência: 180 kW"),
            ("Diesel-Gerador","Pedreiras Jequitinhonha","Araçuaí",0,-16.85,-42.07,"Alto","Usa diesel — candidato solar/híbrido","Potência: 560 kW"),
            ("Diesel-Gerador","Cerâmica Mucuri Ltda","Teófilo Otoni",0,-17.86,-41.50,"Médio","Usa diesel — candidato solar/híbrido","Potência: 240 kW"),
        ],
        "BA": [
            ("Rural-Irrigacao","Fazenda Chapada","Barreiras",720,-12.15,-44.99,"Alto","Sem rede próxima","Área: 720 ha · Pivô central"),
            ("Rural-Irrigacao","Agropecuária São João","Luís Eduardo Magalhães",340,-12.09,-45.79,"Alto","Sem rede próxima","Área: 340 ha · Pivô central"),
            ("Rural-Irrigacao","Fazenda Sertão Verde","Irecê",290,-11.30,-41.85,"Médio","Verificar","Área: 290 ha"),
            ("Rural-Irrigacao","Grupo Rural Oeste","Correntina",810,-13.34,-44.64,"Alto","Sem rede próxima","Área: 810 ha · Irrigação por pivô"),
            ("Rural-Irrigacao","Fazenda Bom Sucesso","São Desidério",550,-12.36,-44.97,"Alto","Sem rede próxima","Área: 550 ha"),
            ("Mineracao","Mineradora Chapada Diamantina","Mucugê",560,-13.00,-41.36,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Diamante"),
            ("Mineracao","Extratora Bahia Ltda","Jacobina",190,-11.18,-40.51,"Médio","Área remota — alto risco diesel","Fase: Licenciamento · Substância: Ouro"),
            ("Mineracao","Min. Sertão Baiano","Senhor do Bonfim",280,-10.46,-40.19,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Cromo"),
            ("ACL-GrupoA","Petroquímica Camaçari Ltda","Camaçari",0,-12.69,-38.32,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 15.0 MW","45.678.901/0001-33","Maria Souza","71991234567"),
            ("ACL-GrupoA","Têxtil Nordeste SA","Feira de Santana",0,-12.26,-38.96,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 0.9 MW","56.789.012/0001-44","Carlos Lima","75991234567"),
            ("ACL-GrupoA","Cerâmica Oeste Baiano","Barreiras",0,-12.15,-44.99,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 3.2 MW","67.890.123/0001-55","Ana Costa","77991234567"),
            ("Diesel-Gerador","Fazenda Agropastoril Ltda","Irecê",0,-11.30,-41.85,"Médio","Usa diesel — candidato solar/híbrido","Potência: 180 kW"),
            ("Diesel-Gerador","Cerâmica Nordeste SA","Vitória da Conquista",0,-14.86,-40.84,"Médio","Usa diesel — candidato solar/híbrido","Potência: 430 kW"),
            ("Diesel-Gerador","Mineradora Chapada Diesel","Mucugê",0,-13.00,-41.36,"Alto","Usa diesel — candidato solar/híbrido","Potência: 720 kW"),
        ],
        "ES": [
            ("Rural-Irrigacao","Fazenda Caparaó","Alegre",160,-20.76,-41.53,"Médio","Verificar","Área: 160 ha"),
            ("Rural-Irrigacao","Sítio Santa Maria","Linhares",95,-19.39,-40.06,"Médio","Verificar","Área: 95 ha"),
            ("Rural-Irrigacao","Fazenda Norte Capixaba","São Mateus",220,-18.71,-39.86,"Médio","Sem rede próxima","Área: 220 ha"),
            ("Mineracao","Mineração Espírito Santo SA","Cachoeiro de Itapemirim",140,-20.84,-41.11,"Médio","Área remota — alto risco diesel","Fase: Concessão de Lavra · Substância: Mármore"),
            ("Mineracao","Extratora Capixaba Ltda","Nova Venécia",95,-18.71,-40.40,"Médio","Área remota — alto risco diesel","Fase: Licenciamento · Substância: Granito"),
            ("ACL-GrupoA","Aracruz Celulose SA","Aracruz",0,-19.82,-40.27,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 22.0 MW","67.890.123/0001-55","Carlos Lima","27991234567"),
            ("ACL-GrupoA","Siderúrgica Tubarão SA","Serra",0,-20.13,-40.30,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 45.0 MW","78.901.234/0001-66","Roberto Silva","27991234568"),
            ("Diesel-Gerador","Pedreiras Capixabas SA","Cachoeiro de Itapemirim",0,-20.84,-41.11,"Médio","Usa diesel — candidato solar/híbrido","Potência: 420 kW"),
            ("Diesel-Gerador","Cerâmica Norte ES","São Mateus",0,-18.71,-39.86,"Médio","Usa diesel — candidato solar/híbrido","Potência: 190 kW"),
        ],
    }
    demos = base.get(estado, [
        ("Rural-Irrigacao",f"Fazenda Demo {estado}","Capital",500,-15.0,-50.0,"Alto","Sem rede próxima","Área: 500 ha · DEMO"),
        ("Mineracao",f"Mineradora Demo {estado}","Interior",300,-15.5,-50.5,"Alto","Área remota — alto risco diesel","Fase: Concessão de Lavra · DEMO"),
        ("ACL-GrupoA",f"Indústria Demo {estado}","Capital",0,-15.0,-50.0,"Alto","Conectado — Grupo A / Mercado Livre","Demanda: 3.0 MW · DEMO"),
        ("Diesel-Gerador",f"Gerador Demo {estado}","Interior",0,-15.5,-50.5,"Médio","Usa diesel — candidato solar/híbrido","Potência: 400 kW · DEMO"),
    ])
    resultado = []
    for d in demos:
        lead = {
            "modulo": d[0], "nome": d[1], "municipio": d[2], "area_ha": d[3],
            "lat": d[4], "lon": d[5], "potencial": d[6],
            "situacao_rede": d[7], "observacoes": d[8],
            "estado": estado, "fonte": f"{d[0].split('-')[0]}-demo",
            "cpf_cnpj": d[9] if len(d)>9 else "",
            "socio": d[10] if len(d)>10 else "",
            "telefone": d[11] if len(d)>11 else "",
            "email": "", "porte": "", "cnae": "", "codigo_ref": "DEMO", "situacao": "Ativo",
        }
        resultado.append(lead)
    return resultado

# ─────────────────────────────────────────
# FUNÇÕES DE BUSCA
# ─────────────────────────────────────────
HEADERS = {"User-Agent": "SolarLeadFinder/2.0", "Accept": "application/json"}

def get_json(url, params=None, timeout=25):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def calcular_score(lead):
    s = 5.0
    pot = lead.get("potencial","")
    if pot == "Alto":   s += 2.5
    elif pot == "Médio": s += 1.0
    if "diesel" in str(lead.get("situacao_rede","")).lower(): s += 1.5
    if "remot" in str(lead.get("situacao_rede","")).lower():  s += 1.0
    if lead.get("modulo") == "ACL-GrupoA": s += 1.5
    area = float(lead.get("area_ha",0) or 0)
    if area >= 500: s += 0.5
    elif area >= 200: s += 0.3
    if lead.get("telefone"): s += 0.5
    if lead.get("cpf_cnpj") and "DEMO" not in str(lead.get("cpf_cnpj","")): s += 0.3
    dist = lead.get("dist_km")
    if dist is not None:
        if dist <= 50:    s += 0.5
        elif dist <= 100: s += 0.3
    return round(min(s, 10.0), 1)

def buscar_api_sicar(estado, municipios_filtro=None):
    leads = []
    for pagina in range(1, 6):
        dados = get_json("https://consultapublica.car.gov.br/publico/imoveis/index",
                         params={"estado":estado,"tipo":"IRU","pagina":pagina,"tamanhoPagina":100})
        if not dados or not isinstance(dados,list) or len(dados)==0:
            break
        for item in dados:
            area = float(item.get("area",0) or 0)
            if area < 50: continue
            mun = item.get("nomeMunicipio","")
            if municipios_filtro and mun.upper() not in [m.upper() for m in municipios_filtro]:
                continue
            leads.append({"modulo":"Rural-Irrigacao","nome":item.get("nomePessoa",""),"municipio":mun,"area_ha":round(area,1),"potencial":"Alto" if area>=500 else "Médio","situacao_rede":"Verificar","observacoes":f"Área: {area:.0f} ha","lat":item.get("latitude",0) or 0,"lon":item.get("longitude",0) or 0,"fonte":"SICAR","cpf_cnpj":item.get("cpf",item.get("cnpj","")),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":item.get("codigo",""),"situacao":item.get("situacao","")})
        time.sleep(0.3)
    return leads

def buscar_api_anm(estado, municipios_filtro=None):
    leads = []
    for offset in range(0, 400, 100):
        dados = get_json("https://geo.anm.gov.br/geoserver/sigmine/wfs",
                         params={"service":"WFS","version":"2.0.0","request":"GetFeature","typeName":"sigmine:BRASIL","outputFormat":"application/json","CQL_FILTER":f"UF='{estado}'","count":100,"startIndex":offset},timeout=45)
        if not dados or "features" not in dados or len(dados["features"])==0:
            break
        for f in dados["features"]:
            p = f.get("properties",{})
            area = float(p.get("AREA_HA",0) or 0)
            fase = p.get("FASE","")
            mun = p.get("MUNICIPIO","")
            if municipios_filtro and mun.upper() not in [m.upper() for m in municipios_filtro]:
                continue
            try:
                coords = f.get("geometry",{}).get("coordinates",[[[[0,0]]]])
                pts = coords[0][0] if f.get("geometry",{}).get("type")=="MultiPolygon" else coords[0]
                lat = round(sum(pt[1] for pt in pts)/len(pts),6)
                lon = round(sum(pt[0] for pt in pts)/len(pts),6)
            except:
                lat,lon = 0,0
            leads.append({"modulo":"Mineracao","nome":p.get("NOME",""),"municipio":mun,"area_ha":round(area,1),"potencial":"Alto" if area>=200 else "Médio","situacao_rede":"Área remota — alto risco diesel","observacoes":f"Fase: {fase} · Substância: {p.get('SUB','')}","lat":lat,"lon":lon,"fonte":"ANM-SIGMINE","cpf_cnpj":p.get("CPF_CNPJ",""),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":p.get("PROCESSO",""),"situacao":fase})
        time.sleep(0.5)
    return leads

def buscar_api_aneel(estado, tipo="diesel"):
    leads = []
    filtro = {"SigUF":estado}
    if tipo == "diesel": filtro["DscCombustivel"] = "Óleo Diesel"
    dados = get_json("https://dadosabertos.aneel.gov.br/api/3/action/datastore_search",
                     params={"resource_id":"b1bd71e7-d0ad-4214-9053-cbd58e9564a7","limit":500,"filters":json.dumps(filtro)})
    if dados and dados.get("success"):
        for r in dados.get("result",{}).get("records",[]):
            pot = float(r.get("MdaPotenciaFiscalizadaKw",0) or 0)
            if tipo == "diesel":
                leads.append({"modulo":"Diesel-Gerador","nome":r.get("NomEmpreendimento",""),"municipio":r.get("NomMunicipio",""),"area_ha":0,"potencial":"Alto" if pot>=500 else "Médio","situacao_rede":"Usa diesel — candidato solar/híbrido","observacoes":f"Potência: {pot:.0f} kW","lat":r.get("NumLatitude",0) or 0,"lon":r.get("NumLongitude",0) or 0,"fonte":"ANEEL-BIG","cpf_cnpj":r.get("CpfCnpj",""),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":r.get("CodCEG",""),"situacao":r.get("DscFaseUsina","")})
            else:
                leads.append({"modulo":"ACL-GrupoA","nome":r.get("NomAgente",r.get("NomEmpreendimento","")),"municipio":r.get("NomMunicipio",""),"area_ha":0,"potencial":"Alto","situacao_rede":"Conectado — Grupo A / Mercado Livre","observacoes":f"Categoria: {r.get('DscCategoria','')}","lat":0,"lon":0,"fonte":"ANEEL","cpf_cnpj":r.get("CnpjParticipante",r.get("CpfCnpj","")),"socio":"","telefone":"","email":"","porte":"","cnae":"","codigo_ref":r.get("CodCEG",""),"situacao":"Ativo"})
    return leads

def buscar_leads(estados, modulos, situacoes, score_min, cidade_ref, raio_km, regioes_sel):
    todos = []
    total_etapas = len(estados) * len(modulos)
    etapa = 0
    progress = st.progress(0)
    status = st.empty()

    # Geocodificar cidade de referência
    lat_ref, lon_ref = None, None
    if cidade_ref:
        estado_ref = estados[0] if estados else "MG"
        lat_ref, lon_ref = geocodificar_cidade(cidade_ref, estado_ref)
        if lat_ref:
            status.markdown(f"<p style='color:#4ade80;font-size:12px'>📍 {cidade_ref} localizada: {lat_ref:.4f}, {lon_ref:.4f}</p>",unsafe_allow_html=True)
            time.sleep(0.5)

    for estado in estados:
        # Municípios filtrados por região
        municipios_regiao = []
        if regioes_sel.get(estado) and regioes_sel[estado] != "Todas as regiões":
            municipios_regiao = REGIOES.get(estado,{}).get(regioes_sel[estado],[])

        demos_estado = gerar_demo_estado(estado)

        for mod in modulos:
            etapa += 1
            progress.progress(int((etapa/total_etapas)*100))
            status.markdown(f"<p style='color:#94a3b8;font-size:12px'>Consultando {mod} em {estado}...</p>",unsafe_allow_html=True)

            leads_mod = []

            if mod == "Rural-Irrigacao":
                leads_mod = buscar_api_sicar(estado, municipios_regiao or None)
                if not leads_mod:
                    leads_mod = [l for l in demos_estado if l["modulo"]=="Rural-Irrigacao"]

            elif mod == "Mineracao":
                leads_mod = buscar_api_anm(estado, municipios_regiao or None)
                if not leads_mod:
                    leads_mod = [l for l in demos_estado if l["modulo"]=="Mineracao"]

            elif mod == "ACL-GrupoA":
                leads_mod = buscar_api_aneel(estado, tipo="acl")
                if not leads_mod:
                    leads_mod = [l for l in demos_estado if l["modulo"]=="ACL-GrupoA"]

            elif mod == "Diesel-Gerador":
                leads_mod = buscar_api_aneel(estado, tipo="diesel")
                if not leads_mod:
                    leads_mod = [l for l in demos_estado if l["modulo"]=="Diesel-Gerador"]

            # Calcular distância até cidade de referência
            for lead in leads_mod:
                lead["estado"] = estado
                if lat_ref and lon_ref and lead.get("lat") and lead.get("lon"):
                    try:
                        dist = distancia_km(lat_ref, lon_ref, lead["lat"], lead["lon"])
                        lead["dist_km"] = round(dist, 1)
                    except:
                        lead["dist_km"] = None
                else:
                    lead["dist_km"] = None
                lead["score"] = calcular_score(lead)

            todos += leads_mod
            time.sleep(0.2)

    progress.empty()
    status.empty()

    if not todos:
        return pd.DataFrame()

    df = pd.DataFrame(todos)

    # Filtrar por raio
    if lat_ref and lon_ref and raio_km and raio_km > 0:
        df = df[df["dist_km"].apply(lambda x: x is not None and x <= raio_km)]

    # Filtrar por situação
    if situacoes and "Todos" not in situacoes:
        mask = pd.Series([False]*len(df), index=df.index)
        if "Zero-grid / Sem rede" in situacoes:
            mask |= df["situacao_rede"].str.contains("remot|Sem rede|zero",case=False,na=False)
        if "Usa diesel" in situacoes:
            mask |= df["situacao_rede"].str.contains("diesel",case=False,na=False)
        if "ACL / Grupo A" in situacoes:
            mask |= df["situacao_rede"].str.contains("Grupo A",case=False,na=False)
        if "Alto consumo" in situacoes:
            mask |= df["modulo"].isin(["ACL-GrupoA","Diesel-Gerador"])
        df = df[mask]

    df = df[df["score"] >= score_min]
    return df.sort_values("score", ascending=False).reset_index(drop=True)

def gerar_excel(df):
    colunas = ["score","potencial","modulo","estado","municipio","nome","cpf_cnpj","socio","telefone","email","porte","area_ha","dist_km","situacao_rede","situacao","lat","lon","cnae","codigo_ref","observacoes","fonte"]
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
        cores = {"Alto":("1A2E1A","4ADE80"),"Médio":("1A1A2E","60A5FA"),"Baixo":("2E1A1A","F87171")}
        for i, row in enumerate(ws.iter_rows(min_row=2), 0):
            if i < len(df):
                bg,fc = cores.get(df.iloc[i].get("potencial",""),("1E293B","E2E8F0"))
                for cell in row:
                    cell.fill = PatternFill("solid", fgColor=bg)
                    cell.font = Font(color=fc, size=9)
        for i,w in enumerate([7,10,16,6,20,35,18,25,14,28,12,8,10,28,15,10,10,30,15,40,12],1):
            ws.column_dimensions[get_column_letter(i)].width = w
    return output.getvalue()

# ─────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────

# Header
col_h1, col_h2 = st.columns([5,1])
with col_h1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
    <div style="width:40px;height:40px;background:#f59e0b;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px">☀️</div>
    <div>
    <h1 style="margin:0;font-size:22px;font-weight:500;color:#f1f5f9!important">Solar Lead Finder</h1>
    <p style="margin:0;font-size:12px;color:#475569!important">Prospecção automática · Fontes públicas oficiais</p>
    </div></div>""",unsafe_allow_html=True)
with col_h2:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Sair",key="logout"):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("""
<span class="badge-fonte">SICAR</span>
<span class="badge-fonte">ANM</span>
<span class="badge-fonte">CCEE</span>
<span class="badge-fonte">ANEEL</span>
<span style="font-size:11px;color:#475569"> · Dados abertos do governo federal</span>
<hr style="margin:12px 0">
""",unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"<p style='font-size:12px;color:#475569'>Usuário: <b style='color:#f59e0b'>{st.session_state.get('usuario','')}</b></p>",unsafe_allow_html=True)
    st.markdown("### Filtros")
    st.markdown("---")

    # Estados
    estados_sel = st.multiselect("Estados", options=TODOS_ESTADOS, default=["MG","BA","ES"])

    # Região por estado
    regioes_sel = {}
    if estados_sel:
        st.markdown("---")
        st.markdown("**Região (por estado)**")
        for est in estados_sel:
            if est in REGIOES:
                opcoes_reg = list(REGIOES[est].keys())
                reg = st.selectbox(f"Região de {est}", options=opcoes_reg, key=f"reg_{est}")
                regioes_sel[est] = reg

    st.markdown("---")
    st.markdown("**Localização de referência**")
    cidade_ref = st.text_input("Cidade central", placeholder="Ex: Teófilo Otoni", help="Deixe vazio para buscar em todo o estado")
    raio_km = st.slider("Raio de busca (km)", 0, 500, 0, 25, help="0 = sem filtro de raio")
    if raio_km > 0:
        st.caption(f"Buscando num raio de {raio_km} km ao redor de {cidade_ref or 'cidade informada'}")

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

# RESULTADOS
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
            with st.spinner("Consultando fontes públicas..."):
                df = buscar_leads(estados_sel, modulos_sel, situacoes, score_min, cidade_ref, raio_km if raio_km > 0 else None, regioes_sel)
                st.session_state.df_resultado = df
                st.session_state.buscou = True

if st.session_state.buscou and not st.session_state.df_resultado.empty:
    df = st.session_state.df_resultado

    ref_txt = f" · Raio: {raio_km} km de {cidade_ref}" if (raio_km and cidade_ref) else ""
    st.success(f"✓ {len(df)} leads encontrados{ref_txt}")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total de leads", len(df))
    with c2: st.metric("Alto potencial", len(df[df["potencial"]=="Alto"]))
    with c3: st.metric("Usam diesel", len(df[df["situacao_rede"].str.contains("diesel",case=False,na=False)]))
    with c4: st.metric("Com CNPJ", len(df[df["cpf_cnpj"].astype(str).str.len()>5]))

    st.markdown("---")

    col_f1, col_f2 = st.columns([2,1])
    with col_f1:
        filtro_mod = st.selectbox("Filtrar por módulo", ["Todos"]+list(df["modulo"].unique()))
    with col_f2:
        ordenar = st.selectbox("Ordenar por", ["Score","Distância (km)","Município"])

    df_view = df if filtro_mod=="Todos" else df[df["modulo"]==filtro_mod]
    if ordenar == "Distância (km)" and "dist_km" in df_view.columns:
        df_view = df_view.sort_values("dist_km", na_position="last")
    elif ordenar == "Município":
        df_view = df_view.sort_values("municipio")

    colunas_tabela = [c for c in ["score","potencial","estado","municipio","dist_km","nome","modulo","situacao_rede","telefone","observacoes","fonte"] if c in df_view.columns]
    st.dataframe(
        df_view[colunas_tabela].reset_index(drop=True),
        use_container_width=True, height=440,
        column_config={
            "score": st.column_config.NumberColumn("Score", format="%.1f"),
            "dist_km": st.column_config.NumberColumn("Dist. km", format="%.0f km"),
            "estado": st.column_config.TextColumn("UF", width=55),
            "municipio": st.column_config.TextColumn("Município", width=140),
            "nome": st.column_config.TextColumn("Nome / Razão Social", width=210),
            "modulo": st.column_config.TextColumn("Módulo", width=120),
            "situacao_rede": st.column_config.TextColumn("Situação", width=200),
            "observacoes": st.column_config.TextColumn("Observações", width=200),
        }
    )

    st.markdown("---")
    col1,col2 = st.columns([2,1])
    with col1:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Baixar planilha Excel completa",
            data=gerar_excel(df.copy()),
            file_name=f"leads_solar_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col2:
        st.caption(f"{len(df)} leads · {len(df[df['potencial']=='Alto'])} alto potencial")

    if df["fonte"].str.contains("demo",case=False,na=False).any():
        st.info("ℹ️ Registros com '-demo' na coluna Fonte são ilustrativos (API indisponível no momento). Os demais são dados reais.")

elif st.session_state.buscou:
    st.warning("Nenhum lead encontrado. Reduza o score mínimo, aumente o raio ou amplie os estados.")
else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px">
    <div style="font-size:52px;margin-bottom:16px">☀️</div>
    <p style="font-size:16px;color:#64748b">Configure os filtros e clique em <b style="color:#f59e0b">Buscar leads agora</b></p>
    <p style="font-size:13px;color:#374151;margin-top:8px">SICAR · ANM · CCEE · ANEEL · Receita Federal</p>
    </div>""",unsafe_allow_html=True)
