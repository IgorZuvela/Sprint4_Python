import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv 
from google import genai
from google.genai.errors import APIError

from casa_inteligente import SmartHome # Apenas SmartHome é importado agora

load_dotenv()

st.set_page_config(layout="wide", page_title="Smart Home - Solução Final Goodwe")


def carregar_estado():
    if 'home' not in st.session_state:
        st.session_state.home = SmartHome()

    if 'log_potencia' not in st.session_state:
        # Cria histórico inicial
        historico_tempo = [datetime.now() - timedelta(minutes=i) for i in range(5, 0, -1)]
        st.session_state.log_potencia = pd.DataFrame({
            'Tempo': historico_tempo,
            'Geração Solar (W)': [0] * 5,
            'Consumo Total (W)': [0] * 5
        })
    return st.session_state.home


def toggle_aparelho(nome):
    """Função de controle manual dos aparelhos."""
    home = carregar_estado()
    estado_atual = home.aparelhos[nome]["estado"]
    novo_estado = "Desligado" if estado_atual == "Ligado" else "Ligado"
    home.controlar_aparelho(nome, novo_estado)
    st.rerun()


def registrar_log(geracao, consumo):
    """Adiciona a leitura atual ao log e remove a leitura mais antiga."""
    log = st.session_state.log_potencia
    novo_log = pd.DataFrame({
        'Tempo': [datetime.now()],
        'Geração Solar (W)': [geracao],
        'Consumo Total (W)': [consumo]
    })
    st.session_state.log_potencia = pd.concat([log.iloc[1:], novo_log], ignore_index=True)


def call_gemini_api(log_data_prompt):
    """Implementação real da API Gemini."""
    
    # Tenta carregar a chave da variável de ambiente (GEMINI_API_KEY)
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key:
        return (
            "🚨 **CHAVE API NÃO ENCONTRADA:** Defina a variável GEMINI_API_KEY no arquivo `.env` para ativar a análise da IA."
            "\n\n*(Usando Resposta Simulada para fins de demonstração)*\n\n"
            "🤖 **Consultor Energético IA - Análise Rápida**\n"
            "- **Eficiência:** A estratégia de autoconsumo foi eficiente. Sugestão: agendar aparelhos de alto consumo para horários de pico solar (12h-14h)."
        )

    try:
        client = genai.Client(api_key=gemini_key) 
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Modelo rápido e eficiente para esta tarefa
            contents=[log_data_prompt]
        )
        return "🤖 **Análise de Log - Resposta Gemini:**\n\n" + response.text
    
    except APIError as e:
        return f"🚨 Erro na API Gemini (Verifique a Chave): {e}"
    
    except Exception as e:
        return f"🚨 Erro inesperado: {e}"

# =========================================================================
# === INÍCIO DA INTERFACE STREAMLIT ===
# =========================================================================

