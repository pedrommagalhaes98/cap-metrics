import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle

# Configurar para português
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (16, 10)

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

# Calcular valores base
custos_por_variante = df_analise.groupby('variant')['annual_cost'].sum()
custo_control = custos_por_variante['control']
custo_treatment = custos_por_variante['treatment-b']
reducao_total = custo_control - custo_treatment

print(f"=== ANÁLISE DE CASCATA DE CUSTOS ===")
print(f"Custo Controle: R$ {custo_control:,.2f}")
print(f"Custo Treatment-B: R$ {custo_treatment:,.2f}")
print(f"Redução Total: R$ {reducao_total:,.2f}")

# 1. ANÁLISE DO IMPACTO DO SQUAD PHONE
phone_squad_data = df_analise[df_analise['actor_squad'] == 'phone']
phone_control = phone_squad_data[phone_squad_data['variant'] == 'control']['annual_cost'].sum()
phone_treatment = phone_squad_data[phone_squad_data['variant'] == 'treatment-b']['annual_cost'].sum()
impacto_phone_squad = phone_control - phone_treatment

print(f"\n=== COMPONENTE 1: MUDANÇA NO SQUAD PHONE ===")
print(f"Custo Phone Squad Control: R$ {phone_control:,.2f}")
print(f"Custo Phone Squad Treatment-B: R$ {phone_treatment:,.2f}")
print(f"Economia Squad Phone: R$ {impacto_phone_squad:,.2f}")

# 2. ANÁLISE DO IMPACTO POR CANAL (inbound_call vs outros)
inbound_data = df_analise[df_analise['activity_type'] == 'inbound_call']
inbound_control = inbound_data[inbound_data['variant'] == 'control']['annual_cost'].sum()
inbound_treatment = inbound_data[inbound_data['variant'] == 'treatment-b']['annual_cost'].sum()
impacto_inbound = inbound_control - inbound_treatment

outros_canais_data = df_analise[df_analise['activity_type'] != 'inbound_call']
outros_control = outros_canais_data[outros_canais_data['variant'] == 'control']['annual_cost'].sum()
outros_treatment = outros_canais_data[outros_canais_data['variant'] == 'treatment-b']['annual_cost'].sum()
impacto_outros_canais = outros_control - outros_treatment

print(f"\n=== COMPONENTE 2: MUDANÇA POR CANAL ===")
print(f"Economia Inbound Calls: R$ {impacto_inbound:,.2f}")
print(f"Economia Outros Canais: R$ {impacto_outros_canais:,.2f}")

# 3. ANÁLISE DO IMPACTO DO VOLUME TOTAL
tickets_control = df_analise[df_analise['variant'] == 'control']['tickets'].sum()
tickets_treatment = df_analise[df_analise['variant'] == 'treatment-b']['tickets'].sum()
reducao_tickets = tickets_control - tickets_treatment
percent_reducao_volume = (reducao_tickets / tickets_control) * 100

print(f"\n=== COMPONENTE 3: REDUÇÃO DE VOLUME ===")
print(f"Tickets Control: {tickets_control:,}")
print(f"Tickets Treatment-B: {tickets_treatment:,}")
print(f"Redução de tickets: {reducao_tickets:,} ({percent_reducao_volume:.2f}%)")

# Estimar impacto do volume baseado no custo médio por ticket
custo_medio_por_ticket_control = custo_control / tickets_control
impacto_volume_estimado = reducao_tickets * custo_medio_por_ticket_control

print(f"Custo médio por ticket (Control): R$ {custo_medio_por_ticket_control:.2f}")
print(f"Economia estimada por redução de volume: R$ {impacto_volume_estimado:,.2f}")

# 4. ANÁLISE DE PAY PER TICKET vs PAY PER TIME
ppt_data = df_analise[df_analise['is_ppt'] == 1]
ppt_control = ppt_data[ppt_data['variant'] == 'control']['annual_cost'].sum()
ppt_treatment = ppt_data[ppt_data['variant'] == 'treatment-b']['annual_cost'].sum()
impacto_ppt = ppt_control - ppt_treatment

