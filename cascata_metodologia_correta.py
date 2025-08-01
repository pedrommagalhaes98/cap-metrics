import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

print("=== METODOLOGIA CORRETA: PRICE-VOLUME-MIX DECOMPOSITION ===")

# Valores base
control_data = df_analise[df_analise['variant'] == 'control']
treatment_data = df_analise[df_analise['variant'] == 'treatment-b']

custo_control = control_data['annual_cost'].sum()
custo_treatment = treatment_data['annual_cost'].sum()
reducao_total = custo_control - custo_treatment

tickets_control = control_data['tickets'].sum()
tickets_treatment = treatment_data['tickets'].sum()

print(f"Custo Controle: R$ {custo_control:,.0f}")
print(f"Custo Treatment-B: R$ {custo_treatment:,.0f}")
print(f"Redução Total: R$ {reducao_total:,.0f}")

print(f"\n=== DECOMPOSIÇÃO METODOLOGICAMENTE CORRETA ===")

# MÉTODO: Isolamento de cada efeito mantendo outros constantes

# 1. EFEITO VOLUME PURO
# Se Treatment-B tivesse o mesmo mix e eficiência do Control, mas com seu volume
custo_medio_control = custo_control / tickets_control
efeito_volume_puro = (tickets_treatment - tickets_control) * custo_medio_control

print(f"\n1. EFEITO VOLUME PURO:")
print(f"   Volume Control: {tickets_control:,} tickets")
print(f"   Volume Treatment-B: {tickets_treatment:,} tickets")
print(f"   Mudança Volume: {tickets_treatment - tickets_control:,} tickets")
print(f"   Custo médio Control: R$ {custo_medio_control:.2f}/ticket")
print(f"   Efeito Volume: R$ {efeito_volume_puro:,.0f}")

# 2. EFEITO MIX PURO
# Mudança na distribuição entre squads, mantendo volume do Treatment-B e eficiência do Control
print(f"\n2. EFEITO MIX PURO:")

# Calcular mix percentual por squad
control_por_squad = control_data.groupby('actor_squad').agg({
    'tickets': 'sum',
    'annual_cost': 'sum'
}).reset_index()
control_por_squad['percent_tickets'] = control_por_squad['tickets'] / tickets_control
control_por_squad['custo_por_ticket'] = control_por_squad['annual_cost'] / control_por_squad['tickets']

treatment_por_squad = treatment_data.groupby('actor_squad').agg({
    'tickets': 'sum',
    'annual_cost': 'sum'
}).reset_index()
treatment_por_squad['percent_tickets'] = treatment_por_squad['tickets'] / tickets_treatment

# Merge para ter ambos os mixes
mix_analysis = control_por_squad[['actor_squad', 'percent_tickets', 'custo_por_ticket']].rename(
    columns={'percent_tickets': 'mix_control', 'custo_por_ticket': 'custo_control_per_ticket'}
).merge(
    treatment_por_squad[['actor_squad', 'percent_tickets']].rename(
        columns={'percent_tickets': 'mix_treatment'}
    ), on='actor_squad', how='outer'
).fillna(0)

# Calcular efeito mix para cada squad
mix_analysis['mudanca_mix'] = mix_analysis['mix_treatment'] - mix_analysis['mix_control']
mix_analysis['efeito_mix_squad'] = (
    mix_analysis['mudanca_mix'] * tickets_treatment * mix_analysis['custo_control_per_ticket']
)

efeito_mix_total = mix_analysis['efeito_mix_squad'].sum()

print(f"   Principais mudanças de mix:")
top_mix_changes = mix_analysis.nlargest(5, 'efeito_mix_squad')[['actor_squad', 'mudanca_mix', 'efeito_mix_squad']]
for _, row in top_mix_changes.iterrows():
    squad = row['actor_squad']
    mudanca = row['mudanca_mix'] * 100
    efeito = row['efeito_mix_squad']
    print(f"   {squad}: {mudanca:+.1f}pp → R$ {efeito:,.0f}")

bottom_mix_changes = mix_analysis.nsmallest(5, 'efeito_mix_squad')[['actor_squad', 'mudanca_mix', 'efeito_mix_squad']]
for _, row in bottom_mix_changes.iterrows():
    squad = row['actor_squad']
    mudanca = row['mudanca_mix'] * 100
    efeito = row['efeito_mix_squad']
    if efeito < -100000:  # Só mostrar mudanças significativas
        print(f"   {squad}: {mudanca:+.1f}pp → R$ {efeito:,.0f}")

print(f"\n   Efeito MIX total: R$ {efeito_mix_total:,.0f}")

# 3. EFEITO EFICIÊNCIA/PREÇO PURO
# Mudança no custo por ticket dentro de cada squad, usando o volume do Treatment-B
print(f"\n3. EFEITO EFICIÊNCIA/PREÇO PURO:")

# Para cada squad, calcular mudança no custo por ticket
efficiency_analysis = []
for squad in treatment_por_squad['actor_squad']:
    control_squad = control_data[control_data['actor_squad'] == squad]
    treatment_squad = treatment_data[treatment_data['actor_squad'] == squad]
    
    if len(control_squad) > 0 and len(treatment_squad) > 0:
        # Custo por ticket
        control_cost_per_ticket = control_squad['annual_cost'].sum() / control_squad['tickets'].sum()
        treatment_cost_per_ticket = treatment_squad['annual_cost'].sum() / treatment_squad['tickets'].sum()
        treatment_tickets = treatment_squad['tickets'].sum()
        
        # Efeito eficiência
        mudanca_cost_per_ticket = treatment_cost_per_ticket - control_cost_per_ticket
        efeito_eficiencia_squad = mudanca_cost_per_ticket * treatment_tickets
        
        efficiency_analysis.append({
            'squad': squad,
            'treatment_tickets': treatment_tickets,
            'mudanca_cost_per_ticket': mudanca_cost_per_ticket,
            'efeito_eficiencia': efeito_eficiencia_squad
        })

