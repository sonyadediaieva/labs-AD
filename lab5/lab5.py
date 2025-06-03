import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button, CheckButtons
import numpy as np
from scipy.signal import butter, filtfilt


def build_control_panel(fig, grid_area, refresh_view):
    control_axes = {}
    controls = {}

    layout = grid_area.subgridspec(10, 1)

    # Чекбокси
    control_axes['Шум'] = fig.add_subplot(layout[0])
    noise_switch = CheckButtons(control_axes['Шум'], ['Показати шум'], [True])
    noise_switch.on_clicked(lambda label: refresh_view(False))

    control_axes['Фільтр'] = fig.add_subplot(layout[1])
    filter_switch = CheckButtons(control_axes['Фільтр'], ['Показати фільтр'], [True])
    filter_switch.on_clicked(lambda label: refresh_view(False))

    # Слайдери
    slider_specs = [
        ('Амплітуда', (0.1, 4, 1)),
        ('Частота', (0.5, 12, 2)),
        ('Фаза', (0, 2 * np.pi, np.pi / 3)),
        ('Середнє шуму', (-1.5, 1.5, 0)),
        ('Дисперсія шуму', (0.1, 1.5, 0.4))
    ]

    for idx, (label, (low, high, default)) in enumerate(slider_specs, start=2):
        control_axes[label] = fig.add_subplot(layout[idx])
        controls[label] = Slider(control_axes[label], label, low, high, valinit=default)
        controls[label].on_changed(lambda val, flag=(label in ['Середнє шуму', 'Дисперсія шуму']): refresh_view(flag))

    control_axes['Частота зрізу'] = fig.add_subplot(layout[7])
    controls['Частота зрізу'] = Slider(control_axes['Частота зрізу'], 'Частота зрізу', 1.0, 50.0, valinit=12.0)
    controls['Частота зрізу'].on_changed(lambda val: refresh_view(False))

    control_axes['Скидання'] = fig.add_subplot(layout[8])
    reset_button = Button(control_axes['Скидання'], 'Скинути')

    def handle_reset(event):
        for ctrl in controls.values():
            try:
                ctrl.reset()
            except Exception:
                pass
        refresh_view(True)

    reset_button.on_clicked(handle_reset)
    return controls, noise_switch, filter_switch, reset_button

# Запуск програми
def launch_plot_app():
    fig = plt.figure(figsize=(13, 6))
    main_layout = GridSpec(1, 2, figure=fig, width_ratios=[4, 2], wspace=0.25)
    graph_area = fig.add_subplot(main_layout[0, 0])

    signal_curve = noisy_curve = filtered_curve = None
    generated_noise = None

#Оновлення графіка
    def refresh_view(regenerate_noise):
        nonlocal signal_curve, noisy_curve, filtered_curve, generated_noise
        t_axis = np.linspace(0, 1, 600)

        amp = controls['Амплітуда'].val
        freq = controls['Частота'].val
        phase = controls['Фаза'].val

        base_signal = amp * np.sin(2 * np.pi * freq * t_axis + phase)

        if signal_curve is None:
            signal_curve, = graph_area.plot(t_axis, base_signal, label='Сигнал', color='#1f77b4')
        else:
            signal_curve.set_ydata(base_signal)

        if regenerate_noise or generated_noise is None:
            mean_noise = controls['Середнє шуму'].val
            std_dev = controls['Дисперсія шуму'].val
            generated_noise = np.random.normal(mean_noise, std_dev, size=t_axis.shape)

        combined_signal = base_signal + generated_noise

        if noise_toggle.get_status()[0]:
            if noisy_curve is None:
                noisy_curve, = graph_area.plot(t_axis, combined_signal, label='Шум', color='#ff7f0e', alpha=0.5)
            else:
                noisy_curve.set_ydata(combined_signal)
        elif noisy_curve is not None:
            noisy_curve.remove()
            noisy_curve = None

        if filter_toggle.get_status()[0]:
            cutoff = controls['Частота зрізу'].val
            b, a = butter(4, cutoff, btype='low', fs=600)
            filtered_output = filtfilt(b, a, combined_signal)
            if filtered_curve is None:
                filtered_curve, = graph_area.plot(t_axis, filtered_output, label='Фільтр', color='#2ca02c')
            else:
                filtered_curve.set_ydata(filtered_output)
        elif filtered_curve is not None:
            filtered_curve.remove()
            filtered_curve = None

        graph_area.relim()
        graph_area.autoscale_view()
        graph_area.legend()
        fig.canvas.draw_idle()

    controls, noise_toggle, filter_toggle, reset_button = build_control_panel(fig, main_layout[0, 1], refresh_view)
    refresh_view(True)
    plt.show()

if __name__ == '__main__':
    launch_plot_app()

