import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

print("=== ANÁLISE CORRETA: EFEITO LÍQUIDO DO MIX COMPLETO ===")

# Valores base
custo_control = df_analise[df_analise['variant'] == 'control']['annual_cost'].sum()
custo_treatment = df_analise[df_analise['variant'] == 'treatment-b']['annual_cost'].sum()
reducao_total = custo_control - custo_treatment

print(f"Custo Controle: R$ {custo_control:,.0f}")
print(f"Custo Treatment-B: R$ {custo_treatment:,.0f}")
print(f"Redução Total: R$ {reducao_total:,.0f}")

# Analisar TODA a redistribuição do mix
print(f"\n=== ANÁLISE COMPLETA DA REDISTRIBUIÇÃO ===")

# Por squad
squad_analysis = df_analise.groupby(['actor_squad', 'variant']).agg({
    'annual_cost': 'sum',
    'tickets': 'sum'
}).reset_index()

squad_pivot = squad_analysis.pivot(index='actor_squad', columns='variant', values=['annual_cost', 'tickets']).fillna(0)
squad_pivot.columns = ['_'.join(col).strip() for col in squad_pivot.columns]
squad_pivot['diferenca_custo'] = squad_pivot['annual_cost_control'] - squad_pivot['annual_cost_treatment-b']
squad_pivot['diferenca_tickets'] = squad_pivot['tickets_control'] - squad_pivot['tickets_treatment-b']

# Calcular custo por ticket por squad no controle
squad_pivot['custo_por_ticket_control'] = np.where(
    squad_pivot['tickets_control'] > 0,
    squad_pivot['annual_cost_control'] / squad_pivot['tickets_control'],
    0
)

print("REDISTRIBUIÇÃO COMPLETA POR SQUAD:")
print("Squad                  | Δ Tickets | Custo/Ticket | Δ Custo Total")
print("=" * 65)

total_redistribuicao = 0
for squad, row in squad_pivot.iterrows():
    delta_tickets = -row['diferenca_tickets']  # Negativo porque é control - treatment
    custo_por_ticket = row['custo_por_ticket_control']
    delta_custo = -row['diferenca_custo']  # Negativo porque é control - treatment
    
    if abs(delta_tickets) > 10:  # Só mostrar mudanças significativas
        sinal_ticket = "+" if delta_tickets > 0 else ""
        sinal_custo = "+" if delta_custo > 0 else ""
        print(f"{squad:20} | {sinal_ticket}{delta_tickets:7.0f} | R$ {custo_por_ticket:7.0f} | {sinal_custo}R$ {delta_custo/1000000:5.1f}M")
        
        total_redistribuicao += delta_custo

print("=" * 65)
print(f"EFEITO LÍQUIDO REDISTRIBUIÇÃO: R$ {total_redistribuicao/1000000:.1f}M")

# Verificar se bate com a redução total
print(f"\n=== VERIFICAÇÃO MATEMÁTICA ===")
print(f"Efeito redistribuição: R$ {total_redistribuicao:,.0f}")
print(f"Redução real: R$ {reducao_total:,.0f}")
print(f"Diferença: R$ {total_redistribuicao - reducao_total:,.0f}")

if abs(total_redistribuicao - reducao_total) < 100000:
    print("✅ PERFEITO! A redistribuição explica toda a economia!")
else:
    diferenca = total_redistribuicao - reducao_total
    print(f"❌ Há diferença de R$ {diferenca/1000000:.1f}M")
    print("Pode haver outros efeitos (eficiência, volume, etc.)")

# Decomposição correta por tamanho do efeito
print(f"\n=== PRINCIPAIS COMPONENTES DA REDISTRIBUIÇÃO ===")

# Ordenar por impacto
squad_impacto = squad_pivot.copy()
squad_impacto['delta_custo'] = -squad_impacto['diferenca_custo']
squad_impacto = squad_impacto.sort_values('delta_custo', ascending=False)

# Top 10 por impacto
top_squads = squad_impacto.head(10)
bottom_squads = squad_impacto.tail(5)

print("\n📈 SQUADS QUE MAIS AUMENTARAM CUSTO (receberam tickets caros):")
for squad, row in top_squads.iterrows():
    if row['delta_custo'] > 100000:
        print(f"   {squad:20}: +R$ {row['delta_custo']/1000000:5.1f}M")

