# 🌎 Estudo de Viés Cultural do Dataset (GC1) e Compatibilidade com Embalagens Regionais (Sergipe / Nordeste)

**Projeto:** BioCiclo IA — Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem  
**Instituição:** Universidade Federal de Sergipe (UFS) — Departamento de Computação (DComp)  
**Disciplina:** Fundamentos da Inteligência Artificial  

---

## 1. Contextualização: O Problema do *Domain Shift* Cultural e Geográfico

Na área de Visão Computacional, o fenômeno de **Deslocamento de Domínio (*Domain Shift* ou *Dataset Bias*)** ocorre quando a distribuição visual dos dados utilizados no treinamento difere significativamente do ambiente real de operação.

O dataset público adotado no projeto — **Garbage Classification 3 (GC1 v2)**, assim como bases correlatas (*TrashNet* e *TACO*) — foi constituído majoritariamente por fotografias coletadas nos **Estados Unidos, Europa e Ásia**. Ao aplicar esse modelo diretamente na triagem de resíduos em **Aracaju / Sergipe** (no escopo do programa **BioCiclo Urbano / EMSURB** e das cooperativas locais como a **CARE**), emergem quatro contrastes culturais e industriais determinantes:

1. **Predominância de Embalagens Rígidas (EUA/UE) vs. Plásticos Flexíveis Laminados (Nordeste/Brasil):**
   - No dataset estrangeiro, a classe `PLASTIC` é dominada por garrafas PET cilíndricas e galões translúcidos de leite em PEAD (HDPE).
   - No consumo popular nordestino e sergipano, grande parte dos alimentos secos é comercializada em **embalagens plásticas flexíveis (BOPP / PEBD)** fortemente estampadas, como pacotes de **flocão de milho/cuscuz (Maratá, Nordestino, Coringa)**, **café a vácuo ou almofada (Maratá, São Braz)**, leite em saco e pacotes de biscoito (**Treloso, Fortaleza**).
   - **Efeito no Modelo:** Pela ausência de transparência, formato achatado e alta densidade de texto impresso no rótulo, redes treinadas exclusivamente em bases estrangeiras tendem a confundir plásticos flexíveis regionais com **Papel (`PAPER`)** ou **Papelão (`CARDBOARD`)**.

2. **Recipientes Exclusivos da Cultura de Consumo Brasileira:**
   - **Copo plástico de água mineral (200ml com lacre de alumínio — Indaiá, Cristal):** Onipresente em Sergipe e no Nordeste, mas praticamente inexistente em datasets norte-americanos. Além disso, é um resíduo híbrido (corpo em polipropileno `PLASTIC` + tampa lacre em folha de alumínio `METAL`).
   - **Embalagens Cartonadas Longa Vida (*Tetra Pak* — Leite Betânia, Natville, Camponesa, Sucos Maratá):** Possuem geometria idêntica a uma caixa de papelão (`CARDBOARD`), porém são compósitos multicamadas (75% papel, 20% polietileno e 5% alumínio) que exigem enxágue prévio e reciclagem separada do papelão ondulado comum.

3. **Biomassa Tropical de Feiras Livres vs. Frutas de Clima Temperado:**
   - Na classe `BIODEGRADABLE` do GC1, predominam maçãs vermelhas, peras e folhas de outono temperado.
   - Nas feiras livres de Aracaju atendidas pela **EMSURB** e na **Orla da Atalaia**, a biomassa orgânica real é composta por **casca de coco verde**, **casca de macaxeira (mandioca)**, **inhame**, **coentro**, **manga**, **jaca**, **maracujá**, **folha de bananeira** e **bagaço de cana**.
   - **Efeito no Modelo:** O coco verde oxidado (marrom e fibroso) e a casca de macaxeira terrosa assemelham-se cromaticamente ao **Papelão (`CARDBOARD`)**, exigindo adaptação local.

4. **Assimetria de Densidade de Anotações na Classe `BIODEGRADABLE`:**
   - No GC1, uma única imagem de resíduo orgânico frequentemente contém entre **30 e 50 caixas delimitadoras** (ex: pilhas de maçãs), enquanto fotos de plástico ou vidro contêm 1 ou 2 objetos. Sem rebalanceamento no treinamento e calibração pós-inferência, a rede neural desenvolve um viés (*prior*) que super-prediz `BIODEGRADABLE`.

---

## 2. Matriz de Compatibilidade com Marcas e Resíduos da Nossa Região

