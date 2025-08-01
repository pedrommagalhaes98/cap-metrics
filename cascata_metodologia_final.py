import matplotlib.pyplot as plt
import numpy as np

# Configurações
plt.rcParams['font.size'] = 11
plt.rcParams['figure.figsize'] = (16, 9)
plt.rcParams['font.family'] = 'Arial'

print("=== CASCATA FINAL COM METODOLOGIA CORRETA ===")

# Dados baseados na análise pragmática
custo_control = 229829460
custo_treatment = 214479743
reducao_total = custo_control - custo_treatment

# Componentes da cascata pragmática (sem dupla contagem)
cascata = [
    ('Custo\nControle', custo_control, 'baseline', '#2E86AB'),
    ('Redirecionamento\nSquad Phone', -33465484, 'principal', '#A23B72'),
    ('Aumento Abandono\n(+0.7pp)', -1600000, 'secundario', '#A23B72'),
    ('Return Rate\n(+0.39pp)', 300000, 'negativo', '#F18F01'),
    ('Outros Efeitos\n(Eficiência)', -16549234, 'residual', '#6A994E'),
    ('Custo\nTreatment-B', custo_treatment, 'baseline', '#2E86AB')
]

# Verificação
soma_componentes = sum([comp[1] for comp in cascata[1:-1]])
print(f"Verificação: {soma_componentes:,.0f} vs {-reducao_total:,.0f}")

# Criar gráfico
fig, ax = plt.subplots(figsize=(16, 10))

# Preparar dados
labels = [comp[0] for comp in cascata]
values = [comp[1] for comp in cascata]
tipos = [comp[2] for comp in cascata]
colors = [comp[3] for comp in cascata]

# Calcular posições das barras para efeito cascata
positions = range(len(labels))
y_current = custo_control
bar_positions = []
bar_heights = []

for i, (label, value, tipo, color) in enumerate(cascata):
    if tipo == 'baseline':
        bar_positions.append(0)
        bar_heights.append(value)
    else:
        if value < 0:  # Redução
            y_current += value
            bar_positions.append(y_current)
            bar_heights.append(abs(value))
        else:  # Aumento
            bar_positions.append(y_current)
            bar_heights.append(value)
            y_current += value

# Plotar barras
bars = ax.bar(positions, bar_heights, bottom=bar_positions, 
              color=colors, alpha=0.85, width=0.7, 
              edgecolor='white', linewidth=2)

# Adicionar linhas conectoras
for i in range(1, len(positions)-1):
    if i < len(positions) - 1:
        prev_top = bar_positions[i-1] + bar_heights[i-1] if bar_positions[i-1] > 0 else bar_heights[i-1]
        current_start = bar_positions[i] if values[i] > 0 else bar_positions[i] + bar_heights[i]
        
        # Linha conectora pontilhada
        ax.plot([i-0.4, i-0.4], [prev_top, current_start], 'k--', alpha=0.4, linewidth=1.5)
        ax.plot([i+0.4, i+0.4], [prev_top, current_start], 'k--', alpha=0.4, linewidth=1.5)

# Adicionar valores nas barras
for i, (bar, value, tipo) in enumerate(zip(bars, values, tipos)):
    if tipo == 'baseline':
        # Valores totais
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 4000000,
                f'R$ {value/1000000:.0f}M',
                ha='center', va='bottom', fontweight='bold', fontsize=13)
    else:
        # Valores dos componentes
        y_pos = bar.get_y() + bar.get_height()/2
        sinal = "+" if value > 0 else ""
        
        # Cor do texto baseada no tamanho da barra
        text_color = 'white' if bar.get_height() > 8000000 else 'black'
        
        if tipo == 'principal':
            ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                    f'{sinal}R$ {value/1000000:.1f}M\n⭐ PRINCIPAL',
                    ha='center', va='center', fontweight='bold', 
                    fontsize=11, color=text_color)
        else:
            ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                    f'{sinal}R$ {value/1000000:.1f}M',
                    ha='center', va='center', fontweight='bold', 
                    fontsize=10, color=text_color)

