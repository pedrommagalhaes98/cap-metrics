import pandas as pd
import numpy as np

# CUSTOS UNITÁRIOS FORNECIDOS PELO USUÁRIO
agentCostPerSecond = 0.0233
ivrCost = 0.00055
BYOcost = 0.0004
twillioCost = 0.0045
zendeskCost = 0.005

# Custo total por segundo para diferentes canais
phone_cost_per_second = agentCostPerSecond + twillioCost + ivrCost + BYOcost
backoffice_cost_per_second = zendeskCost
chat_cost_per_second = agentCostPerSecond + 0.001  # Assumindo custo do chat

print("=== CUSTOS UNITÁRIOS POR SEGUNDO ===")
print(f"Phone: R$ {phone_cost_per_second:.6f}/segundo")
print(f"Backoffice: R$ {backoffice_cost_per_second:.6f}/segundo")
print(f"Chat: R$ {chat_cost_per_second:.6f}/segundo")

# Carregar dados
try:
    df_routing = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
    df_ppt_costs = pd.read_csv('/Users/pedro.magalhaes/Downloads/Pay_per_ticket_costs.csv')
    print(f"✅ Dados carregados - {len(df_routing)} linhas")
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    exit()

# Filtrar apenas control e treatment-b
df = df_routing[df_routing['variant'].isin(['control', 'treatment-b'])].copy()

print(f"\n=== DADOS FILTRADOS ===")
print(f"Linhas: {len(df)}")
print(f"Variants: {df['variant'].value_counts()}")

# RECALCULAR CUSTOS PAY PER TIME USANDO OS CUSTOS UNITÁRIOS CORRETOS
def calcular_custo_pay_per_time(row):
    """Calcula o custo Pay Per Time baseado no canal e tempo total"""
    time_spent = row['total_time_spent']
    
    if row['activity_type'] == 'phone':
        return time_spent * phone_cost_per_second
    elif row['activity_type'] == 'backoffice':
        return time_spent * backoffice_cost_per_second
    elif row['activity_type'] == 'chat':
        return time_spent * chat_cost_per_second
    else:
        # Para outros canais, usar custo padrão phone
        return time_spent * phone_cost_per_second

# Aplicar recálculo apenas para Pay Per Time (is_ppt == 0)
df['custo_recalculado'] = df.apply(lambda row: 
    calcular_custo_pay_per_time(row) if row['is_ppt'] == 0 else row['annual_cost'], 
    axis=1
)

# Comparar custos originais vs recalculados
df_time_only = df[df['is_ppt'] == 0].copy()

print(f"\n=== COMPARAÇÃO CUSTOS PAY PER TIME ===")
custo_original_total = df_time_only['annual_cost'].sum()
custo_recalculado_total = df_time_only['custo_recalculado'].sum()

print(f"Custo original total (Pay Per Time): R$ {custo_original_total:,.0f}")
print(f"Custo recalculado total (Pay Per Time): R$ {custo_recalculado_total:,.0f}")
print(f"Diferença: R$ {custo_recalculado_total - custo_original_total:,.0f}")
print(f"Variação: {((custo_recalculado_total / custo_original_total) - 1) * 100:.1f}%")

# Análise por canal
print(f"\n=== COMPARAÇÃO POR CANAL (PAY PER TIME) ===")
for canal in df_time_only['activity_type'].unique():
    df_canal = df_time_only[df_time_only['activity_type'] == canal]
    orig = df_canal['annual_cost'].sum()
    recalc = df_canal['custo_recalculado'].sum()
    print(f"{canal:12s}: Original R$ {orig:>10,.0f} | Recalculado R$ {recalc:>10,.0f} | Δ R$ {recalc-orig:>8,.0f}")

# Usar custos recalculados para a análise
df['annual_cost_final'] = df.apply(lambda row: 
    row['custo_recalculado'] if row['is_ppt'] == 0 else row['annual_cost'], 
    axis=1
)

# ANÁLISE GRANULAR COM CUSTOS CORRETOS
print(f"\n" + "="*60)
print("=== ANÁLISE GRANULAR COM CUSTOS REFINADOS ===")
print("="*60)

df_control = df[df['variant'] == 'control'].copy()
df_treatment_b = df[df['variant'] == 'treatment-b'].copy()

custo_control_final = df_control['annual_cost_final'].sum()
custo_treatment_b_final = df_treatment_b['annual_cost_final'].sum()
reducao_total_final = custo_control_final - custo_treatment_b_final

print(f"Custo Control (refinado): R$ {custo_control_final:,.0f}")
print(f"Custo Treatment-B (refinado): R$ {custo_treatment_b_final:,.0f}")
print(f"Redução Total (refinada): R$ {reducao_total_final:,.0f}")

# 1. COMPONENTE: MIX DENTRO DE PAY PER TICKET
print(f"\n=== 1. MIX DENTRO DE PAY PER TICKET ===")
df_ppt_control = df_control[df_control['is_ppt'] == 1].copy()
df_ppt_treatment_b = df_treatment_b[df_treatment_b['is_ppt'] == 1].copy()

custo_ppt_control = df_ppt_control['annual_cost_final'].sum()
custo_ppt_treatment_b = df_ppt_treatment_b['annual_cost_final'].sum()
diferenca_ppt = custo_ppt_control - custo_ppt_treatment_b

