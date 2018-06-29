import torch
import torch.nn as nn
import torchvision
import numpy as np
from wrapper import XRAY
import matplotlib.pyplot as plt

load_model_filepath = 'best_model.tar'
vision_model = torchvision.models.inception_v3()
n_features = vision_model.fc.in_features
vision_model.fc = nn.Linear(n_features, 1)
vision_model = nn.DataParallel(vision_model, device_ids=[0, 1])

# load the model from the saved state
def load_saved_model(optimizer=None):
    state = torch.load(load_model_filepath, map_location='cpu')
    vision_model.load_state_dict(state['state_dict'])
    return vision_model

def run_model(filename, vision_model):
	vision_model.train(False)  # Set model to evaluate mode
	dataset = XRAY('images', [(filename, 0)])
	image, label = dataset[0] # get the image from the dataset
	image.unsqueeze_(0)	
	outputs = vision_model(image)
	score = outputs.tolist()[0][0]
	return score

image = run_model('00000003_001.png', vision_model)
