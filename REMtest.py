from cirq import LineQubit, Circuit, X, measure_each

from mitiq.observable.observable import Observable
from mitiq.observable.pauli import PauliString
from functools import partial

import numpy as np
from cirq.experiments.single_qubit_readout_calibration_test import (
    NoisySingleQubitReadoutSampler,
)

from mitiq import MeasurementResult
from mitiq.raw import execute as raw_execute
from mitiq.rem import post_select
from mitiq.rem import generate_inverse_confusion_matrix
from mitiq import rem

qreg = [LineQubit(i) for i in range(2)]
circuit = Circuit(X.on_each(*qreg))
observable = Observable(PauliString("ZI"), PauliString("IZ"))

print(circuit)


def noisy_readout_executor(circuit, p0, p1, shots=8192) -> MeasurementResult:
    # Replace with code based on your frontend and backend.
    simulator = NoisySingleQubitReadoutSampler(p0, p1)
    result = simulator.run(circuit, repetitions=shots)
    bitstrings = np.column_stack(list(result.measurements.values()))
    return MeasurementResult(bitstrings, qubit_indices = (0, 1))

# Compute the expectation value of the observable.
# Use a noisy executor that has a 25% chance of bit flipping
p_flip = 0.25
noisy_executor = partial(noisy_readout_executor, p0=p_flip, p1=p_flip)
noisy_value = raw_execute(circuit, noisy_executor, observable)

ideal_executor = partial(noisy_readout_executor, p0=0, p1=0)
ideal_value = raw_execute(circuit, ideal_executor, observable)
error = abs((ideal_value - noisy_value)/ideal_value)
print(f"Error without mitigation: {error:.3}")

circuit_with_measurements = circuit.copy()
circuit_with_measurements.append(measure_each(*qreg))
noisy_measurements = noisy_executor(circuit_with_measurements)
print(f"Before postselection: {noisy_measurements.get_counts()}")
postselected_measurements = post_select(noisy_measurements, lambda bits: bits[0] == bits[1])
print(f"After postselection: {postselected_measurements.get_counts()}")
total_measurements = len(noisy_measurements.result)
discarded_measurements = total_measurements - len(postselected_measurements.result)
print(f"Discarded measurements: {discarded_measurements} ({discarded_measurements/total_measurements:.0%} of total)")

mitigated_result = observable._expectation_from_measurements([postselected_measurements])
error = abs((ideal_value - mitigated_result)/ideal_value)
print(f"Error with mitigation (PS): {error:.3}")

# We use a utility method to generate a simple inverse confusion matrix, but
# you can supply your own confusion matrices and invert them using the helper
# function generate_tensored_inverse_confusion_matrix().
inverse_confusion_matrix = generate_inverse_confusion_matrix(2, p_flip, p_flip)

mitigated_result = rem.execute_with_rem(
    circuit,
    noisy_executor,
    observable,
    inverse_confusion_matrix=inverse_confusion_matrix,
)

error = abs((ideal_value - mitigated_result)/ideal_value)
print(f"Error with mitigation (REM): {error:.3}")