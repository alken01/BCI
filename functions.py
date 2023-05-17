import pandas as pd
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
import os
import re
import csv

def process_folder(path_to_folder, chan_name, target_freq=None, extra_name=None, hf=45, lf=1, epoch_length=6, filter=True):
    if extra_name == 'path':
        extra_name = os.path.basename(path_to_folder)+': '
    eeg_data = []    
    for filename in os.listdir(path_to_folder):
        if '_ExG.csv' in filename:
            full_path = os.path.join(path_to_folder, filename)
            
            filename = filename[:filename.rindex('_')]
            
            if extra_name:
                filename = extra_name+filename
            
            target = target_freq
            if target_freq == 'auto':
                number_pattern = r'\d+(?:\.\d+)?'
                filename_copy = filename.replace('_', '.')
                target = [float(x) for x in re.findall(number_pattern, filename_copy)]

            eeg_data.append(EEG_Data(full_path,title = filename, chan_name=chan_name, stimulus_frequency=target, hf=hf, lf=lf, epoch_length=epoch_length, filter=filter))
    return eeg_data

# chan_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6']

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
    timestamp: np.ndarray = None

    def __init__(self, path: str = None, title: str = None, stimulus_frequency: float = None, chan_name: list = None, epoch_length=6, fs=250, lf=1, hf=45, filter=True):
        self.title = title
        self.stimulus_frequency = stimulus_frequency
        self.chan_name = chan_name.copy() 
        self.n_chan = len(chan_name) 
        self.chan_list = ['ch' + str(i) for i in range(1, self.n_chan + 1)]

        if path is not None:
            self.data = pd.read_csv(path)
            self.timestamp = self.data['TimeStamp'].to_numpy()
            try: 
                self.raw_signal = self.data[self.chan_name].to_numpy().T
            except:
                self.raw_signal = self.data[self.chan_list].to_numpy().T
            self.hf = hf
            self.lf = lf
            if filter:
                self.filtered_signal = np.array(filt(self.raw_signal, fs, lf, hf))
            else:
                self.filtered_signal = self.raw_signal.copy()
            self.epoch_signal = reshape_to_epochs(self.filtered_signal, epoch_length=epoch_length, fs=fs)


    def get_epoched_signal(self, epoch_length=6, fs=250):
        return reshape_to_epochs(self.filtered_signal, epoch_length=epoch_length, fs=fs)
    
    def add_signal(self, eeg, stack=False):
        if eeg is None:
            return
        if isinstance(eeg, EEG_Data):
            eeg = eeg.filtered_signal
        if self.filtered_signal is None:
            self.filtered_signal = eeg
        else:
            # keep the minimum length of the two signals
            min_length = min(self.filtered_signal.shape[1], eeg.shape[1])
            # cut the signals to the minimum length
            self.filtered_signal = self.filtered_signal[:, :min_length]
            eeg = eeg[:, :min_length]
            # add the signals
            if stack:
                self.filtered_signal = self.filtered_signal + eeg
            else:
                self.filtered_signal = np.vstack((self.filtered_signal, eeg))


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
    filt_sig = custom_filter(filt_sig, lf, hf, fs, 'bandpass')
    return filt_sig


def new_psd_plot(eeg_data, chan_name, nperseg=20, nfft=20, fs=250, ylim=-1, xmin=None, xlim=None, fig_x=15, fig_y=10):
    if xmin is None:
        xmin = max(eeg_data.lf - 2, 1)
        
    if xlim is None:
        xlim = eeg_data.hf + 2

    title = eeg_data.title
    line = eeg_data.stimulus_frequency
    
    fig, ax = plt.subplots(figsize=(fig_x, fig_y))
    for i in range(len(chan_name)):
        f, psd = signal.welch(eeg_data.filtered_signal[i], fs=fs, nperseg=nperseg*fs, noverlap=0, nfft=nfft*fs)
        ax.plot(f, psd, label='{}'.format(chan_name[i]))
    if line:
        for l in line:
            ax.axvline(x=l, color='gray', linestyle='--')
            ax.text(l+0.2, 0, 'f = '+str(l)+'Hz', color='lightgray')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    
    ax.set_xlim(xmin, xlim)
    ax.set_xticks(np.arange(xmin, xlim, 1))
    if ylim != -1:
        ax.set_ylim(0, ylim)
    ax.legend()
    ax.set_title('PSD ' + title)
    plt.tight_layout()
    plt.show()