| Produto / Resíduo Regional | Marcas / Ocorrência Local (SE/NE) | Classe Real | Predição Típica (GC1 Puro) | Nível de Compatibilidade | Diretriz Local (Aracaju / EMSURB / CARE) |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Pacote de Flocão de Milho / Cuscuz** | Maratá, Nordestino, Coringa, Vitamilho | `PLASTIC` | `PAPER` / `BIODEGRADABLE` | **Baixa (38%)** | Coletor Vermelho (Sacudir restos secos de farinha) |
| **Pacote de Café (Vácuo / Almofada)** | Café Maratá, São Braz, Santa Clara | `PLASTIC` | `CARDBOARD` / `PAPER` | **Baixa (35%)** | Borra no BioCiclo Urbano; embalagem vazia no Coletor Vermelho/Cinza |
| **Caixa Longa Vida (Tetra Pak)** | Leite Betânia, Natville (SE), Camponesa, Sucos Maratá | `CARDBOARD` | `CARDBOARD` / `PAPER` | **Média (72%)** | Coletor Azul / Seletiva (Enxaguar restos de leite e achatar) |
| **Copo de Água Mineral 200ml** | Indaiá, Cristal, Dias D'Ávila | `PLASTIC` | `GLASS` / `PLASTIC` | **Média (58%)** | Destacar totalmente o lacre de alumínio (`METAL`) do copo (`PLASTIC`) |
| **Garrafas PET e Vidro de Bebidas** | Cajuína São Geraldo, Guaraná Antarctica, Frevo, Indaiá | `PLASTIC` / `GLASS` | `PLASTIC` / `GLASS` | **Alta (89%)** | Coletor Vermelho (PET) ou Verde (Vidro); amassar PET e manter tampa |
| **Latas de Alumínio e Conservas** | Skol, Brahma, Pitú, Leite Ninho/Itambé | `METAL` | `METAL` | **Alta (86%)** | Coletor Amarelo; dobrar tampas serrilhadas de aço para dentro |
| **Potes de Margarina / Laticínios** | Deline, Qualy, Primor, Requeijão | `PLASTIC` | `PLASTIC` / `CARDBOARD` | **Média (67%)** | Coletor Vermelho (Polipropileno - PP); remover excesso de gordura |
| **Casca de Coco Verde** | Orla de Atalaia, Feiras Livres de Aracaju | `BIODEGRADABLE` | `CARDBOARD` / `BIODEGRADABLE` | **Baixa (42%)** | BioCiclo Urbano / EMSURB (Exige trituração mecânica prévia da fibra) |
| **Cascas de Macaxeira e Tubérculos** | Feiras Livres, Mercados Thales Ferraz e Albano Franco | `BIODEGRADABLE` | `CARDBOARD` / `BIODEGRADABLE` | **Média (55%)** | Compostagem Prioritária (BioCiclo Urbano) — rica fonte de carbono |
| **Frutas Tropicais e Folhosos** | Coentro, Manga, Jaca, Maracujá, Banana (Feiras SE) | `BIODEGRADABLE` | `BIODEGRADABLE` | **Alta (85%)** | Compostagem Direta (BioCiclo Urbano) em bombonas sem sacolas plásticas |

---

## 3. Soluções Técnicas Implementadas no Projeto

1. **Módulo e Aba Interativa `"Questões Culturais & Marcas Regionais (SE/NE)"` no Streamlit (`app/main.py` e `src/rules/cultural_analysis.py`):**
   - Documenta visualmente as evidências do dataset GC1, apresenta os 10 perfis de embalagens/resíduos regionais e disponibiliza um **Laboratório de Teste ao Vivo** para confrontar fotos reais de embalagens locais contra o modelo.
2. **Calibração Pós-Inferência Anti-Viés (`src/models/detector.py`):**
   - Implementa recalibração de probabilidades (`GC1_PRIOR_CALIBRATION`), filtragem de micro-caixas espúrias e análise cromática de ROI para impedir que objetos recicláveis manufaturados sejam engolidos pelo viés de `BIODEGRADABLE`.
3. **Rebalanceamento Automático de Instâncias no Treinamento (`src/training/train_yolo.py` e `notebooks/Treinamento_BioCiclo_Google_Colab.ipynb`):**
   - Antes de iniciar o fine-tuning do YOLO, o script poda automaticamente o excesso de caixas repetidas em fotos superlotadas da classe `BIODEGRADABLE` e aplica `cls=1.5` e `cos_lr=True`.