print(f"Custo PPT Control: R$ {custo_ppt_control:,.0f}")
print(f"Custo PPT Treatment-B: R$ {custo_ppt_treatment_b:,.0f}")
print(f"Economia PPT: R$ {diferenca_ppt:,.0f}")

# 2. COMPONENTE: MIX DENTRO DE PAY PER TIME
print(f"\n=== 2. MIX DENTRO DE PAY PER TIME ===")
df_time_control = df_control[df_control['is_ppt'] == 0].copy()
df_time_treatment_b = df_treatment_b[df_treatment_b['is_ppt'] == 0].copy()

custo_time_control = df_time_control['annual_cost_final'].sum()
custo_time_treatment_b = df_time_treatment_b['annual_cost_final'].sum()
diferenca_time = custo_time_control - custo_time_treatment_b

print(f"Custo Time Control: R$ {custo_time_control:,.0f}")
print(f"Custo Time Treatment-B: R$ {custo_time_treatment_b:,.0f}")
print(f"Diferença Time: R$ {diferenca_time:,.0f}")

# 3. EFEITO VOLUME (ABANDONO)
print(f"\n=== 3. EFEITO VOLUME (ABANDONO +0.7pp) ===")
volume_base = df_control['tickets'].sum()
aumento_abandono = 0.007  # 0.7pp
tickets_perdidos_abandono = volume_base * aumento_abandono

# Custo médio por ticket inbound (phone principalmente)
df_phone_control = df_control[df_control['activity_type'] == 'phone']
custo_medio_phone = df_phone_control['annual_cost_final'].sum() / df_phone_control['tickets'].sum()

economia_abandono = tickets_perdidos_abandono * custo_medio_phone

print(f"Volume base Control: {volume_base:,.0f} tickets")
print(f"Tickets perdidos abandono: {tickets_perdidos_abandono:,.0f}")
print(f"Custo médio phone: R$ {custo_medio_phone:,.2f}/ticket")
print(f"Economia abandono: R$ {economia_abandono:,.0f}")

# 4. EFEITO RETURN RATE
print(f"\n=== 4. EFEITO RETURN RATE (+0.39pp) ===")
aumento_return = 0.0039  # 0.39pp
tickets_adicionais_return = volume_base * aumento_return

# Custo médio geral
custo_medio_geral = df_control['annual_cost_final'].sum() / df_control['tickets'].sum()
custo_return_rate = tickets_adicionais_return * custo_medio_geral * 0.5  # 50% dos tickets retornam

print(f"Tickets adicionais return: {tickets_adicionais_return:,.0f}")
print(f"Custo médio geral: R$ {custo_medio_geral:,.2f}/ticket")
print(f"Custo adicional return: R$ {custo_return_rate:,.0f}")

# VERIFICAÇÃO FINAL
print(f"\n" + "="*50)
print("=== VERIFICAÇÃO MATEMÁTICA REFINADA ===")
print("="*50)

componentes = [
    ("PPT Mix", diferenca_ppt),
    ("Time Mix", diferenca_time),
    ("Abandono", economia_abandono),
    ("Return Rate", -custo_return_rate),
]

total_componentes = sum([comp[1] for comp in componentes])
outros_efeitos = reducao_total_final - total_componentes

print(f"Custo Control: R$ {custo_control_final:,.0f}")
for nome, valor in componentes:
    sinal = "+" if valor >= 0 else ""
    print(f"{nome:12s}: {sinal}R$ {valor:>10,.0f}")
print(f"{'Outros Efeitos':12s}: {'+' if outros_efeitos >= 0 else ''}R$ {outros_efeitos:>10,.0f}")
print(f"{'='*25}")
print(f"{'Resultado':12s}: R$ {custo_control_final - total_componentes - outros_efeitos:>10,.0f}")
print(f"{'Target':12s}: R$ {custo_treatment_b_final:>10,.0f}")
print(f"{'Diferença':12s}: R$ {abs(custo_treatment_b_final - (custo_control_final - total_componentes - outros_efeitos)):>10,.0f}")

erro_percentual = abs(outros_efeitos / reducao_total_final) * 100
print(f"\n💡 Erro residual: {erro_percentual:.1f}%")

if erro_percentual < 5:
    print("✅ EXCELENTE! Decomposição muito precisa!")
elif erro_percentual < 10:
    print("✅ BOM! Decomposição razoavelmente precisa!")
else:
    print("⚠️  Ainda há espaço para melhoria na decomposição")

print(f"\n=== CASCATA FINAL REFINADA ===")
print(f"Custo Control           : R$ {custo_control_final/1e6:>6.1f}M")
print(f"Mix Pay Per Ticket      : R$ {diferenca_ppt/1e6:>6.1f}M")
print(f"Mix Pay Per Time        : R$ {diferenca_time/1e6:>6.1f}M")
print(f"Economia Abandono       : R$ {economia_abandono/1e6:>6.1f}M")
print(f"Custo Return Rate       : R$ {-custo_return_rate/1e6:>6.1f}M")
print(f"Outros Efeitos          : R$ {outros_efeitos/1e6:>6.1f}M")
print(f"Custo Treatment-B       : R$ {custo_treatment_b_final/1e6:>6.1f}M")