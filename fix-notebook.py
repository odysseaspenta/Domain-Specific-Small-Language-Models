import sys
import nbformat

# Load the notebook
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Remove the problematic widgets metadata
if 'widgets' in nb.metadata:
    del nb.metadata['widgets']

# Save it back
with open(path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

