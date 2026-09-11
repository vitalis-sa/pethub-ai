# CLYVO VET — Componente de Inteligência Artificial Generativa

Documentação técnica do componente de IA do projeto **PetHub** para a CLYVO, desenvolvido para o Sprint 3 da disciplina **Disruptive Architectures: IoT, IoB & Generative AI** — FIAP.

## Grupo
| Nome | RM | Turma |
|---|---|---|
| Ana Flávia Camelo | RM561489 | 2TDSPV |
| Gustavo Kenji Terada | RM562745 | 2TDSPV |
| João Guilherme Carvalho Novaes | RM566234 | 2TDSPV |
| Pedro Chasci Puga | RM565154 | 2TDSPV |
| Lucas Figueiredo Vieira | RM561342 | 2TDSPV |

---


## Links e Repositórios
O ecossistema PetHub é descentralizado em diferentes serviços. Acesse os repositórios abaixo:

* **Backend Veterinário (Java / Spring Boot):** [[Link do Repo Java](https://github.com/vitalis-sa/pethub-java)]
* **Backend Responsável (C# / .NET):** [[Link do Repo C#](https://github.com/vitalis-sa/PetHub-.NET)]
* **Orquestração de Agentes (n8n):** [[Link do n8n](https://afcamelo.app.n8n.cloud/workflow/bRvrj0arRA6AjDco)]

> **📌 Nota sobre o código-fonte de Inteligência Artificial:**
> Não possuímos um repositório isolado contendo "apenas o código da IA". A inteligência artificial foi projetada como uma ferramenta core do sistema e, portanto, está embarcada diretamente na nossa arquitetura. Toda a lógica de montagem de prompts, integração com o SDK do Google Gemini e conversão das respostas estruturadas reside dentro do repositório do **Backend Java** e nos nós do **n8n**. Este repositório atual (pethub-ia) concentra exclusivamente a documentação arquitetural.
> 
> **🧪 Protótipo em Python (ai_service.py):**
> Junto a esta documentação, disponibilizamos o arquivo ai_service.py como uma **Prova de Conceito (PoC) / Protótipo**. Este script foi desenvolvido para validar a lógica de negócios da IA — incluindo a engenharia de prompts, injeção de contexto e formatação do JSON de saída do Gemini. Todo o fluxo funcional desenhado neste arquivo Python serve como base arquitetural e será traduzido e migrado nativamente para o Backend Java (GeminiService) nas próximas iterações.

---
## 1. Problemática
O mercado pet brasileiro enfrenta um gap estrutural: o tutor aciona a clínica quase exclusivamente em urgências ou gatilhos pontuais como vacinação. Isso resulta em baixa recorrência de consultas preventivas, menor LTV por animal e ausência de um histórico clínico longitudinal estruturado entre clínica e responsável.

Somado a isso, as informações clínicas do pet ficam dispersas, como prontuários em papel, dados fragmentados entre clínicas, impedindo uma visão contínua da saúde do animal.

---

## 2. Solução
O PetHub é uma plataforma digital de cuidado veterinário contínuo que conecta responsáveis, veterinários e clínicas em uma jornada inteligente de saúde animal, desde o agendamento ao prontuário gerado por IA.

O diferencial central da solução é a IA que atua dentro do atendimento clínico real. O sistema transcreve a consulta em tempo real, analisa o contexto clínico do paciente e gera automaticamente os documentos médicos para revisão do veterinário, diminuindo o trabalho manual feito para o preenchimento de documentos.

Diferente de chatbots genéricos, temos um chatbot exclusivo para cada pet, que busca informações do histórico do paciente para trazer um auxílio mais preciso ao veterinário.

A plataforma opera sobre três pilares:
*   **Preventivo:** controle de vacinas, tratamentos e consultas, com lembretes automáticos via WhatsApp gerados a partir do encaminhamento do veterinário.
*   **Terapêutico:** histórico clínico completo centralizado: consultas, exames, diagnósticos e pedidos médicos acessíveis para tutor e veterinário a qualquer momento.
*   **IA Generativa na consulta:** o veterinário fala, o sistema transcreve. O Agente LLM analisa a transcrição junto aos dados reais do pet (espécie, raça, idade, peso) e retorna três documentos prontos para revisão: anamnese estruturada, receita médica com medicamentos e exames e um texto de auxílio ao diagnóstico com hipóteses clínicas. Nenhum documento é persistido sem confirmação do veterinário.

### 2.1 Abordagem de IA Adotada e Justificativa Técnica
A abordagem adotada é IA Generativa com LLM (Large Language Model), utilizando o Google Gemini como modelo de linguagem.

Outras abordagens foram consideradas e descartadas. O ML preditivo com modelo treinado exigiria um dataset clínico veterinário rotulado de grande volume, que não existe publicamente (apenas datasets com pouco volume de dados), tornando essa abordagem inviável para um MVP. O sistema de regras não lida com a variabilidade natural do discurso médico em texto livre e é incapaz de interpretar contexto clínico complexo. O NLP clássico identifica entidades isoladas mas não consegue redigir documentos médicos estruturados sem um pipeline customizado extenso.

A IA Generativa resolve todos esses problemas nativamente: compreende linguagem natural médica em português, estrutura documentos clínicos completos, raciocina sobre diagnósticos diferenciais e opera sem necessidade de dados de treinamento próprios. É a abordagem ideal para MVP.

O Google Gemini foi escolhido por sua velocidade e custo adequados ao volume de tokens de uma transcrição de consultas, pelo suporte multimodal que permite análise de PDFs e imagens de exames, pela facilidade de integração via SDK com o backend Java e via node nativo no n8n, e pela infraestrutura GCP que está sendo usada no projeto.

### 2.2 Contribuição da IA para a Solução
A Inteligência Artificial contribui para a solução atuando de forma integrada na personalização, no apoio à decisão e na recomendação de serviços. A personalização ocorre através da geração dinâmica de documentos embasados nos dados reais do paciente, considerando informações como espécie, raça, idade, peso e a transcrição exata da consulta. No que diz respeito ao apoio à decisão, o modelo fornece um auxílio diagnóstico ao veterinário, levantando hipóteses clínicas e destacando pontos de atenção com base no contexto do atendimento. Por fim, a IA otimiza a recomendação de serviços ao identificar automaticamente vacinas e exames mencionados durante a fala, garantindo que sejam incluídos diretamente na receita médica gerada.

### 2.3 Jornada do Usuário
Para ilustrar a experiência prática com a plataforma, o diagrama a seguir mapeia a Jornada do Usuário, detalhando as interações simultâneas entre o Tutor e o Veterinário.

O fluxo demonstra como o sistema conecta os dois perfis em um ciclo contínuo de cuidado: a jornada inicia-se no acompanhamento e agendamento pelo tutor, passa pelo atendimento clínico, onde a Inteligência Artificial atua nos bastidores transcrevendo o áudio e gerando a documentação médica para revisão do profissional, e se encerra com o envio de lembretes preventivos e personalizados de volta ao tutor via WhatsApp, fechando o ciclo de engajamento e saúde do pet.

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de jornada do usuário] -->
![Diagrama de jornada do usuário](./jornada-usuario.png)

---

## 3. Arquitetura da Solução
A solução é composta por três camadas principais.
A camada de apresentação é o App Mobile em React Native, que serve tanto o tutor quanto o veterinário. É nessa camada que ocorre a gravação do áudio da consulta e a transcrição via Speech-to-Text nativo do dispositivo.
A camada de aplicação contém três serviços: o Backend Responsável em .NET, responsável pelas regras de negócio do tutor, como agendamento, lembretes e histórico; o Backend Veterinário em Java com Spring Boot, responsável pelas regras clínicas, gerenciamento de prontuários e pela integração com o Agente LLM para geração de documentos; e o n8n, que opera como agente de chat diagnóstico, recebendo mensagens do veterinário via Webhook, buscando dados do pet no MongoDB e chamando o Gemini para gerar insights diagnósticos.
A camada de persistência é o MongoDB, banco de dados único compartilhado pelos dois backends, onde são armazenados todos os dados clínicos: pets, consultas, diagnósticos, exames, vacinas, lembretes e prontuários.

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de arquitetura de componentes] -->
![Diagrama de arquitetura de componentes](./arquitetura-componentes.png)

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de arquitetura de integração] -->
![Diagrama de arquitetura de integração](./arquitetura-integracao.png)

### 3.1 Fluxo de Dados: Geração de Documentos por Consulta
O fluxo de geração de documentos com IA começa no app mobile, quando o veterinário inicia uma consulta presencial ou teleconsulta. O app grava o áudio do atendimento e realiza a transcrição localmente via Speech-to-Text nativo do dispositivo.

A transcrição em texto é enviada para o Backend do Veterinário (Java/Spring Boot). O backend busca os dados do pet no MongoDB — espécie, raça, idade e peso — e monta um prompt contextualizado combinando a transcrição com esses dados. Esse prompt é enviado ao Agente LLM (Gemini), que analisa o contexto clínico e retorna quatro documentos estruturados: a anamnese com o relato clínico organizado, a receita médica com medicamentos, exames e vacinas, o auxílio ao diagnóstico com hipóteses clínicas e pontos de atenção, e a lista de vacinas identificadas na consulta.

Os documentos retornam para o app, onde o veterinário revisa, edita se necessário e confirma. Somente após a confirmação os documentos são salvos no MongoDB, atualizando o prontuário e o histórico do pet.

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de fluxo de dados do App Mobile] -->
![Diagrama de fluxo de dados do App Mobile](./fluxo-app-mobile.png)

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de fluxo de dados do backend do Veterinário] -->
![Diagrama de fluxo de dados do backend do Veterinário](./fluxo-backend-veterinario.png)

