import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar para português
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (14, 8)

# Carregar dados
print("Carregando dados...")
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')

print(f"Total de linhas: {len(df)}")
print(f"Colunas: {df.columns.tolist()}")
print(f"Variantes únicas: {df['variant'].unique()}")

# Filtrar para control e treatment-b apenas
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

print(f"\nDados filtrados - Control e Treatment-B:")
print(f"Linhas: {len(df_analise)}")

# Calcular custos totais por variante
custos_por_variante = df_analise.groupby('variant')['annual_cost'].sum()
print(f"\nCustos anuais totais:")
print(f"Control: R$ {custos_por_variante['control']:,.2f}")
print(f"Treatment-B: R$ {custos_por_variante['treatment-b']:,.2f}")
print(f"Redução total: R$ {custos_por_variante['control'] - custos_por_variante['treatment-b']:,.2f}")

# Analisar por canal (activity_type)
print(f"\nAnálise por canal:")
analise_canal = df_analise.groupby(['variant', 'activity_type']).agg({
    'annual_cost': 'sum',
    'tickets': 'sum',
    'transfers': 'sum',
    'total_time_spent': 'sum'
}).reset_index()

# Pivot para comparar control vs treatment-b
pivot_canal = analise_canal.pivot(index='activity_type', columns='variant', values='annual_cost').fillna(0)
pivot_canal['diferenca'] = pivot_canal['control'] - pivot_canal['treatment-b']
pivot_canal['percent_mudanca'] = (pivot_canal['diferenca'] / pivot_canal['control']) * 100

print(pivot_canal.round(2))

# Analisar por squad
print(f"\nAnálise por squad:")
analise_squad = df_analise.groupby(['variant', 'actor_squad']).agg({
    'annual_cost': 'sum',
    'tickets': 'sum',
    'transfers': 'sum'
}).reset_index()

pivot_squad = analise_squad.pivot(index='actor_squad', columns='variant', values='annual_cost').fillna(0)
pivot_squad['diferenca'] = pivot_squad['control'] - pivot_squad['treatment-b']
pivot_squad['percent_mudanca'] = (pivot_squad['diferenca'] / pivot_squad['control']) * 100

# Mostrar top 10 squads por impacto
top_squads = pivot_squad.nlargest(10, 'diferenca')
print("Top 10 squads por redução de custo:")
print(top_squads.round(2))

# Analisar mudança no mix de tickets
print(f"\nAnálise do mix de tickets:")
tickets_por_variante = df_analise.groupby('variant')['tickets'].sum()
print(f"Total tickets Control: {tickets_por_variante['control']:,}")
print(f"Total tickets Treatment-B: {tickets_por_variante['treatment-b']:,}")
print(f"Redução de tickets: {tickets_por_variante['control'] - tickets_por_variante['treatment-b']:,}")
print(f"% Redução: {((tickets_por_variante['control'] - tickets_por_variante['treatment-b']) / tickets_por_variante['control']) * 100:.2f}%")

# Calcular mudança do mix phone vs outros canais
mix_control = df_analise[df_analise['variant'] == 'control'].groupby('activity_type')['tickets'].sum()
mix_treatment = df_analise[df_analise['variant'] == 'treatment-b'].groupby('activity_type')['tickets'].sum()

print(f"\nMix por canal:")
print(f"Control:")
print((mix_control / mix_control.sum() * 100).round(2))
print(f"\nTreatment-B:")
print((mix_treatment / mix_treatment.sum() * 100).round(2))

# Analisar phone squad especificamente (impacto do direcionamento)
phone_data = df_analise[df_analise['activity_type'] == 'inbound_call']
if len(phone_data) > 0:
    print(f"\nAnálise específica do canal phone (inbound_call):")
    phone_analysis = phone_data.groupby(['variant', 'actor_squad']).agg({
        'annual_cost': 'sum',
        'tickets': 'sum'
    }).reset_index()
    
    phone_pivot = phone_analysis.pivot(index='actor_squad', columns='variant', values='tickets').fillna(0)
    phone_pivot['diferenca_tickets'] = phone_pivot['control'] - phone_pivot['treatment-b']
    
    print("Mudança de tickets no canal phone por squad:")
    print(phone_pivot.round(0))

# Preparar dados para a cascata
print(f"\nCalculando componentes da cascata...")

# Componente 1: Mudança no volume total (abandono)
total_control = custos_por_variante['control']
total_treatment = custos_por_variante['treatment-b']
reducao_total = total_control - total_treatment

# Vamos simular os componentes baseados nas informações fornecidas
# Unanswered rate: +0.7 p.p. (de 5.88% para 6.58%) = +11.98%
# Return rate: +0.39 p.p. (de 21.09% para 21.49%) = +1.86%

print(f"Redução total de custos: R$ {reducao_total:,.2f}")

# Criar o gráfico de cascata
componentes = {
    'Custo Controle': total_control,
    'Mudança de Mix Phone→Outros Squads': 0,  # A ser calculado
    'Redução Volume (Abandono)': 0,  # A ser calculado
    'Aumento Return Rate': 0,  # A ser calculado
    'Outros Fatores': 0,  # A ser calculado
    'Custo Treatment-B': total_treatment
}

print(f"\nComponentes identificados:")
for comp, valor in componentes.items():
    print(f"{comp}: R$ {valor:,.2f}")
