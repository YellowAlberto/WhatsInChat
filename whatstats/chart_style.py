"""Estilo visual común de las gráficas interactivas (Plotly) de la web.

Todas las gráficas se construyen con estas funciones para que compartan paleta,
tipografía, márgenes y tooltips:

- Un único color de marca (teal) y un color de acento (ámbar) que solo se usa
  para resaltar el valor máximo de cada gráfica.
- Sin cuadrículas, bordes ni barras de color: etiquetas directas sobre las
  barras y títulos cortos alineados a la izquierda.
- Fondo transparente y colores neutros: el fondo lo pone la tarjeta de la web.
  Los colores de texto y las escalas de los mapas de calor se ajustan al modo
  claro/oscuro con JavaScript (ver `aplicarTemaGraficas` en resultados.html).
"""

import plotly.graph_objects as go
import plotly.io as pio

COLOR_PRINCIPAL = "#14b8a6"   # teal-500
COLOR_ACENTO = "#f59e0b"      # amber-500, solo para resaltar el máximo
COLOR_TEXTO = "#64748b"       # slate-500: legible en claro y oscuro hasta que JS lo ajusta
FUENTE = ("Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, "
          "'Helvetica Neue', Arial, sans-serif")

# Escala de los mapas de calor (opaca: así el texto de las celdas se autocontrasta).
# JS cambia entre estas dos según el tema: mantener sincronizadas con resultados.html.
ESCALA_CALOR_OSCURO = [[0, "#17303c"], [0.5, "#0d9488"], [1, "#5eead4"]]
ESCALA_CALOR_CLARO = [[0, "#f0fdfa"], [0.5, "#5eead4"], [1, "#0f766e"]]

CONFIG_PLOTLY = {"displayModeBar": False, "responsive": True}


def a_html(fig, div_id):
    """Convierte la figura en el fragmento HTML que se incrusta en la plantilla."""
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, div_id=div_id, config=CONFIG_PLOTLY)


def _colores_destacando_maximo(valores):
    maximo = max(valores) if len(valores) else 0
    return [COLOR_ACENTO if (maximo > 0 and v == maximo) else COLOR_PRINCIPAL for v in valores]


def _rango_con_aire(valores, factor=1.18):
    maximo = max(valores) if len(valores) else 0
    return [0, maximo * factor] if maximo > 0 else None


def _aplicar_estilo(fig, titulo, subtitulo=None, altura=None, margen=None):
    titulo_cfg = dict(text=titulo, x=0, xanchor="left", font=dict(size=18, family=FUENTE))
    if subtitulo:
        titulo_cfg["subtitle"] = dict(text=subtitulo, font=dict(size=12, color=COLOR_TEXTO))
    fig.update_layout(
        template="simple_white",
        title=titulo_cfg,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FUENTE, color=COLOR_TEXTO, size=13),
        margin=margen or dict(t=90 if subtitulo else 60, b=24, l=20, r=20),
        hoverlabel=dict(bgcolor="#0f172a", bordercolor=COLOR_PRINCIPAL,
                        font=dict(family=FUENTE, color="#f1f5f9", size=13)),
        showlegend=False,
        bargap=0.35,
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


def barras_horizontales(df, col_valor, col_categoria, titulo, subtitulo=None, texto=None,
                        texto_formato="%{text:,}", hover=None, customdata=None, altura=None,
                        tamano_etiqueta_y=None, margen_der=70):
    """Barras horizontales. `df` debe venir ya ordenado de menor a mayor
    (así la barra más larga queda arriba). La barra máxima se resalta en ámbar."""
    valores = df[col_valor].tolist()
    categorias = df[col_categoria].tolist()
    if texto is None:
        texto = valores
    if hover is None:
        hover = "<b>%{y}</b><br>%{x:,}<extra></extra>"

    fig = go.Figure(go.Bar(
        x=valores, y=categorias, orientation="h",
        text=texto, texttemplate=texto_formato, textposition="outside", cliponaxis=False,
        textfont=dict(size=12),
        customdata=customdata, hovertemplate=hover,
        marker=dict(color=_colores_destacando_maximo(valores), cornerradius=6),
    ))
    _aplicar_estilo(fig, titulo, subtitulo, altura,
                    margen=dict(t=90 if subtitulo else 60, b=24, l=20, r=margen_der))
    fig.update_xaxes(visible=False, range=_rango_con_aire(valores))
    fig.update_yaxes(type="category", showline=False, showgrid=False, ticks="",
                     ticksuffix="  ", automargin=True,
                     tickfont=dict(size=tamano_etiqueta_y) if tamano_etiqueta_y else None)
    return fig