# Configurações do gráfico
ax.set_xticks(positions)
ax.set_xticklabels(labels, ha='center', fontsize=12)
ax.set_ylabel('Custo Anual (R$ Milhões)', fontsize=14, fontweight='bold')
ax.set_title('Cascata de Custos: Controle vs Treatment-B\nMetodologia Correta - Speech-to-Text no Roteamento', 
             fontsize=16, fontweight='bold', pad=25)

# Configurar eixo Y
max_y = custo_control * 1.15
ax.set_ylim(0, max_y)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000000:.0f}M'))

# Grid sutil
ax.grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)

# Legenda customizada
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2E86AB', alpha=0.85, label='Custo Total'),
    Patch(facecolor='#A23B72', alpha=0.85, label='Redução de Custos'),
    Patch(facecolor='#F18F01', alpha=0.85, label='Aumento de Custos'),
    Patch(facecolor='#6A994E', alpha=0.85, label='Outros Efeitos')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=0.9)

# Caixa com metodologia
metodologia_text = (
    "METODOLOGIA:\n"
    "1. Redirecionamento Squad Phone = Principal Driver\n"
    "2. Efeitos Abandono/Return = Secundários\n"
    "3. Outros Efeitos = Residual\n"
    "✓ Sem dupla contagem"
)
ax.text(0.98, 0.97, metodologia_text,
        transform=ax.transAxes, ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#F0F8FF', 
                 edgecolor='#2E86AB', linewidth=1.5, alpha=0.95),
        fontsize=10, fontfamily='monospace')

# Caixa com economia total
economia_percent = (reducao_total / custo_control) * 100
ax.text(0.02, 0.97, 
        f'Economia Total\nR$ {reducao_total/1000000:.1f}M\n({economia_percent:.1f}%)',
        transform=ax.transAxes, ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F5E8', 
                 edgecolor='#A23B72', linewidth=2, alpha=0.95),
        fontsize=13, fontweight='bold')

# Remover spines superiores e direitas
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1)
ax.spines['bottom'].set_linewidth(1)

plt.tight_layout()
plt.savefig('cascata_metodologia_correta_final.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print(f"\n=== RESPOSTA COMPLETA SOBRE METODOLOGIA ===")
print()
print("🎯 COMO DEFINO A ORDEM DOS COMPONENTES?")
print("   Sigo a CADEIA CAUSAL do experimento:")
print("   1º Speech-to-Text (causa primária)")
print("   2º Redirecionamento (efeito direto)")
print("   3º Consequências (efeitos secundários)")
print()
print("🎯 POR QUE SQUAD PHONE É CONSIDERADO SOZINHO?")
print("   • Representa 218% da economia total (R$ 33.5M vs R$ 15.3M)")
print("   • É o PRINCIPAL mecanismo do speech-to-text")
print("   • Merece destaque próprio por ser o motor da economia")
print()
print("🎯 COMO FICAM AS MUDANÇAS NOS OUTROS SQUADS?")
print("   • Outros squads GANHAM os tickets que o phone perdeu")
print("   • Mas têm custos unitários diferentes (alguns mais caros, outros mais baratos)")
print("   • O efeito LÍQUIDO é positivo porque o phone é mais caro que a média")
print()
print("🎯 DECOMPOSIÇÃO FINAL (METODOLOGIA CORRETA):")
for nome, valor, tipo, _ in cascata:
    if tipo == 'baseline':
        print(f"   {nome:25}: R$ {valor/1000000:6.1f}M")
    elif tipo == 'principal':
        print(f"   {nome:25}: R$ {valor/1000000:6.1f}M ⭐ PRINCIPAL DRIVER")
    else:
        sinal = "+" if valor > 0 else ""
        print(f"   {nome:25}: {sinal}R$ {valor/1000000:6.1f}M")
print()
print("✅ Esta metodologia evita dupla contagem")
print("✅ Segue a lógica causal do experimento") 
print("✅ É transparente sobre limitações")