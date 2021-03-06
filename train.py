# -*- coding: utf-8 -*-
# Time : 2022/5/17 6:20 PM
# Author : sk-w
# Email : 15734082105@163.com
# File : train.py.py
# Project : AlexNet-Pytorch

import argparse
import time

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms

from dataset import CustomImageDataset
from net import AlexNet

parser = argparse.ArgumentParser(description="AlexNet Traing Parameters")
parser.add_argument('--data_url',
                    help='path to training/inference dataset folder',
                    default='./data')

parser.add_argument('--train_url',
                    help='model folder to save/load',
                    default='./model')

parser.add_argument(
    '--device_target',
    type=str,
    default="Ascend",
    choices=['Ascend', 'GPU', 'CPU'],
    help='device where the code will be implemented (default: Ascend)')

parser.add_argument('--classes', default='11', help='--epoch')
parser.add_argument('--learning_rate', default='1e-1', help="learning_rate")
parser.add_argument('--batch_size', default='4', help='batch_size')
parser.add_argument('--epoch', default='1', help='--epoch')
parser.add_argument('--save_path', default='/model', help='--epoch')

if __name__ == '__main__':
    args = parser.parse_args()

    imgTransform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((224, 224)),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])


    def labelTransform(x):
        return F.one_hot(torch.tensor(eval(x)), num_classes=eval(args.classes))


    # train data
    trainData = CustomImageDataset("/dataset/dataset", "/dataset/dataset/train10.txt", imgTransform, labelTransform)
    trainData = DataLoader(trainData, batch_size=eval(args.batch_size), shuffle=True)
    valData = CustomImageDataset("/dataset/dataset", "/dataset/dataset/val10.txt", imgTransform, labelTransform)
    valData = DataLoader(valData, batch_size=eval(args.batch_size), shuffle=True)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


    net = AlexNet(eval(args.classes)).to(device)

    optimizer = torch.optim.SGD(net.parameters(), lr=eval(args.learning_rate))

    loss_fn = nn.CrossEntropyLoss()

    print('epoch_size is:{}'.format(eval(args.epoch)))
    loss_data = []
    for epoch in range(eval(args.epoch)):
        loss_epoch_data = []
        for batch, (X, y) in enumerate(trainData):
            # compute prediction and loss
            pred = net.forward(X.to(device))
            loss = loss_fn(pred.to(device), y.float().to(device))

            # backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if batch % 10 == 0:
                print(f'epoch:{epoch} batch_size:{batch} loss:{loss.item()}')
                loss_epoch_data.append(loss.item())
        loss_data.append(loss_epoch_data)

    trainLoss = np.array(loss_data).T
    locale_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
    np.savetxt(args.save_path + '/' + locale_time + '.csv', trainLoss, delimiter=',')
    torch.save(net, args.save_path + '/' + 'AlexNet_' + locale_time + '.pth')
