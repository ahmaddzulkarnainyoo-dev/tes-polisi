import plotly.graph_objects as go
import streamlit as st

def generate_psychogram(scores):
    # scores: dict {'Kecerdasan': 85, 'Kepribadian': 70, 'Sikap Kerja': 90, ...}
    
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Radar Chart harus 'tertutup', jadi kita tambahin data pertama di akhir
    categories = [*categories, categories[0]]
    values = [*values, values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Profil Psikologis Anda',
        line_color='#1f77b4'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        title="Psychogram Result"
    )
    
    return fig

# Cara pakenya di Streamlit:
# score_data = {'Kecerdasan': 80, 'Kepribadian': 65, 'Sikap Kerja': 75, 'Adaptasi': 85}
# st.plotly_chart(generate_psychogram(score_data))
 
