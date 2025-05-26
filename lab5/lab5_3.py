import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

START_AMP = 1.2
START_FREQ = 1.0
START_PHASE = 0.0
START_NOISE_MEAN = 0.0
START_NOISE_VAR = 0.05

time = np.linspace(0, 10, 1000)


def generate_harmonic(amp, freq, phase, t):
    return amp * np.sin(2 * np.pi * freq * t + phase)


def apply_noise(signal, noise):
    return signal + noise


def noise_array(mean, var, size):
    return np.random.normal(loc=mean, scale=np.sqrt(var), size=size)


def average_filter(signal, win=20):
    output = np.zeros_like(signal)
    for i in range(len(signal)):
        start = max(0, i - win)
        end = min(len(signal), i + win)
        output[i] = np.mean(signal[start:end])
    return output


st.title("Синусоїда з шумом та фільтрацією (Altair + Streamlit)")
st.sidebar.header("Параметри сигналу")

amp = st.sidebar.slider('Амплітуда', 0.1, 3.0, START_AMP, step=0.1)
freq = st.sidebar.slider('Частота (Гц)', 0.1, 10.0, START_FREQ, step=0.1)
phase = st.sidebar.slider('Фаза (рад)', 0.0, 2 * np.pi, START_PHASE, step=0.1)
mean_n = st.sidebar.slider('Середнє шуму', -1.0, 1.0, START_NOISE_MEAN, step=0.05)
var_n = st.sidebar.slider('Дисперсія шуму', 0.0, 1.0, START_NOISE_VAR, step=0.01)

selected_filter = st.sidebar.selectbox('Оберіть тип фільтра', ['Ковзне середнє'])

base_signal = generate_harmonic(amp, freq, phase, time)
noise_signal = noise_array(mean_n, var_n, len(time))
noisy_signal = apply_noise(base_signal, noise_signal)

if selected_filter == 'Ковзне середнє':
    filtered_signal = average_filter(noisy_signal, win=20)
else:
    filtered_signal = noisy_signal


df = pd.DataFrame({
    'Час': time,
    'Сигнал без шуму': base_signal,
    'Сигнал з шумом': noisy_signal,
    'Після фільтра': filtered_signal
})

st.subheader("Сигнал без шуму + шум")
chart1 = alt.Chart(df).mark_line(color='gray').encode(
    x='Час', y='Сигнал з шумом') + alt.Chart(df).mark_line(color='blue').encode(
    x='Час', y='Сигнал без шуму')
st.altair_chart(chart1.properties(width=750, height=300), use_container_width=True)

st.subheader("Сигнал без шуму + після фільтра")
chart2 = alt.Chart(df).mark_line(color='blue').encode(
    x='Час', y='Сигнал без шуму') + alt.Chart(df).mark_line(color='green').encode(
    x='Час', y='Після фільтра')
st.altair_chart(chart2.properties(width=750, height=300), use_container_width=True)