def psd_plot_interactive(eeg_data_list, chan_name, nperseg_max=20, nfft_max=20, fs=250, ylim=-1, xmin=None, xlim=None, fig_x=15, fig_y=10):
    
    def plot_psd(nperseg, nfft, x_min, x_lim, y_lim):
        for eeg_data in eeg_data_list:
            if x_min is None:
                x_min = max(eeg_data.lf - 2, 1)
            
            if x_lim is None:
                x_lim = eeg_data.hf + 2

            title = eeg_data.title
            line = eeg_data.stimulus_frequency
            
            fig, ax = plt.subplots(figsize=(fig_x, fig_y))
            for i in range(len(chan_name)):
                f, psd = signal.welch(eeg_data.filtered_signal[i], fs=fs, nperseg=nperseg*fs, noverlap=0, nfft=nfft*fs)
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

def chan_hemisphere(chan_name):
    # left hemisphere -> odd numbers (1,3,5,7) 
    left_hemisphere = [chan for chan in chan_name if chan[-1].isdigit() and int(chan[-1]) % 2 != 0]
    # right hemisphere -> even numbers (2,4,6,8)
    right_hemisphere = [chan for chan in chan_name if chan[-1].isdigit() and int(chan[-1]) % 2 == 0]
    # midline -> z
    midline_hemisphere = [chan for chan in chan_name if chan[-1] == 'z']
    return left_hemisphere, midline_hemisphere, right_hemisphere

def hemisphere_signal_avg(eeg, chan_name):
    left_hemisphere, midline_hemisphere, right_hemisphere = chan_hemisphere(chan_name)

    # seperate the signal into left and right hemisphere and take the average per channel
    left_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in left_hemisphere],:], axis=0)
    right_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in right_hemisphere],:], axis=0)
    midline_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in midline_hemisphere],:], axis=0)
    
    return left_hemisphere_signal, midline_hemisphere_signal, right_hemisphere_signal

def plot_spectrogram_and_bands(eeg,title=None, band_freqs=None, f_min=5, f_max=15, fs=250, nfft=3, nperseg=3):
    if band_freqs:
        f_min = min(band_freqs) - 2
        f_max = max(band_freqs) + 2
    else:
        band_freqs = [f_min, f_max]
    total_signal = np.mean(eeg.filtered_signal, axis=0)
    left_hemisphere_signal, midline_hemisphere_signal, right_hemisphere_signal = hemisphere_signal_avg(eeg, chan_name)

    def masked_spectogram(singal, nperseg=3,nfft=3):
        frequencies, times, spectrogram = signal.spectrogram(singal, fs=fs, nperseg=fs*nperseg, noverlap=fs*nperseg/2, scaling='spectrum', mode='psd', nfft=fs*nfft)
        mask = (frequencies >= f_min) & (frequencies <= f_max)
        spectrogram_masked = spectrogram[mask, :]
        frequencies_masked = frequencies[mask]
        return frequencies_masked, times, spectrogram_masked
    
    # Plot the spectrogram using matplotlib
    
    # fig, axs = plt.subplots(nrows=2, ncols=3,figsize=(15, 6))
    fig, axs = plt.subplots(nrows=2, ncols=3,figsize=(15, 6))
    def plot_sepctro(ax, signal, title):
        frequencies_masked, times, spectrogram_masked = masked_spectogram(signal, nperseg=nperseg,nfft=nfft)
        ax.pcolormesh(times, frequencies_masked, spectrogram_masked)
        ax.set_ylim(f_min, f_max)
        ax.set_ylabel('Frequency [Hz]')
        ax.set_xlabel('Time [sec]')
        ax.set_title(title)
    
    # plot spectro per each channel in a 2 by 4
    # for i, chan in enumerate(chan_name):
    #     if i < 4:
    #         plot_sepctro(axs[0,i], eeg.filtered_signal[i,:], chan)
    #     else:
    #         plot_sepctro(axs[1,i-4], eeg.filtered_signal[i,:], chan)


    plot_sepctro(axs[0,0], left_hemisphere_signal, 'Left Hemisphere Signal')
    plot_sepctro(axs[0,1], midline_hemisphere_signal, 'Midline Signal')
    plot_sepctro(axs[0,2], right_hemisphere_signal, 'Right Hemisphere Signal')

    def plot_bands(ax, signal, title):
        frequencies_masked, times, spectrogram_masked = masked_spectogram(signal)
        # Plot the PSDs in the frequency bands of interest through time
        for i, band_freq in enumerate(band_freqs):
            band_mask = (frequencies_masked >= band_freq-1) & (frequencies_masked <= band_freq+1)
            psd = np.mean(spectrogram_masked[band_mask, :], axis=0)
            ax.plot(times, psd, label=f'{band_freqs[i]} Hz band')
        ax.set_xlim(times[0], times[-1])
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('PSD')
        ax.legend()
        ax.set_title(title)

    if band_freqs:
        plot_bands(axs[1,0], left_hemisphere_signal, 'Left Hemisphere Signal')
        plot_bands(axs[1,1], left_hemisphere_signal-right_hemisphere_signal, 'Delta Left vs Right')
        plot_bands(axs[1,2], right_hemisphere_signal, 'Right Hemisphere Signal')
    
    if title:
        fig.suptitle(title)
    plt.tight_layout()
    plt.show()


