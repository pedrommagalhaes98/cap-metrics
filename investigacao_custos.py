import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')

# Filtrar apenas control e treatment-b
df = df[df['variant'].isin(['control', 'treatment-b'])]

print("=== INVESTIGAÇÃO DOS CUSTOS ===")

# Analisar algumas linhas específicas para entender a escala
print("\n=== ANÁLISE DE ALGUMAS LINHAS (PAY PER TIME) ===")
df_time = df[df['is_ppt'] == 0].head(10)

for idx, row in df_time.iterrows():
    time_spent = row['total_time_spent']
    annual_cost = row['annual_cost']
    tickets = row['tickets']
    
    if time_spent > 0:
        custo_por_segundo = annual_cost / time_spent
        custo_por_ticket = annual_cost / tickets if tickets > 0 else 0
        
        print(f"{row['activity_type']:12s} | Time: {time_spent:>8,.0f}s | Cost: R$ {annual_cost:>10,.0f} | R$/s: {custo_por_segundo:.4f} | R$/tkt: {custo_por_ticket:.0f}")

# Vamos calcular o custo médio por segundo para cada canal
print(f"\n=== CUSTO MÉDIO POR SEGUNDO POR CANAL (PAY PER TIME) ===")
df_time_all = df[df['is_ppt'] == 0]

for canal in df_time_all['activity_type'].unique():
    df_canal = df_time_all[df_time_all['activity_type'] == canal]
    
    total_time = df_canal['total_time_spent'].sum()
    total_cost = df_canal['annual_cost'].sum()
    
    if total_time > 0:
        custo_por_segundo = total_cost / total_time
        print(f"{canal:15s}: R$ {custo_por_segundo:.6f}/segundo")

# Verificar se há multiplicadores ou fatores de anualização
print(f"\n=== INVESTIGAÇÃO DE FATORES DE ESCALA ===")

# Custos unitários fornecidos
agentCostPerSecond = 0.0233
ivrCost = 0.00055
BYOcost = 0.0004
twillioCost = 0.0045
zendeskCost = 0.005

phone_cost_per_second = agentCostPerSecond + twillioCost + ivrCost + BYOcost
backoffice_cost_per_second = zendeskCost

print(f"Custo unitário phone esperado: R$ {phone_cost_per_second:.6f}/segundo")
print(f"Custo unitário backoffice esperado: R$ {backoffice_cost_per_second:.6f}/segundo")

# Calcular fatores multiplicadores
df_phone = df_time_all[df_time_all['activity_type'] == 'inbound_call']
df_backoffice = df_time_all[df_time_all['activity_type'] == 'backoffice']

if len(df_phone) > 0:
    total_time_phone = df_phone['total_time_spent'].sum()
    total_cost_phone = df_phone['annual_cost'].sum()
    custo_real_phone = total_cost_phone / total_time_phone if total_time_phone > 0 else 0
    fator_phone = custo_real_phone / phone_cost_per_second if phone_cost_per_second > 0 else 0
    print(f"\nPhone - Custo real: R$ {custo_real_phone:.6f}/s | Fator: {fator_phone:.1f}x")

if len(df_backoffice) > 0:
    total_time_backoffice = df_backoffice['total_time_spent'].sum()
    total_cost_backoffice = df_backoffice['annual_cost'].sum()
    custo_real_backoffice = total_cost_backoffice / total_time_backoffice if total_time_backoffice > 0 else 0
    fator_backoffice = custo_real_backoffice / backoffice_cost_per_second if backoffice_cost_per_second > 0 else 0
    print(f"Backoffice - Custo real: R$ {custo_real_backoffice:.6f}/s | Fator: {fator_backoffice:.1f}x")

# Verificar se os dados estão em dias em vez de total
print(f"\n=== VERIFICAÇÃO DE UNIDADES DE TEMPO ===")
df_sample = df_time_all.head(5)

for idx, row in df_sample.iterrows():
    days = row['days']
    time_spent = row['total_time_spent']
    avg_time = row['average_time_spent']
    tickets = row['tickets']
    
    # Calcular tempo total esperado
    tempo_total_esperado = avg_time * tickets
    
    print(f"Squad: {row['actor_squad']:15s} | Days: {days:2.0f} | Total_time: {time_spent:>8,.0f} | Avg*Tickets: {tempo_total_esperado:>8,.0f} | Ratio: {time_spent/tempo_total_esperado:.2f}")

# Verificar se há projeção anual
print(f"\n=== VERIFICAÇÃO DE FATORES ANUAIS ===")
for idx, row in df_sample.iterrows():
    days = row['days']
    tickets = row['tickets']
    annual_cost = row['annual_cost']
    
    # Fator de anualização baseado em dias
    if days > 0:
        fator_anual_dias = 365 / days
        tickets_anuais_esperados = tickets * fator_anual_dias
        
        print(f"Squad: {row['actor_squad']:15s} | Days: {days:2.0f} | Tickets período: {tickets:4.0f} | Tickets anuais esperados: {tickets_anuais_esperados:>8,.0f}")