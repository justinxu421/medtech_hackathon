from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import numpy as np
from PIL import Image
import os.path as osp

class XRAY(Dataset):
    """
    A customized data loader for XRAY dataset.
    """
    def __init__(self, path, filename_label_list, input_size = 299):
        """ Intialize the XRAY dataset
        Args:
            - root: root directory of the dataset
            - transform: a custom transform function
            - preload: if preload the dataset into memory
        """
        self.image_paths = []
        self.labels = []
        #resize to 360 and then crop to 299, which is the input size for inception
        self.transform = transforms.Compose([transforms.Resize(360),
                                            transforms.CenterCrop(input_size),
                                            transforms.ToTensor(),
                                            transforms.Normalize([0.5,0.5,0.5],[0.25,0.25,0.25])])
        for filename, label in filename_label_list:
            # construct a path to the image
            self.image_paths.append(osp.join(path, filename))
            self.labels.append(label)

    def __getitem__(self, index):
        """ Get a sample from the dataset
        """
        path = self.image_paths[index]
        img_slice = Image.open(path)
        img_slice = self.transform(img_slice)

        label = self.labels[index]
        return img_slice, label

    def __len__(self):
        """
        Total number of samples in the dataset
        """
        return len(self.image_paths)