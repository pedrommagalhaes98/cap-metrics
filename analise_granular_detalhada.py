import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

print("=== ANÁLISE GRANULAR DETALHADA ===")

# Valores base
custo_control = df_analise[df_analise['variant'] == 'control']['annual_cost'].sum()
custo_treatment = df_analise[df_analise['variant'] == 'treatment-b']['annual_cost'].sum()
reducao_total = custo_control - custo_treatment

tickets_control = df_analise[df_analise['variant'] == 'control']['tickets'].sum()
tickets_treatment = df_analise[df_analise['variant'] == 'treatment-b']['tickets'].sum()

print(f"Custo Controle: R$ {custo_control:,.0f}")
print(f"Custo Treatment-B: R$ {custo_treatment:,.0f}")
print(f"Redução Total: R$ {reducao_total:,.0f}")

print(f"\n=== 1. COMPONENTE: MIX DENTRO DE PAY PER TICKET (is_ppt === 1) ===")

# Filtrar apenas Pay Per Ticket
ppt_data = df_analise[df_analise['is_ppt'] == 1].copy()

if len(ppt_data) > 0:
    # Análise por squad dentro de PPT
    ppt_control = ppt_data[ppt_data['variant'] == 'control']
    ppt_treatment = ppt_data[ppt_data['variant'] == 'treatment-b']
    
    ppt_custo_control = ppt_control['annual_cost'].sum()
    ppt_custo_treatment = ppt_treatment['annual_cost'].sum()
    ppt_diferenca = ppt_custo_control - ppt_custo_treatment
    
    print(f"Custo PPT Control: R$ {ppt_custo_control:,.0f}")
    print(f"Custo PPT Treatment-B: R$ {ppt_custo_treatment:,.0f}")
    print(f"Diferença PPT: R$ {ppt_diferenca:,.0f}")
    
    # Análise detalhada por squad PPT
    ppt_analysis = ppt_data.groupby(['actor_squad', 'variant']).agg({
        'annual_cost': 'sum',
        'tickets': 'sum',
        'transfers': 'sum'
    }).reset_index()
    
    ppt_pivot = ppt_analysis.pivot(index='actor_squad', columns='variant', values=['annual_cost', 'tickets', 'transfers']).fillna(0)
    ppt_pivot.columns = ['_'.join(col).strip() for col in ppt_pivot.columns]
    ppt_pivot['diferenca_custo'] = ppt_pivot['annual_cost_control'] - ppt_pivot['annual_cost_treatment-b']
    ppt_pivot['diferenca_tickets'] = ppt_pivot['tickets_control'] - ppt_pivot['tickets_treatment-b']
    
    print(f"\nMudanças nos squads PPT:")
    for squad, row in ppt_pivot.iterrows():
        if abs(row['diferenca_custo']) > 50000:
            delta_tickets = -row['diferenca_tickets']
            delta_custo = -row['diferenca_custo']
            sinal_ticket = "+" if delta_tickets > 0 else ""
            sinal_custo = "+" if delta_custo > 0 else ""
            print(f"   {squad:20}: {sinal_ticket}{delta_tickets:6.0f} tickets → {sinal_custo}R$ {delta_custo/1000000:5.1f}M")

print(f"\n=== 2. COMPONENTE: MIX DENTRO DE PAY PER TIME (is_ppt === 0) ===")

# Filtrar apenas Pay Per Time
time_data = df_analise[df_analise['is_ppt'] == 0].copy()

time_control = time_data[time_data['variant'] == 'control']
time_treatment = time_data[time_data['variant'] == 'treatment-b']

time_custo_control = time_control['annual_cost'].sum()
time_custo_treatment = time_treatment['annual_cost'].sum()
time_diferenca = time_custo_control - time_custo_treatment

print(f"Custo Time Control: R$ {time_custo_control:,.0f}")
print(f"Custo Time Treatment-B: R$ {time_custo_treatment:,.0f}")
print(f"Diferença Time: R$ {time_diferenca:,.0f}")