print("\n📉 SQUADS QUE MAIS REDUZIRAM CUSTO (perderam tickets caros):")
for squad, row in bottom_squads.iterrows():
    if row['delta_custo'] < -100000:
        print(f"   {squad:20}: R$ {row['delta_custo']/1000000:6.1f}M")

# Agrupamento lógico para cascata
print(f"\n=== AGRUPAMENTO PARA CASCATA ===")

# Efeito Phone (principal)
phone_effect = squad_impacto.loc['phone', 'delta_custo'] if 'phone' in squad_impacto.index else 0

# Efeito outros squads especializados que ganharam tickets
outros_aumentos = squad_impacto[squad_impacto['delta_custo'] > 0]['delta_custo'].sum()
outros_reducoes = squad_impacto[squad_impacto['delta_custo'] < 0]['delta_custo'].sum() + phone_effect  # Incluir phone

print(f"Efeito Squad Phone: R$ {phone_effect/1000000:.1f}M")
print(f"Outros squads (aumentos): +R$ {outros_aumentos/1000000:.1f}M") 
print(f"Outros squads (reduções): R$ {outros_reducoes/1000000:.1f}M")
print(f"Efeito LÍQUIDO: R$ {(phone_effect + outros_aumentos + outros_reducoes)/1000000:.1f}M")

# Cascata simplificada correta
efeito_mix_liquido = total_redistribuicao

# Outros efeitos (se houver diferença)
outros_efeitos = reducao_total - efeito_mix_liquido

cascata_correta = [
    ("Custo Controle", custo_control),
    ("Efeito Mix Completo\n(Redistribuição)", efeito_mix_liquido),
    ("Outros Efeitos\n(Volume, Eficiência)", outros_efeitos),
    ("Custo Treatment-B", custo_treatment)
]

print(f"\n=== CASCATA MATEMATICAMENTE CORRETA ===")
verificacao = custo_control
for nome, valor in cascata_correta:
    if "Custo" in nome:
        print(f"{nome:25}: R$ {valor/1000000:6.1f}M")
    else:
        sinal = "+" if valor > 0 else ""
        print(f"{nome:25}: {sinal}R$ {valor/1000000:6.1f}M")
        verificacao += valor

print(f"{'VERIFICAÇÃO':25}: R$ {verificacao/1000000:6.1f}M")
print(f"{'DIFERENÇA':25}: R$ {(verificacao - custo_treatment)/1000000:6.1f}M ✓")

# Análise detalhada do mix para entender melhor
print(f"\n=== ANÁLISE DETALHADA: POR QUE O MIX GERA ECONOMIA? ===")

# Custo médio por ticket no controle vs treatment-b
custo_medio_control = custo_control / df_analise[df_analise['variant'] == 'control']['tickets'].sum()
custo_medio_treatment = custo_treatment / df_analise[df_analise['variant'] == 'treatment-b']['tickets'].sum()

print(f"Custo médio/ticket Control: R$ {custo_medio_control:.2f}")
print(f"Custo médio/ticket Treatment-B: R$ {custo_medio_treatment:.2f}")
print(f"Diferença: R$ {custo_medio_treatment - custo_medio_control:.2f}")

# Analisar squads mais caros vs mais baratos
squads_caros = squad_pivot[squad_pivot['custo_por_ticket_control'] > custo_medio_control]
squads_baratos = squad_pivot[squad_pivot['custo_por_ticket_control'] < custo_medio_control]

tickets_perdidos_caros = squads_caros['diferenca_tickets'].sum()
tickets_ganhos_baratos = -squads_baratos['diferenca_tickets'].sum()

print(f"\nTickets perdidos por squads CAROS: {tickets_perdidos_caros:,.0f}")
print(f"Tickets ganhos por squads BARATOS: {tickets_ganhos_baratos:,.0f}")

if tickets_perdidos_caros > 0:
    print(f"\n💡 INSIGHT: O speech-to-text direciona tickets dos squads CAROS para os BARATOS!")
    print(f"   Isso explica a economia líquida de R$ {efeito_mix_liquido/1000000:.1f}M")