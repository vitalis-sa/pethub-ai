import json
import re
import google.generativeai as genai
from app.core.config import settings

# Configura a chave da API
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"


async def generate_consultation_documents(transcricao: str, pet_data: dict) -> dict:
    """
    Recebe a transcrição completa de uma consulta e os dados do pet,
    e retorna { anamnese, receitaMedica, auxilioDiagnostico, vacinasIdentificadas }.

    - anamnese: documento clínico estruturado em markdown
    - receitaMedica: exames, remédios e vacinas prescritos (markdown)
    - auxilioDiagnostico: insights para o veterinário — NÃO é um diagnóstico
    - vacinasIdentificadas: lista de vacinas mencionadas na consulta (para salvar no pet)
    """
    if not settings.GEMINI_API_KEY:
        return {
            "anamnese": "⚠️ API Key não configurada.",
            "receitaMedica": "⚠️ API Key não configurada.",
            "auxilioDiagnostico": "⚠️ API Key não configurada.",
            "vacinasIdentificadas": [],
        }

    nome_pet = pet_data.get("nome", "paciente")
    especie = pet_data.get("especie", "animal")
    raca = pet_data.get("raca", "")
    idade = pet_data.get("idade", "")
    peso = pet_data.get("peso", "")

    prompt = f"""Você é um assistente clínico veterinário especializado em documentação médica.
Analise a transcrição abaixo de uma consulta veterinária e gere TRÊS documentos separados.

**Dados do Paciente:**
- Nome: {nome_pet}
- Espécie: {especie}
- Raça: {raca}
- Idade: {idade} anos
- Peso: {peso} kg

**Transcrição da consulta:**
{transcricao}

---

Retorne APENAS um JSON válido com exatamente esta estrutura (sem texto fora do JSON):

{{
  "anamnese": "...",
  "receitaMedica": "...",
  "auxilioDiagnostico": "...",
  "vacinasIdentificadas": ["...", "..."]
}}

**Instruções para cada campo:**

### anamnese
Documento de anamnese clínica estruturado em markdown. Inclua as seções:
- **Motivo da Consulta**: queixa principal relatada pelo tutor
- **Histórico Clínico**: informações relevantes do histórico mencionadas
- **Exame Físico**: achados do exame físico mencionados pelo veterinário
- **Sinais e Sintomas**: sintomas identificados na consulta
- **Observações**: outras informações relevantes

### receitaMedica
Receita médica veterinária em markdown com as seções que se aplicarem:
- **Medicamentos Prescritos**: nome, dosagem, frequência, duração
- **Exames Solicitados**: nome do exame e justificativa
- **Vacinas Indicadas**: vacinas mencionadas ou recomendadas

### auxilioDiagnostico
⚠️ IMPORTANTE: Este campo é um AUXÍLIO para o veterinário, NÃO um diagnóstico.
Escreva insights e considerações clínicas em markdown, começando sempre com o aviso:
> ⚠️ Este é um auxílio da IA para o veterinário. A decisão diagnóstica é exclusivamente do profissional.

Depois apresente:
- **Considerações Clínicas**: padrões ou achados relevantes da transcrição
- **Diagnósticos Diferenciais a Considerar**: possibilidades a investigar (nunca afirme)
- **Pontos de Atenção**: alertas clínicos relevantes

### vacinasIdentificadas
Array de strings com os nomes das vacinas mencionadas na consulta (para registro no prontuário).
Se nenhuma vacina foi mencionada, retorne array vazio [].

Retorne APENAS o JSON, sem markdown em volta, sem blocos de código.
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=4000,
            ),
        )

        text = response.text.strip()
        # Remove possíveis blocos de código markdown
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        parsed = json.loads(text)
        return {
            "anamnese": parsed.get("anamnese", ""),
            "receitaMedica": parsed.get("receitaMedica", ""),
            "auxilioDiagnostico": parsed.get("auxilioDiagnostico", ""),
            "vacinasIdentificadas": parsed.get("vacinasIdentificadas", []),
        }

    except json.JSONDecodeError as e:
        print(f"[ai_service] Erro ao parsear JSON da IA: {e}\nResposta: {text[:500]}")
        return {
            "anamnese": "Erro ao gerar anamnese. Verifique a transcrição.",
            "receitaMedica": "Erro ao gerar receita médica.",
            "auxilioDiagnostico": "Erro ao gerar auxílio diagnóstico.",
            "vacinasIdentificadas": [],
        }
    except Exception as e:
        print(f"[ai_service] Erro na geração de documentos: {e}")
        return {
            "anamnese": f"Erro: {str(e)}",
            "receitaMedica": f"Erro: {str(e)}",
            "auxilioDiagnostico": f"Erro: {str(e)}",
            "vacinasIdentificadas": [],
        }


async def extract_exam_summary(file_bytes: bytes, mime_type: str) -> str:
    """
    Usa o Gemini Vision para ler um PDF ou imagem de exame e extrair
    um resumo técnico do laudo.
    """
    if not settings.GEMINI_API_KEY:
        return "Simulação de laudo de IA (API KEY ausente)."

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = (
            "Você é um assistente veterinário. Leia o exame laboratorial ou imagem médica "
            "anexado e retorne um RESUMO TÉCNICO CURTO. Para exames de imagem, descreva o laudo. "
            "Para exames de análises clínicas, liste os resultados no formato: "
            "NOME DO EXAME: VALOR - STATUS (ex: HEMOGLOBINA: 12g/dL - ABAIXO DO RECOMENDADO). "
            "Seja direto e objetivo. Não invente dados."
        )

        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": file_bytes},
        ])

        return response.text.strip()

    except Exception as e:
        print(f"[ai_service] Erro na extração de exame via IA: {e}")
        return f"Erro ao processar exame: {str(e)}"