time_data = df_analise[df_analise['is_ppt'] == 0]
time_control = time_data[time_data['variant'] == 'control']['annual_cost'].sum()
time_treatment = time_data[time_data['variant'] == 'treatment-b']['annual_cost'].sum()
impacto_time = time_control - time_treatment

print(f"\n=== COMPONENTE 4: MODALIDADE DE PAGAMENTO ===")
print(f"Economia Pay Per Ticket: R$ {impacto_ppt:,.2f}")
print(f"Economia Pay Per Time: R$ {impacto_time:,.2f}")

# 5. SIMULAÇÃO DOS EFEITOS DE ABANDONO E RETURN RATE
# Baseado nas informações fornecidas:
# - Unanswered rate: +0.7 p.p. (11.98% de aumento)
# - Return rate: +0.39 p.p. (1.86% de aumento)

# O aumento do abandono reduz custos diretos mas pode aumentar return rate
volume_base_estimado = tickets_control
aumento_abandono_percent = 0.7 / 100  # 0.7 p.p.
reducao_por_abandono = volume_base_estimado * aumento_abandono_percent
economia_abandono = reducao_por_abandono * custo_medio_por_ticket_control

aumento_return_rate = 0.39 / 100  # 0.39 p.p.
# Return rate gera custos adicionais em outros canais
custo_adicional_return = volume_base_estimado * aumento_return_rate * (custo_medio_por_ticket_control * 0.5)  # Assumindo 50% do custo original

print(f"\n=== COMPONENTE 5: EFEITOS DE ABANDONO E RETURN RATE ===")
print(f"Economia por aumento do abandono: R$ {economia_abandono:,.2f}")
print(f"Custo adicional por return rate: R$ {custo_adicional_return:,.2f}")
print(f"Impacto líquido: R$ {economia_abandono - custo_adicional_return:,.2f}")

# CONSTRUÇÃO DA CASCATA
componentes = [
    ('Custo Controle', custo_control, custo_control),
    ('Redirecionamento Squad Phone', -impacto_phone_squad, custo_control - impacto_phone_squad),
    ('Mudança Mix Canais', -(impacto_inbound - impacto_phone_squad), 0),  # Ajustar para não double count
    ('Redução Volume (Abandono)', -economia_abandono, 0),
    ('Aumento Return Rate', custo_adicional_return, 0),
    ('Outros Fatores', 0, 0),  # Residual
    ('Custo Treatment-B', 0, custo_treatment)
]

# Ajustar o "Outros Fatores" como residual
outros_fatores = custo_treatment - (custo_control - impacto_phone_squad - economia_abandono + custo_adicional_return)
componentes[5] = ('Outros Fatores', outros_fatores, custo_treatment - outros_fatores)

print(f"\n=== CASCATA DE CUSTOS ===")
valor_acumulado = custo_control
for i, (nome, impacto, _) in enumerate(componentes):
    if i == 0:
        print(f"{nome}: R$ {impacto:,.2f}")
    elif i == len(componentes) - 1:
        print(f"{nome}: R$ {impacto:,.2f}")
    else:
        valor_acumulado += impacto
        print(f"{nome}: R$ {impacto:,.2f} (Acumulado: R$ {valor_acumulado:,.2f})")

# CRIAR GRÁFICO DE CASCATA
fig, ax = plt.subplots(figsize=(16, 10))

# Posições x para as barras
x_positions = range(len(componentes))
labels = [comp[0] for comp in componentes]
values = [comp[1] for comp in componentes]

# Calcular posições y para a cascata
y_bottom = 0
y_tops = []
colors = []

for i, value in enumerate(values):
    if i == 0:  # Custo Controle
        y_tops.append(value)
        colors.append('steelblue')
        y_bottom = value
    elif i == len(values) - 1:  # Custo Treatment-B
        y_tops.append(value)
        colors.append('steelblue')
    else:
        if value < 0:  # Redução (verde)
            colors.append('green')
            y_tops.append(abs(value))
            y_bottom += value
        else:  # Aumento (vermelho)
            colors.append('red')
            y_tops.append(value)
            y_bottom += value