def barras_verticales(df, col_categoria, col_valor, titulo, subtitulo=None, hover=None, altura=None):
    """Barras verticales (p. ej. mensajes por año). La barra máxima en ámbar."""
    valores = df[col_valor].tolist()
    categorias = df[col_categoria].astype(str).tolist()
    if hover is None:
        hover = "<b>%{x}</b><br>%{y:,}<extra></extra>"

    fig = go.Figure(go.Bar(
        x=categorias, y=valores,
        text=valores, texttemplate="%{text:,}", textposition="outside", cliponaxis=False,
        textfont=dict(size=12), hovertemplate=hover,
        marker=dict(color=_colores_destacando_maximo(valores), cornerradius=6),
    ))
    _aplicar_estilo(fig, titulo, subtitulo, altura)
    fig.update_xaxes(type="category", showline=False, showgrid=False, ticks="")
    fig.update_yaxes(visible=False, range=_rango_con_aire(valores, 1.2))
    return fig


def linea_actividad_horaria(df, titulo):
    """Curva suave de mensajes por hora (columnas 'Hora' y 'Mensajes'), con
    área bajo la curva y la hora pico resaltada en ámbar."""
    horas = df["Hora"].tolist()
    valores = df["Mensajes"].tolist()
    maximo = max(valores) if valores else 0
    colores = [COLOR_ACENTO if (maximo > 0 and v == maximo) else COLOR_PRINCIPAL for v in valores]
    tamanos = [11 if (maximo > 0 and v == maximo) else 6 for v in valores]

    fig = go.Figure(go.Scatter(
        x=horas, y=valores, mode="lines+markers",
        line=dict(color=COLOR_PRINCIPAL, width=3, shape="spline", smoothing=0.7),
        marker=dict(color=colores, size=tamanos, line=dict(width=0)),
        fill="tozeroy", fillcolor="rgba(20,184,166,0.14)",
        hovertemplate="<b>%{x}:00 h</b><br>%{y:,} mensajes<extra></extra>",
    ))
    _aplicar_estilo(fig, titulo)
    fig.update_xaxes(tickmode="linear", tick0=0, dtick=2, ticksuffix="h",
                     showline=False, showgrid=False, ticks="")
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="rgba(100,116,139,0.18)",
                     zeroline=False, ticks="", rangemode="tozero", automargin=True)
    return fig


def mapa_calor(z, x, y, titulo, hover, subtitulo=None, texto=None, altura=None, margen=None,
               titulo_x=None, dtick_x=None, tickangle_x=None):
    """Mapa de calor sin barra de color, con celdas separadas y filas de arriba
    a abajo en el orden recibido."""
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y, colorscale=ESCALA_CALOR_OSCURO, showscale=False,
        xgap=3, ygap=3, hoverongaps=False, hovertemplate=hover,
        text=texto, texttemplate="%{text}" if texto is not None else None,
        textfont=dict(size=11),
    ))
    _aplicar_estilo(fig, titulo, subtitulo, altura, margen)
    xaxis = dict(showline=False, showgrid=False, ticks="", automargin=True)
    if titulo_x:
        xaxis["title"] = dict(text=titulo_x, font=dict(size=12))
    if dtick_x:
        xaxis.update(tickmode="linear", tick0=0, dtick=dtick_x)
    if tickangle_x is not None:
        xaxis["tickangle"] = tickangle_x
    fig.update_xaxes(**xaxis)
    fig.update_yaxes(autorange="reversed", showline=False, showgrid=False, ticks="", automargin=True)
    return fig
