# Guia de Colaboração para a Equipe (Git & Desenvolvimento)

Este guia serve para orientar todos os colegas do grupo a clonar, configurar e contribuir com o projeto de forma organizada.

---

## 🚀 1. Configurando o Ambiente pela Primeira Vez

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/jpasx/biociclo-ia.git
cd biociclo-ia
```

### Passo 2: Criar e Ativar o Ambiente Virtual (Python)
No Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

No Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar as Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configurar o Arquivo de Ambiente (.env)
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
(No Windows PowerShell: `copy .env.example .env`)

---

## 💻 2. Executando a Aplicação Web (Streamlit)

Para testar a interface gráfica interativa do projeto:
```bash
streamlit run app/main.py
```
O navegador abrirá automaticamente no endereço `http://localhost:8501`.

---

## 🗂️ 3. Baixando o Dataset Oficial
Para baixar o dataset completo do Roboflow Universe (GC1):
1. Adicione sua chave gratuita do Roboflow no arquivo `.env` (`ROBOFLOW_API_KEY=sua_chave`).
2. Execute o comando:
```bash
python -m src.data.download_dataset
```

---

## 🧠 4. Treinando o Modelo YOLO
Para rodar o fine-tuning com os dados baixados:
```bash
python -m src.training.train_yolo --epochs 50 --batch 16 --device cpu
```
*(Se você possuir placa de vídeo NVIDIA com CUDA, troque `--device cpu` por `--device 0`)*

Ao término do treino, o arquivo com os melhores pesos (`best.pt`) será copiado automaticamente para `models/weights/best.pt`, e a aplicação Streamlit passará a utilizá-lo!

---

## 🌿 5. Boas Práticas de Trabalho em Equipe com Git

Para evitar conflitos de código (*merge conflicts*):

1. **Nunca faça commits diretamente na branch `main`!**
2. Crie uma branch para cada tarefa:
   ```bash
   git checkout -b feature/nome-da-sua-tarefa
   ```
3. Faça suas alterações e commite com mensagens descritivas:
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   ```
4. Envie sua branch para o GitHub:
   ```bash
   git push origin feature/nome-da-sua-tarefa
   ```
5. Abra um **Pull Request (PR)** no GitHub para que os outros colegas possam revisar antes de mesclar na `main`.
