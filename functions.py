import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
import os
import re

def process_folder(path_to_folder, chan_name, target_freq=None, extra_name=None, hf=45, lf=1):
    if not extra_name:
        extra_name = os.path.basename(path_to_folder)+': '
    eeg_data = []    
    for filename in os.listdir(path_to_folder):
        if '_ExG.csv' in filename:
            full_path = os.path.join(path_to_folder, filename)
            
            if extra_name:
                filename = extra_name+filename[:filename.rindex('_')]
            else:
                filename = filename[:filename.rindex('_')]
            
            target = target_freq
            if target_freq == 'auto':
                number_pattern = r'\d+(?:\.\d+)?'
                filename_copy = filename.replace('_', '.')
                target = [float(x) for x in re.findall(number_pattern, filename_copy)]

            eeg_data.append(EEG_Data(full_path,title = filename, chan_name=chan_name, stimulus_frequency=target, hf=hf, lf=lf))
    return eeg_data

chan_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']

class EEG_Data:
    raw_signal: np.ndarray = None
    filtered_signal: np.ndarray = None
    epoch_signal: np.ndarray = None
    chan_name: list = None
    chan_list: list = None
    n_chan: int = None
    title: str = None
    stimulus_frequency: float = None
    hf: float = None
    lf: float = None

    def __init__(self, path: str, title: str = None, stimulus_frequency: float= None, chan_name: list = None, epoch_length = 6, fs=250, lf=5, hf=45):
        self.data = pd.read_csv(path)
        self.title = title
        self.stimulus_frequency = stimulus_frequency
        self.chan_name = chan_name.copy()
        
        self.n_chan = len(chan_name)
        self.chan_list = ['ch' + str(i) for i in range(1, self.n_chan + 1)]

        self.raw_signal = self.data[chan_list].to_numpy().T
        self.hf = hf
        self.lf = lf
        self.filtered_signal = np.array(filt(self.raw_signal, fs, lf, hf))
        self.epoch_signal = reshape_to_epochs(self.filtered_signal, epoch_length=epoch_length, fs=fs)

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
        


    def remove_channels(self, chan_name_list):
        print('Original channel names:', self.chan_name)
        for channel in chan_name_list:
            # get index in chan_name where channel is
            index = self.chan_name.index(channel)

            # remove channel from chan_name
            self.chan_name.pop(index)
            self.chan_list.pop(index)
            self.n_chan = len(self.chan_name)

            # remove channel from filtered_signal, raw_signal, epoch_signal
            self.filtered_signal = np.delete(self.filtered_signal, index, 0)
            self.raw_signal = np.delete(self.raw_signal, index, 0)
            self.epoch_signal = np.delete(self.epoch_signal, index, 0)
        print('Updated channel names:', self.chan_name)


            
   


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
def filt(sig,fs, lf, hf):
    filt_sig = custom_filter(sig, 45, 55, fs, 'bandstop') 
    filt_sig = custom_filter(sig, lf, hf, fs, 'bandpass')
    return filt_sig


def psd_plot_interactive(eeg_data, chan_name, nperseg_max=20, nfft_max=20, fs=250, ylim=-1, xmin=None, xlim=None, fig_x=15, fig_y=10):
    
    def plot_psd(nperseg, nfft, x_min, x_lim, y_lim):
        for eeg in eeg_data:
            if x_min is None:
                x_min = max(eeg.lf - 2, 1)
            
            if x_lim is None:
                x_lim = eeg.hf + 2

            title = eeg.title
            line = eeg.stimulus_frequency
            
            fig, ax = plt.subplots(figsize=(fig_x, fig_y))
            for i in range(len(eeg.filtered_signal)):
                f, psd = signal.welch(eeg.filtered_signal[i], fs=fs, nperseg=nperseg*fs, noverlap=0, nfft=nfft*fs)
                ax.plot(f, psd, label='{}'.format(chan_name[i]))
            if line:
                for l in line:
                    ax.axvline(x=l, color='gray', linestyle='--')
                    ax.text(l+0.2, 0, 'f = '+str(l)+'Hz', color='lightgray')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Amplitude')
            
            ax.set_xlim(x_min, x_lim)
            ax.set_xticks(np.arange(x_min, x_lim, 1))
            if y_lim != -1:
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

    widgets.interact(plot_psd, nperseg=nperseg_slider, nfft=nfft_slider, x_min=xmin, x_lim=xlim, y_lim=ylim)

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


def reshape_to_epochs(data, epoch_length=3, fs=250):
    n_channels, n_samples = data.shape
    n_epochs = int(n_samples / (epoch_length * fs))
    epoch_samples = epoch_length * fs
    epoch_data = np.zeros((n_epochs, n_channels, epoch_samples))
    
    for i in range(n_epochs):
        start = i * epoch_samples
        end = start + epoch_samples
        epoch_data[i] = data[:, start:end]

    return epoch_data

