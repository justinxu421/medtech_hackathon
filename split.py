import glob
import os.path as osp
import numpy as np
from sklearn.model_selection import train_test_split

def split_data(labels_csv, balanced = False, train_size=0.7, max_rows=4999):
    """ Splits the data into train, validation, and test filenames"""
    # read in labels_csv and create dictionary
    label_array = np.genfromtxt(labels_csv, delimiter=',', dtype='str', skip_header=1, max_rows=max_rows)
    adjusted_labels = [(entry[0], entry[1].split('|')) for entry in label_array]

    # rough mapping from disease to urgency
    labels = {'Nodules': 3, 'Masses' : 3, 'Atelectasis' : 3, 'Effusion' : 2, 'Edema' : 2, 
              'Cardiomegaly':2, 'Pneumonia':2, 'Consolidation':2, 'Infiltration':2, 'Pneumothorax':1}
    filename_labels = []
    for name, diseases in adjusted_labels:
        scores = []
        for disease in diseases:
            if disease in labels:
                scores.append(labels[disease])
            else:
                scores.append(0)
        label_score = np.mean(scores)
        filename_labels.append((name, label_score))

    print(filename_labels[:5])
    print('num experiments is', len(filename_labels))
    
    # if balanced:
    #     # downsample all these labels to try to balance the labels
    #     labels = np.array([x[1] for x in filename_labels])
    #     i_class0 = np.where(labels == 0)[0]
    #     i_class1 = np.where(labels == 1)[0]
    #     i_class2 = np.where(labels == 2)[0]

    #     n_class0 = len(i_class0)
    #     n_class1 = len(i_class1)

    #     i_class0_downsampled = np.random.choice(i_class0, size=n_class1, replace=False)
    #     filenames_indices = np.hstack((i_class0_downsampled, i_class1, i_class2)) 
    #     filename_labels = [filename_labels[i] for i in range(len(labels)) if i in filenames_indices]
    

    train_filenames, test_filenames = train_test_split(filename_labels,
                                                        train_size=train_size,
                                                        random_state=42,
                                                        shuffle=True)

    val_filenames, test_filenames = train_test_split(test_filenames,
                                                        train_size=0.5,
                                                        random_state=42,
                                                        shuffle=True)

    return train_filenames, val_filenames, test_filenames

def main():
    image_folder = 'images'
    label_path = 'Data_Entry_2017.csv'
    split_data(image_folder, label_path)

if __name__ == '__main__':
    main()