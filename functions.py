import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import mne
import ipywidgets as widgets
from dataclasses import dataclass


chan_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']
class EEG_Data:
    raw_signal: np.ndarray = None
    filtered_signal: np.ndarray = None
    epoch_signal: np.ndarray = None

    def cut_signal(self, start, end=None, cut_to=True, fs=250):
        start = int(start * fs)
        if end:
            end = int(end * fs)
        output = []
        for i in range(0, len(self.filtered_signal)):
            if cut_to:
                output.append(self.filtered_signal[i][start:end])
            else:
                output.append(self.filtered_signal[i][start:len(self.filtered_signal[i]) - end])       
        self.filtered_signal = np.array(output)


    def __init__(self, path: str, title: str = None, stimulus_frequency: float= None, chan_name: list = None):
        self.data = pd.read_csv(path)
        self.title = title
        self.stimulus_frequency = stimulus_frequency
        self.chan_name = chan_name
        
        self.n_chan = len(chan_name)
        self.chan_list = ['ch' + str(i) for i in range(1, self.n_chan + 1)]

        self.raw_signal = self.data[chan_list].to_numpy().T
        self.filtered_signal = np.array(filt(self.raw_signal))


# Source https://github.com/Mentalab-hub/explorepy/blob/master/examples/ssvep_demo/offline_analysis.py
def custom_filter(exg, lf, hf, fs, type):
    """
    
    Args:
        exg: EEG signal with the shape: (N_chan, N_sample)
        lf: Low cutoff frequency
        hf: High cutoff frequency
        fs: Sampling rate
        type: Filter type, 'bandstop' or 'bandpass'

    Returns:
        (numpy ndarray): Filtered signal (N_chan, N_sample)
    """
    N = 4
    b, a = signal.butter(N, [lf / (fs/2), hf / (fs/2)], type)
    return signal.filtfilt(b, a, exg)

# Signal filtering, bandpass 1-30Hz, bandstop 45-55Hz
def filt(sig,fs=250, lf=1, hf=30):
    # filt_sig = custom_filter(sig, 45, 55, fs, 'bandstop') 
    filt_sig = custom_filter(sig, lf, hf, fs, 'bandpass')
    return filt_sig


def psd_plot_interactive(eeg_data, chan_name, nperseg_max=20, nfft_max=20, fs=250, x_min=1, x_lim=30, y_lim=125, fig_x=15,fig_y=5):
    
    def plot_psd(nperseg, nfft):
        for eeg in eeg_data:
            n_samples = eeg.filtered_signal.shape[1]
            title = eeg.title
            line = eeg.stimulus_frequency
            
            fig, ax = plt.subplots(figsize=(fig_x, fig_y))
            for i in range(len(eeg.filtered_signal)):
                f, psd = signal.welch(eeg.filtered_signal[i], fs=fs, nperseg=nperseg*fs, noverlap=0, nfft=nfft*fs)
                ax.plot(f, psd, label='{}'.format(chan_name[i]))
            if line:
                ax.axvline(x=line, color='gray', linestyle='--')
                ax.text(line+0.2, 20, 'f = '+str(line)+'Hz', fontsize=12, color='gray')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Amplitude')
            ax.set_xlim(x_min, x_lim)
            ax.set_xticks(np.arange(x_min, x_lim, 1))
            ax.set_ylim(0, y_lim)
            ax.legend()
            ax.set_title('PSD ' + title)
            plt.tight_layout()
            plt.show()

    def update_nfft_range(*args):
        nfft_slider.min = nperseg_slider.value

    nperseg_slider = widgets.IntSlider(value=20, min=1, max=nperseg_max, step=1, description='nperseg*fs:')
    nfft_slider = widgets.IntSlider(value=20, min=nperseg_slider.value, max=nfft_max, step=1, description='nfft*fs:')

    nperseg_slider.observe(update_nfft_range, 'value')

    widgets.interact(plot_psd, nperseg=nperseg_slider, nfft=nfft_slider)

def amplitude_plot(filt_signal, chan_name, title = '', fs=250, lim = 150,xlim=None):
    n_samples = filt_signal.shape[1]

    # Generate a time vector for the signal
    t = np.arange(n_samples) / fs

    # Create a single plot with a single subplot
    fig, ax = plt.subplots(figsize=(15, 3))

    # Loop through each signal and plot it on the same subplot
    for i in range(len(filt_signal)):
        ax.plot(t, filt_signal[i], label='{}'.format(chan_name[i]))

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_ylim(-1*lim, lim)
    if xlim:
        ax.set_xlim(0, xlim)
    ax.legend()
    ax.set_title(title)
    plt.tight_layout()
    plt.show()




def reshape_to_epochs(data, epoch_length=3, sfreq=250):
    n_channels, n_samples = data.shape
    n_epochs = int(n_samples / (epoch_length * sfreq))
    epoch_samples = epoch_length * sfreq
    epoch_data = np.zeros((n_epochs, n_channels, epoch_samples))
    
    for i in range(n_epochs):
        start = i * epoch_samples
        end = start + epoch_samples
        epoch_data[i] = data[:, start:end]

    return epoch_data