import rclpy
from rclpy.serialization import deserialize_message
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from sensor_msgs.msg import JointState
import pandas as pd
import matplotlib.pyplot as plt

def read_joint_position(bag_path, joint_name="joint_1"):
    storage_options = StorageOptions(uri=bag_path, storage_id="sqlite3")
    converter_options = ConverterOptions(output_serialization_format="cdr")

    # Initialize reader
    reader = SequentialReader()
    reader.open(storage_options, converter_options)

    # Lists to store timestamps and positions
    timestamps = []
    positions = []
    velocities = []

    # Variable to store the initial timestamp
    initial_timestamp = None

    # Read messages from bag file
    while reader.has_next():
        topic, serialized_msg, timestamp = reader.read_next()
        
        if topic == "/joint_states":
            msg = deserialize_message(serialized_msg, JointState)

            # Check if joint_1 is in the list of joint names
            if joint_name in msg.name:

                # Set the initial timestamp if it's the first message
                if initial_timestamp is None:
                    initial_timestamp = timestamp

                normalized_timestamp = (timestamp - initial_timestamp) / 1e9

                index = msg.name.index(joint_name)  # Get index of joint_1
                timestamps.append(normalized_timestamp)        # Record timestamp
                positions.append(msg.position[index])  # Record position of joint_1
                velocities.append(msg.velocity[index])

    # Create a DataFrame for analysis
    data = pd.DataFrame({
        'timestamp': timestamps,
        'position': positions,
        'velocity': velocities,
    })
    return data

# Path to your bag file
bag_path = 'rosbag2_2024_10_30-11_07_48'  # Replace with your actual bag file path

# Extract data
joint_name = "L_hip_joint"
df = read_joint_position(bag_path, joint_name=joint_name)

# Plot the position data over time (in seconds)
plt.figure(figsize=(10, 5))
plt.plot(df['timestamp'], df['velocity'], label=f'{joint_name} velocity')

# Labeling the plot
plt.xlabel('Time (seconds)')
plt.ylabel('velocity (radians)')
plt.title(f'velocity of {joint_name} Over Time')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()