#### 3.1.1 Dados Utilizados pela IA Para a Geração de Documentos
Para garantir personalização real, precisamos dos dados anteriores do pet. A dosagem de medicamentos na receita usa o peso; o auxílio diagnóstico usa a espécie e predisposições da raça. Então utilizamos:
1. Transcrição de áudio: Input principal (texto livre).
2. Dados do pet (MongoDB): Espécie, raça, idade, peso e histórico.

### 3.2 Fluxo de Dados: Chat Diagnóstico com n8n
O chat diagnóstico opera de forma independente do fluxo de consulta. O veterinário envia uma mensagem pelo chatbot no app mobile. Essa mensagem é recebida pelo n8n via Webhook.

Dentro do n8n, o agente busca os dados do pet diretamente no MongoDB para contextualizar a conversa. Com os dados do pet e a mensagem do veterinário, monta um prompt contextualizado e o envia ao Gemini via node nativo do n8n. O Gemini gera uma resposta com insights diagnósticos, que é retornada ao veterinário pelo chatbot.

Todo o processamento ocorre dentro do n8n, sem passar pelo Backend do Veterinário.

<!-- [COLOQUE A IMAGEM ABAIXO: Diagrama de fluxo de dados da integração n8n] -->
![Diagrama de fluxo de dados da integração n8n](./fluxo-n8n.png)

<!-- [COLOQUE A IMAGEM ABAIXO: Fluxo do n8n Print] -->
![Fluxo do n8n](./print-n8n.png)

#### 3.2.1 Dados Utilizados pela IA Para o Chat Diagnóstico
Para permitir que o veterinário faça perguntas baseadas no contexto longitudinal real do animal, não em um modelo genérico, usamos:
*   **Histórico Clínico (MongoDB):** Consultas anteriores, diagnósticos, vacinas, exames e lembretes ativos.


