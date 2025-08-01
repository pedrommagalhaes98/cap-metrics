import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Carregar dados
df_routing = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')

# Filtrar apenas control e treatment-b
df = df_routing[df_routing['variant'].isin(['control', 'treatment-b'])].copy()

print("=== ANÁLISE GRANULAR FINAL COM CUSTOS CORRETOS ===")
print("(Usando os custos do dataset que já incluem todos os fatores)")

# Separar grupos
df_control = df[df['variant'] == 'control'].copy()
df_treatment_b = df[df['variant'] == 'treatment-b'].copy()

# Custos totais
custo_control = df_control['annual_cost'].sum()
custo_treatment_b = df_treatment_b['annual_cost'].sum()
reducao_total = custo_control - custo_treatment_b

print(f"\nCusto Control: R$ {custo_control:,.0f}")
print(f"Custo Treatment-B: R$ {custo_treatment_b:,.0f}")
print(f"Redução Total: R$ {reducao_total:,.0f}")

# 1. COMPONENTE: MIX DENTRO DE PAY PER TICKET (is_ppt == 1)
print(f"\n" + "="*60)
print("=== 1. COMPONENTE: MIX DENTRO DE PAY PER TICKET ===")
print("="*60)

df_ppt_control = df_control[df_control['is_ppt'] == 1].copy()
df_ppt_treatment_b = df_treatment_b[df_treatment_b['is_ppt'] == 1].copy()

custo_ppt_control = df_ppt_control['annual_cost'].sum()
custo_ppt_treatment_b = df_ppt_treatment_b['annual_cost'].sum()
componente_ppt = custo_ppt_control - custo_ppt_treatment_b

print(f"Custo PPT Control: R$ {custo_ppt_control:,.0f}")
print(f"Custo PPT Treatment-B: R$ {custo_ppt_treatment_b:,.0f}")
print(f"Economia PPT: R$ {componente_ppt:,.0f}")

# Detalhar mudanças por squad PPT
print(f"\nMudanças nos squads PPT:")
squads_ppt = set(df_ppt_control['actor_squad'].unique()) | set(df_ppt_treatment_b['actor_squad'].unique())

for squad in sorted(squads_ppt):
    control_squad = df_ppt_control[df_ppt_control['actor_squad'] == squad]
    treatment_squad = df_ppt_treatment_b[df_ppt_treatment_b['actor_squad'] == squad]
    
    tickets_control = control_squad['tickets'].sum()
    tickets_treatment = treatment_squad['tickets'].sum()
    custo_control_squad = control_squad['annual_cost'].sum()
    custo_treatment_squad = treatment_squad['annual_cost'].sum()
    
    delta_tickets = tickets_treatment - tickets_control
    delta_custo = custo_control_squad - custo_treatment_squad
    
    if delta_tickets != 0 or delta_custo != 0:
        print(f"   {squad:20s}: {delta_tickets:>6.0f} tickets → R$ {delta_custo/1e6:>6.1f}M")

# 2. COMPONENTE: MIX DENTRO DE PAY PER TIME (is_ppt == 0)
print(f"\n" + "="*60)
print("=== 2. COMPONENTE: MIX DENTRO DE PAY PER TIME ===")
print("="*60)

df_time_control = df_control[df_control['is_ppt'] == 0].copy()
df_time_treatment_b = df_treatment_b[df_treatment_b['is_ppt'] == 0].copy()

custo_time_control = df_time_control['annual_cost'].sum()
custo_time_treatment_b = df_time_treatment_b['annual_cost'].sum()
componente_time = custo_time_control - custo_time_treatment_b

print(f"Custo Time Control: R$ {custo_time_control:,.0f}")
print(f"Custo Time Treatment-B: R$ {custo_time_treatment_b:,.0f}")
print(f"Diferença Time: R$ {componente_time:,.0f}")

# Análise detalhada de Time por squad
print(f"\nMudanças detalhadas nos squads Pay Per Time:")
print(f"Squad                | Δ Tickets | Δ Tempo Total | Δ Tempo/Ticket | Δ Custo")
print(f"=" * 80)

squads_time = set(df_time_control['actor_squad'].unique()) | set(df_time_treatment_b['actor_squad'].unique())

