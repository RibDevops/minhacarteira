# AUDITORIA CSS - MINHACARTEIRA

**Data:** 30/09/2026 09:29:17

---

## 1. INVENTARIO DE ARQUIVOS CSS

**Total de arquivos CSS:** 20

### Arquivos encontrados:

- [ADMIN] `static\admin\css\autocomplete.css` (9.24 KB)
- [ADMIN] `static\admin\css\base.css` (22.75 KB)
- [ADMIN] `static\admin\css\changelists.css` (7.05 KB)
- [ADMIN] `static\admin\css\dark_mode.css` (2.87 KB)
- [ADMIN] `static\admin\css\dashboard.css` (0.46 KB)
- [ADMIN] `static\admin\css\forms.css` (8.81 KB)
- [ADMIN] `static\admin\css\login.css` (0.99 KB)
- [ADMIN] `static\admin\css\nav_sidebar.css` (2.89 KB)
- [ADMIN] `static\admin\css\responsive.css` (17.06 KB)
- [ADMIN] `static\admin\css\responsive_rtl.css` (2.03 KB)
- [ADMIN] `static\admin\css\rtl.css` (4.95 KB)
- [ADMIN] `static\admin\css\unusable_password_field.css` (0.67 KB)
- [ADMIN] `static\admin\css\widgets.css` (12.29 KB)
- [VENDOR] `static\admin\css\vendor\select2\select2.css` (17.42 KB)
- [VENDOR] `static\admin\css\vendor\select2\select2.min.css` (14.62 KB)
- [CUSTOM] `static\css\custom.css` (17.65 KB)
- [CUSTOM] `static\css\dark-mode.css` (1.33 KB)
- [CUSTOM] `static\css\fab.css` (1.47 KB)
- [VENDOR] `static\vendor\bootstrap\css\bootstrap.min.css` (227.49 KB)
- [VENDOR] `static\vendor\bootstrap-icons\font\bootstrap-icons.min.css` (80.02 KB)

**Resumo:**
- Custom (nosso codigo): 3
- Vendor (bibliotecas externas): 4
- Admin Django: 13

---

## 2. ANALISE DOS CSS CUSTOMIZADOS

### `static\css\custom.css`

- **Tamanho:** 17.65 KB
- **Linhas:** 698

- **Seletores CSS:** aprox. 108

- **Variaveis CSS:** 1 encontradas [OK]

- **Media Queries:** 6

- **Cores hardcoded:** 96 [ATENCAO]
  - HEX: 70
  - RGB/RGBA: 26

- **!important encontrados:** 5 [ATENCAO]

- **Sombras (box-shadow):** 19

- **Border-radius:** 14


### `static\css\dark-mode.css`

- **Tamanho:** 1.33 KB
- **Linhas:** 70

- **Seletores CSS:** aprox. 12

- **Variaveis CSS:** 6 encontradas [OK]

- **Media Queries:** 0

- **Cores hardcoded:** 29 [ATENCAO]
  - HEX: 29
  - RGB/RGBA: 0

- **!important encontrados:** 3 [ATENCAO]

- **Sombras (box-shadow):** 0

- **Border-radius:** 0


### `static\css\fab.css`

- **Tamanho:** 1.47 KB
- **Linhas:** 78

- **Seletores CSS:** aprox. 12

- **Variaveis CSS:** Nenhuma encontrada [ATENCAO]

- **Media Queries:** 2

- **Cores hardcoded:** 8 [ATENCAO]
  - HEX: 6
  - RGB/RGBA: 2

- **Sombras (box-shadow):** 2

- **Border-radius:** 1


---

## 3. ANALISE DE USO NOS TEMPLATES

**Total de templates HTML:** 36

### Top 20 classes CSS mais usadas:

- `bi` usado 147x
- `btn` usado 114x
- `fw-bold` usado 63x
- `text-center` usado 52x
- `mb-3` usado 46x
- `shadow-sm` usado 46x
- `btn-sm` usado 44x
- `text-muted` usado 40x
- `d-flex` usado 40x
- `text-primary` usado 33x
- `card` usado 33x
- `border-0` usado 32x
- `container` usado 31x
- `mb-4` usado 31x
- `mt-4` usado 29x
- `mb-0` usado 29x
- `row` usado 29x
- `align-items-center` usado 27x
- `card-body` usado 25x
- `d-block` usado 24x

---

## 4. PROBLEMAS IDENTIFICADOS

[ATENCAO] Nao ha design tokens (variaveis CSS em :root)

[ATENCAO] Muitas cores hardcoded (133) - dificulta manutencao

---

## 5. OPORTUNIDADES DE MELHORIA

### 5.1 Design System iOS-style

- [ ] Criar arquivo design-tokens.css com variaveis CSS
- [ ] Definir paleta de cores (primaria, secundaria, backgrounds, textos)
- [ ] Definir escala de espacamentos (4px, 8px, 12px, 16px, 24px, 32px, 48px)
- [ ] Definir escala tipografica (font-size, line-height, font-weight)
- [ ] Definir sombras padronizadas (iOS-style: suaves e discretas)
- [ ] Definir border-radius padrao (8px, 12px, 16px)

### 5.2 Refatoracao CSS

- [ ] Migrar cores hardcoded para variaveis CSS
- [ ] Criar components.css (botoes, cards, inputs, badges)
- [ ] Criar utilities.css (margin, padding, display, text-align)
- [ ] Integrar dark-mode usando variaveis CSS
- [ ] Remover !important desnecessarios
- [ ] Consolidar seletores duplicados

### 5.3 Modernizacao Visual (iOS-style)

- [ ] Aplicar border-radius: 12px em cards e containers
- [ ] Aplicar sombras suaves (box-shadow: 0 2px 8px rgba(0,0,0,0.08))
- [ ] Usar tipografia moderna (system-ui, -apple-system, SF Pro Display)
- [ ] Implementar estados hover/focus/active refinados
- [ ] Adicionar transicoes suaves (transition: all 0.2s ease)
- [ ] Usar cores suaves e gradientes sutis
- [ ] Melhorar espacamentos (mais respiro, menos compactacao)

### 5.4 Responsividade

- [ ] Revisar breakpoints mobile (< 768px)
- [ ] Melhorar layout do dashboard em mobile
- [ ] Ajustar formularios para telas pequenas
- [ ] Testar em iOS Safari e Android Chrome

### 5.5 Performance

- [ ] Minificar CSS customizado
- [ ] Remover CSS nao utilizado (PurgeCSS)
- [ ] Usar apenas vendor CSS necessario

---

## 6. PLANO DE REFATORACAO

### BLOCO 2: Design Tokens
- Criar static/css/design-tokens.css
- Definir todas as variaveis CSS (:root)
- Testar em um componente isolado

### BLOCO 3: Componentes Base
- Criar static/css/components.css
- Refatorar botoes
- Refatorar cards
- Refatorar inputs/forms
- Refatorar badges/tags

### BLOCO 4: Modernizacao Visual
- Aplicar design tokens em custom.css
- Ajustar border-radius, sombras, espacamentos
- Melhorar tipografia
- Refinar estados interativos

### BLOCO 5: Dark Mode Integrado
- Migrar dark-mode.css para variaveis CSS
- Criar toggle dark/light
- Testar todos os componentes

### BLOCO 6: Responsividade
- Ajustar breakpoints
- Melhorar mobile-first
- Testar em dispositivos reais

---

## 7. PROXIMOS PASSOS

Execute o script de refatoracao:

```powershell
.\02_criar_design_tokens.ps1
```

