import numpy as np

# Set the filter order and step size
filter_order = 10
step_size = 0.1

# Initialize the filter coefficients
filter_coeffs = np.zeros(filter_order)

# Set the reference signal frequency
ref_freq = 10  # Change this to the desired SSVEP frequency

# Initialize the phase accumulator
phase_acc = 0

# Process the EEG data
for i in range(len(eeg_data)):
    # Generate the reference signal
    ref_signal = np.sin(2*np.pi*ref_freq*i/Fs + phase_acc)
    
    # Calculate the filter output
    filter_output = np.dot(filter_coeffs, ref_signal)
    
    # Calculate the error signal
    error_signal = eeg_data[i] - filter_output
    
    # Update the filter coefficients using RLS
    filter_coeffs += step_size*error_signal*ref_signal / (np.dot(ref_signal, ref_signal) + 1e-6)
    
    # Update the phase accumulator
    phase_acc += 2*np.pi*ref_freq/Fs
    
    # Ensure that the phase accumulator stays within 0-2*pi range
    if phase_acc >= 2*np.pi:
        phase_acc -= 2*np.pi
