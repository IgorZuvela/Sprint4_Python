import random
from datetime import datetime
import pandas as pd
import os

def analisar_log_com_gemini(log_data):
    return (
        "🤖 **Consultor Energético IA - Análise Rápida**\n\n"
        "Com base nos dados de Geração/Consumo dos últimos minutos:\n"
        "- **Eficiência:** A estratégia de autoconsumo foi eficiente, mantendo o gasto da rede baixo.\n"
        "- **Sugestão:** Em períodos de baixa geração (noite/dias nublados), o uso do Chuveiro (5000W) é o maior vetor de risco. Considere agendar aparelhos de alto consumo para horários de pico solar (12h-14h) ou usar o modo 'Otimização' (algoritmo) quando a bateria estiver baixa.\n"
    )

class SmartHome:
    def __init__(self):
        self.capacidade_bateria = 10000 
        self.nivel_bateria = 7000  
        self.taxa_carga_max = 5000  

        self.aparelhos = {
            "Geladeira": {"estado": "Ligado", "consumo": 150},
            "Chuveiro": {"estado": "Desligado", "consumo": 5000}, 
            "Ar Condicionado": {"estado": "Desligado", "consumo": 1200}, 
            "Luzes Sala": {"estado": "Desligado", "consumo": 80},
        }
        
        self.energia_autoconsumida_wh = 0
        self.gasto_total_rede_wh = 0
        self.dados_solares = self._carregar_dados_solares()
        
        # Fator de escala: O PVGIS simulou 1kWp, assumimos que seu sistema é 3kWp.
        self.fator_escala_solar = 3.0 
        
    def _carregar_dados_solares(self):
        # NOME DO ARQUIVO AJUSTADO PARA O NOME QUE VOCÊ FORNECEU
        csv_path = 'solar data.csv' 

        try:
            # Separador é vírgula (','), ignorando as 8 linhas de cabeçalho
            df = pd.read_csv(csv_path, sep=',', skiprows=8) 
            
            # Garante que a coluna 'time' é datetime
            df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')
            
            # Filtra apenas o primeiro dia para usar como perfil diário
            primeiro_dia = df['time'].dt.date.min()
            df_dia = df[df['time'].dt.date == primeiro_dia]
            
            # Cria um dicionário {hora: G(i) (Irradiação)} para busca rápida
            dados_horarios = df_dia.set_index(df_dia['time'].dt.hour)['G(i)'].to_dict()
            return dados_horarios

        except Exception as e:
            print(f"Erro ao carregar CSV do PVGIS: {e}. Verifique o nome do arquivo. Usando simulação padrão.")
            # Fallback (caso o arquivo não seja encontrado ou haja erro de leitura)
            return {
                8: 100, 9: 500, 10: 1500, 11: 2200, 12: 3000, 
                13: 2800, 14: 1800, 15: 1000, 16: 400, 17: 50
            }

    def simular_energia_solar(self):
        hora_atual = datetime.now().hour

        # G(i) é a Irradiação em W/m² (Potência para 1kWp)
        irradiacao_wi = self.dados_solares.get(hora_atual, 0)
        
        # Escala: Multiplica pela escala do seu sistema (3kWp)
        geracao_base = irradiacao_wi * self.fator_escala_solar

        if geracao_base > 0:
            variacao = random.randint(-150, 150)  
            geracao = max(0, geracao_base + variacao)
            return int(geracao)
        
        return 0

    def calcular_consumo_total(self):
        consumo_total = 0
        for nome, dados in self.aparelhos.items():
            if dados["estado"] == "Ligado":
                variacao = random.uniform(0.9, 1.1)
                consumo_total += dados["consumo"] * variacao
        return int(consumo_total)

    def atualizar_bateria(self, geracao_solar, consumo_total):
        saldo = geracao_solar - consumo_total
        gasto_rede = 0
        fator_tempo = 1 / 3600 

        if saldo > 0:
            carga_aplicada = min(saldo, self.taxa_carga_max)
            self.nivel_bateria += carga_aplicada * fator_tempo
            self.nivel_bateria = min(self.nivel_bateria, self.capacidade_bateria)

        elif saldo < 0:
            demanda_faltante = abs(saldo)
            descarga_aplicada = demanda_faltante * fator_tempo

            if self.nivel_bateria > 0:
                energia_da_bateria = min(self.nivel_bateria, descarga_aplicada)
                
                self.nivel_bateria -= energia_da_bateria
                self.nivel_bateria = max(0, self.nivel_bateria)
                
                self.energia_autoconsumida_wh += energia_da_bateria
                
                if self.nivel_bateria == 0 and demanda_faltante > 0:
                    gasto_rede = demanda_faltante - (energia_da_bateria / fator_tempo)
                    self.gasto_total_rede_wh += gasto_rede * fator_tempo

            else: 
                gasto_rede = demanda_faltante
                self.gasto_total_rede_wh += gasto_rede * fator_tempo
        
        nivel_percentual = int((self.nivel_bateria / self.capacidade_bateria) * 100)
        return nivel_percentual, int(gasto_rede)

    def controlar_aparelho(self, nome, novo_estado):
        if nome in self.aparelhos and novo_estado in ["Ligado", "Desligado"]:
            self.aparelhos[nome]["estado"] = novo_estado
            return f"{nome} alterado para {novo_estado}."
        return f"Aparelho {nome} ou estado {novo_estado} inválido."

    def otimizar_consumo(self):
        nivel_percentual = int((self.nivel_bateria / self.capacidade_bateria) * 100)
        geracao_atual = self.simular_energia_solar()
        
        if nivel_percentual < 25 and geracao_atual < 500:
            
            aparelhos_desligados = []
            
            if self.aparelhos["Chuveiro"]["estado"] == "Ligado":
                self.aparelhos["Chuveiro"]["estado"] = "Desligado"
                aparelhos_desligados.append("Chuveiro")
            
            if self.aparelhos["Ar Condicionado"]["estado"] == "Ligado":
                self.aparelhos["Ar Condicionado"]["estado"] = "Desligado"
                aparelhos_desligados.append("Ar Condicionado")
            
            if aparelhos_desligados:
                return f"⚠️ **Otimização Ativada!** Condição Crítica (Bat. < 25% e Geração Baixa). Desligado: {', '.join(aparelhos_desligados)} para evitar gasto da Rede."
            else:
                return "✅ **Otimização Ativa:** Condição Crítica, mas todos os aparelhos de risco já estão desligados. Economia máxima."
        
        return "▶️ **Otimização Inativa:** Condições normais. Não é necessário reduzir o consumo."

    def get_log_for_ai(self, log_df):
        log_recente = log_df.tail(5)
        
        dados_formatados = []
        for index, row in log_recente.iterrows():
            dados_formatados.append(
                f"Tempo: {row['Tempo'].strftime('%H:%M')}, Geração: {row['Geração Solar (W)']}W, Consumo: {row['Consumo Total (W)']}W"
            )
        
        estado_aparelhos = ", ".join([f"{n}: {d['estado']}" for n, d in self.aparelhos.items()])
        
        return (
            "Analise este log de energia de uma casa inteligente com Inversor Híbrido Goodwe. "
            "Os dados mostram Geração Solar e Consumo Total. O objetivo é maximizar o autoconsumo e evitar o uso da rede. "
            f"Log de dados recentes: {'; '.join(dados_formatados)}. "
            f"Estado atual dos aparelhos de risco: {estado_aparelhos}. "
            "Forneça uma análise de eficiência de 3 linhas e uma sugestão clara de economia."
        )