def hemisphere_signal_avg(eeg, chan_name):
    left_hemisphere, midline_hemisphere, right_hemisphere = chan_hemisphere(chan_name)

    # seperate the signal into left and right hemisphere and take the average per channel
    left_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in left_hemisphere],:], axis=0)
    right_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in right_hemisphere],:], axis=0)
    midline_hemisphere_signal = np.mean(eeg.filtered_signal[[chan_name.index(chan) for chan in midline_hemisphere],:], axis=0)
    
    return left_hemisphere_signal, midline_hemisphere_signal, right_hemisphere_signal

def plot_spectrogram_and_bands(eeg, chan_name, title=None, band_freqs=None, f_min=5, f_max=15, fs=250, nfft=3, nperseg=3):
    if band_freqs:
        f_min = min(band_freqs) - 2
        f_max = max(band_freqs) + 2
    else:
        band_freqs = [f_min, f_max]
    total_signal = np.mean(eeg.filtered_signal, axis=0)
    left_hemisphere_signal, midline_hemisphere_signal, right_hemisphere_signal = hemisphere_signal_avg(eeg, chan_name)

    def masked_spectogram(singal, nperseg=6,nfft=6):
        # filter it first from f_min to f_max
        singal = custom_filter(singal, f_min, f_max, fs, 'bandpass')

        frequencies, times, spectrogram = signal.spectrogram(singal, fs=fs, nperseg=fs*nperseg, noverlap=fs*nperseg/2, scaling='spectrum', mode='psd', nfft=fs*nfft)
        mask = (frequencies >= f_min) & (frequencies <= f_max)
        spectrogram_masked = spectrogram[mask, :]
        frequencies_masked = frequencies[mask]
        return frequencies_masked, times, spectrogram_masked
    
    # Plot the spectrogram using matplotlib
    
    # fig, axs = plt.subplots(nrows=2, ncols=3,figsize=(15, 6))
    fig, axs = plt.subplots(nrows=1, ncols=4,figsize=(15, 3))
    def plot_sepctro(ax, signal, title, nfft, nperseg):
        frequencies_masked, times, spectrogram_masked = masked_spectogram(signal, nperseg=nperseg,nfft=nfft)
        ax.pcolormesh(times, frequencies_masked, spectrogram_masked, cmap ='magma')
        ax.set_ylim(f_min, f_max)
        ax.set_ylabel('Frequency [Hz]')
        ax.set_xlabel('Time [sec]')
        ax.set_title(title)
        # add yline for stimulus
        # for stim in eeg.stimulus_frequency:
        #     ax.axhline(y=stim, color='gray', linestyle='--')

    plot_sepctro(axs[0], left_hemisphere_signal, 'Left Hemisphere Signal', nfft, nperseg)
    plot_sepctro(axs[1], midline_hemisphere_signal, 'Midline Signal', nfft, nperseg)
    plot_sepctro(axs[2], right_hemisphere_signal, 'Right Hemisphere Signal', nfft, nperseg)
    plot_sepctro(axs[3], right_hemisphere_signal-left_hemisphere_signal, 'Delta Signal', nfft, nperseg)

    if title:
        fig.suptitle(title)
    plt.tight_layout()
    plt.show()
    