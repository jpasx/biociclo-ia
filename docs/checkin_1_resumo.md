# Check-in 1: Contextualização e Proposta do Projeto

**Instituição:** Universidade Federal de Sergipe (UFS)  
**Departamento:** Departamento de Computação (DComp)  
**Disciplina:** Fundamentos da Inteligência Artificial  
**Projeto:** Sistema Inteligente para Classificação de Resíduos por Imagem  

---

## 1. Contextualização do Problema
O projeto surge a partir do **BioCiclo Urbano**, iniciativa de compostagem promovida pela **Prefeitura de Aracaju** e desenvolvida em articulação com a **Empresa Municipal de Serviços Urbanos (EMSURB)**. A iniciativa busca ampliar o aproveitamento de resíduos orgânicos provenientes de mercados, feiras e outros estabelecimentos, direcionando-os para processos de compostagem.

Nesse contexto, o presente projeto propõe o desenvolvimento de uma ferramenta de Inteligência Artificial que possa atuar como uma camada de apoio à identificação e à separação dos resíduos, contribuindo para as etapas iniciais de sua destinação.

A proposta consiste em utilizar técnicas de Visão Computacional e Aprendizado de Máquina, por meio do modelo **YOLO (You Only Look Once)**, para identificar diferentes categorias de resíduos a partir de imagens. O sistema não se limitará aos resíduos orgânicos: ele deverá reconhecer qualquer tipo de lixo contemplado nas categorias definidas (como papel, papelão, plástico, metal, vidro, rejeitos e resíduos orgânicos) e, a partir da classificação realizada, indicar se o material é lixo orgânico ou lixo comum, apresentando uma sugestão de destinação adequada — a compostagem, no caso dos resíduos orgânicos.

---

## 2. Justificativa
A correta separação dos resíduos é fundamental para possibilitar seu reaproveitamento e reduzir o volume destinado ao descarte convencional. No contexto do BioCiclo Urbano, a identificação adequada dos resíduos pode contribuir para que materiais com potencial de aproveitamento sejam direcionados corretamente aos processos de compostagem.

Entretanto, os resíduos gerados em feiras, mercados e residências raramente chegam separados: materiais orgânicos costumam estar misturados a plásticos, papéis, metais e vidros. Por isso, uma ferramenta que reconheça diferentes tipos de lixo, e não apenas o orgânico, é mais útil na prática, pois permite distinguir o que deve seguir para a compostagem do que deve ser encaminhado como lixo comum.

---

## 3. Tabela de Categorias e Destinação Proposta

| Categoria | Tipo de Lixo | Sugestão de Destinação |
| :--- | :--- | :--- |
| **Orgânico** | Orgânico | Compostagem (BioCiclo Urbano) |
| **Papel** | Comum / Reciclável | Coleta seletiva / reciclagem |
| **Papelão** | Comum / Reciclável | Coleta seletiva / reciclagem |
| **Plástico** | Comum / Reciclável | Coleta seletiva / reciclagem |
| **Metal** | Comum / Reciclável | Coleta seletiva / reciclagem |
| **Vidro** | Comum / Reciclável | Coleta seletiva / reciclagem |
| **Rejeito (trash)** | Comum / Rejeito | Coleta convencional / aterro sanitário |
