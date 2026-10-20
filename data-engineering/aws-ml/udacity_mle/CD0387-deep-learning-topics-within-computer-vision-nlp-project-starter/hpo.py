#TODO: Import your dependencies.
#For instance, below are some dependencies you might need if you are using Pytorch
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.models as models
import torchvision.transforms as transforms
import os
from torchvision import datasets
from torch.utils.data import DataLoader
import smdebug.pytorch as smd

import argparse
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def test(model, test_loader, criterion, hook=None):
    '''
    TODO: Complete this function that can take a model and a 
          testing data loader and will get the test accuray/loss of the model
          Remember to include any debugging/profiling hooks that you might need
    '''
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model=model.to(device)
    
    model.eval()
    # ===================================================#
    # 3. Set the SMDebug hook for the validation phase. #
    # ===================================================#
    if hook:
        hook.set_mode(smd.modes.EVAL)
        
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data=data.to(device)
            target=target.to(device)
            output = model(data)
            # test_loss += F.nll_loss(output, target, reduction="sum").item()  # sum up batch loss
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print(
        "\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n".format(
            test_loss, correct, len(test_loader.dataset), 100.0 * correct / len(test_loader.dataset)
        )
    )
    

def train(model, train_loader, epochs, criterion, optimizer, hook=None):
    '''
    TODO: Complete this function that can take a model and
          data loaders for training and will get train the model
          Remember to include any debugging/profiling hooks that you might need
    '''
    
    model.train()

    if hook:
        hook.set_mode(smd.modes.TRAIN)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model=model.to(device)

    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(train_loader):
            data=data.to(device)
            target=target.to(device)
            optimizer.zero_grad()
            output = model(data)
            # loss = F.nll_loss(output, target)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            if batch_idx % 100 == 0:
                print(
                    "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                        epoch,
                        batch_idx * len(data),
                        len(train_loader.dataset),
                        100.0 * batch_idx / len(train_loader),
                        loss.item(),
                    )
                )
    
def net():
    '''
    TODO: Complete this function that initializes your model
          Remember to use a pretrained model
    '''

    model = models.resnet18(weights='DEFAULT')
    for param in model.parameters():
        param.requires_grad = False   

    num_features=model.fc.in_features
    model.fc = nn.Sequential(
                   nn.Linear(num_features, 133))
    
    return model


def create_data_loaders(data_train, data_test, batch_size_train, batch_size_test):
    '''
    This is an optional function that you may or may not need to implement
    depending on whether you need to use data loaders or not
    '''

    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to 224x224
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], 
                             [0.229, 0.224, 0.225])  # ImageNet normalization
    ])

    train_dataset = datasets.ImageFolder(root=data_train, transform=transform)
    test_dataset  = datasets.ImageFolder(root=data_test,  transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size_train, shuffle=True, num_workers=0)
    test_loader  = DataLoader(test_dataset,  batch_size=batch_size_test, shuffle=False, num_workers=0)

    return train_loader, test_loader

def main(args):

    train_loader, test_loader = create_data_loaders(
        args.data_train, args.data_test, args.batch_size, args.test_batch_size
    )
    '''
    TODO: Initialize a model by calling the net function
    '''
    model=net()
    
    '''
    TODO: Create your loss and optimizer
    '''
    loss_criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=args.lr)
    
    '''
    TODO: Call the train function to start training your model
    Remember that you will need to set up a way to get training data from S3
    '''
    train(model, train_loader, args.epochs, loss_criterion, optimizer)
    
    '''
    TODO: Test the model to see its accuracy
    '''
    test(model, test_loader, loss_criterion)
    
    '''
    TODO: Save the trained model
    '''
    torch.save(model.state_dict(), os.path.join(args.model_dir, "model.pth"))


if __name__=='__main__':
    
    parser = argparse.ArgumentParser(description="PyTorch dogImages model tunning")
    
    '''
    TODO: Specify all the hyperparameters you need to use to train your model.
    '''
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        metavar="N",
        help="input batch size for training (default: 64)",
    )
    parser.add_argument(
        "--test-batch-size",
        type=int,
        default=1000,
        metavar="N",
        help="input batch size for testing (default: 1000)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=14,
        metavar="N",
        help="number of epochs to train (default: 14)",
    )
    parser.add_argument(
        "--lr", type=float, default=1.0, metavar="LR", help="learning rate (default: 1.0)"
    )
    

    # train_kwargs = {"batch_size": args.batch_size}
    # test_kwargs = {"batch_size": args.test_batch_size}

    parser.add_argument("--data-train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
    # for hyparameter tunning, we set valid as the test set:
    parser.add_argument("--data-test", type=str, default=os.environ["SM_CHANNEL_VALID"])
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])

    args = parser.parse_args()
    
    main(args)