st.title("⚡ Solução Final Integrada - Goodwe Smart Home (Sprint 4)")
st.caption(f"Simulação de Dados em Tempo Real e Algoritmo Preditivo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

home = carregar_estado()

# 1. Cálculos de Fluxo
geracao_solar = home.simular_energia_solar()
consumo_total = home.calcular_consumo_total()
nivel_bateria_perc, gasto_rede = home.atualizar_bateria(geracao_solar, consumo_total)
registrar_log(geracao_solar, consumo_total)


# --- Seção 1: Arquitetura e Fluxo de Energia ---
st.header("1. Fluxo de Energia e Arquitetura Goodwe")

# Justificativa de Hardware (Requisito Goodwe)
with st.container(border=True):
    st.subheader("🛠️ Hardware Goodwe (Simulado)")
    col_inv, col_bat_hw = st.columns(2)
    col_inv.markdown(f"**Inversor Híbrido:** Goodwe ES 5000")
    col_inv.markdown(f"*Capacidade Máxima de Carga/Descarga:* `{home.taxa_carga_max} W`")
    col_bat_hw.markdown(f"**Bateria de Alta Voltagem:** Goodwe Lynx Home U")
    col_bat_hw.markdown(f"*Capacidade Total de Armazenamento:* `{home.capacidade_bateria:,} Wh`".replace(",", "."))
    st.caption("O sistema é projetado para integração total com a linha de produtos Goodwe.")

# Métricas Principais
col_gen, col_con, col_bat, col_rede, col_sust = st.columns(5)

col_gen.metric(
    label="⚡ Geração Solar (W) - (Perfil PVGIS)",
    value=f"{geracao_solar:,}".replace(",", ".")
)
col_con.metric(
    label="🏠 Consumo Total (W)",
    value=f"{consumo_total:,}".replace(",", ".")
)
col_bat.metric(
    label="🔋 Nível da Bateria",
    value=f"{nivel_bateria_perc}%",
    delta=f"Capacidade: {int(home.nivel_bateria):,} Wh".replace(",", ".")
)
col_rede.metric(
    label="🌐 Gasto da Rede (W)",
    value=f"{gasto_rede:,}".replace(",", "."),
    delta_color="inverse",
    delta="Cuidado! Usando a Rede." if gasto_rede > 0 else "Energia 100% Própria."
)

# KPI de Sustentabilidade (Requisito Sustentabilidade)
# 0.0005 kg CO2/Wh é uma simulação de fator de emissão médio
co2_evitado = home.energia_autoconsumida_wh * 0.000005 
col_sust.metric(
    label="🌿 CO2 Evitado (kg)",
    value=f"{co2_evitado:.2f}",
    delta="Autoconsumo: Alta Eficiência.",
    delta_color="normal"
)

# Gráfico
st.subheader("Gráfico de Potência em Tempo Real (5 min)")
st.line_chart(
    st.session_state.log_potencia,
    x='Tempo',
    y=['Geração Solar (W)', 'Consumo Total (W)'],
    use_container_width=True
)

st.markdown("---")


# --- Seção 2: Controle, Automação e Otimização (A Inovação) ---
st.header("2. Otimização Inteligente e Controle de Carga")

# BOTÃO DE OTIMIZAÇÃO (O ALGORITMO PREDITIVO)
col_btn, col_msg = st.columns([1, 2])

with col_btn:
    if st.button("🤖 ATIVAR OTIMIZAÇÃO INTELIGENTE", use_container_width=True, type="primary"):
        mensagem_otimizacao = home.otimizar_consumo()
        st.session_state.otimizacao_status = mensagem_otimizacao # Armazena o resultado
        st.rerun()

# Exibe o status da otimização
if 'otimizacao_status' in st.session_state:
    with col_msg:
        if "Ativada" in st.session_state.otimizacao_status:
            st.warning(st.session_state.otimizacao_status)
        else:
            st.success(st.session_state.otimizacao_status)
else:
    with col_msg:
        st.info("Algoritmo de Otimização Inativo. Clique para que o sistema decida se precisa reduzir o consumo automaticamente.")


# Controle Manual
st.subheader("Controle Manual de Carga")
cols = st.columns(len(home.aparelhos))
i = 0

for nome, dados in home.aparelhos.items():
    comsumo_exibicao = f"({dados['consumo']}W)"

    with cols[i]:
        st.markdown(f"**{nome}**")
        emoji = "🟢" if dados["estado"] == "Ligado" else "🔴"
        st.info(f"{emoji} Status: {dados['estado']} {comsumo_exibicao}")

        if st.button(f"Alternar Estado ({nome})", key=f"btn_{nome}"):
            toggle_aparelho(nome)

st.markdown("---")


# --- Seção 3: Consultor Energético IA (A Inovação de Alto Impacto) ---
st.header("3. Consultor Energético IA (Análise Preditiva)")

col_ai_btn, col_ai_analise = st.columns([1, 2])

with col_ai_btn:
    if st.button("🧠 Gerar Análise de Logs (IA Gemini)", use_container_width=True):
        st.session_state.ia_analise = "Analisando dados com Gemini..."
        # Pega o log formatado da SmartHome
        log_prompt = home.get_log_for_ai(st.session_state.log_potencia)
        # Chama a função que contém a API
        st.session_state.ia_analise = call_gemini_api(log_prompt) 

with col_ai_analise:
    if 'ia_analise' in st.session_state:
        st.markdown(st.session_state.ia_analise)
    else:
        st.info("A IA analisa seu histórico para dar sugestões de economia e eficiência.")

st.markdown("---")
st.caption("Tabela de Histórico de Potência (Log)")
st.dataframe(
    st.session_state.log_potencia.sort_values(by='Tempo', ascending=False),
    hide_index=True
)