for squad in sorted(squads_time):
    control_squad = df_time_control[df_time_control['actor_squad'] == squad]
    treatment_squad = df_time_treatment_b[df_time_treatment_b['actor_squad'] == squad]
    
    tickets_control = control_squad['tickets'].sum()
    tickets_treatment = treatment_squad['tickets'].sum()
    time_control = control_squad['total_time_spent'].sum()
    time_treatment = treatment_squad['total_time_spent'].sum()
    custo_control_squad = control_squad['annual_cost'].sum()
    custo_treatment_squad = treatment_squad['annual_cost'].sum()
    
    delta_tickets = tickets_treatment - tickets_control
    delta_time = time_treatment - time_control
    delta_custo = custo_control_squad - custo_treatment_squad
    
    # Tempo médio por ticket
    time_per_ticket_control = time_control / tickets_control if tickets_control > 0 else 0
    time_per_ticket_treatment = time_treatment / tickets_treatment if tickets_treatment > 0 else 0
    delta_time_per_ticket = time_per_ticket_treatment - time_per_ticket_control
    
    if abs(delta_tickets) >= 1 or abs(delta_custo) >= 10000:  # Filtrar mudanças significativas
        print(f"{squad:20s} | {delta_tickets:>9.0f} | {delta_time/3600:>+10.0f}h | {delta_time_per_ticket:>+10.0f}s | R$ {delta_custo/1e6:>6.1f}M")

# 3. COMPONENTE: EFEITO VOLUME (ABANDONO +0.7pp)
print(f"\n" + "="*60)
print("=== 3. COMPONENTE: EFEITO VOLUME (ABANDONO +0.7pp) ===")
print("="*60)

volume_base = df_control['tickets'].sum()
aumento_abandono = 0.007  # 0.7pp
tickets_perdidos_abandono = volume_base * aumento_abandono

# Usar custo médio de chamadas inbound (phone)
df_inbound_control = df_control[df_control['activity_type'] == 'inbound_call']
if len(df_inbound_control) > 0:
    custo_medio_inbound = df_inbound_control['annual_cost'].sum() / df_inbound_control['tickets'].sum()
else:
    # Fallback: usar custo médio geral
    custo_medio_inbound = df_control['annual_cost'].sum() / df_control['tickets'].sum()

componente_abandono = tickets_perdidos_abandono * custo_medio_inbound

print(f"Volume base Control: {volume_base:,.0f} tickets")
print(f"Aumento abandono: +0.7pp")
print(f"Tickets perdidos por abandono: {tickets_perdidos_abandono:,.0f}")
print(f"Custo médio inbound: R$ {custo_medio_inbound:,.2f}/ticket")
print(f"Economia por abandono: R$ {componente_abandono:,.0f}")

# 4. COMPONENTE: EFEITO RETURN RATE (+0.39pp)
print(f"\n" + "="*60)
print("=== 4. COMPONENTE: EFEITO RETURN RATE (+0.39pp) ===")
print("="*60)

aumento_return = 0.0039  # 0.39pp
tickets_adicionais_return = volume_base * aumento_return

# Custo médio geral (todos os canais)
custo_medio_geral = df_control['annual_cost'].sum() / df_control['tickets'].sum()

# Assumir que 50% dos returns geram custo adicional
componente_return_rate = tickets_adicionais_return * custo_medio_geral * 0.5

print(f"Volume base Control: {volume_base:,.0f} tickets")
print(f"Aumento return rate: +0.39pp")
print(f"Tickets adicionais return: {tickets_adicionais_return:,.0f}")
print(f"Custo médio geral: R$ {custo_medio_geral:,.2f}/ticket")
print(f"Custo adicional return (50%): R$ {componente_return_rate:,.0f}")

# VERIFICAÇÃO MATEMÁTICA FINAL
print(f"\n" + "="*60)
print("=== VERIFICAÇÃO MATEMÁTICA FINAL ===")
print("="*60)

componentes = [
    ("Mix PPT", componente_ppt),
    ("Mix Time", componente_time),
    ("Abandono", componente_abandono),
    ("Return Rate", -componente_return_rate),  # Negativo porque é custo adicional
]

total_componentes = sum([comp[1] for comp in componentes])
outros_efeitos = reducao_total - total_componentes

print(f"Custo Control           : R$ {custo_control:>12,.0f}")
for nome, valor in componentes:
    sinal = "+" if valor >= 0 else ""
    print(f"{nome:20s}: {sinal}R$ {valor:>12,.0f}")
