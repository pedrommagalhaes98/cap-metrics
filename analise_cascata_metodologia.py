import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv('/Users/pedro.magalhaes/Downloads/Phone_Routing_Mix.csv')
df_analise = df[df['variant'].isin(['control', 'treatment-b'])].copy()

print("=== ANÁLISE METODOLÓGICA DA CASCATA ===")

# Valores base
custo_control = df_analise[df_analise['variant'] == 'control']['annual_cost'].sum()
custo_treatment = df_analise[df_analise['variant'] == 'treatment-b']['annual_cost'].sum()
reducao_total = custo_control - custo_treatment

print(f"Custo Controle: R$ {custo_control:,.0f}")
print(f"Custo Treatment-B: R$ {custo_treatment:,.0f}")
print(f"Redução Total: R$ {reducao_total:,.0f}")

print(f"\n=== PROBLEMA 1: DUPLA CONTAGEM ===")
print("A mudança no squad 'phone' já inclui:")
print("- Efeito volume (menos tickets)")
print("- Efeito mix (mudança de squad)")  
print("- Efeito modalidade pagamento")
print("Não posso tratá-los separadamente!")

print(f"\n=== ANÁLISE CORRETA: EFEITOS INDEPENDENTES ===")

# 1. EFEITO VOLUME TOTAL (primeiro na cascata)
tickets_control = df_analise[df_analise['variant'] == 'control']['tickets'].sum()
tickets_treatment = df_analise[df_analise['variant'] == 'treatment-b']['tickets'].sum()
mudanca_volume_tickets = tickets_treatment - tickets_control
custo_medio_ticket = custo_control / tickets_control

efeito_volume = mudanca_volume_tickets * custo_medio_ticket

print(f"\n1. EFEITO VOLUME TOTAL:")
print(f"   Tickets Control: {tickets_control:,}")
print(f"   Tickets Treatment-B: {tickets_treatment:,}")
print(f"   Mudança Volume: {mudanca_volume_tickets:,} tickets")
print(f"   Custo médio/ticket: R$ {custo_medio_ticket:.2f}")
print(f"   Efeito Volume: R$ {efeito_volume:,.0f}")

# 2. EFEITO MIX DE SQUADS (assumindo volume constante)
print(f"\n2. EFEITO MIX DE SQUADS:")
print("   Análise squad por squad (mantendo volume Control constante):")

# Calcular custo por squad por ticket
analysis_by_squad = []
for squad in df_analise['actor_squad'].unique():
    squad_data = df_analise[df_analise['actor_squad'] == squad]
    
    if len(squad_data[squad_data['variant'] == 'control']) > 0 and len(squad_data[squad_data['variant'] == 'treatment-b']) > 0:
        # Control
        control_data = squad_data[squad_data['variant'] == 'control']
        control_tickets = control_data['tickets'].sum()
        control_cost = control_data['annual_cost'].sum()
        control_cost_per_ticket = control_cost / control_tickets if control_tickets > 0 else 0
        
        # Treatment
        treatment_data = squad_data[squad_data['variant'] == 'treatment-b']
        treatment_tickets = treatment_data['tickets'].sum()
        treatment_cost = treatment_data['annual_cost'].sum()
        treatment_cost_per_ticket = treatment_cost / treatment_tickets if treatment_tickets > 0 else 0
        
        # Mudança de mix: diferença de tickets
        mudanca_tickets = treatment_tickets - control_tickets
        
        # Efeito mix: se mudança de tickets for para squad mais caro/barato
        # Usar custo per ticket do control como baseline
        if control_tickets > 0:
            efeito_mix_squad = mudanca_tickets * control_cost_per_ticket
            analysis_by_squad.append({
                'squad': squad,
                'control_tickets': control_tickets,
                'treatment_tickets': treatment_tickets,
                'mudanca_tickets': mudanca_tickets,
                'control_cost_per_ticket': control_cost_per_ticket,
                'efeito_mix': efeito_mix_squad,
                'control_cost': control_cost,
                'treatment_cost': treatment_cost,
                'mudanca_custo_total': treatment_cost - control_cost
            })

# Criar DataFrame para análise
df_squad_analysis = pd.DataFrame(analysis_by_squad)
df_squad_analysis = df_squad_analysis.sort_values('mudanca_custo_total')

