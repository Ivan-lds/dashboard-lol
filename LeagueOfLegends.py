import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

df = pd.read_csv('dataset.csv')
df.head()

st.title("Dashboard de Análise de Jogos")
st.markdown("Análise detalhada de dados de jogos")

@st.cache_data
def load_data():
    df['gameDuration'] = df['gameDuration'] / 60
  
    boolean_columns = ['win', 'firstBlood', 'firstTower', 'firstInhibitor', 'firstBaron', 'firstDragon']
    for col in boolean_columns:
        df[col] = df[col].map({1: 'Sim', 0: 'Não'})
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Erro ao carregar os dados. Verifique se o arquivo dataset.csv está no local correto.")
    st.stop()

st.sidebar.header("Filtros")

season_filter = st.sidebar.multiselect(
    "Selecione as temporadas",
    options=sorted(df['seasonId'].unique()),
    default=sorted(df['seasonId'].unique())
)

df_filtered = df[df['seasonId'].isin(season_filter)]

st.subheader("Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

total_games = len(df_filtered)
col1.metric("Total de Jogos", f"{total_games:,}")

avg_duration = df_filtered['gameDuration'].mean()
col2.metric("Duração Média", f"{avg_duration:.1f} min")

win_rate = (df_filtered['win'] == 'Sim').mean() * 100
col3.metric("Taxa de Vitória", f"{win_rate:.1f}%")

first_objectives = ['firstBlood', 'firstTower', 'firstInhibitor', 'firstBaron', 'firstDragon']
most_common_first = df_filtered[first_objectives].apply(lambda x: (x == 'Sim').sum()).idxmax()
col4.metric("Objetivo Mais Comum", most_common_first.replace('first', ''))


st.markdown("---")

col_top1, col_top2 = st.columns(2)

with col_top1:
    fig_duration = px.histogram(
        df_filtered,
        x='gameDuration',
        nbins=30,
        title='Distribuição da Duração dos Jogos',
        labels={'gameDuration': 'Duração (minutos)', 'count': 'Quantidade de Jogos'}
    )
    fig_duration.update_layout(
        title_x=0.5,
        showlegend=False
    )
    st.plotly_chart(fig_duration, use_container_width=True)

with col_top2:
    first_objective_rates = []
    for obj in first_objectives:
        rate = (df_filtered[obj] == 'Sim').mean() * 100
        first_objective_rates.append({
            'Objetivo': obj.replace('first', ''),
            'Taxa (%)': rate
        })

    df_rates = pd.DataFrame(first_objective_rates)

    fig_objectives = px.bar(
        df_rates,
        x='Objetivo',
        y='Taxa (%)',
        title='Taxa de Primeiros Objetivos',
        color='Taxa (%)',
        color_continuous_scale='Viridis'
    )
    fig_objectives.update_layout(
        title_x=0.5,
        showlegend=False
    )
    st.plotly_chart(fig_objectives, use_container_width=True)

col_bottom1, col_bottom2 = st.columns(2)

with col_bottom1:
    season_stats = df_filtered.groupby('seasonId').agg({
        'gameDuration': 'mean',
        'win': lambda x: (x == 'Sim').mean() * 100
    }).reset_index()

    fig_season = go.Figure()
    fig_season.add_trace(go.Scatter(
        x=season_stats['seasonId'],
        y=season_stats['gameDuration'],
        name='Duração Média',
        line=dict(color='blue')
    ))
    fig_season.add_trace(go.Scatter(
        x=season_stats['seasonId'],
        y=season_stats['win'],
        name='Taxa de Vitória',
        line=dict(color='red'),
        yaxis='y2'
    ))

    fig_season.update_layout(
        title='Evolução da Duração e Taxa de Vitória por Temporada',
        xaxis_title='Temporada',
        yaxis_title='Duração Média (minutos)',
        yaxis2=dict(
            title='Taxa de Vitória (%)',
            overlaying='y',
            side='right'
        ),
        title_x=0.5
    )
    st.plotly_chart(fig_season, use_container_width=True)

with col_bottom2:
    objective_matrix = df_filtered[first_objectives].apply(lambda x: (x == 'Sim').astype(int))
    correlation_matrix = objective_matrix.corr()

    fig_corr = px.imshow(
        correlation_matrix,
        title='Correlação entre Primeiros Objetivos',
        color_continuous_scale='RdBu',
        labels=dict(
            x='Objetivo',
            y='Objetivo',
            color='Correlação'
        )
    )
    fig_corr.update_layout(
        title_x=0.5,
        xaxis=dict(tickangle=45)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("""
### Explicações das Análises

1. **Métricas Principais**:
   - Total de Jogos: Número total de partidas analisadas
   - Duração Média: Tempo médio de duração das partidas em minutos
   - Taxa de Vitória: Porcentagem de jogos vencidos
   - Objetivo Mais Comum: Objetivo que mais frequentemente é conquistado primeiro

2. **Distribuição da Duração**:
   - Mostra como os tempos de jogo estão distribuídos
   - Ajuda a identificar a duração típica de uma partida

3. **Taxa de Primeiros Objetivos**:
   - Mostra a frequência com que cada objetivo é conquistado primeiro
   - Permite identificar quais objetivos são mais prioritários

4. **Análise Temporal**:
   - Mostra como a duração média e a taxa de vitória evoluem ao longo das temporadas
   - Permite identificar tendências e mudanças no meta-jogo

5. **Correlação entre Objetivos**:
   - Mostra como os diferentes objetivos se relacionam entre si
   - Valores próximos de 1 indicam forte correlação positiva
   - Valores próximos de -1 indicam forte correlação negativa
   - Valores próximos de 0 indicam pouca ou nenhuma correlação
""")