print(f"{'Outros Efeitos':20s}: {'+' if outros_efeitos >= 0 else ''}R$ {outros_efeitos:>12,.0f}")
print(f"{'='*35}")
print(f"{'Resultado':20s}: R$ {custo_control - total_componentes - outros_efeitos:>12,.0f}")
print(f"{'Target':20s}: R$ {custo_treatment_b:>12,.0f}")

diferenca_final = abs(custo_treatment_b - (custo_control - total_componentes - outros_efeitos))
print(f"{'Diferença':20s}: R$ {diferenca_final:>12,.0f}")

erro_percentual = abs(outros_efeitos / reducao_total) * 100
print(f"\n💡 Erro residual: {erro_percentual:.1f}%")

if erro_percentual < 5:
    print("✅ EXCELENTE! Decomposição muito precisa!")
elif erro_percentual < 10:
    print("✅ BOM! Decomposição razoavelmente precisa!")
else:
    print("⚠️  Ainda há margem para refinamento")

# CASCATA FINAL
print(f"\n" + "="*60)
print("=== 🎯 CASCATA GRANULAR FINAL 🎯 ===")
print("="*60)

print(f"Custo Control           : R$ {custo_control/1e6:>7.1f}M")
print(f"Mix Pay Per Ticket      : R$ {componente_ppt/1e6:>7.1f}M  ← Squad Phone principalmente")
print(f"Mix Pay Per Time        : R$ {componente_time/1e6:>7.1f}M  ← Outros squads + tempo médio")
print(f"Economia Abandono       : R$ {componente_abandono/1e6:>7.1f}M  ← +0.7pp menos chamadas")
print(f"Custo Return Rate       : R$ {-componente_return_rate/1e6:>7.1f}M  ← +0.39pp mais returns")
print(f"Outros Efeitos          : R$ {outros_efeitos/1e6:>7.1f}M  ← Residual")
print(f"Custo Treatment-B       : R$ {custo_treatment_b/1e6:>7.1f}M")

print(f"\n💡 INSIGHTS PRINCIPAIS:")
print(f"   • PPT (Squad Phone): Principal driver R$ {componente_ppt/1e6:.1f}M")
print(f"   • Time: Efeito contrário R$ {componente_time/1e6:.1f}M")  
print(f"   • Abandono vs Return: Saldo R$ {(componente_abandono - componente_return_rate)/1e6:.1f}M")
print(f"   • Separação PPT vs Time revela dinâmicas opostas!")

# Criar gráfico da cascata
plt.figure(figsize=(12, 8))

# Dados para o gráfico
categorias = ['Custo\nControl', 'Mix PPT', 'Mix Time', 'Abandono', 'Return\nRate', 'Outros\nEfeitos', 'Custo\nTreatment-B']
valores = [custo_control/1e6, componente_ppt/1e6, componente_time/1e6, componente_abandono/1e6, -componente_return_rate/1e6, outros_efeitos/1e6, custo_treatment_b/1e6]
cores = ['blue', 'green', 'red', 'green', 'red', 'gray', 'blue']

# Calcular posições acumuladas
posicoes = [0]
for i in range(1, len(valores)-1):
    posicoes.append(posicoes[-1] + valores[i])
posicoes.append(0)  # Treatment-B volta para zero

# Criar barras
bars = plt.bar(categorias, valores, color=cores, alpha=0.7, edgecolor='black')

# Adicionar valores nas barras
for i, (bar, valor) in enumerate(zip(bars, valores)):
    if i == 0 or i == len(valores)-1:
        # Control e Treatment-B
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                f'R$ {valor:.1f}M', ha='center', va='center', fontweight='bold')
    else:
        # Componentes
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2 if valor >= 0 else bar.get_height()/2,
                f'{valor:+.1f}M', ha='center', va='center', fontweight='bold')

plt.title('Cascata de Custos: Control → Treatment-B\n(Análise Granular PPT vs PPTime)', fontsize=14, fontweight='bold')
plt.ylabel('Custo Anual (R$ Milhões)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# Salvar o gráfico
plt.savefig('cascata_granular_final.png', dpi=300, bbox_inches='tight')
print(f"\n📊 Gráfico salvo como 'cascata_granular_final.png'")

plt.show()