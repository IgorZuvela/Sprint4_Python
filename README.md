# ⚡ Solução Final Integrada: Goodwe Smart Home (Sprint 4)

## 🏡 Gerenciamento de Energia Inteligente com Otimização Preditiva e IA

Este projeto implementa um sistema de gerenciamento de energia (Home Energy Management System - HEMS) simulando a arquitetura de um inversor híbrido Goodwe, com foco em maximizar o **autoconsumo**, minimizar o **gasto da rede elétrica** e integrar **Inteligência Artificial (IA)** para análise e tomada de decisão.

---

## 👥 Equipe 

* **Membros:** [Igor Zuvela, João Vitor, Miguel Vanucci, Giovanna Fernandes]
* **RM:** [563602, 566541, 563491, 565434]
* **Disciplina:** [Pensamento Computacional e automação com python]

---

## 📐 Descrição Detalhada da Arquitetura Final e Integração

O projeto segue uma arquitetura modular, permitindo o escalonamento e a fácil manutenção dos componentes:

### 1. Sistema Físico (Simulado)
* **Geração:** Dados de Irradiação Solar (W/m²) importados de relatórios **PVGIS** (`solar data.csv`), escalados para um sistema hipotético de **3kWp** (Painéis Solares).
* **Armazenamento:** Simulação de uma Bateria de Alta Voltagem **Goodwe Lynx Home U** (Capacidade: 10.000 Wh), controlada por limites de carga/descarga.
* **Inversor Híbrido:** O coração da lógica de gerenciamento, simulando um inversor **Goodwe ES Series** (Taxa Máx. de Carga: 5.000W).

### 2. Fluxo de Dados e Componentes
A lógica central está na classe `SmartHome` (`casa_inteligente.py`), que realiza o loop de simulação:

1.  **Geração:** `SmartHome.simular_energia_solar()`
2.  **Consumo:** `SmartHome.calcular_consumo_total()` (baseado no estado atual dos aparelhos).
3.  **Gerenciamento:** `SmartHome.atualizar_bateria()` decide o fluxo:
    * Se **Geração > Consumo**, a energia excedente carrega a bateria.
    * Se **Consumo > Geração**, a demanda é atendida primeiro pela bateria.
    * Se a bateria estiver esgotada, o **Gasto da Rede (W)** é registrado.

### 3. Inovação e IA
* **Algoritmo Preditivo de Otimização (`SmartHome.otimizar_consumo`):** O sistema checa automaticamente duas condições críticas (Bateria `< 25%` E Geração Solar `< 500W`) para evitar a compra de energia, desligando automaticamente aparelhos de alto risco (Chuveiro, Ar Condicionado).
* **Consultor Energético IA:** Utiliza a API **Gemini (Google GenAI)** para analisar o `log_potencia` recente e gerar, em tempo real, sugestões de economia e eficiência, traduzindo dados brutos em ações práticas para o usuário final.

---

## 🎯 Justificativa de Alinhamento (Desafio Goodwe e Disciplina)

| Requisito | Alinhamento ao Projeto |
| :--- | :--- |
| **Desafio Goodwe:** HEMS | Implementação completa de controle de fluxo de energia (Geração, Bateria, Consumo e Rede). |
| **Desafio Goodwe:** Sustentabilidade | Cálculo e exibição do **CO2 Evitado (kg)**, quantificando o benefício ambiental do autoconsumo. |
| **Inovação (Disciplina)** | Integração do algoritmo de otimização preditiva (redução de gastos) e do **Consultor IA (Gemini)** para análise proativa. |
| **Arquitetura (Disciplina)** | Uso de Python, **Streamlit** (frontend), **Pandas** (dados) e ambiente virtual isolado, garantindo a portabilidade da solução. |

---

## 📈 Resultados Obtidos

### Resultados Quantitativos
* **Simulação Realista:** Os dados de Geração Solar refletem o perfil solar geográfico (PVGIS), permitindo testes práticos em diferentes horários do dia.
* **Otimização Comprovada:** Ao ativar a otimização, o sistema demonstrou capacidade de evitar picos de consumo da rede quando a bateria está baixa e o sol está fraco.
* **Acúmulo de Sustentabilidade:** A métrica de **CO2 Evitado (kg)** é acumulativa, permitindo a quantificação do impacto ambiental ao longo do tempo.

### Resultados Qualitativos
* **UX/UI Eficiente:** O dashboard Streamlit é intuitivo, com KPIs claros e controle manual de carga, replicando a experiência de um software de monitoramento de inversores.
* **Análise Inteligente:** A integração da IA transforma o
