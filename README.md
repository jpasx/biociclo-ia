# 🌿 BioCiclo IA: Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/YOLO-Ultralytics-orange.svg)](https://docs.ultralytics.com/)
[![Web App](https://img.shields.io/badge/App-Streamlit-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![UFS](https://img.shields.io/badge/UFS-DComp-darkgreen.svg)](https://dcomp.ufs.br/)

Projeto acadêmico desenvolvido para a disciplina de **Fundamentos da Inteligência Artificial**, no **Departamento de Computação (DComp)** da **Universidade Federal de Sergipe (UFS)**.

---

## 📌 Contextualização e Motivação

O projeto nasce inspirado na iniciativa **BioCiclo Urbano**, programa de compostagem promovido pela **Prefeitura de Aracaju** e executado em articulação com a **Empresa Municipal de Serviços Urbanos (EMSURB)**. O objetivo central da iniciativa é ampliar o reaproveitamento de resíduos orgânicos gerados em feiras livres, mercados municipais e estabelecimentos urbanos, direcionando-os para processos sustentáveis de compostagem.

### O Desafio
Na prática, os resíduos raramente chegam previamente separados: materiais orgânicos com alto potencial de adubagem costumam estar misturados a plásticos, latas, papéis e rejeitos. 

### Nossa Solução
Desenvolver um sistema inteligente baseado em **Visão Computacional** e redes neurais **YOLO**, que atua como uma ferramenta de apoio à triagem:
1. Detecta e delimita resíduos em fotografias;
2. Classifica a categoria do material (orgânico, plástico, metal, vidro, papel, papelão, etc.);
3. Determina se o material é **Lixo Orgânico** ou **Lixo Comum/Reciclável**;
4. Fornece uma recomendação clara de destinação, incentivando a **Compostagem (BioCiclo Urbano)** e a **Coleta Seletiva**.

---

## 🎯 Regras de Decisão e Destinação Sugerida

Em conformidade com a proposta do projeto (Check-in 1 e 2), a relação entre as categorias identificadas e as orientações de descarte é dada por:

| Categoria Detectada | Grupo de Lixo | Sugestão de Destinação | Ação Recomendada |
| :--- | :--- | :--- | :--- |
| **Orgânico / Biodegradável** | **Orgânico** | **Compostagem (BioCiclo Urbano)** | Direcionar para leiras de compostagem ou composteiras locais |
| **Papel** | Comum / Reciclável | Coleta Seletiva / Reciclagem | Enviar seco e limpo para cooperativas de reciclagem |
| **Papelão** | Comum / Reciclável | Coleta Seletiva / Reciclagem | Desmontar caixas e evitar contaminação por óleo/graxa |
| **Plástico** | Comum / Reciclável | Coleta Seletiva / Reciclagem | Enxaguar resíduos líquidos e amassar embalagens PET |
| **Metal** | Comum / Reciclável | Coleta Seletiva / Reciclagem | Amassar latas e dobrar partes cortantes |
| **Vidro** | Comum / Reciclável | Coleta Seletiva / Reciclagem | Separar por cor; embalar cacos pontiagudos com proteção |
| **Rejeito / Tecido** | Comum / Rejeito | Coleta Convencional / Aterro | Destinar ao recolhimento público convencional ou doação |

> ⚠️ **Tratamento de Incerteza:** Caso o modelo apresente confiança inferior ao limiar de segurança (configurável, ex: `< 50%`), a interface emite um alerta preventivo solicitando uma nova fotografia (com melhor iluminação e enquadramento), evitando descarte incorreto.

---

## 🗂️ Estrutura do Repositório

```text
biociclo-ia/
├── app/
│   ├── main.py                  # Aplicação Web Streamlit (MVP interativo)
│   └── components/
│       ├── __init__.py
│       └── ui_helpers.py        # Componentes visuais, cards e estilos CSS
├── src/
│   ├── __init__.py
│   ├── config.py                # Configurações globais (paths, classes, cores)
│   ├── rules/
│   │   ├── __init__.py
│   │   └── destination.py       # Regras de negócio e tabela de destinação
│   ├── models/
│   │   ├── __init__.py
│   │   └── detector.py          # Wrapper de inferência YOLO com fallback automático
│   ├── data/
│   │   ├── __init__.py
│   │   ├── download_dataset.py  # Script para download do Garbage Classification 3
│   │   └── generate_samples.py  # Gerador de amostras de teste locais
│   └── training/
│       ├── __init__.py
│       ├── train_yolo.py        # Script de treinamento (fine-tuning)
│       └── evaluate.py          # Avaliação de métricas (mAP@50, Recall, Precisão)
├── data/
│   └── samples/                 # Imagens para teste rápido na interface
├── models/
│   └── weights/                 # Diretório onde os pesos finais (best.pt) são salvos
├── docs/
│   ├── checkin_1_resumo.md      # Resumo formal do Check-in 1
│   ├── checkin_2_resumo.md      # Resumo formal do Check-in 2
│   └── guia_colaboracao.md      # Guia prático de Git e workflow para o grupo
├── notebooks/
│   └── 01_exploracao_dataset.ipynb # Análise exploratória e visualização do dataset
├── .env.example                 # Exemplo de configuração de variáveis de ambiente
├── .gitignore                   # Regras de exclusão do Git
├── LICENSE                      # Licença MIT
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

---

## 🚀 Como Começar (Guia Rápido)

### 1. Clonar o repositório
```bash
git clone https://github.com/jpasx/biociclo-ia.git
cd biociclo-ia
```

### 2. Criar ambiente virtual Python
No Windows:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
No Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Executar a aplicação Web (Streamlit)
```bash
streamlit run app/main.py
```
Acesse no seu navegador: `http://localhost:8501`.

---

## 📊 Fonte de Dados e Treinamento

O projeto adota como base primária:
- **GARBAGE CLASSIFICATION 3 (GC1) v2**: Disponível no [Roboflow Universe](https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/2).
- Contém **10.464 imagens anotadas** para detecção de objetos em formato YOLO com licença CC BY 4.0.
- 7 classes: `BIODEGRADABLE`, `CARDBOARD`, `CLOTH`, `GLASS`, `METAL`, `PAPER`, `PLASTIC`.

### Baixar o Dataset:
1. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
2. Adicione sua chave de API gratuita do Roboflow no arquivo `.env`.
3. Execute o download automatizado:
   ```bash
   python -m src.data.download_dataset
   ```

### Treinar o Modelo YOLO:
```bash
python -m src.training.train_yolo --epochs 50 --batch 16 --device cpu
```
*(Caso use GPU NVIDIA, informe `--device 0`)*

### Avaliar o Modelo:
```bash
python -m src.training.evaluate --model models/weights/best.pt
```

---

## 👥 Colaboração da Equipe

Consulte o arquivo [`docs/guia_colaboracao.md`](docs/guia_colaboracao.md) para detalhes sobre fluxo de branches, pull requests e boas práticas no Git.

---

## 📚 Referências

- **Roboflow Universe:** Material Identification. *Garbage Classification 3 (GC1)*, 2026.
- **Ultralytics YOLO:** Ultralytics Object Detection Documentation.
- **TrashNet Dataset:** Gary Thung & Mindy Yang, Stanford University.
- **Iniciativa BioCiclo Urbano:** Prefeitura Municipal de Aracaju & EMSURB.
