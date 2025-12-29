"""Kenobase V2.0 Web Dashboard - Streamlit-basierte Visualisierung.

Dieses Modul implementiert ein interaktives Web-Dashboard fuer Kenobase V2.0.
Bietet 5 Hauptseiten: Home, Analysis, Backtest, Physics, Config.

Usage:
    streamlit run scripts/dashboard.py
    # oder mit Config:
    streamlit run scripts/dashboard.py -- --config config/default.yaml

Requirements:
    pip install streamlit plotly
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import streamlit as st

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.config import KenobaseConfig, load_config
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.pipeline.runner import PipelineResult, PipelineRunner
from kenobase.pipeline.output_formats import OutputFormatter, OutputFormat

if TYPE_CHECKING:
    import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Kenobase V2.0 Dashboard",
    page_icon=":game_die:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Session State Management ---
def init_session_state() -> None:
    """Initialisiert den Streamlit Session State."""
    if "config" not in st.session_state:
        st.session_state.config = None
    if "draws" not in st.session_state:
        st.session_state.draws = []
    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False


# --- Helper Functions ---
def load_default_config() -> KenobaseConfig:
    """Laedt die Standard-Konfiguration."""
    config_path = PROJECT_ROOT / "config" / "default.yaml"
    return load_config(str(config_path))


def get_data_files() -> list[Path]:
    """Findet alle verfuegbaren Daten-Dateien."""
    data_dirs = [
        PROJECT_ROOT / "data" / "raw" / "keno",
        PROJECT_ROOT / "data" / "raw" / "eurojackpot",
        PROJECT_ROOT / "data" / "raw" / "lotto",
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "Keno_GPTs",
    ]

    files = []
    for data_dir in data_dirs:
        if data_dir.exists():
            files.extend(data_dir.glob("*.csv"))

    return sorted(files)


def result_to_dict(result: PipelineResult) -> dict:
    """Konvertiert PipelineResult zu serialisierbarem Dict."""
    data = {
        "timestamp": result.timestamp.isoformat(),
        "draws_count": result.draws_count,
        "warnings": result.warnings,
        "config_snapshot": result.config_snapshot,
    }

    # Frequency results
    data["frequency_results"] = [
        {
            "number": r.number,
            "count": r.count,
            "relative_frequency": r.relative_frequency,
            "classification": r.classification,
        }
        for r in result.frequency_results
    ]

    # Pair frequency results
    data["pair_frequency_results"] = [
        {
            "pair": list(r.pair),
            "count": r.count,
            "relative_frequency": r.relative_frequency,
            "classification": r.classification,
        }
        for r in result.pair_frequency_results[:50]  # Top 50
    ]

    # Physics result
    if result.physics_result:
        pr = result.physics_result
        data["physics_result"] = {
            "stability_score": pr.stability_score,
            "is_stable_law": pr.is_stable_law,
            "criticality_score": pr.criticality_score,
            "criticality_level": pr.criticality_level,
            "hurst_exponent": pr.hurst_exponent,
            "regime_complexity": pr.regime_complexity,
            "recommended_max_picks": pr.recommended_max_picks,
        }
        if pr.avalanche_result:
            ar = pr.avalanche_result
            data["physics_result"]["avalanche"] = {
                "theta": ar.theta,
                "state": ar.state.value,
                "is_safe_to_bet": ar.is_safe_to_bet,
            }

    # Pipeline selection
    if result.pipeline_selection:
        ps = result.pipeline_selection
        data["pipeline_selection"] = {
            "selected_name": ps.selected.name,
            "selected_action": ps.selected_action,
        }

    return data


# --- Page: Home ---
def page_home() -> None:
    """Startseite mit Uebersicht und Daten-Laden."""
    st.title("Kenobase V2.0 Dashboard")
    st.markdown("""
    Willkommen beim **Kenobase V2.0** Analyse-Dashboard.

    Dieses Tool ermoeglicht:
    - Frequenzanalyse von Lottozahlen
    - Physics-Layer Analyse (Model Laws A/B/C)
    - Avalanche-Risk Assessment
    - Backtest-Visualisierung
    """)

    st.divider()

    # Config loading
    st.subheader("1. Konfiguration")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Standard-Config laden", type="primary"):
            st.session_state.config = load_default_config()
            st.success("Konfiguration geladen!")

    with col2:
        uploaded_config = st.file_uploader(
            "Oder YAML-Config hochladen:",
            type=["yaml", "yml"],
            key="config_upload",
        )
        if uploaded_config:
            import yaml
            try:
                config_data = yaml.safe_load(uploaded_config)
                st.session_state.config = KenobaseConfig(**config_data)
                st.success("Custom Config geladen!")
            except Exception as e:
                st.error(f"Fehler beim Laden: {e}")

    # Show current config
    if st.session_state.config:
        cfg = st.session_state.config
        st.info(f"Aktive Config: v{cfg.version}, Game: {cfg.active_game}")

    st.divider()

    # Data loading
    st.subheader("2. Daten laden")

    data_files = get_data_files()

    if data_files:
        selected_file = st.selectbox(
            "CSV-Datei waehlen:",
            options=data_files,
            format_func=lambda x: f"{x.parent.name}/{x.name}",
        )

        if st.button("Daten laden", type="primary", disabled=not st.session_state.config):
            if not st.session_state.config:
                st.error("Bitte zuerst Config laden!")
            else:
                with st.spinner("Lade Daten..."):
                    try:
                        loader = DataLoader()
                        draws = loader.load(str(selected_file))
                        st.session_state.draws = draws
                        st.session_state.data_loaded = True
                        st.success(f"{len(draws)} Ziehungen geladen!")
                    except Exception as e:
                        st.error(f"Fehler: {e}")
    else:
        st.warning("Keine CSV-Dateien gefunden. Bitte Daten in data/raw/ ablegen.")

        # File upload fallback
        uploaded_data = st.file_uploader(
            "Oder CSV-Datei hochladen:",
            type=["csv"],
            key="data_upload",
        )
        if uploaded_data and st.session_state.config:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                tmp.write(uploaded_data.getvalue())
                tmp_path = tmp.name

            try:
                loader = DataLoader()
                draws = loader.load(tmp_path)
                st.session_state.draws = draws
                st.session_state.data_loaded = True
                st.success(f"{len(draws)} Ziehungen geladen!")
            except Exception as e:
                st.error(f"Fehler: {e}")

    # Show data summary
    if st.session_state.data_loaded and st.session_state.draws:
        st.divider()
        st.subheader("3. Daten-Uebersicht")

        draws = st.session_state.draws
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Ziehungen", len(draws))
        with col2:
            st.metric("Spieltyp", draws[0].game_type if draws else "N/A")
        with col3:
            if draws:
                date_range = f"{draws[0].date.strftime('%d.%m.%Y')} - {draws[-1].date.strftime('%d.%m.%Y')}"
                st.metric("Zeitraum", date_range)
        with col4:
            if draws:
                st.metric("Zahlen/Ziehung", len(draws[0].numbers))


# --- Page: Analysis ---
def page_analysis() -> None:
    """Analyse-Seite mit Pipeline-Ausfuehrung."""
    st.title("Analyse")

    if not st.session_state.data_loaded:
        st.warning("Bitte zuerst Daten auf der Home-Seite laden.")
        return

    config = st.session_state.config
    draws = st.session_state.draws

    # Analysis options
    st.subheader("Analyse-Parameter")

    col1, col2 = st.columns(2)

    with col1:
        n_draws = st.slider(
            "Anzahl Ziehungen analysieren:",
            min_value=10,
            max_value=len(draws),
            value=min(500, len(draws)),
            step=10,
        )

    with col2:
        combination_input = st.text_input(
            "Kombination analysieren (optional, z.B. '1,5,17,23,42,55'):",
            placeholder="1,5,17,23,42,55",
        )

    # Parse combination
    combination = None
    if combination_input:
        try:
            combination = [int(x.strip()) for x in combination_input.split(",")]
            st.info(f"Kombination: {combination}")
        except ValueError:
            st.error("Ungueltige Kombination. Format: 1,2,3,4,5,6")

    # Run analysis
    if st.button("Analyse starten", type="primary"):
        with st.spinner("Fuehre Analyse aus..."):
            try:
                runner = PipelineRunner(config)
                result = runner.run(
                    draws=draws[:n_draws],
                    combination=combination,
                )
                st.session_state.pipeline_result = result
                st.success(f"Analyse abgeschlossen! {len(result.warnings)} Warnungen.")
            except Exception as e:
                st.error(f"Fehler bei Analyse: {e}")
                logger.exception("Analysis failed")

    # Show results
    if st.session_state.pipeline_result:
        result = st.session_state.pipeline_result
        result_dict = result_to_dict(result)

        st.divider()
        st.subheader("Ergebnisse")

        # Warnings
        if result.warnings:
            with st.expander(f"Warnungen ({len(result.warnings)})", expanded=True):
                for w in result.warnings:
                    st.warning(w)

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Frequenzen", "Paare", "Export"])

        with tab1:
            st.markdown("### Zahlen-Frequenzen")

            # Sort options
            sort_by = st.radio(
                "Sortieren nach:",
                ["Haeufigkeit (absteigend)", "Nummer (aufsteigend)"],
                horizontal=True,
            )

            freq_data = result_dict["frequency_results"]
            if sort_by == "Haeufigkeit (absteigend)":
                freq_data = sorted(freq_data, key=lambda x: x["count"], reverse=True)
            else:
                freq_data = sorted(freq_data, key=lambda x: x["number"])

            # Display as table
            import pandas as pd
            df_freq = pd.DataFrame(freq_data)
            df_freq["relative_frequency"] = df_freq["relative_frequency"].apply(lambda x: f"{x:.4f}")

            st.dataframe(
                df_freq,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "number": "Zahl",
                    "count": "Anzahl",
                    "relative_frequency": "Rel. Frequenz",
                    "classification": "Klassifikation",
                },
            )

            # Chart
            if st.checkbox("Frequenz-Chart anzeigen", value=True):
                try:
                    import plotly.express as px

                    df_chart = pd.DataFrame(freq_data[:30])  # Top 30
                    fig = px.bar(
                        df_chart,
                        x="number",
                        y="count",
                        color="classification",
                        color_discrete_map={
                            "hot": "#ff6b6b",
                            "cold": "#4dabf7",
                            "normal": "#868e96",
                        },
                        title="Top 30 Zahlen nach Haeufigkeit",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    st.info("Plotly nicht installiert. Installieren mit: pip install plotly")

        with tab2:
            st.markdown("### Paar-Frequenzen (Top 30)")

            pair_data = result_dict.get("pair_frequency_results", [])[:30]
            if pair_data:
                import pandas as pd

                df_pairs = pd.DataFrame(pair_data)
                df_pairs["pair"] = df_pairs["pair"].apply(lambda x: f"{x[0]}-{x[1]}")
                df_pairs["relative_frequency"] = df_pairs["relative_frequency"].apply(lambda x: f"{x:.4f}")

                st.dataframe(
                    df_pairs,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "pair": "Paar",
                        "count": "Anzahl",
                        "relative_frequency": "Rel. Frequenz",
                        "classification": "Klassifikation",
                    },
                )
            else:
                st.info("Keine Paar-Daten verfuegbar.")

        with tab3:
            st.markdown("### Export")

            export_format = st.selectbox(
                "Format:",
                ["JSON", "Markdown", "HTML", "CSV"],
            )

            formatter = OutputFormatter()

            if export_format == "JSON":
                output = formatter.format(result_dict, OutputFormat.JSON)
                st.download_button(
                    "JSON herunterladen",
                    data=output,
                    file_name="kenobase_analysis.json",
                    mime="application/json",
                )
                with st.expander("Vorschau"):
                    st.code(output[:2000] + "..." if len(output) > 2000 else output, language="json")

            elif export_format == "Markdown":
                output = formatter.format(result_dict, OutputFormat.MARKDOWN)
                st.download_button(
                    "Markdown herunterladen",
                    data=output,
                    file_name="kenobase_analysis.md",
                    mime="text/markdown",
                )
                with st.expander("Vorschau"):
                    st.markdown(output)

            elif export_format == "HTML":
                output = formatter.format(result_dict, OutputFormat.HTML)
                st.download_button(
                    "HTML herunterladen",
                    data=output,
                    file_name="kenobase_analysis.html",
                    mime="text/html",
                )
                with st.expander("Vorschau"):
                    st.components.v1.html(output, height=400, scrolling=True)

            else:  # CSV
                output = formatter.format(result_dict, OutputFormat.CSV)
                st.download_button(
                    "CSV herunterladen",
                    data=output,
                    file_name="kenobase_analysis.csv",
                    mime="text/csv",
                )
                with st.expander("Vorschau"):
                    st.code(output[:2000] + "..." if len(output) > 2000 else output)


# --- Page: Backtest ---
def page_backtest() -> None:
    """Backtest-Seite mit Walk-Forward Simulation."""
    st.title("Backtest")

    if not st.session_state.data_loaded:
        st.warning("Bitte zuerst Daten auf der Home-Seite laden.")
        return

    config = st.session_state.config
    draws = st.session_state.draws

    st.markdown("""
    Der Backtest simuliert die Analyse-Pipeline auf historischen Daten
    und misst die Vorhersage-Qualitaet.
    """)

    st.subheader("Backtest-Parameter")

    col1, col2, col3 = st.columns(3)

    with col1:
        n_periods = st.slider(
            "Anzahl Perioden:",
            min_value=5,
            max_value=50,
            value=10,
        )

    with col2:
        window_size = st.slider(
            "Fenstergroesse (Ziehungen):",
            min_value=50,
            max_value=500,
            value=100,
        )

    with col3:
        step_size = st.slider(
            "Schrittweite:",
            min_value=10,
            max_value=100,
            value=20,
        )

    if st.button("Backtest starten", type="primary"):
        if len(draws) < window_size + n_periods * step_size:
            st.error(f"Nicht genuegend Daten. Benoetigt: {window_size + n_periods * step_size}, Vorhanden: {len(draws)}")
            return

        progress = st.progress(0, text="Backtest laeuft...")
        results = []

        runner = PipelineRunner(config)

        for i in range(n_periods):
            start_idx = i * step_size
            end_idx = start_idx + window_size

            if end_idx >= len(draws):
                break

            period_draws = draws[start_idx:end_idx]

            try:
                result = runner.run(period_draws)

                # Extract key metrics
                metrics = {
                    "period": i + 1,
                    "start_date": period_draws[0].date.strftime("%Y-%m-%d"),
                    "end_date": period_draws[-1].date.strftime("%Y-%m-%d"),
                    "n_draws": len(period_draws),
                    "n_warnings": len(result.warnings),
                }

                if result.physics_result:
                    metrics["stability"] = result.physics_result.stability_score
                    metrics["criticality"] = result.physics_result.criticality_score
                    metrics["hurst"] = result.physics_result.hurst_exponent

                results.append(metrics)

            except Exception as e:
                st.warning(f"Periode {i+1} fehlgeschlagen: {e}")

            progress.progress((i + 1) / n_periods, text=f"Periode {i+1}/{n_periods}")

        progress.empty()

        if results:
            st.success(f"Backtest abgeschlossen! {len(results)} Perioden analysiert.")

            import pandas as pd
            df_results = pd.DataFrame(results)

            # Show metrics table
            st.subheader("Backtest-Ergebnisse")
            st.dataframe(df_results, use_container_width=True, hide_index=True)

            # Charts
            if "stability" in df_results.columns:
                try:
                    import plotly.express as px

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.line(
                            df_results,
                            x="period",
                            y="stability",
                            title="Stabilitaet ueber Zeit",
                            markers=True,
                        )
                        fig.add_hline(y=0.9, line_dash="dash", line_color="green", annotation_text="Threshold")
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.line(
                            df_results,
                            x="period",
                            y="criticality",
                            title="Criticality ueber Zeit",
                            markers=True,
                        )
                        fig.add_hline(y=0.7, line_dash="dash", line_color="orange", annotation_text="Warning")
                        fig.add_hline(y=0.85, line_dash="dash", line_color="red", annotation_text="Critical")
                        st.plotly_chart(fig, use_container_width=True)

                except ImportError:
                    st.info("Plotly nicht installiert fuer Charts.")

            # Summary statistics
            st.subheader("Zusammenfassung")

            col1, col2, col3 = st.columns(3)

            with col1:
                if "stability" in df_results.columns:
                    avg_stability = df_results["stability"].mean()
                    st.metric(
                        "Durchschn. Stabilitaet",
                        f"{avg_stability:.3f}",
                        delta="Stabil" if avg_stability >= 0.9 else "Instabil",
                        delta_color="normal" if avg_stability >= 0.9 else "inverse",
                    )

            with col2:
                if "criticality" in df_results.columns:
                    avg_crit = df_results["criticality"].mean()
                    st.metric(
                        "Durchschn. Criticality",
                        f"{avg_crit:.3f}",
                        delta="OK" if avg_crit < 0.7 else "Warnung",
                        delta_color="normal" if avg_crit < 0.7 else "inverse",
                    )

            with col3:
                total_warnings = df_results["n_warnings"].sum()
                st.metric("Gesamt Warnungen", total_warnings)


# --- Page: Physics ---
def page_physics() -> None:
    """Physics-Layer Visualisierung."""
    st.title("Physics Layer")

    if not st.session_state.pipeline_result:
        st.warning("Bitte zuerst eine Analyse auf der Analyse-Seite durchfuehren.")
        return

    result = st.session_state.pipeline_result

    if not result.physics_result:
        st.warning("Physics Layer war nicht aktiviert. Bitte Config pruefen.")
        return

    physics = result.physics_result

    st.markdown("""
    Die Physics-Layer Analyse basiert auf drei Model Laws:
    - **Gesetz A (Stabilitaet):** Teste ob Muster ueber Zeit stabil bleiben
    - **Gesetz B (Least-Action):** Waehle die einfachste Pipeline
    - **Gesetz C (Criticality):** Identifiziere kritische Zustaende
    """)

    st.divider()

    # Model Law A: Stability
    st.subheader("Gesetz A: Stabilitaet")

    col1, col2 = st.columns(2)

    with col1:
        stability_pct = physics.stability_score * 100
        st.metric(
            "Stabilitaets-Score",
            f"{physics.stability_score:.3f}",
            delta=f"{'Stabil' if physics.is_stable_law else 'Instabil'}",
            delta_color="normal" if physics.is_stable_law else "inverse",
        )

        st.progress(min(physics.stability_score, 1.0))

    with col2:
        st.metric("Hurst-Exponent", f"{physics.hurst_exponent:.3f}")
        st.caption(
            "H > 0.5: Trending, H < 0.5: Mean-Reverting, H = 0.5: Random Walk"
        )

    st.divider()

    # Model Law C: Criticality
    st.subheader("Gesetz C: Criticality")

    col1, col2, col3 = st.columns(3)

    with col1:
        crit_color = {
            "LOW": "green",
            "MEDIUM": "yellow",
            "HIGH": "orange",
            "CRITICAL": "red",
        }.get(physics.criticality_level, "gray")

        st.metric(
            "Criticality-Score",
            f"{physics.criticality_score:.3f}",
        )
        st.markdown(f"**Level:** :{crit_color}[{physics.criticality_level}]")

    with col2:
        st.metric("Regime-Komplexitaet", physics.regime_complexity)

    with col3:
        st.metric("Empfohlene Max-Picks", physics.recommended_max_picks)

    st.divider()

    # Avalanche Analysis
    st.subheader("Avalanche-Analyse")

    if physics.avalanche_result:
        avalanche = physics.avalanche_result

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Theta (Verlustwahrscheinlichkeit)", f"{avalanche.theta:.3f}")

        with col2:
            state_color = {
                "SAFE": "green",
                "MODERATE": "yellow",
                "WARNING": "orange",
                "CRITICAL": "red",
            }.get(avalanche.state.value, "gray")

            st.metric("Avalanche-State", avalanche.state.value)
            st.markdown(f":{state_color}[{avalanche.state.value}]")

        with col3:
            st.metric(
                "Wett-Empfehlung",
                "JA" if avalanche.is_safe_to_bet else "NEIN",
                delta="Safe" if avalanche.is_safe_to_bet else "Risiko",
                delta_color="normal" if avalanche.is_safe_to_bet else "inverse",
            )

        # Theta visualization
        st.markdown("### Theta-Schwellen")

        try:
            import plotly.graph_objects as go

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avalanche.theta * 100,
                number={"suffix": "%"},
                title={"text": "Verlustwahrscheinlichkeit (Theta)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 50], "color": "lightgreen"},
                        {"range": [50, 75], "color": "yellow"},
                        {"range": [75, 85], "color": "orange"},
                        {"range": [85, 100], "color": "red"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 85,
                    },
                },
            ))

            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        except ImportError:
            st.info("Plotly nicht installiert fuer Gauge-Chart.")

    else:
        st.info("Keine Avalanche-Analyse verfuegbar. Bitte Kombination angeben.")


# --- Page: Config ---
def page_config() -> None:
    """Konfigurations-Uebersicht und -Bearbeitung."""
    st.title("Konfiguration")

    if not st.session_state.config:
        st.warning("Keine Konfiguration geladen. Bitte auf Home-Seite laden.")
        return

    config = st.session_state.config

    # Display current config
    st.subheader("Aktuelle Konfiguration")

    tabs = st.tabs(["Allgemein", "Physics", "Analyse", "Spiele"])

    with tabs[0]:
        st.markdown("### Allgemeine Einstellungen")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Version", config.version, disabled=True)
            st.text_input("Aktives Spiel", config.active_game, disabled=True)

        with col2:
            st.checkbox("Debug-Modus", config.debug, disabled=True)

    with tabs[1]:
        st.markdown("### Physics-Layer Einstellungen")

        physics_cfg = config.physics

        col1, col2 = st.columns(2)

        with col1:
            st.checkbox("Model Laws aktiviert", physics_cfg.enable_model_laws, disabled=True)
            st.slider(
                "Stabilitaets-Threshold",
                0.0, 1.0,
                physics_cfg.stability_threshold,
                disabled=True,
            )
            st.checkbox("Least-Action aktiviert", physics_cfg.enable_least_action, disabled=True)

        with col2:
            st.checkbox("Avalanche aktiviert", physics_cfg.enable_avalanche, disabled=True)
            st.checkbox("Anti-Avalanche Modus", physics_cfg.anti_avalanche_mode, disabled=True)
            st.slider(
                "Criticality Warning",
                0.0, 1.0,
                physics_cfg.criticality_warning_threshold,
                disabled=True,
            )
            st.slider(
                "Criticality Critical",
                0.0, 1.0,
                physics_cfg.criticality_critical_threshold,
                disabled=True,
            )

    with tabs[2]:
        st.markdown("### Analyse-Einstellungen")

        analysis_cfg = config.analysis

        col1, col2 = st.columns(2)

        with col1:
            st.slider(
                "Min Frequenz Threshold",
                0.0, 1.0,
                analysis_cfg.min_frequency_threshold,
                disabled=True,
            )
            st.number_input(
                "Duo Min Occurrences",
                value=analysis_cfg.duo_min_occurrences,
                disabled=True,
            )
            st.number_input(
                "Zehnergruppen Max/Gruppe",
                value=analysis_cfg.zehnergruppen_max_per_group,
                disabled=True,
            )

        with col2:
            st.slider(
                "Max Frequenz Threshold",
                0.0, 1.0,
                analysis_cfg.max_frequency_threshold,
                disabled=True,
            )
            st.number_input(
                "Trio Min Occurrences",
                value=analysis_cfg.trio_min_occurrences,
                disabled=True,
            )
            st.checkbox(
                "111-Prinzip aktiviert",
                analysis_cfg.enable_111_principle,
                disabled=True,
            )

    with tabs[3]:
        st.markdown("### Spiel-Konfigurationen")

        for game_key, game_cfg in config.games.items():
            with st.expander(f"{game_cfg.name} ({game_key})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.text_input(f"Name ({game_key})", game_cfg.name, disabled=True, key=f"name_{game_key}")
                    st.text_input(
                        f"Zahlenbereich ({game_key})",
                        f"{game_cfg.numbers_range[0]} - {game_cfg.numbers_range[1]}",
                        disabled=True,
                        key=f"range_{game_key}",
                    )

                with col2:
                    st.number_input(
                        f"Zahlen pro Ziehung ({game_key})",
                        value=game_cfg.numbers_to_draw,
                        disabled=True,
                        key=f"draw_{game_key}",
                    )
                    if game_cfg.bonus_range:
                        st.text_input(
                            f"Bonus-Bereich ({game_key})",
                            f"{game_cfg.bonus_range[0]} - {game_cfg.bonus_range[1]}",
                            disabled=True,
                            key=f"bonus_{game_key}",
                        )

    st.divider()

    # Export config
    st.subheader("Config exportieren")

    import yaml

    try:
        from kenobase.core.config import _config_to_yaml_dict

        config_dict = _config_to_yaml_dict(config)
        config_yaml = yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)

        st.download_button(
            "YAML herunterladen",
            data=config_yaml,
            file_name="kenobase_config.yaml",
            mime="text/yaml",
        )

        with st.expander("Config als YAML"):
            st.code(config_yaml, language="yaml")

    except Exception as e:
        st.error(f"Fehler beim Export: {e}")


# --- Main Navigation ---
def main() -> None:
    """Hauptfunktion mit Navigation."""
    init_session_state()

    # Sidebar navigation
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Seite waehlen:",
        ["Home", "Analysis", "Backtest", "Physics", "Config"],
        label_visibility="collapsed",
    )

    # Status indicators in sidebar
    st.sidebar.divider()
    st.sidebar.markdown("### Status")

    if st.session_state.config:
        st.sidebar.success(f"Config: v{st.session_state.config.version}")
    else:
        st.sidebar.warning("Config: Nicht geladen")

    if st.session_state.data_loaded:
        st.sidebar.success(f"Daten: {len(st.session_state.draws)} Ziehungen")
    else:
        st.sidebar.warning("Daten: Nicht geladen")

    if st.session_state.pipeline_result:
        st.sidebar.success("Analyse: Verfuegbar")
    else:
        st.sidebar.info("Analyse: Nicht ausgefuehrt")

    # Render selected page
    pages = {
        "Home": page_home,
        "Analysis": page_analysis,
        "Backtest": page_backtest,
        "Physics": page_physics,
        "Config": page_config,
    }

    pages[page]()

    # Footer
    st.sidebar.divider()
    st.sidebar.caption("Kenobase V2.0")
    st.sidebar.caption("Physics-inspired Lottery Analysis")


if __name__ == "__main__":
    main()
