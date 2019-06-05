import numpy as np
import matplotlib.pyplot as plt

p_default = (0.88, 0.51, 0.40, 0.33)
r_default = (0.91, 0.46, 0.32, 0.20)

p_class_weighted = (0.87, 0.52, 0.43, 1.0)
r_class_weighted = (0.93, 0.41, 0.29, 0.60)

p_data_augmented = (0.93, 0.32, 0.43, 0.50)
r_data_augmented = (0.71, 0.75, 0.39, 0.40)

indices = np.arange(len(p_default))
width = 0.20

# Precision1
fig, ax = plt.subplots()
default = ax.bar(indices - width, p_default, width, label="Default")
class_weighted = ax.bar(indices, p_class_weighted, width, label="Class-weighted")
data_augmented = ax.bar(indices + width, p_data_augmented, width, label="Data augmentation")

ax.set_ylabel('Precision')
ax.set_ylim(0, 1)
ax.set_title('Precision by training method, per CDR class')
ax.set_xticks(indices)
ax.set_xticklabels(('Non-demented', 'Very mild', 'Mild', 'Moderate'))
ax.legend(loc='upper center')

plt.savefig("../report/img/precision_comparison.pdf", transparent=True)

# Recall
fig, ax = plt.subplots()
default = ax.bar(indices - width, r_default, width, label="Default")
class_weighted = ax.bar(indices, r_class_weighted, width, label="Class-weighted")
data_augmented = ax.bar(indices + width, r_data_augmented, width, label="Data augmentation")

ax.set_ylabel('Precision')
ax.set_ylim(0, 1)
ax.set_title('Recall by training method, per CDR class')
ax.set_xticks(indices)
ax.set_xticklabels(('Non-demented', 'Very mild', 'Mild', 'Moderate'))
ax.legend(loc='upper center')

plt.savefig("../report/img/recall_comparison.pdf", transparent=True)