df_efficiency = pd.DataFrame(efficiency_analysis)
efeito_eficiencia_total = df_efficiency['efeito_eficiencia'].sum()

print(f"   Principais mudanças de eficiência:")
# Mostrar top e bottom 5
top_eff = df_efficiency.nlargest(5, 'efeito_eficiencia')
bottom_eff = df_efficiency.nsmallest(5, 'efeito_eficiencia')

for _, row in top_eff.iterrows():
    if row['efeito_eficiencia'] > 100000:
        print(f"   {row['squad']}: R$ {row['mudanca_cost_per_ticket']:+.0f}/ticket → R$ {row['efeito_eficiencia']:,.0f}")

for _, row in bottom_eff.iterrows():
    if row['efeito_eficiencia'] < -100000:
        print(f"   {row['squad']}: R$ {row['mudanca_cost_per_ticket']:+.0f}/ticket → R$ {row['efeito_eficiencia']:,.0f}")

print(f"\n   Efeito EFICIÊNCIA total: R$ {efeito_eficiencia_total:,.0f}")

# 4. VERIFICAÇÃO
print(f"\n=== VERIFICAÇÃO METODOLÓGICA ===")
total_calculado = efeito_volume_puro + efeito_mix_total + efeito_eficiencia_total
print(f"Efeito Volume: R$ {efeito_volume_puro:,.0f}")
print(f"Efeito Mix: R$ {efeito_mix_total:,.0f}")
print(f"Efeito Eficiência: R$ {efeito_eficiencia_total:,.0f}")
print(f"Total Calculado: R$ {total_calculado:,.0f}")
print(f"Redução Real: R$ {reducao_total:,.0f}")
print(f"Diferença: R$ {total_calculado - reducao_total:,.0f}")

diferenca_percent = abs(total_calculado - reducao_total) / reducao_total * 100
print(f"Erro: {diferenca_percent:.1f}%")

# 5. ORDEM LÓGICA PARA A CASCATA
print(f"\n=== ORDEM LÓGICA CORRETA PARA CASCATA ===")
print("1. EFEITO VOLUME: Mudança no número total de tickets")
print("   - Causado por: abandono (+0.7pp), return rate effects")
print("   - Mantém mix e eficiência constantes")
print()
print("2. EFEITO MIX: Redistribuição entre squads")  
print("   - Causado por: melhor direcionamento speech-to-text")
print("   - Mantém volume total e eficiência constantes")
print()
print("3. EFEITO EFICIÊNCIA: Mudança custo/ticket por squad")
print("   - Causado por: melhor matching, mudança PPT vs PPTime")
print("   - Usa volume e mix finais")

# 6. INTERPRETAÇÃO DOS RESULTADOS
print(f"\n=== INTERPRETAÇÃO DOS RESULTADOS ===")

if abs(diferenca_percent) < 5:
    print("✅ Decomposição VÁLIDA (erro < 5%)")
    
    print(f"\n📊 PRINCIPAIS DRIVERS:")
    componentes = [
        ("Volume", efeito_volume_puro),
        ("Mix", efeito_mix_total), 
        ("Eficiência", efeito_eficiencia_total)
    ]
    
    for nome, valor in sorted(componentes, key=lambda x: abs(x[1]), reverse=True):
        percent_contribuicao = abs(valor) / abs(reducao_total) * 100
        sinal = "redução" if valor < 0 else "aumento"
        print(f"   {nome}: R$ {valor/1000000:.1f}M ({sinal}) - {percent_contribuicao:.0f}% da economia")
        
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   A economia de R$ {reducao_total/1000000:.1f}M vem principalmente de:")
    
    if abs(efeito_mix_total) > abs(efeito_volume_puro) and abs(efeito_mix_total) > abs(efeito_eficiencia_total):
        print(f"   1. MUDANÇA DE MIX: Speech-to-text redistribui tickets do squad 'phone' caro")
        print(f"      para squads especializados mais baratos")
    elif abs(efeito_volume_puro) > abs(efeito_mix_total):
        print(f"   1. REDUÇÃO DE VOLUME: Menos tickets totais devido ao abandono")
    else:
        print(f"   1. MELHORIA DE EFICIÊNCIA: Menores custos por ticket")

else:
    print("❌ Decomposição com problemas - erro muito alto")
    print("Pode haver efeitos cruzados não capturados na metodologia")

# Preparar dados para cascata final
cascata_componentes = [
    ('Custo Controle', custo_control),
    ('Efeito Volume', efeito_volume_puro),
    ('Efeito Mix', efeito_mix_total),
    ('Efeito Eficiência', efeito_eficiencia_total),
    ('Custo Treatment-B', custo_treatment)
]

print(f"\n=== COMPONENTES PARA CASCATA VISUAL ===")
for nome, valor in cascata_componentes:
    if 'Custo' in nome:
        print(f"{nome}: R$ {valor:,.0f}")
    else:
        sinal = "+" if valor > 0 else ""
        print(f"{nome}: {sinal}R$ {valor:,.0f}")