print("\nTop 10 squads por mudança de custo:")
print(df_squad_analysis[['squad', 'mudanca_tickets', 'control_cost_per_ticket', 'mudanca_custo_total']].head(10).to_string(index=False))

# Efeito MIX total
efeito_mix_total = df_squad_analysis['efeito_mix'].sum()
print(f"\nEfeito MIX total (mudança distribuição): R$ {efeito_mix_total:,.0f}")

# 3. EFEITO EFICIÊNCIA (custo por ticket dentro de cada squad)
print(f"\n3. EFEITO EFICIÊNCIA:")
print("   Mudança no custo por ticket dentro de cada squad:")

efeito_eficiencia_total = 0
for _, row in df_squad_analysis.iterrows():
    squad = row['squad']
    control_tickets = row['control_tickets']
    treatment_tickets = row['treatment_tickets']
    control_cost_per_ticket = row['control_cost_per_ticket']
    
    # Calcular custo per ticket no treatment
    if treatment_tickets > 0:
        treatment_cost_per_ticket = row['treatment_cost'] / treatment_tickets
        mudanca_cost_per_ticket = treatment_cost_per_ticket - control_cost_per_ticket
        
        # Efeito eficiência: mudança no custo/ticket * tickets do treatment
        efeito_eficiencia_squad = mudanca_cost_per_ticket * treatment_tickets
        efeito_eficiencia_total += efeito_eficiencia_squad
        
        if abs(efeito_eficiencia_squad) > 100000:  # Só mostrar mudanças significativas
            print(f"   {squad}: R$ {mudanca_cost_per_ticket:.2f}/ticket * {treatment_tickets:,} tickets = R$ {efeito_eficiencia_squad:,.0f}")

print(f"\nEfeito EFICIÊNCIA total: R$ {efeito_eficiencia_total:,.0f}")

# 4. VERIFICAÇÃO
print(f"\n=== VERIFICAÇÃO ===")
total_efeitos = efeito_volume + efeito_mix_total + efeito_eficiencia_total
print(f"Efeito Volume: R$ {efeito_volume:,.0f}")
print(f"Efeito Mix: R$ {efeito_mix_total:,.0f}")
print(f"Efeito Eficiência: R$ {efeito_eficiencia_total:,.0f}")
print(f"Total Calculado: R$ {total_efeitos:,.0f}")
print(f"Redução Real: R$ {reducao_total:,.0f}")
print(f"Diferença: R$ {total_efeitos - reducao_total:,.0f}")

# 5. ORDENAÇÃO LÓGICA DA CASCATA
print(f"\n=== ORDENAÇÃO LÓGICA CORRETA ===")
print("1. EFEITO VOLUME: Mudança no número total de tickets")
print("   - Abandono (+0.7pp) reduz volume total")
print("   - Return rate (+0.39pp) pode gerar volume adicional")
print()
print("2. EFEITO MIX: Redistribuição entre squads (volume constante)")
print("   - Speech-to-text direciona melhor → squads especializados")
print("   - Squad 'phone' perde tickets → outros ganham")
print()
print("3. EFEITO EFICIÊNCIA: Mudança custo/ticket dentro de cada squad")
print("   - Melhor direcionamento → menor tempo médio")
print("   - Mudança PPT vs PPTime → diferentes custos")

# Análise específica do squad phone
print(f"\n=== ANÁLISE ESPECÍFICA: SQUAD PHONE ===")
phone_data = df_squad_analysis[df_squad_analysis['squad'] == 'phone']
if len(phone_data) > 0:
    phone_row = phone_data.iloc[0]
    print(f"Squad Phone perdeu {abs(phone_row['mudanca_tickets']):,} tickets")
    print(f"Economia total squad phone: R$ {abs(phone_row['mudanca_custo_total']):,.0f}")
    print(f"Isso representa:")
    print(f"- Efeito MIX: R$ {phone_row['efeito_mix']:,.0f} (tickets que saíram)")
    print(f"- Efeito EFICIÊNCIA: R$ {phone_row['mudanca_custo_total'] - phone_row['efeito_mix']:,.0f} (melhoria custo/ticket)")