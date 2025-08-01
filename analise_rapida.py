# Análise rápida: % de retornos após chamadas "unanswered" por variant

# Assumindo que você já tem o dataframe callsXpDf carregado
df = callsXpDf.copy()

# Ordenar por customer e call_id
df = df.sort_values(['customer__id', 'call__id'])

# Identificar chamadas de retorno
retornos = df[df['first_contact_in_24_hours'] == False]

# Para cada retorno, encontrar a chamada anterior
results = []
for _, row in retornos.iterrows():
    anteriores = df[(df['customer__id'] == row['customer__id']) & 
                   (df['call__id'] < row['call__id'])]
    
    if len(anteriores) > 0:
        anterior = anteriores.iloc[-1]
        results.append({
            'variant': row.get('variant', 'N/A'),
            'foi_unanswered_anterior': anterior['interpretation'] == 'unanswered'
        })

# Calcular percentuais por variant
import pandas as pd
df_results = pd.DataFrame(results)
analise = df_results.groupby('variant')['foi_unanswered_anterior'].agg(['count', 'sum', 'mean'])
analise.columns = ['total_retornos', 'retornos_pos_unanswered', 'percentual']
analise['percentual'] = analise['percentual'] * 100

print("% de retornos após chamadas 'unanswered' por variant:")
print(analise.round(2)) 