import base64
import re
from io import BytesIO
from pathlib import Path

import streamlit as st
from openai import OpenAI
from PIL import Image


client = OpenAI()


# =========================================================
# CONFIGURAÇÃO
# =========================================================

AVATAR_SOMMINHA = "mascote_avatar.png"
AVATAR_CLIENTE = "avatar_cliente.png"


st.set_page_config(
    page_title="Assistente Virtual Somma Rio",
    page_icon=AVATAR_SOMMINHA,
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# LOGO PARA MARCA D'ÁGUA
# =========================================================

def criar_logo_transparente(caminho):
    arquivo = Path(caminho)

    if not arquivo.exists():
        return ""

    imagem = Image.open(arquivo).convert("RGBA")
    pixels = imagem.load()

    for y in range(imagem.height):
        for x in range(imagem.width):

            r, g, b, a = pixels[x, y]

            brilho = (r + g + b) / 3

            if brilho > 180:

                alpha = int(
                    min(
                        255,
                        max(
                            0,
                            (brilho - 180) * 3.4
                        )
                    )
                )

                pixels[x, y] = (
                    255,
                    255,
                    255,
                    alpha
                )

            else:

                pixels[x, y] = (
                    r,
                    g,
                    b,
                    0
                )

    buffer = BytesIO()

    imagem.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode()


logo_base64 = criar_logo_transparente(
    "logo_somma.png"
)


# =========================================================
# CSS SOMMA
# =========================================================

st.markdown(
    f"""
<style>

/* FUNDO */

.stApp {{
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(0, 142, 255, 0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 100% 0%,
            rgba(0, 224, 165, 0.08),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #080d12 0%,
            #090f15 100%
        );

    color: #ffffff;
}}


/* MARCA D'ÁGUA */

.stApp::before {{
    content: "";

    position: fixed;

    width: 380px;
    height: 380px;

    left: 50%;
    top: 59%;

    transform:
        translate(-50%, -50%);

    background-image:
        url("data:image/png;base64,{logo_base64}");

    background-repeat:
        no-repeat;

    background-position:
        center;

    background-size:
        contain;

    opacity:
        0.017;

    pointer-events:
        none;

    z-index:
        0;
}}


/* REMOVE ELEMENTOS STREAMLIT */

[data-testid="stHeader"] {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
}}

[data-testid="stToolbar"] {{
    display: none !important;
}}

[data-testid="stDecoration"] {{
    display: none !important;
}}

header {{
    display: none !important;
    height: 0 !important;
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}


/* ÁREA PRINCIPAL */

.block-container {{
    position: relative;

    z-index: 1;

    max-width: 980px;

    padding-top:
        0.25rem !important;

    padding-bottom:
        4.5rem !important;
}}


[data-testid="stMainBlockContainer"] {{
    padding-top:
        0.25rem !important;
}}


/* ESPAÇAMENTOS */

[data-testid="stVerticalBlock"] {{
    gap: 0.55rem;
}}


[data-testid="stHorizontalBlock"] {{
    gap: 0.75rem;
}}


/* TÍTULO */

h1 {{
    font-size:
        1.95rem !important;

    font-weight:
        760 !important;

    letter-spacing:
        -0.7px !important;

    margin-top:
        0 !important;

    margin-bottom:
        0.05rem !important;

    line-height:
        1.05 !important;
}}


[data-testid="stCaptionContainer"] {{
    color:
        #8594a3;

    font-size:
        0.88rem;

    margin-top:
        0.10rem !important;
}}


/* DIVISÓRIA */

hr {{
    border:
        none !important;

    height:
        1px !important;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(0, 218, 180, 0.24),
            transparent
        ) !important;

    margin-top:
        0.30rem !important;

    margin-bottom:
        0.55rem !important;
}}


/* BOTÃO */

.stButton > button {{
    width:
        100%;

    min-height:
        40px;

    border-radius:
        12px;

    border:
        1px solid
        rgba(0, 220, 185, 0.24);

    background:
        linear-gradient(
            90deg,
            #078ef4 0%,
            #08cbb0 100%
        );

    color:
        white;

    font-weight:
        650;

    box-shadow:
        0 8px 24px
        rgba(0, 160, 180, 0.10);

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease;
}}


.stButton > button:hover {{
    color:
        white;

    transform:
        translateY(-1px);

    box-shadow:
        0 10px 30px
        rgba(0, 190, 180, 0.18);

    border:
        1px solid
        rgba(255,255,255,0.15);
}}


/* CHAT */

[data-testid="stChatMessage"] {{
    border-radius:
        18px;

    padding:
        12px 15px;

    margin-top:
        0 !important;

    margin-bottom:
        7px !important;

    background:
        rgba(15, 23, 31, 0.64);

    border:
        1px solid
        rgba(255,255,255,0.055);

    backdrop-filter:
        blur(9px);

    box-shadow:
        0 8px 28px
        rgba(0,0,0,0.10);
}}


/* AVATAR */

[data-testid="stChatMessage"] img {{
    border-radius:
        50%;

    box-shadow:
        0 5px 18px
        rgba(0, 205, 190, 0.14);
}}


/* INDICADOR DE DIGITAÇÃO */

.somminha-typing-wrapper {{
    width: 100%;
    margin: 4px 0 10px 0;
}}

.somminha-typing {{
    width: 54px;
    height: 36px;

    display: flex;
    align-items: center;
    justify-content: center;

    gap: 5px;

    background:
        rgba(11, 21, 28, 0.96);

    border:
        1px solid
        rgba(0, 210, 190, 0.14);

    border-radius:
        18px;

    box-shadow:
        0 8px 24px
        rgba(0,0,0,0.16);
}}

.somminha-typing span {{
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background:
        #08cbb0;

    opacity: 0.28;

    animation:
        somminhaTyping 1.15s infinite ease-in-out;
}}

.somminha-typing span:nth-child(1) {{
    animation-delay: 0s;
}}

.somminha-typing span:nth-child(2) {{
    animation-delay: 0.16s;
}}

.somminha-typing span:nth-child(3) {{
    animation-delay: 0.32s;
}}

@keyframes somminhaTyping {{

    0%,
    60%,
    100% {{
        opacity: 0.25;
        transform: translateY(0);
    }}

    30% {{
        opacity: 1;
        transform: translateY(-2px);
    }}
}}


/* INPUT PERSONALIZADO */

[data-testid="stChatInput"] {{
    background:
        rgba(9, 18, 26, 0.97) !important;

    border:
        1.5px solid
        rgba(0, 214, 201, 0.72) !important;

    border-radius:
        22px !important;

    outline:
        none !important;

    overflow:
        hidden !important;

    box-shadow:
        0 0 0 1px rgba(0, 214, 201, 0.05),
        0 0 24px rgba(0, 214, 201, 0.08),
        0 14px 36px rgba(0,0,0,0.28) !important;

    transition:
        border-color 0.18s ease,
        box-shadow 0.18s ease !important;

    padding:
        0 !important;
}}


[data-testid="stChatInput"]:focus-within {{
    border:
        1.5px solid
        rgba(0, 231, 220, 0.95) !important;

    outline:
        none !important;

    box-shadow:
        0 0 0 1px rgba(0, 231, 220, 0.08),
        0 0 30px rgba(0, 231, 220, 0.14),
        0 14px 36px rgba(0,0,0,0.30) !important;
}}


[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div {{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    border-radius: 22px !important;
    margin: 0 !important;
}}


[data-testid="stChatInput"] > div {{
    padding: 0 !important;
}}


[data-testid="stChatInput"] > div > div {{
    padding:
        7px 9px 7px 16px !important;

    min-height:
        62px !important;

    display:
        flex !important;

    align-items:
        center !important;
}}


[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="input"],
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"] > div,
[data-testid="stChatInput"] [data-baseweb="input"] > div,
[data-testid="stChatInput"] [data-baseweb="base-input"] > div {{
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}}


[data-testid="stChatInput"] [data-baseweb="textarea"]:focus,
[data-testid="stChatInput"] [data-baseweb="textarea"]:focus-within,
[data-testid="stChatInput"] [data-baseweb="input"]:focus,
[data-testid="stChatInput"] [data-baseweb="input"]:focus-within,
[data-testid="stChatInput"] [data-baseweb="base-input"]:focus,
[data-testid="stChatInput"] [data-baseweb="base-input"]:focus-within {{
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}}


[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:focus-visible,
[data-testid="stChatInput"] input,
[data-testid="stChatInput"] input:focus,
[data-testid="stChatInput"] input:focus-visible {{
    color: #ffffff !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}}


[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {{
    color:
        rgba(210, 223, 232, 0.55) !important;
}}


[data-testid="stChatInput"] *,
[data-testid="stChatInput"] *::before,
[data-testid="stChatInput"] *::after {{
    outline-color:
        transparent !important;
}}


/* BOTÃO ENVIAR */

[data-testid="stChatInput"] button {{
    min-width:
        88px !important;

    width:
        88px !important;

    height:
        46px !important;

    min-height:
        46px !important;

    border-radius:
        15px !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.08) !important;

    background:
        linear-gradient(
            90deg,
            #078ef4 0%,
            #08cbb0 100%
        ) !important;

    outline:
        none !important;

    box-shadow:
        0 8px 22px
        rgba(0, 175, 220, 0.18) !important;

    display:
        flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    padding:
        0 16px !important;

    margin-right:
        1px !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease !important;
}}


[data-testid="stChatInput"] button:hover {{
    transform:
        translateY(-1px) !important;

    filter:
        brightness(1.06) !important;

    box-shadow:
        0 10px 26px
        rgba(0, 190, 220, 0.26) !important;
}}


[data-testid="stChatInput"] button:disabled {{
    opacity:
        0.52 !important;

    transform:
        none !important;

    box-shadow:
        0 5px 16px
        rgba(0, 160, 200, 0.10) !important;
}}


[data-testid="stChatInput"] button svg {{
    display:
        none !important;
}}


[data-testid="stChatInput"] button::before {{
    content:
        "Enviar";

    display:
        block;

    color:
        #f4fdff;

    font-size:
        0.92rem;

    font-weight:
        650;

    letter-spacing:
        0.1px;
}}


[data-testid="stBottomBlockContainer"] {{
    padding-bottom:
        2.1rem !important;
}}


/* MÉTRICAS */

[data-testid="stMetric"] {{
    background:
        linear-gradient(
            145deg,
            rgba(16, 26, 34, 0.96),
            rgba(11, 22, 29, 0.96)
        );

    border:
        1px solid
        rgba(0, 210, 180, 0.13);

    padding:
        18px;

    border-radius:
        17px;

    box-shadow:
        0 10px 28px
        rgba(0,0,0,0.18);
}}


/* BARRA DE PROGRESSO */

[data-testid="stProgress"] {{
    margin-top:
        0.35rem !important;

    margin-bottom:
        0.45rem !important;
}}

[data-testid="stProgress"] > div {{
    height:
        10px !important;

    background:
        rgba(255, 255, 255, 0.08) !important;

    border-radius:
        999px !important;

    overflow:
        hidden !important;

    box-shadow:
        inset 0 0 0 1px
        rgba(255, 255, 255, 0.025) !important;
}}

[data-testid="stProgress"] > div > div {{
    background:
        linear-gradient(
            90deg,
            #2b8ef8 0%,
            #1fd1be 100%
        ) !important;

    border-radius:
        999px !important;

    box-shadow:
        0 0 10px rgba(43, 142, 248, 0.22),
        0 0 18px rgba(31, 209, 190, 0.12) !important;

    transition:
        width 0.35s ease !important;
}}


/* EXPANDER */

[data-testid="stExpander"] {{
    border:
        1px solid
        rgba(0, 210, 180, 0.12);

    border-radius:
        15px;

    background:
        rgba(11, 20, 27, 0.90);

    overflow:
        hidden;
}}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# MENSAGEM INICIAL
# =========================================================

MENSAGEM_INICIAL = (
    "Olá! Eu sou o **Somminha**, assistente virtual da **Somma Rio**. "
    "Antes de continuarmos, como posso te chamar?"
)


# =========================================================
# ESTADO
# =========================================================

if "mensagens" not in st.session_state:

    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": MENSAGEM_INICIAL
        }
    ]


# =========================================================
# CABEÇALHO
# =========================================================

col_logo, col_titulo, col_botao = st.columns(
    [0.65, 5.5, 1.65],
    vertical_alignment="center"
)


with col_logo:

    st.image(
        AVATAR_SOMMINHA,
        width=58
    )


with col_titulo:

    st.title(
        "Assistente Virtual Somma Rio"
    )

    st.caption(
        "Inteligência comercial • Qualificação de oportunidades imobiliárias"
    )


with col_botao:

    if st.button(
        "＋ Nova conversa",
        use_container_width=True
    ):

        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": MENSAGEM_INICIAL
            }
        ]

        if "resumo_corretor" in st.session_state:
            del st.session_state.resumo_corretor

        st.rerun()


st.divider()


# =========================================================
# INTELIGÊNCIA DO SOMMINHA
# =========================================================

INSTRUCOES = """
Você é o Somminha, assistente virtual de pré-atendimento e
qualificação de leads da Somma Rio, uma imobiliária do Rio de Janeiro.

PRINCÍPIO:
O SOMMINHA QUALIFICA.
O CORRETOR ATENDE.
O CORRETOR VENDE.

Você não é corretor.

Não faça:
- consultoria imobiliária
- negociação
- proposta
- agendamento de visita
- análise financeira
- solicitação de telefone
- solicitação de WhatsApp
- solicitação de documentos

Sua função é:
- entender o motivo do contato
- interpretar o que o cliente já informou
- fazer poucas perguntas úteis
- identificar quando o cliente quer continuar falando
- identificar quando o cliente quer parar de responder
- organizar o lead
- calcular o score
- entregar contexto para o corretor

=========================================================
ABERTURA DEPOIS DO NOME
=========================================================

Depois que o cliente disser o nome,
NÃO comece com uma lista fechada como:

"Você quer comprar, alugar ou investir?"

Isso é inadequado porque "investir" é objetivo,
enquanto comprar ou alugar são formas de operação.

Prefira uma pergunta aberta e natural.

Exemplo recomendado:

"Prazer, Pedro. Me conta: o que te trouxe até a Somma Rio
e em qual região ou empreendimento você tem interesse?"

Outra possibilidade:

"Prazer, Pedro. Me conta um pouco do que você está buscando."

A intenção é permitir que o cliente fale naturalmente
e entregue várias informações de uma vez.

Depois extraia tudo antes de perguntar novamente.

=========================================================
REGRA PRINCIPAL
=========================================================

O CLIENTE FALA COMO CLIENTE.
O SOMMINHA ORGANIZA COMO SISTEMA.

Antes de perguntar:

1. leia TODO o histórico
2. extraia tudo que já foi informado
3. identifique o motivo do contato
4. identifique o que realmente ainda importa
5. veja o que você já perguntou
6. observe se alguma pergunta foi ignorada
7. avalie a abertura do cliente
8. só depois decida se deve perguntar novamente

Nunca pergunte algo que já foi informado.

Aceite informações aproximadas.

Aceite linguagem informal.

=========================================================
REGRA CRÍTICA — NÃO REPITA PERGUNTA IGNORADA
=========================================================

Se você fez uma pergunta
e o cliente NÃO respondeu essa pergunta,
não repita automaticamente.

Não reformule tentando obter a mesma informação.

Exemplo:

Somminha:

"Quantos quartos você procura?"

Cliente:

"Quero conhecer o imóvel primeiro."

ERRADO:

"Mas quantos quartos você procura?"

ERRADO:

"Só para confirmar, seriam quantos quartos?"

CORRETO:

interprete que o cliente quer avançar
para o atendimento comercial.

Pare de qualificar.

Encaminhe para o corretor.

=========================================================
QUANDO FIZER DUAS PERGUNTAS
=========================================================

Se fizer duas perguntas
e o cliente responder apenas uma:

não obrigue a resposta da outra.

Exemplo:

"Quantos quartos você procura?
E precisa de vaga?"

Cliente:

"2 quartos."

Registre:

Quartos:
2.

Vaga:
Não informado.

Não é obrigatório perguntar vaga novamente.

=========================================================
MUDANÇA DE DIREÇÃO DO CLIENTE
=========================================================

Algumas respostas mostram que o cliente
quer sair da etapa de qualificação.

Exemplos:

"Quero conhecer o imóvel primeiro."

"Gostaria de ver o imóvel antes."

"Prefiro conhecer primeiro."

"Quero mais informações antes."

"Queria entender melhor esse imóvel."

"Depois eu vejo isso."

"Prefiro falar disso depois."

"Primeiro quero saber mais sobre o apartamento."

"Quero falar com alguém sobre esse imóvel."

Nesses casos:

NÃO faça novas perguntas.

NÃO repita perguntas.

NÃO tente completar score.

ENCERRE A QUALIFICAÇÃO.

Gere o resumo.

O corretor assume.

=========================================================
DIFERENÇA IMPORTANTE
=========================================================

RESPOSTA CURTA:

"2 quartos."

"Barra."

"Investir."

"Até 1 milhão."

Não significa resistência.

O cliente respondeu.

Pode continuar se fizer sentido.

DESVIO OU LIMITE:

"Quero conhecer primeiro."

"Prefiro ver o imóvel."

"Depois respondo isso."

"Só quero as informações."

"Quero falar com o corretor."

Significa:

pare de perguntar.

=========================================================
NOME
=========================================================

Quando souber o nome:

- registre
- não pergunte novamente
- use ocasionalmente
- não use em toda mensagem

=========================================================
MOTIVO DO CONTATO
=========================================================

Se o cliente perguntar:

- preço
- localização
- empreendimento
- disponibilidade
- informações de anúncio

responda primeiro quando souber.

Nunca invente:

- preço
- disponibilidade
- localização
- empreendimento
- metragem
- unidade
- desconto
- condição comercial
- prazo de entrega

Quando não souber:

"Essa informação precisa ser confirmada pela nossa equipe."

Depois só continue qualificando
se o cliente estiver receptivo.

=========================================================
COMPORTAMENTO DO LEAD
=========================================================

Classifique internamente como:

COLABORATIVO
NEUTRO
RESISTENTE

COLABORATIVO:

fala mais,
explica contexto,
fornece várias informações,
acrescenta detalhes espontaneamente.

Você pode:

- aprofundar um pouco
- fazer até duas perguntas relacionadas

NEUTRO:

responde normalmente,
pode usar respostas curtas,
continua participando,
não demonstra incômodo.

Você deve:

- ser curto
- normalmente perguntar uma coisa por vez
- não prolongar

RESISTENTE:

deixa claro que não quer continuar.

Exemplos:

"Só quero o preço."

"Só me manda as informações."

"Não quero responder."

"Prefiro não passar esses dados."

"Quero falar com um corretor."

Você deve:

- não insistir
- não repetir
- responder o que puder
- encerrar

=========================================================
QUALIFICAÇÃO
=========================================================

As informações relevantes são:

1. Faixa de investimento
2. Região ou empreendimento
3. Objetivo
4. Quartos ou suítes
5. Origem / anúncio / interesse específico
6. Preferência relevante

Não é obrigatório obter todas.

Não siga ordem fixa.

Não pergunte apenas para completar campos.

=========================================================
OBJETIVO
=========================================================

Objetivo significa finalidade do imóvel.

Exemplos:

- morar
- investir
- renda
- patrimônio
- segunda residência

Não use "comprar ou investir" como alternativas,
pois uma pessoa pode comprar justamente para investir.

Pergunta adequada:

"Esse imóvel seria para morar ou investir?"

=========================================================
NÃO PERGUNTE
=========================================================

Não pergunte:

- financiamento
- recursos próprios
- entrada
- valor de entrada
- quando pretende comprar
- prazo de compra

Se surgir espontaneamente:

registre em Observações.

Não aprofunde.

Não dê pontos.

=========================================================
SCORE
=========================================================

FAIXA DE INVESTIMENTO — máximo 25

Clara:
25

Aproximada:
20

Muito vaga:
10

Não informada:
0


REGIÃO / EMPREENDIMENTO — máximo 20

Específica:
20

Duas regiões possíveis:
15

Região ampla:
10

Não informada:
0


OBJETIVO — máximo 15

Morar, investir, renda,
patrimônio ou segunda residência:
15

Parcialmente identificado:
5

Não informado:
0


QUARTOS / SUÍTES — máximo 15

Definido ou intervalo definido:
15

Aproximado:
10

Não informado:
0


ORIGEM / INTERESSE — máximo 15

Anúncio, imóvel, rua ou
empreendimento específico:
15

Canal conhecido sem produto identificado:
10

Contato genérico procurando imóvel:
5

Sem contexto:
0


PREFERÊNCIA RELEVANTE — máximo 10

Preferência útil identificada:
10

Nenhuma:
0

Pode incluir:

- pronto
- lançamento
- compra direta com construtora
- metragem
- varanda
- vaga
- localização específica
- necessidade familiar
- imóvel para venda
- interesse espontâneo em visita
- característica importante

TOTAL:
100 pontos.

=========================================================
CLASSIFICAÇÃO
=========================================================

80 a 100:
Lead Quente.

50 a 79:
Lead Morno.

0 a 49:
Lead Frio.

Nunca revele ao cliente.

=========================================================
SCORE NÃO É META
=========================================================

Não faça perguntas apenas para aumentar score.

O score descreve o contexto obtido.

Ele NÃO determina quantas perguntas devem ser feitas.

=========================================================
COMO PERGUNTAR
=========================================================

Não transforme a conversa em formulário.

COLABORATIVO:

pode fazer até duas perguntas relacionadas.

NEUTRO:

prefira uma pergunta.

RESISTENTE:

não faça nova pergunta.

=========================================================
EVITE BATERIA DE PREFERÊNCIAS
=========================================================

Evite:

"Quer pronto ou lançamento,
vaga, varanda ou outra característica?"

Isso parece formulário.

Se realmente for útil perguntar preferência:

"Tem alguma característica do imóvel
que seja especialmente importante para você?"

Mas somente se ainda fizer sentido aprofundar.

=========================================================
REGRA DE PARADA
=========================================================

Antes de cada nova pergunta,
pergunte internamente:

"Um corretor já conseguiria assumir
essa conversa sem começar do zero?"

Se SIM:

PARE.

Também pare se o cliente:

- desviar de uma pergunta
- pedir para conhecer o imóvel
- pedir atendimento
- pedir mais informações antes
- mostrar que quer avançar
- demonstrar resistência
- ignorar aquela linha de qualificação

=========================================================
MODO COLETA
=========================================================

Se ainda existir uma informação
realmente útil E o cliente estiver receptivo:

- faça pergunta natural
- seja curto
- não repita pergunta ignorada
- NÃO gere resumo

=========================================================
MODO ENCERRAMENTO
=========================================================

Encerre quando:

- houver contexto suficiente

OU

- houver resistência

OU

- o cliente quiser avançar para conhecer o imóvel

OU

- quiser atendimento do corretor

OU

- uma pergunta for ignorada e o contexto já for suficiente

Ao encerrar:

- não faça perguntas
- envie mensagem curta
- gere resumo interno

REGRA ABSOLUTA:

PERGUNTA = SEM RESUMO.

RESUMO = SEM PERGUNTA.

=========================================================
RESPOSTA FINAL
=========================================================

Use:

<CLIENTE>
Mensagem breve e natural de encerramento.
Sem perguntas.
</CLIENTE>

<RESUMO>
Nome:
Origem ou referência do contato:
Região ou empreendimento:
Faixa de investimento:
Quartos ou suítes:
Objetivo:
Preferência relevante:
Score:
Classificação:
Observações:
Próxima ação sugerida:
</RESUMO>

Score:
somente número.

Se algo não foi informado:

Não informado.

Observações:

somente fatos úteis.

Próxima ação:

sempre destinada ao corretor.

=========================================================
TOM E HUMANIDADE
=========================================================

Natural.
Humano.
Profissional.
Curto.

IMPORTANTE:

Não use "Perfeito" como resposta padrão.

Não comece várias mensagens consecutivas com:

"Perfeito"
"Ótimo"
"Excelente"
"Certo"
"Entendi"

Varie naturalmente ou simplesmente vá direto à pergunta.

Exemplo ruim:

"Perfeito, Pedro. Qual sua faixa?"

Depois:

"Perfeito, Pedro. Quantos quartos?"

Depois:

"Perfeito, Pedro. Seria para morar?"

Isso soa automatizado.

Exemplo melhor:

"Prazer, Pedro. Me conta um pouco do que você está buscando."

Depois:

"Você já tem uma faixa de investimento em mente?"

Depois:

"E esse imóvel seria para morar ou investir?"

Não precisa validar cada resposta.

Também:

- não elogie escolhas
- não recite tudo que o cliente acabou de falar
- não use o nome em toda mensagem
- não diga "só mais uma pergunta"
- não diga "só mais duas rapidinhas"
- não diga "preciso confirmar mais algumas coisas"

O cliente deve sentir uma conversa,
não uma ficha sendo preenchida.

O SOMMINHA QUALIFICA.
O CORRETOR ATENDE.
O CORRETOR VENDE.
"""


# =========================================================
# CHAT
# =========================================================

for mensagem in st.session_state.mensagens:

    if mensagem["role"] == "assistant":

        with st.chat_message(
            "assistant",
            avatar=AVATAR_SOMMINHA
        ):

            st.markdown(
                mensagem["content"]
            )

    else:

        with st.chat_message(
            "user",
            avatar=AVATAR_CLIENTE
        ):

            st.markdown(
                mensagem["content"]
            )


# =========================================================
# INPUT
# =========================================================

mensagem_usuario = st.chat_input(
    "Digite sua mensagem..."
)


if mensagem_usuario:

    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": mensagem_usuario
        }
    )


    with st.chat_message(
        "user",
        avatar=AVATAR_CLIENTE
    ):

        st.markdown(
            mensagem_usuario
        )


    # =====================================================
    # HISTÓRICO COMPLETO
    # =====================================================

    historico = []

    for mensagem in st.session_state.mensagens:

        historico.append(
            {
                "role": mensagem["role"],
                "content": mensagem["content"]
            }
        )


    # =====================================================
    # INDICADOR DE DIGITAÇÃO
    # =====================================================

    indicador_digitacao = st.empty()

    indicador_digitacao.markdown(
        """
        <div class="somminha-typing-wrapper">
            <div class="somminha-typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # CHAMADA DA IA
    # =====================================================

    try:

        resposta = client.responses.create(
            model="gpt-5-mini",
            instructions=INSTRUCOES,
            input=historico
        )


        texto_resposta = (
            resposta.output_text or ""
        ).strip()


        # =========================================
        # PROTEÇÃO CONTRA RESPOSTA VAZIA
        # =========================================

        if not texto_resposta:

            texto_cliente = (
                "Não consegui gerar a resposta agora. "
                "Pode enviar sua mensagem novamente?"
            )

        else:

            texto_cliente = texto_resposta


            # =====================================
            # EXTRAI TEXTO DO CLIENTE
            # =====================================

            if (
                "<CLIENTE>" in texto_resposta
                and "</CLIENTE>" in texto_resposta
            ):

                texto_cliente = (
                    texto_resposta
                    .split("<CLIENTE>")[1]
                    .split("</CLIENTE>")[0]
                    .strip()
                )


            # =====================================
            # PROTEÇÃO:
            # RESUMO SÓ EXISTE SEM PERGUNTA
            # =====================================

            resposta_tem_pergunta = (
                "?" in texto_cliente
            )


            if (
                "<RESUMO>" in texto_resposta
                and "</RESUMO>" in texto_resposta
                and not resposta_tem_pergunta
            ):

                resumo_corretor = (
                    texto_resposta
                    .split("<RESUMO>")[1]
                    .split("</RESUMO>")[0]
                    .strip()
                )

                st.session_state.resumo_corretor = (
                    resumo_corretor
                )


    except Exception:

        texto_cliente = (
            "Não consegui processar sua solicitação agora. "
            "Tente novamente em alguns instantes."
        )


    # =====================================================
    # REMOVE INDICADOR
    # =====================================================

    indicador_digitacao.empty()


    # =====================================================
    # EXIBE RESPOSTA
    # =====================================================

    if texto_cliente.strip():

        with st.chat_message(
            "assistant",
            avatar=AVATAR_SOMMINHA
        ):

            st.markdown(
                texto_cliente
            )


        st.session_state.mensagens.append(
            {
                "role": "assistant",
                "content": texto_cliente
            }
        )


# =========================================================
# ÁREA INTERNA
# =========================================================

if "resumo_corretor" in st.session_state:

    resumo = st.session_state.resumo_corretor

    score = None
    classificacao = None


    for linha in resumo.splitlines():

        linha_limpa = linha.strip()


        if linha_limpa.lower().startswith(
            "score:"
        ):

            numeros = re.findall(
                r"\d+",
                linha_limpa
            )

            if numeros:

                try:

                    score = int(
                        numeros[0]
                    )

                except ValueError:

                    score = None


        if linha_limpa.lower().startswith(
            "classificação:"
        ):

            classificacao = (
                linha_limpa
                .split(":", 1)[1]
                .strip()
            )


    st.divider()


    col_titulo_painel, col_status_painel = st.columns(
        [4, 1.6],
        vertical_alignment="center"
    )


    with col_titulo_painel:

        st.subheader(
            "📋 Inteligência Comercial"
        )

        st.caption(
            "Área interna para priorização e direcionamento do atendimento."
        )


    with col_status_painel:

        if classificacao:

            if "quente" in classificacao.lower():

                st.success(
                    "🔥 Lead Quente"
                )

            elif "morno" in classificacao.lower():

                st.warning(
                    "🟡 Lead Morno"
                )

            else:

                st.info(
                    "🔵 Lead Frio"
                )


    if score is not None:

        score_exibicao = max(
            0,
            min(
                score,
                100
            )
        )

        col_score, col_classificacao = st.columns(
            2
        )


        with col_score:

            st.metric(
                "Score comercial",
                f"{score_exibicao}/100"
            )


        with col_classificacao:

            st.metric(
                "Prioridade",
                classificacao
                if classificacao
                else "Em análise"
            )


        st.progress(
            score_exibicao / 100
        )


    with st.expander(
        "📄 Resumo completo da qualificação",
        expanded=False
    ):

        st.text(
            resumo
        )