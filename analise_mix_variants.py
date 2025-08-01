import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import normaltest

def carregar_dados(caminho_arquivo):
    """
    Carrega e prepara os dados para análise
    """
    df = pd.read_csv(caminho_arquivo)
    
    # Remover linhas com valores nulos na coluna actor_queue
    df = df.dropna(subset=['actor_queue'])
    
    # Remover filas com volume muito baixo (< 50 chamadas total)
    df['total_chamadas'] = df[['control', 'treatment-a', 'treatment-b', 'treatment-c']].sum(axis=1)
    df_filtrado = df[df['total_chamadas'] >= 50].copy()
    
    print(f"Total de filas no dataset: {len(df)}")
    print(f"Filas após filtrar volume baixo (≥50 chamadas): {len(df_filtrado)}")
    print(f"Total de chamadas no dataset: {df['total_chamadas'].sum():,}")
    
    return df_filtrado

def teste_chi_quadrado_mix(df):
    """
    Testa se há diferença significativa no mix de chamadas entre variants
    """
    print("\n" + "="*60)
    print("TESTE CHI-QUADRADO - MIX DE VARIANTS POR FILA")
    print("="*60)
    
    # Criar matriz de dados para o teste (filas x variants)
    dados_matriz = df[['control', 'treatment-a', 'treatment-b', 'treatment-c']].values
    
    # Aplicar teste chi-quadrado
    chi2, p_valor, dof, expected = chi2_contingency(dados_matriz)
    
    print(f"Chi-quadrado: {chi2:.4f}")
    print(f"P-valor: {p_valor:.6f}")
    print(f"Graus de liberdade: {dof}")
    
    # Interpretação
    alpha = 0.05
    if p_valor < alpha:
        print(f"✅ RESULTADO: Diferença SIGNIFICATIVA (p < {alpha})")
        print("   → O mix de variants NÃO está distribuído uniformemente entre as filas")
        print("   → Há evidência de que os treatments afetam diferentemente cada fila")
    else:
        print(f"❌ RESULTADO: Diferença NÃO significativa (p ≥ {alpha})")
        print("   → O mix de variants está relativamente uniforme entre as filas")
    
    # Calcular desvios padronizados (residuais)
    residuais_padronizados = (dados_matriz - expected) / np.sqrt(expected)
    
    print(f"\n--- FILAS COM MAIORES DESVIOS ---")
    filas_com_desvios = []
    for i, fila in enumerate(df['actor_queue']):
        desvio_maximo = np.max(np.abs(residuais_padronizados[i]))
        if desvio_maximo > 2:  # Desvio considerável
            filas_com_desvios.append((fila, desvio_maximo))
    
    filas_com_desvios.sort(key=lambda x: x[1], reverse=True)
    for fila, desvio in filas_com_desvios[:5]:
        print(f"  {fila}: desvio máximo = {desvio:.2f}")
    
    return chi2, p_valor, residuais_padronizados

def analisar_volume_total_variants(df):
    """
    Compara o volume total entre variants usando ANOVA/Kruskal-Wallis
    """
    print("\n" + "="*60)
    print("ANÁLISE DE VOLUME TOTAL POR VARIANT")
    print("="*60)
    
    # Calcular totais por variant
    totais = {
        'control': df['control'].sum(),
        'treatment-a': df['treatment-a'].sum(),
        'treatment-b': df['treatment-b'].sum(),
        'treatment-c': df['treatment-c'].sum()
    }
    
    print("Volume total por variant:")
    for variant, total in totais.items():
        print(f"  {variant}: {total:,} chamadas")
    
    # Para análise estatística, vamos tratar cada fila como uma observação
    control = df['control'].values
    treatment_a = df['treatment-a'].values
    treatment_b = df['treatment-b'].values
    treatment_c = df['treatment-c'].values
    
    # Teste de normalidade
    _, p_normal_control = normaltest(control)
    _, p_normal_ta = normaltest(treatment_a)
    _, p_normal_tb = normaltest(treatment_b)
    _, p_normal_tc = normaltest(treatment_c)
    
    dados_normais = all(p > 0.05 for p in [p_normal_control, p_normal_ta, p_normal_tb, p_normal_tc])
    
    if dados_normais:
        print(f"\n--- ANOVA (dados com distribuição normal) ---")
        f_stat, p_valor_anova = f_oneway(control, treatment_a, treatment_b, treatment_c)
        print(f"F-statistic: {f_stat:.4f}")
        print(f"P-valor: {p_valor_anova:.6f}")
        teste_usado = "ANOVA"
        p_valor_final = p_valor_anova
    else:
        print(f"\n--- KRUSKAL-WALLIS (dados não normais) ---")
        h_stat, p_valor_kw = kruskal(control, treatment_a, treatment_b, treatment_c)
        print(f"H-statistic: {h_stat:.4f}")
        print(f"P-valor: {p_valor_kw:.6f}")
        teste_usado = "Kruskal-Wallis"
        p_valor_final = p_valor_kw
    
    # Interpretação
    alpha = 0.05
    if p_valor_final < alpha:
        print(f"✅ RESULTADO ({teste_usado}): Diferença SIGNIFICATIVA (p < {alpha})")
        print("   → Há diferença significativa no volume entre pelo menos dois variants")
    else:
        print(f"❌ RESULTADO ({teste_usado}): Diferença NÃO significativa (p ≥ {alpha})")
        print("   → Não há evidência de diferença significativa no volume entre variants")
    
    return totais, p_valor_final

