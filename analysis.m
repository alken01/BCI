% Load the EEG time series data from a CSV file
eeg_data = readmatrix('data/Alken-27March/BR-23M/BL_1148_Rivalry_test_Alken_ExG.csv', 'Delimiter', ',');

% Extract the EEG channels (columns 2 to 9)
eeg_data = eeg_data(:, 2:9);

% Define the frequency range of interest
freq_range = [5 18];

% Define the sampling rate
fs = 250; % Replace 250 with your sampling rate

% Compute the time vector
t = 0:1/fs:(size(eeg_data, 1)-1)/fs;

% Compute the power spectral density (PSD) using Welch's method
nfft = 5*fs;
window = hamming(nfft);
noverlap = nfft/2;
[pxx, f] = pwelch(eeg_data, window, noverlap, nfft, fs);

% Select the frequency range of interest
idx_freq = find(f >= freq_range(1) & f <= freq_range(2));

% Compute the time-frequency representation (TFR) using Morlet wavelets
freqs = logspace(log10(freq_range(1)), log10(freq_range(2)), 100);
scales = fs./freqs;
cwt_data = cwt(eeg_data', scales, 'morl');
power = abs(cwt_data).^2;

% Compute the average power across channels
mean_power = mean(power, 1);

% Plot the PSD
figure;
plot(f(idx_freq), 10*log10(pxx(idx_freq, :)));
xlabel('Frequency (Hz)');
ylabel('Power/frequency (dB/Hz)');
title('Power spectral density');

% Plot the TFR
figure;
imagesc(t, freqs, 10*log10(mean_power));
set(gca, 'YDir', 'normal');
xlabel('Time (s)');
ylabel('Frequency (Hz)');
title('Time-frequency representation');
