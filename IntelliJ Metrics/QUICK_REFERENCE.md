# ⚡ Referência Rápida - GitHub CLI no Cursor

## 🚀 Workflow Básico

### Criar PR
```bash
# Criar branch
git checkout -b feature/nome

# Fazer mudanças, commit e push
git add .
git commit -m "mensagem"
git push origin feature/nome

# Criar PR
gh pr create --title "Título" --body "Descrição"
```

### Gerenciar PR
```bash
gh pr list                    # Listar PRs
gh pr view 123                # Ver detalhes
gh pr edit 123 --title "..."  # Editar
gh pr checkout 123            # Testar PR
gh pr merge 123 --squash      # Mergear
```

## 📋 Cheat Sheet

| Ação | Comando |
|------|---------|
| **Criar PR** | `gh pr create` |
| **Listar PRs** | `gh pr list` |
| **Ver PR** | `gh pr view [numero]` |
| **Editar PR** | `gh pr edit [numero]` |
| **Mergear PR** | `gh pr merge [numero]` |
| **Fechar PR** | `gh pr close [numero]` |
| **Reabrir PR** | `gh pr reopen [numero]` |
| **Checkout PR** | `gh pr checkout [numero]` |
| **Comentar** | `gh pr comment [numero] --body "..."` |
| **Aprovar** | `gh pr review [numero] --approve` |
| **Ver diff** | `gh pr diff [numero]` |
| **Ver checks** | `gh pr checks [numero]` |
| **Status** | `gh pr status` |

## 💬 Como Usar no Cursor

1. **Via Chat do Cursor:**
   - Você pode pedir: "Crie um PR para a branch atual"
   - Ou: "Liste os PRs abertos"
   - Ou: "Faça merge do PR #123"

2. **Via Terminal Integrado:**
   - Use os comandos `gh` diretamente
   - O Cursor executará automaticamente

3. **Pedir Ajuda:**
   - "Me ajude a criar um PR"
   - "Como faço merge de um PR?"
   - "Mostre os PRs que precisam de review"

## 🎯 Exemplos Práticos

### Exemplo 1: Feature completa
```bash
git checkout -b feature/nova-metrica
# ... edite arquivos ...
git add .
git commit -m "feat: adiciona métrica de performance"
git push origin feature/nova-metrica
gh pr create --title "feat: Nova métrica de performance" \
             --body "Adiciona métrica para medir performance do IntelliJ"
```

### Exemplo 2: Correção rápida
```bash
git checkout -b fix/bug-calculo
# ... corrija o bug ...
git add .
git commit -m "fix: corrige cálculo de média"
git push origin fix/bug-calculo
gh pr create --title "fix: Corrige cálculo de média" \
             --body "Corrige erro no cálculo da média das métricas" \
             --label bug
```

### Exemplo 3: Atualizar PR após review
```bash
# Você está na branch do PR
git add .
git commit -m "fix: ajusta conforme review"
git push
# PR atualiza automaticamente!
```

### Exemplo 4: Mergear PR
```bash
gh pr merge 123 --squash --delete-branch
```

## 🤖 Comandos que Você Pode Pedir ao Cursor

- "Crie uma branch chamada feature/dashboard"
- "Faça commit das mudanças atuais com a mensagem 'feat: adiciona dashboard'"
- "Suba as mudanças para o GitHub"
- "Crie um PR com o título 'Adiciona Dashboard'"
- "Liste todos os PRs abertos"
- "Faça merge do PR #5 com squash"
- "Mostre as mudanças do PR #3"
- "Adicione um comentário no PR #2 dizendo 'LGTM!'"

## ⚙️ Configuração Atual

- **Usuário:** pedrommagalhaes98
- **Repositório:** pedrommagalhaes98/cap-metrics
- **Branch Padrão:** master
- **Protocolo:** HTTPS
- **Permissões:** repo, read:org, gist

## 📚 Documentação Completa

Para mais detalhes, veja: `GITHUB_WORKFLOW_GUIDE.md`

---

**Status da Integração:** ✅ Ativa e Funcionando!