def analisar_proporcoes_por_fila(df, top_n=5):
    """
    Analisa as filas com maior mudança proporcional entre control e treatments
    """
    print("\n" + "="*60)
    print("ANÁLISE DE PROPORÇÕES - FILAS COM MAIORES MUDANÇAS")
    print("="*60)
    
    # Calcular proporções para cada fila
    df_prop = df.copy()
    total_por_fila = df_prop[['control', 'treatment-a', 'treatment-b', 'treatment-c']].sum(axis=1)
    
    for col in ['control', 'treatment-a', 'treatment-b', 'treatment-c']:
        df_prop[f'{col}_prop'] = df_prop[col] / total_por_fila * 100
    
    # Calcular desvio em relação ao esperado (25% cada)
    esperado = 25.0
    for col in ['control', 'treatment-a', 'treatment-b', 'treatment-c']:
        df_prop[f'{col}_desvio'] = df_prop[f'{col}_prop'] - esperado
    
    # Identificar filas com maiores desvios
    df_prop['desvio_maximo'] = df_prop[['control_desvio', 'treatment-a_desvio', 
                                       'treatment-b_desvio', 'treatment-c_desvio']].abs().max(axis=1)
    
    filas_top = df_prop.nlargest(top_n, 'desvio_maximo')
    
    print(f"Top {top_n} filas com maiores desvios do esperado (25% cada variant):")
    print()
    
    for _, fila in filas_top.iterrows():
        print(f"🏢 {fila['actor_queue']} (Total: {fila['total_chamadas']:,} chamadas)")
        print(f"   Control: {fila['control_prop']:.1f}% (desvio: {fila['control_desvio']:+.1f}%)")
        print(f"   Treatment-A: {fila['treatment-a_prop']:.1f}% (desvio: {fila['treatment-a_desvio']:+.1f}%)")
        print(f"   Treatment-B: {fila['treatment-b_prop']:.1f}% (desvio: {fila['treatment-b_desvio']:+.1f}%)")
        print(f"   Treatment-C: {fila['treatment-c_prop']:.1f}% (desvio: {fila['treatment-c_desvio']:+.1f}%)")
        print()
    
    return df_prop