# Análise detalhada por squad Time
time_analysis = time_data.groupby(['actor_squad', 'variant']).agg({
    'annual_cost': 'sum',
    'tickets': 'sum',
    'total_time_spent': 'sum'
}).reset_index()

time_pivot = time_analysis.pivot(index='actor_squad', columns='variant', values=['annual_cost', 'tickets', 'total_time_spent']).fillna(0)
time_pivot.columns = ['_'.join(col).strip() for col in time_pivot.columns]
time_pivot['diferenca_custo'] = time_pivot['annual_cost_control'] - time_pivot['annual_cost_treatment-b']
time_pivot['diferenca_tickets'] = time_pivot['tickets_control'] - time_pivot['tickets_treatment-b']
time_pivot['diferenca_time'] = time_pivot['total_time_spent_control'] - time_pivot['total_time_spent_treatment-b']

# Calcular tempo médio por ticket
time_pivot['avg_time_control'] = np.where(
    time_pivot['tickets_control'] > 0,
    time_pivot['total_time_spent_control'] / time_pivot['tickets_control'],
    0
)
time_pivot['avg_time_treatment'] = np.where(
    time_pivot['tickets_treatment-b'] > 0,
    time_pivot['total_time_spent_treatment-b'] / time_pivot['tickets_treatment-b'],
    0
)
time_pivot['diferenca_avg_time'] = time_pivot['avg_time_control'] - time_pivot['avg_time_treatment']

print(f"\nMudanças nos squads Pay Per Time:")
print(f"Squad                | Δ Tickets | Δ Tempo Total | Δ Tempo/Ticket | Δ Custo")
print("=" * 80)
for squad, row in time_pivot.iterrows():
    if abs(row['diferenca_custo']) > 50000:
        delta_tickets = -row['diferenca_tickets']
        delta_time_total = -row['diferenca_time']
        delta_avg_time = -row['diferenca_avg_time']
        delta_custo = -row['diferenca_custo']
        
        sinal_ticket = "+" if delta_tickets > 0 else ""
        sinal_time = "+" if delta_time_total > 0 else ""
        sinal_avg = "+" if delta_avg_time > 0 else ""
        sinal_custo = "+" if delta_custo > 0 else ""
        
        print(f"{squad:20} | {sinal_ticket}{delta_tickets:7.0f} | {sinal_time}{delta_time_total/3600:8.0f}h | {sinal_avg}{delta_avg_time:9.0f}s | {sinal_custo}R$ {delta_custo/1000000:4.1f}M")

print(f"\n=== 3. COMPONENTE: EFEITO VOLUME (ABANDONO +0.7pp) ===")

# Calcular efeito do aumento do abandono
# Unanswered rate: de 5.88% para 6.58% = +0.7pp = +11.98% relativo
aumento_abandono_pp = 0.7 / 100  # 0.7 pontos percentuais
volume_perdido_abandono = tickets_control * aumento_abandono_pp

# Estimar custo médio dos tickets abandonados
# Assumindo que são principalmente inbound calls (mais caros)
inbound_data = df_analise[df_analise['activity_type'] == 'inbound_call']
inbound_control = inbound_data[inbound_data['variant'] == 'control']
custo_medio_inbound = inbound_control['annual_cost'].sum() / inbound_control['tickets'].sum() if inbound_control['tickets'].sum() > 0 else 0

economia_abandono = volume_perdido_abandono * custo_medio_inbound

print(f"Volume base (Control): {tickets_control:,.0f} tickets")
print(f"Aumento abandono: +{aumento_abandono_pp*100:.1f}pp")
print(f"Tickets perdidos por abandono: {volume_perdido_abandono:,.0f}")
print(f"Custo médio inbound call: R$ {custo_medio_inbound:.2f}/ticket")
print(f"Economia por abandono: R$ {economia_abandono:,.0f}")

