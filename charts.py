# =============================================================
# charts.py — Funciones de visualizacion con Matplotlib.
# Cada funcion recibe datos procesados y retorna una figura fig.
# Sin dependencias de Streamlit ni de data_utils.
# =============================================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# -------------------------------------------------------------
# MODELO ESTRUCTURAL CON FUERZAS SISMICAS
# -------------------------------------------------------------

def graficar_modelo_estructural(lista_pisos, alturas_entrepiso,
                                 cortante_real_diseno, es_oscuro=False):
    """Esquema del edificio con vectores de carga sismica por piso.

    Parametros
    ----------
    lista_pisos : list[str]
    alturas_entrepiso : np.ndarray
    cortante_real_diseno : np.ndarray  (cortante de diseno por piso)
    es_oscuro : bool

    Retorna
    -------
    fig : matplotlib.figure.Figure
    """
    z_coords  = np.insert(np.cumsum(alturas_entrepiso), 0, 0.0)
    n_floors  = len(lista_pisos)

    bg_plot   = "#1e293b" if es_oscuro else "#ffffff"
    text_plot = "#f8fafc" if es_oscuro else "#0f172a"
    line_col  = "#38bdf8" if es_oscuro else "#0284c7"
    arrow_col = "#f97316" if es_oscuro else "#ea580c"

    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
    fig.patch.set_facecolor(bg_plot)
    ax.set_facecolor(bg_plot)

    # Base rigida
    ax.plot([-2.5, 2.5], [0, 0], color=text_plot, lw=3)
    for x_h in np.linspace(-2.2, 2.2, 14):
        ax.plot([x_h, x_h - 0.25], [0, -0.4], color=text_plot, lw=1.5)

    # Columnas, vigas y nodos
    for i in range(len(z_coords) - 1):
        z_bot, z_top = z_coords[i], z_coords[i + 1]
        ax.plot([-0.7, -0.7], [z_bot, z_top], color=line_col, lw=2.5, zorder=2)
        ax.plot([ 0.7,  0.7], [z_bot, z_top], color=line_col, lw=2.5, zorder=2)
        ax.plot([-0.9,  0.9], [z_top, z_top], color=text_plot, lw=3,   zorder=3)
        ax.scatter([0.0], [z_top], s=380, color=line_col, edgecolors=text_plot,
                   linewidth=2, zorder=4)
        ax.text(0.0, z_top, f"m_{i+1}", color="#ffffff", ha="center", va="center",
                fontweight="bold", fontsize=9, zorder=5)

    # Fuerzas por piso
    fuerzas = np.zeros(n_floors)
    for i in range(n_floors):
        fuerzas[i] = (cortante_real_diseno[i] if i == n_floors - 1
                      else cortante_real_diseno[i] - cortante_real_diseno[i + 1])
    max_f = max(fuerzas) if max(fuerzas) > 0 else 1.0

    for i in range(n_floors):
        z_lvl        = z_coords[i + 1]
        f_val        = fuerzas[i]
        arrow_length = 1.2 + 2.0 * (f_val / max_f)
        x_start      = -0.9 - arrow_length

        ax.annotate("", xy=(-0.9, z_lvl), xytext=(x_start, z_lvl),
                    arrowprops=dict(facecolor=arrow_col, edgecolor=arrow_col,
                                   width=3, headwidth=10, headlength=10), zorder=6)
        ax.text(x_start + 0.1, z_lvl + 0.3, f"{f_val:.1f} tonf",
                color=text_plot, fontweight="bold", fontsize=10,
                fontfamily="Times New Roman", zorder=7)
        ax.text(1.2, z_lvl, f"{lista_pisos[i]} (h = {z_lvl:.1f} m)",
                color=text_plot, va="center", fontweight="bold", fontsize=10,
                fontfamily="Times New Roman", zorder=7)

    ax.set_xlim(-4.8, 4.2)
    ax.set_ylim(-1.0, max(z_coords) + 1.5)
    ax.axis("off")
    ax.set_title(
        "Modelo Estructural y Fuerzas Sismicas de Diseno por Piso",
        color=text_plot, fontweight="bold", fontsize=13,
        fontfamily="Times New Roman", pad=15,
    )
    plt.tight_layout()
    return fig


# -------------------------------------------------------------
# PERFILES MODALES DE FUERZAS Y CORTANTES
# -------------------------------------------------------------

