# 🚀 Guia de Workflow GitHub via Cursor

## Comandos Principais para PRs

### 1️⃣ Criar uma Nova Branch e PR

```bash
# Criar e mudar para uma nova branch
git checkout -b feature/minha-nova-feature

# Fazer suas mudanças...
# Adicionar arquivos
git add .

# Commit
git commit -m "feat: adiciona nova funcionalidade"

# Push da branch
git push origin feature/minha-nova-feature

# Criar PR direto pelo terminal
gh pr create --title "Minha Nova Feature" --body "Descrição detalhada da feature"
```

### 2️⃣ Listar PRs

```bash
# Ver todos os PRs abertos
gh pr list

# Ver seus PRs
gh pr list --author "@me"

# Ver PRs por status
gh pr list --state all  # todos
gh pr list --state open  # abertos
gh pr list --state closed  # fechados
gh pr list --state merged  # mergeados
```

### 3️⃣ Ver Detalhes de um PR

```bash
# Ver detalhes de um PR específico (por número)
gh pr view 123

# Ver o PR da branch atual
gh pr view

# Abrir PR no navegador
gh pr view --web
```

### 4️⃣ Editar um PR

```bash
# Editar título e descrição
gh pr edit 123 --title "Novo Título" --body "Nova descrição"

# Adicionar reviewers
gh pr edit 123 --add-reviewer username1,username2

# Adicionar labels
gh pr edit 123 --add-label bug,enhancement

# Mudar base branch
gh pr edit 123 --base main
```

### 5️⃣ Fazer Checkout de um PR

```bash
# Fazer checkout de um PR para testar localmente
gh pr checkout 123

# Ou pelo link do PR
gh pr checkout https://github.com/pedrommagalhaes98/cap-metrics/pull/123
```

### 6️⃣ Atualizar um PR Existente

```bash
# Fazer mudanças adicionais no PR
git add .
git commit -m "fix: corrige problema X"
git push

# O PR é atualizado automaticamente!
```

### 7️⃣ Mergear um PR

```bash
# Mergear PR (método merge)
gh pr merge 123

# Mergear com squash
gh pr merge 123 --squash

# Mergear com rebase
gh pr merge 123 --rebase

# Mergear e deletar branch
gh pr merge 123 --delete-branch

# Mergear automaticamente quando checks passarem
gh pr merge 123 --auto
```

### 8️⃣ Fechar um PR sem Mergear

```bash
# Fechar PR
gh pr close 123

# Fechar com comentário
gh pr close 123 --comment "Não é mais necessário"
```

### 9️⃣ Reabrir um PR

```bash
gh pr reopen 123
```

### 🔟 Comentar em um PR

```bash
# Adicionar comentário
gh pr comment 123 --body "Ótimo trabalho!"

# Adicionar review
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Precisa de ajustes"
gh pr review 123 --comment --body "Apenas um comentário"
```

### 1️⃣1️⃣ Verificar Status de Checks

```bash
# Ver status dos checks do PR
gh pr checks

# Ver status de um PR específico
gh pr checks 123
```

### 1️⃣2️⃣ Ver Diff do PR

```bash
# Ver mudanças do PR
gh pr diff 123
```

## 🔄 Workflow Completo - Exemplo Prático

### Cenário: Adicionar uma nova feature

```bash
# 1. Atualizar main
git checkout main
git pull origin main

# 2. Criar branch para feature
git checkout -b feature/adicionar-dashboard

# 3. Fazer as mudanças no código
# ... editar arquivos ...

# 4. Commit das mudanças
git add .
git commit -m "feat: adiciona dashboard de métricas"

# 5. Push da branch
git push origin feature/adicionar-dashboard

# 6. Criar PR
gh pr create \
  --title "feat: Adiciona Dashboard de Métricas" \
  --body "Este PR adiciona um dashboard interativo para visualizar métricas do IntelliJ" \
  --reviewer seu-colega \
  --label enhancement

# 7. Se precisar fazer mudanças após review
git add .
git commit -m "fix: ajusta layout do dashboard"
git push

# 8. Quando aprovado, mergear
gh pr merge --squash --delete-branch
```

## 🎯 Comandos Úteis Adicionais

```bash
# Ver PR atual (da branch que você está)
gh pr status

# Sincronizar fork (se for um fork)
gh repo sync

# Ver informações do repositório
gh repo view

# Clonar um PR como branch
gh pr checkout 123

# Listar branches
git branch -a

# Voltar para main
git checkout main

# Deletar branch local
git branch -d feature/minha-branch

# Forçar deleção de branch local
git branch -D feature/minha-branch
```

## 💡 Dicas Pro

1. **Criar PR em modo interativo:**
   ```bash
   gh pr create
   # Vai te guiar passo a passo
   ```

2. **Template de PR:**
   Você pode criar templates em `.github/pull_request_template.md`

3. **Auto-merge quando CI passar:**
   ```bash
   gh pr merge 123 --auto --squash
   ```

4. **Ver PRs que precisam de review:**
   ```bash
   gh pr list --search "review-requested:@me"
   ```

5. **Criar PR draft:**
   ```bash
   gh pr create --draft
   ```

6. **Converter draft para ready:**
   ```bash
   gh pr ready 123
   ```

## 🚨 Comandos de Emergência

```bash
# Desfazer último commit (mantém mudanças)
git reset HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Desfazer push (CUIDADO!)
git push --force origin branch-name

# Atualizar branch com main
git checkout feature/minha-branch
git merge main
# ou
git rebase main

# Resolver conflitos e continuar rebase
git add .
git rebase --continue
```

## 📝 Aliases Úteis

Adicione ao seu `~/.gitconfig`:

```bash
[alias]
    # Aliases para GitHub CLI
    prc = !gh pr create
    prv = !gh pr view
    prl = !gh pr list
    prm = !gh pr merge --squash --delete-branch
    
    # Aliases Git comuns
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
```

---

**Repositório:** pedrommagalhaes98/cap-metrics  
**Usuário GitHub:** pedrommagalhaes98  
**Protocolo:** HTTPS  
**Scopes:** repo, read:org, gist