def criar_visualizacoes(df, df_prop):
    """
    Cria visualizações para análise
    """
    print("\n" + "="*60)
    print("CRIANDO VISUALIZAÇÕES")
    print("="*60)
    
    # Configurar estilo
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Volume total por variant
    variants = ['control', 'treatment-a', 'treatment-b', 'treatment-c']
    volumes = [df[variant].sum() for variant in variants]
    
    axes[0,0].bar(variants, volumes, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    axes[0,0].set_title('Volume Total por Variant', fontsize=14, fontweight='bold')
    axes[0,0].set_ylabel('Número de Chamadas')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for i, v in enumerate(volumes):
        axes[0,0].text(i, v + max(volumes)*0.01, f'{v:,}', ha='center', fontweight='bold')
    
    # 2. Distribuição de proporções por fila (boxplot)
    prop_data = [df_prop[f'{variant}_prop'].values for variant in variants]
    bp = axes[0,1].boxplot(prop_data, labels=variants, patch_artist=True)
    axes[0,1].axhline(y=25, color='red', linestyle='--', alpha=0.7, label='Esperado (25%)')
    axes[0,1].set_title('Distribuição de Proporções por Fila', fontsize=14, fontweight='bold')
    axes[0,1].set_ylabel('Proporção (%)')
    axes[0,1].legend()
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Colorir boxplots
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # 3. Top 10 filas por volume
    top_filas = df.nlargest(10, 'total_chamadas')
    filas_nomes = [fila.split(' - ')[1] if ' - ' in fila else fila for fila in top_filas['actor_queue']]
    
    x = np.arange(len(filas_nomes))
    width = 0.2
    
    axes[1,0].bar(x - width*1.5, top_filas['control'], width, label='Control', color='#1f77b4')
    axes[1,0].bar(x - width/2, top_filas['treatment-a'], width, label='Treatment-A', color='#ff7f0e')
    axes[1,0].bar(x + width/2, top_filas['treatment-b'], width, label='Treatment-B', color='#2ca02c')
    axes[1,0].bar(x + width*1.5, top_filas['treatment-c'], width, label='Treatment-C', color='#d62728')
    
    axes[1,0].set_title('Top 10 Filas - Volume por Variant', fontsize=14, fontweight='bold')
    axes[1,0].set_ylabel('Número de Chamadas')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(filas_nomes, rotation=45, ha='right')
    axes[1,0].legend()
    
    # 4. Heatmap de desvios
    filas_para_heatmap = df_prop.nlargest(15, 'desvio_maximo')
    desvios_matrix = filas_para_heatmap[['control_desvio', 'treatment-a_desvio', 
                                        'treatment-b_desvio', 'treatment-c_desvio']].values
    
    filas_labels = [fila.split(' - ')[1] if ' - ' in fila else fila 
                   for fila in filas_para_heatmap['actor_queue']]
    
    im = axes[1,1].imshow(desvios_matrix, cmap='RdBu_r', aspect='auto', vmin=-15, vmax=15)
    axes[1,1].set_title('Desvios do Esperado - Top 15 Filas', fontsize=14, fontweight='bold')
    axes[1,1].set_xticks(range(4))
    axes[1,1].set_xticklabels(['Control', 'Treatment-A', 'Treatment-B', 'Treatment-C'])
    axes[1,1].set_yticks(range(len(filas_labels)))
    axes[1,1].set_yticklabels(filas_labels, fontsize=8)
    
    # Adicionar colorbar
    plt.colorbar(im, ax=axes[1,1], label='Desvio (%)')
    
    plt.tight_layout()
    plt.savefig('analise_mix_variants.png', dpi=300, bbox_inches='tight')
    print("📊 Gráficos salvos em: analise_mix_variants.png")
    
    return fig

def main():
    """
    Função principal que executa toda a análise
    """
    # Caminho do arquivo
    caminho_arquivo = "/Users/pedro.magalhaes/Downloads/Queue_analisys___routing_with_entities (21).csv"
    
    print("🔍 ANÁLISE ESTATÍSTICA DE MIX DE VARIANTS")
    print("="*70)
    
    # Carregar dados
    df = carregar_dados(caminho_arquivo)
    
    # Executar testes
    chi2, p_chi2, residuais = teste_chi_quadrado_mix(df)
    totais, p_volume = analisar_volume_total_variants(df)
    df_prop = analisar_proporcoes_por_fila(df)
    
    # Criar visualizações
    fig = criar_visualizacoes(df, df_prop)
    
    # Resumo final
    print("\n" + "="*70)
    print("📋 RESUMO EXECUTIVO")
    print("="*70)
    
    print(f"🔢 Dataset: {len(df)} filas analisadas")
    print(f"📞 Total de chamadas: {df['total_chamadas'].sum():,}")
    
    print(f"\n📊 Resultados dos Testes:")
    print(f"   • Chi-quadrado (mix por fila): p = {p_chi2:.6f}")
    print(f"   • Análise de volume: p = {p_volume:.6f}")
    
    alpha = 0.05
    if p_chi2 < alpha:
        print(f"\n✅ CONCLUSÃO PRINCIPAL:")
        print(f"   Há evidência estatística SIGNIFICATIVA de que os treatments")
        print(f"   afetam diferentemente o volume de chamadas entre as filas.")
        print(f"   Isso pode indicar:")
        print(f"   → Efeito real dos treatments no comportamento dos usuários")
        print(f"   → Possível confounding que precisa ser investigado")
        print(f"   → Necessidade de análise estratificada por fila")
    else:
        print(f"\n❌ CONCLUSÃO PRINCIPAL:")
        print(f"   NÃO há evidência estatística significativa de mudança no mix.")
        print(f"   O experimento parece estar balanceado entre as filas.")
    
    print(f"\n💡 RECOMENDAÇÕES:")
    print(f"   1. Investigar filas com maiores desvios individualmente")
    print(f"   2. Considerar análise estratificada por tipo de fila")
    print(f"   3. Verificar se há fatores externos (sazonalidade, problemas técnicos)")
    print(f"   4. Analisar métricas de outcome principais levando isso em conta")

if __name__ == "__main__":
    main() 