def graficar_perfiles_modales(lista_pisos, F_modales, V_modales, es_oscuro=False):
    """Grafico de dos paneles: fuerzas y cortantes modales por piso.

    Retorna
    -------
    fig : matplotlib.figure.Figure
    """
    posiciones = np.arange(1, len(lista_pisos) + 1)

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"]  = ["Times New Roman"]

    bg_plot   = "#1e293b" if es_oscuro else "#ffffff"
    bg_ax     = "#0f172a" if es_oscuro else "#f8fafc"
    text_plot = "#f8fafc" if es_oscuro else "#0f172a"
    grid_col  = "#94a3b8" if es_oscuro else "#cbd5e1"
    colores   = (["#38bdf8", "#f97316", "#22c55e"] if es_oscuro
                 else ["#0284c7", "#ea580c", "#16a34a"])

    fig, (ax_f, ax_v) = plt.subplots(1, 2, figsize=(14, 5), dpi=110)
    fig.patch.set_facecolor(bg_plot)
    ax_f.set_facecolor(bg_ax)
    ax_v.set_facecolor(bg_ax)

    for i, color in enumerate(colores):
        ax_f.plot(F_modales[i], posiciones, marker="o",
                  label=f"Modo {i+1}", color=color, linewidth=2.2)
        ax_v.plot(V_modales[i], posiciones, marker="s",
                  label=f"Modo {i+1}", color=color, linewidth=2.2)

    for ax in (ax_f, ax_v):
        ax.axvline(0, color=grid_col, linestyle="--")
        ax.set_yticks(posiciones)
        ax.set_yticklabels(lista_pisos, color=text_plot,
                           fontfamily="Times New Roman")
        ax.tick_params(colors=text_plot)
        ax.grid(True, linestyle=":", alpha=0.5, color=grid_col)
        ax.legend()

    ax_f.set_title("Fuerzas Sismicas Modales (F)", color=text_plot,
                   fontweight="bold", fontfamily="Times New Roman")
    ax_v.set_title("Cortantes Modales de Piso (V)", color=text_plot,
                   fontweight="bold", fontfamily="Times New Roman")
    plt.tight_layout()
    return fig


# -------------------------------------------------------------
# COMBINACIONES MODALES (ABS, SRSS, CQC, REAL) — 4 PANELES
# -------------------------------------------------------------

def graficar_combinaciones_modales(lista_pisos, V_abs, V_srss, V_cqc, V_real):
    """Cuatro paneles de barras horizontales para cada metodo de combinacion.

    Retorna
    -------
    fig : matplotlib.figure.Figure
    """
    posiciones = np.arange(1, len(lista_pisos) + 1)

    fig, ((ax_abs, ax_srss), (ax_cqc, ax_real)) = plt.subplots(
        2, 2, figsize=(15, 10), dpi=120
    )
    fig.suptitle(
        "COMBINACIONES MODALES DE CORTANTE POR PISO",
        fontsize=16, fontweight="bold", color="#14253C", y=0.98,
    )

    paneles = [
        (ax_abs,  V_abs,  r"Cortante Suma Absoluta ($V_{ABS}$)",     "#20C4D6"),
        (ax_srss, V_srss, r"Cortante SRSS ($V_{SRSS}$)",             "#8652B8"),
        (ax_cqc,  V_cqc,  r"Cortante CQC ($V_{CQC}$)",               "#BA549C"),
        (ax_real, V_real, r"Cortante Real de Diseno ($V_{REAL}$)",   "#1A426C"),
    ]

    for ax, datos, titulo, color_barra in paneles:
        ax.barh(posiciones, datos, color=color_barra,
                edgecolor="black", alpha=0.90, height=0.6)
        val_max = max(float(np.max(np.abs(datos))), 1e-9)
        for idx, val in enumerate(datos):
            desp = val_max * 0.02
            ax.text(
                val + (desp if val >= 0 else -desp), posiciones[idx],
                f"{val:.3f} tonf",
                va="center", ha="left" if val >= 0 else "right",
                fontweight="bold", fontsize=8, color="#181E24",
            )
        ax.set_yticks(posiciones)
        ax.set_yticklabels(lista_pisos, fontsize=10)
        ax.set_title(titulo, fontsize=12, fontweight="bold", color="#010812", pad=10)
        ax.set_xlabel("Cortante (tonf)")
        ax.grid(True, linestyle=":", alpha=0.6, color="#BDC3C7", axis="x")
        ax.set_xlim(
            min(0, float(np.min(datos)) - val_max * 0.12),
            val_max * 1.25,
        )
        ax.set_axisbelow(True)

    fig.tight_layout(rect=[0, 0, 1, 0.93], h_pad=2.5, w_pad=2.0)
    return fig


# -------------------------------------------------------------
# ANIMACION DINAMICA — MODELO DE MASA CONCENTRADA (RESORTES)
# -------------------------------------------------------------

