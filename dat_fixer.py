data_path = r'C:\Users\txjam\Documents\homework\design\static_grid.dat'
output_path = r'C:\Users\txjam\Documents\homework\design\stat_grid_5.dat'

# Read the file
with open(data_path, 'r') as f:
    lines = f.readlines()

# Find the line indices
por_idx = None
permj_idx = None
cpor_idx = None

for i, line in enumerate(lines):
    if 'POR ALL' in line:
        por_idx = i
    elif 'PERMJ ALL' in line:
        permj_idx = i
    elif 'CPOR 1E-7' in line:
        cpor_idx = i

# Extract sections
por_values = lines[por_idx + 1:permj_idx]
permj_values = lines[permj_idx + 1:cpor_idx]

# Build new content
new_lines = []
new_lines.extend(lines[:por_idx + 1])  # Everything up to and including 'POR ALL'
new_lines.extend(por_values * 5)  # Repeat POR values 5 times
new_lines.append(lines[permj_idx])  # 'PERMJ ALL' line
new_lines.extend(permj_values * 5)  # Repeat PERMJ values 5 times
new_lines.extend(lines[cpor_idx:])  # Rest of the file from 'CPOR 1E-7'

# Write to new file
with open(output_path, 'w') as f:
    f.writelines(new_lines)

print(f"Modified file saved to {output_path}")