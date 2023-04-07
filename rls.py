import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Load the raw EEG data
eeg_data = np.loadtxt('eeg_data.txt')

# Set the sampling rate and the filter cutoff frequencies
fs = 250
low_cutoff = 6
high_cutoff = 30

# Apply a bandpass filter to the EEG data
b, a = signal.butter(4, [low_cutoff / (fs / 2), high_cutoff / (fs / 2)], btype='bandpass')
filtered_data = signal.filtfilt(b, a, eeg_data)

# Initialize the RLS filter
M = 100  # Filter order
lambda_ = 0.99  # Forgetting factor
P = lambda_**(-1) * np.eye(M)
w = np.zeros((M, 1))
ref_freq = 15  # Target SSVEP frequency

# Apply the RLS filter to the filtered EEG data
num_samples = filtered_data.shape[0]
ssvep = np.zeros(num_samples)
for n in range(num_samples):
    x = np.sin(2 * np.pi * ref_freq * n / fs)  # Reference signal
    y = np.dot(w.T, x)  # Estimated output
    e = filtered_data[n] - y  # Error signal
    k = np.dot(P, x) / (lambda_ + np.dot(np.dot(x.T, P), x))  # Kalman gain
    w = w + k * e  # Filter coefficients update
    P = (P - np.dot(np.dot(k, x.T), P)) / lambda_  # Covariance matrix update
    ssvep[n] = y  # SSVEP estimate

# Generate the spectrogram of the SSVEP signal
f, t, Sxx = signal.spectrogram(ssvep, fs=fs, nperseg=512, noverlap=256)
plt.pcolormesh(t, f, 10*np.log10(Sxx), cmap='jet')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.ylim([0, 35])
plt.colorbar()
plt.show()