def _generar_puntos_resorte(p1, p2, num_vueltas=5, ancho=0.20):
    """Calcula las coordenadas del camino de un resorte entre dos puntos."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    longitud = np.hypot(dx, dy)
    if longitud == 0:
        return np.array([x1]), np.array([y1])

    n_pts  = num_vueltas * 2
    t_vals = np.linspace(0, 1, n_pts + 2)
    x_loc  = t_vals * longitud
    y_loc  = np.zeros(n_pts + 2)
    y_loc[1:-1] = np.tile([ancho, -ancho], num_vueltas)

    angulo = np.arctan2(dy, dx)
    ca, sa = np.cos(angulo), np.sin(angulo)
    x_glob = x1 + x_loc * ca - y_loc * sa
    y_glob = y1 + x_loc * sa + y_loc * ca
    return x_glob, y_glob


def generar_animacion_modos(alturas_entrepiso, periodos_modales,
                            matriz_formas_modales, w_modo,
                            num_pisos, es_oscuro=False):
    """Genera la animacion dinamica de modos vibracionales.

    Retorna
    -------
    html_code : str   (HTML con JavaScript para reproducir la animacion)
    """
    vector_alturas = np.insert(np.cumsum(alturas_entrepiso), 0, 0.0)
    escala   = 8.0
    fps      = 20
    cuadros  = 80
    t        = np.linspace(0, 2.5, cuadros)

    bg_plot   = "#1e293b" if es_oscuro else "#ffffff"
    bg_ax     = "#0f172a" if es_oscuro else "#f8fafc"
    text_plot = "#f8fafc" if es_oscuro else "#0f172a"
    colores   = (["#38bdf8", "#f97316", "#22c55e"] if es_oscuro
                 else ["#0284c7", "#ea580c", "#16a34a"])

    fig_anim, ejes = plt.subplots(1, 3, figsize=(13, 6), dpi=110)
    fig_anim.patch.set_facecolor(bg_plot)

    elementos = []
    for m in range(3):
        ax = ejes[m]
        ax.set_facecolor(bg_ax)
        ax.set_xlim(-2.8, 2.8)
        ax.set_ylim(-1.0, max(vector_alturas) + 1.8)
        ax.set_title(f"Modo {m+1} (T={periodos_modales[m]:.3f}s)",
                     color=text_plot, fontweight="bold", fontfamily="Times New Roman")
        ax.tick_params(colors=text_plot)
        ax.grid(True, linestyle=":", alpha=0.3, color="#cbd5e1")

        ax.plot([-1.5, 1.5], [0, 0], color=text_plot, lw=3.0)
        for x_h in np.linspace(-1.3, 1.3, 10):
            ax.plot([x_h, x_h - 0.2], [0, -0.3], color=text_plot, lw=1.2)

        lineas_resortes = []
        for _ in range(num_pisos):
            ln, = ax.plot([], [], color=text_plot, lw=1.8, zorder=2)
            lineas_resortes.append(ln)

        nodos = ax.scatter([], [], s=550, color=colores[m],
                           edgecolors=text_plot, linewidth=2, zorder=4)
        textos = [
            ax.text(0, 0, f"$m_{{{p+1}}}$", color="#ffffff",
                    ha="center", va="center", fontweight="bold",
                    fontsize=9, zorder=5)
            for p in range(num_pisos)
        ]
        elementos.append({"resortes": lineas_resortes, "nodos": nodos,
                           "textos": textos, "modo_idx": m})

    def animate(frame):
        artistas = []
        for elem in elementos:
            m   = elem["modo_idx"]
            osc = np.cos(w_modo[m] * t[frame])
            dx  = matriz_formas_modales[m] * escala * osc
            pos_x = np.insert(dx, 0, 0.0)
            pos_y = vector_alturas
            for p in range(num_pisos):
                rx, ry = _generar_puntos_resorte(
                    (pos_x[p], pos_y[p]), (pos_x[p+1], pos_y[p+1])
                )
                elem["resortes"][p].set_data(rx, ry)
                artistas.append(elem["resortes"][p])
            elem["nodos"].set_offsets(
                np.column_stack((pos_x[1:], pos_y[1:]))
            )
            artistas.append(elem["nodos"])
            for p in range(num_pisos):
                elem["textos"][p].set_position((pos_x[p+1], pos_y[p+1]))
                artistas.append(elem["textos"][p])
        return artistas

    anim = animation.FuncAnimation(
        fig_anim, animate, frames=cuadros,
        interval=1000 / fps, blit=True
    )
    html_code = anim.to_jshtml()
    plt.close(fig_anim)
    return html_code
