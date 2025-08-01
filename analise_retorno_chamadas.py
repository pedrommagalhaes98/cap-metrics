import pandas as pd
import numpy as np

def analisar_retorno_vs_unanswered(callsXpDf):
    """
    Analisa o percentual de chamadas de retorno que tiveram a chamada anterior como "unanswered",
    agrupado por variant.
    
    Args:
        callsXpDf (DataFrame): DataFrame com as chamadas
        
    Returns:
        DataFrame: Análise por variant
    """
    
    # Assumindo que temos uma coluna de timestamp para ordenar as chamadas
    # Se não tiver, vamos assumir que call__id está em ordem cronológica
    df = callsXpDf.copy()
    
    # Ordenar por customer__id e call__id (assumindo ordem cronológica)
    df = df.sort_values(['customer__id', 'call__id'])
    
    # Identificar chamadas de retorno (não são o primeiro contato em 24h)
    chamadas_retorno = df[df['first_contact_in_24_hours'] == False].copy()
    
    print(f"Total de chamadas no dataset: {len(df)}")
    print(f"Total de chamadas de retorno: {len(chamadas_retorno)}")
    
    if len(chamadas_retorno) == 0:
        print("Não há chamadas de retorno no dataset")
        return pd.DataFrame()
    
    # Para cada chamada de retorno, encontrar a chamada anterior do mesmo cliente
    results = []
    
    for idx, row in chamadas_retorno.iterrows():
        customer_id = row['customer__id']
        call_id = row['call__id']
        variant = row.get('variant', 'N/A')  # Assumindo que há uma coluna variant
        
        # Encontrar todas as chamadas anteriores do mesmo cliente
        chamadas_anteriores = df[
            (df['customer__id'] == customer_id) & 
            (df['call__id'] < call_id)
        ].sort_values('call__id')
        
        if len(chamadas_anteriores) > 0:
            # Pegar a chamada imediatamente anterior
            chamada_anterior = chamadas_anteriores.iloc[-1]
            
            results.append({
                'call__id_retorno': call_id,
                'customer__id': customer_id,
                'variant': variant,
                'call__id_anterior': chamada_anterior['call__id'],
                'interpretation_anterior': chamada_anterior['interpretation'],
                'foi_unanswered_anterior': chamada_anterior['interpretation'] == 'unanswered'
            })
    
    if not results:
        print("Não foi possível encontrar chamadas anteriores para as chamadas de retorno")
        return pd.DataFrame()
    
    # Converter para DataFrame
    df_analise = pd.DataFrame(results)
    
    print(f"\nChamadas de retorno com chamada anterior identificada: {len(df_analise)}")
    
    # Calcular estatísticas por variant
    stats_por_variant = df_analise.groupby('variant').agg({
        'foi_unanswered_anterior': ['count', 'sum', 'mean']
    }).round(4)
    
    # Flatten column names
    stats_por_variant.columns = ['total_retornos', 'retornos_pos_unanswered', 'perc_retornos_pos_unanswered']
    stats_por_variant['perc_retornos_pos_unanswered'] = stats_por_variant['perc_retornos_pos_unanswered'] * 100
    
    # Estatísticas gerais
    total_retornos = len(df_analise)
    retornos_pos_unanswered = df_analise['foi_unanswered_anterior'].sum()
    perc_geral = (retornos_pos_unanswered / total_retornos * 100) if total_retornos > 0 else 0
    
    print(f"\n=== RESULTADOS GERAIS ===")
    print(f"Total de retornos analisados: {total_retornos}")
    print(f"Retornos após chamada 'unanswered': {retornos_pos_unanswered}")
    print(f"Percentual geral: {perc_geral:.2f}%")
    
    print(f"\n=== RESULTADOS POR VARIANT ===")
    print(stats_por_variant)
    
    # Análise adicional dos tipos de interpretation na chamada anterior
    print(f"\n=== DISTRIBUIÇÃO DOS STATUS ANTERIORES ===")
    distribuicao_status = df_analise['interpretation_anterior'].value_counts()
    distribuicao_perc = (distribuicao_status / len(df_analise) * 100).round(2)
    
    for status, count in distribuicao_status.items():
        perc = distribuicao_perc[status]
        print(f"{status}: {count} ({perc}%)")
    
    return stats_por_variant, df_analise

# Exemplo de uso:
# Assumindo que você já tem o dataframe callsXpDf carregado
# resultado, detalhes = analisar_retorno_vs_unanswered(callsXpDf)

# Se quiser salvar os resultados:
# resultado.to_csv('analise_retorno_por_variant.csv')
# detalhes.to_csv('detalhes_chamadas_retorno.csv', index=False) 