print(f"\n=== 4. COMPONENTE: EFEITO RETURN RATE (+0.39pp) ===")

# Return rate: de 21.09% para 21.49% = +0.39pp = +1.86% relativo
aumento_return_pp = 0.39 / 100  # 0.39 pontos percentuais
volume_adicional_return = tickets_control * aumento_return_pp

# Return rate gera custos adicionais em outros canais
# Assumindo 50% do custo original (canal mais barato que o abandonado)
custo_medio_geral = custo_control / tickets_control
custo_adicional_return = volume_adicional_return * custo_medio_geral * 0.5

print(f"Volume base (Control): {tickets_control:,.0f} tickets")
print(f"Aumento return rate: +{aumento_return_pp*100:.2f}pp")
print(f"Tickets adicionais return: {volume_adicional_return:,.0f}")
print(f"Custo médio geral: R$ {custo_medio_geral:.2f}/ticket")
print(f"Custo adicional return (50%): R$ {custo_adicional_return:,.0f}")

print(f"\n=== 5. VERIFICAÇÃO DOS COMPONENTES ===")

total_componentes = ppt_diferenca + time_diferenca + economia_abandono - custo_adicional_return
diferenca_residual = reducao_total - total_componentes

print(f"Componente PPT: R$ {ppt_diferenca:,.0f}")
print(f"Componente Time: R$ {time_diferenca:,.0f}")
print(f"Economia Abandono: R$ {economia_abandono:,.0f}")
print(f"Custo Return Rate: -R$ {custo_adicional_return:,.0f}")
print(f"Total Calculado: R$ {total_componentes:,.0f}")
print(f"Redução Real: R$ {reducao_total:,.0f}")
print(f"Diferença (outros efeitos): R$ {diferenca_residual:,.0f}")

erro_percent = abs(diferenca_residual) / reducao_total * 100
print(f"Erro: {erro_percent:.1f}%")

print(f"\n=== CASCATA GRANULAR PROPOSTA ===")
cascata_granular = [
    ("Custo Controle", custo_control),
    ("Mix Pay Per Ticket", ppt_diferenca),
    ("Mix Pay Per Time", time_diferenca),
    ("Economia Abandono (+0.7pp)", economia_abandono),
    ("Custo Return Rate (+0.39pp)", -custo_adicional_return),
    ("Outros Efeitos", diferenca_residual),
    ("Custo Treatment-B", custo_treatment)
]

verificacao = custo_control
for nome, valor in cascata_granular:
    if "Custo" in nome:
        print(f"{nome:30}: R$ {valor/1000000:6.1f}M")
    else:
        sinal = "+" if valor > 0 else ""
        print(f"{nome:30}: {sinal}R$ {valor/1000000:6.1f}M")
        verificacao += valor

print(f"{'VERIFICAÇÃO':30}: R$ {verificacao/1000000:6.1f}M")
diferenca_final = verificacao - custo_treatment
print(f"{'DIFERENÇA':30}: R$ {diferenca_final/1000000:6.1f}M")

if abs(diferenca_final) < 100000:
    print("✅ CASCATA MATEMATICAMENTE CORRETA!")
else:
    print("❌ Ainda há diferenças - precisa refinar")

print(f"\n=== INSIGHTS DA ANÁLISE GRANULAR ===")
print(f"1. Mix PPT vs Mix Time: Separar é importante pois têm dinâmicas diferentes")
print(f"2. Abandono: Economia significativa de R$ {economia_abandono/1000000:.1f}M")
print(f"3. Return Rate: Custo adicional pequeno de R$ {custo_adicional_return/1000000:.1f}M")
print(f"4. Efeito líquido abandono vs return: R$ {(economia_abandono - custo_adicional_return)/1000000:.1f}M")
print(f"5. PPT vs Time: {('PPT' if ppt_diferenca > time_diferenca else 'Time')} tem maior impacto")