# Desenhar as barras
bars = []
y_current = custo_control

for i, (label, value) in enumerate(zip(labels, values)):
    if i == 0:  # Primeira barra (Custo Controle)
        bar = ax.bar(i, value, color='steelblue', alpha=0.7, width=0.6)
        bars.append(bar)
        
        # Adicionar valor no topo
        ax.text(i, value + 2000000, f'R$ {value/1000000:.1f}M', 
                ha='center', va='bottom', fontweight='bold', fontsize=11)
                
    elif i == len(values) - 1:  # Última barra (Custo Treatment-B)
        bar = ax.bar(i, value, color='steelblue', alpha=0.7, width=0.6)
        bars.append(bar)
        
        # Adicionar valor no topo
        ax.text(i, value + 2000000, f'R$ {value/1000000:.1f}M', 
                ha='center', va='bottom', fontweight='bold', fontsize=11)
                
    else:  # Barras intermediárias
        if value < 0:  # Redução
            bar = ax.bar(i, abs(value), bottom=y_current + value, 
                        color='green', alpha=0.7, width=0.6)
            # Linha conectora
            ax.plot([i-0.3, i-0.3], [y_current, y_current + value], 'k--', alpha=0.5)
            ax.plot([i+0.3, i+0.3], [y_current, y_current + value], 'k--', alpha=0.5)
            
            # Adicionar valor
            ax.text(i, y_current + value/2, f'R$ {value/1000000:.1f}M', 
                    ha='center', va='center', fontweight='bold', fontsize=10, color='white')
            y_current += value
            
        else:  # Aumento
            bar = ax.bar(i, value, bottom=y_current, 
                        color='red', alpha=0.7, width=0.6)
            # Linha conectora
            ax.plot([i-0.3, i-0.3], [y_current, y_current + value], 'k--', alpha=0.5)
            ax.plot([i+0.3, i+0.3], [y_current, y_current + value], 'k--', alpha=0.5)
            
            # Adicionar valor
            ax.text(i, y_current + value/2, f'+R$ {value/1000000:.1f}M', 
                    ha='center', va='center', fontweight='bold', fontsize=10, color='white')
            y_current += value
        
        bars.append(bar)

# Configurações do gráfico
ax.set_xticks(x_positions)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_ylabel('Custo Anual (R$ Milhões)', fontsize=12, fontweight='bold')
ax.set_title('Cascata de Custos: Controle vs Treatment-B\n(Impacto do Speech-to-Text no Roteamento)', 
             fontsize=14, fontweight='bold', pad=20)

# Formatação do eixo Y
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000000:.0f}M'))

# Grid
ax.grid(True, alpha=0.3, axis='y')

# Legenda
green_patch = mpatches.Patch(color='green', alpha=0.7, label='Redução de Custos')
red_patch = mpatches.Patch(color='red', alpha=0.7, label='Aumento de Custos')
blue_patch = mpatches.Patch(color='steelblue', alpha=0.7, label='Custo Total')
ax.legend(handles=[green_patch, red_patch, blue_patch], loc='upper right')

# Adicionar valor de economia total
economia_total = custo_control - custo_treatment
ax.text(0.5, 0.95, f'Economia Total: R$ {economia_total/1000000:.1f}M ({(economia_total/custo_control)*100:.1f}%)', 
        transform=ax.transAxes, ha='center', va='top', 
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
        fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('cascata_custos_speech_to_text.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"\n=== RESUMO EXECUTIVO ===")
print(f"O experimento Speech-to-Text resultou em uma economia de R$ {reducao_total/1000000:.1f}M ({(reducao_total/custo_control)*100:.1f}%)")
print(f"Principal driver: Redirecionamento do squad 'phone' genérico para squads especializados")
print(f"Economia do squad phone: R$ {impacto_phone_squad/1000000:.1f}M")
print(f"Efeito do abandono: +R$ {economia_abandono/1000000:.1f}M de economia")
print(f"Efeito do return rate: -R$ {custo_adicional_return/1000000:.1f}M de custo adicional")