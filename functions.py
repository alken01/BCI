import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import mne
from dataclasses import dataclass

@dataclass
class EEG_Data:
    data: pd.core.frame.DataFrame = None
    raw_signal: np.ndarray = None
    filtered_signal: np.ndarray = None
    cleaned_signal: np.ndarray = None
    epoch_signal: np.ndarray = None
    title: str = None
    stimulus_frequency: float= None
    cut_start:int = None
    cut_end:int = None

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
    filt_sig = custom_filter(sig, 45, 55, fs, 'bandstop') 
    filt_sig = custom_filter(filt_sig, lf, hf, fs, 'bandpass')
    return filt_sig


def psd_plot(filt_signal, chan_name, title='', fs=250, x_min=1, x_lim=30, y_lim = 125, line=None):
    n_samples = filt_signal.shape[1]

    # Generate a time vector for the signal
    t = np.arange(n_samples) / fs

    # Create a single plot with a single subplot
    fig, ax = plt.subplots(figsize=(15, 3))

    # Loop through each signal and plot it on the same subplot
    for i in range(len(filt_signal)):
        f, psd = signal.welch(filt_signal[i], fs=fs, nperseg=20*fs, noverlap=0, nfft=20*fs)
        ax.plot(f, psd, label='{}'.format(chan_name[i]))

    if line:
        ax.axvline(x=line, color='gray', linestyle='--')
        ax.text(line+0.2, 20, 'f = '+str(line)+'Hz', fontsize=12, color='gray')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_xlim(x_min, x_lim)
    ax.set_ylim(0, y_lim)
    ax.legend()
    ax.set_title('PSD ' + title)
    plt.tight_layout()
    plt.show()


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

def cut_ends(filt_signal, start, end=None, fs=250):
    cut_start = int(start * fs)
    cut_end = int(end * fs)
    output = []
    
    for i in range(0,len(filt_signal)):
        output.append(filt_signal[i][cut_start:len(filt_signal[i])-cut_end])
    return np.array(output)

def cut_from_to(filt_signal, start, end, fs=250):
    cut_start = int(start * fs)
    cut_end = int(end * fs)
    output = []
    
    for i in range(0,len(filt_signal)):
        output.append(filt_signal[i][cut_start:cut_end])
    return np.array(output)


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