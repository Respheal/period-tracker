# https://stackoverflow.com/a/50854247

SMOOTHING_FACTOR = (
    3  # Example smoothing factor (probably make this a fractional range 0-1?)
)
counter = 0
average = 1.0

counter += 1
value = 50.0  # Example new temperature value
average = average + (value - average) / min(counter, SMOOTHING_FACTOR)
print(f"Updated average temperature: {average}")

counter += 1
value = 99.6  # Example new temperature value
average = average + (value - average) / min(counter, SMOOTHING_FACTOR)
print(f"Updated average temperature: {average}")

counter += 1
value = 22.6  # Example new temperature value
average = average + (value - average) / min(counter, SMOOTHING_FACTOR)
print(f"Updated average temperature: {average}")

counter += 1
value = 99.6  # Example new temperature value
average = average + (value - average) / min(counter, SMOOTHING_FACTOR)
print(f"Updated average temperature: {average}")

counter += 1
value = 33.0  # Example new temperature value
average = average + (value - average) / min(counter, SMOOTHING_FACTOR)
print(f"Updated average temperature: {average}")
