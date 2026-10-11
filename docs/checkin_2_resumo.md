# Check-in 2: Demonstração da Fonte de Dados e Modelo Previsto

**Instituição:** Universidade Federal de Sergipe (UFS)  
**Departamento:** Departamento de Computação (DComp)  
**Disciplina:** Fundamentos da Inteligência Artificial  

---

## 1. Fonte de Dados Selecionada

### Base Principal: GARBAGE CLASSIFICATION 3 (GC1) v2
- **Autor/Origem:** Material Identification, disponível no Roboflow Universe.
- **Formato:** Detecção de objetos YOLO (`classe centro_x centro_y largura altura`).
- **Dimensão:** 10.464 imagens com anotações espaciais.
- **Licença:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Classes Informadas (7):**
  1. `BIODEGRADABLE` (Orgânico/Biodegradável)
  2. `CARDBOARD` (Papelão)
  3. `CLOTH` (Tecido/Têxtil)
  4. `GLASS` (Vidro)
  5. `METAL` (Metal)
  6. `PAPER` (Papel)
  7. `PLASTIC` (Plástico)

### Fonte Secundária / Alternativa:
- **TrashNet** (Stanford - Gary Thung & Mindy Yang): 2.500 imagens em 6 classes (`glass`, `paper`, `cardboard`, `plastic`, `metal`, `trash`).
- **Organic Waste Computer Vision Dataset** (Roboflow): Para reforçar a classe orgânica.

---

## 2. Modelo e Algoritmo Previsto
- **Arquitetura:** YOLO nano (`yolo11n` ou `yolov8n`), pré-treinado em COCO.
- **Abordagem de Treinamento:** Aprendizado Supervisionado por Transferência (*Transfer Learning / Fine-Tuning*).
- **Saídas por Objeto:** Caixa delimitadora (bounding box), classe prevista e nível de confiança.
- **Tratamento de Incerteza:** Se a confiança for menor que o limiar estipulado (ex: 50%), o sistema não fornece decisão categórica, solicitando nova foto.

---

## 3. Métricas de Avaliação
- Precisão (*Precision*)
- Revocação (*Recall*)
- mAP@50 e mAP@50:95
- Matriz de Confusão por classe

---

## 4. Entregável Prático (MVP)
Protótipo interativo desenvolvido em **Streamlit**, permitindo:
1. Envio de fotografia (ou webcam);
2. Destaque do resíduo e exibição da probabilidade;
3. Indicação se é Lixo Orgânico ou Lixo Comum;
4. Sugestão clara de destinação (Compostagem BioCiclo Urbano, Coleta Seletiva, etc.).
