import csv
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from numpy import matrix
from math import pow
import math
import random
import os.path
import json

class ocrNN:
	# Shuffle the indices of the 5000 samples and use the first 3500 for
	# training and the rest for testing.
	sampleIndices = list(range(5000))
	random.shuffle(sampleIndices)

	LEARNING_RATE = 0.1
	NN_FILE_PATH = 'nn.json'

	# Load data samples and labels into matrix
	dataMatrix = np.loadtxt(open('data.csv', 'rb'), delimiter = ',')
	dataLabels = np.loadtxt(open('dataLabels.csv', 'rb'))

	# Convert from numpy ndarrays to python lists
	dataMatrix = dataMatrix.tolist()
	dataLabels = dataLabels.tolist()

	def randInitializeWeights(self, sizeIn, sizeOut):
		return [x * 0.12 - 0.06 for x in np.random.rand(sizeOut, sizeIn)]

	# The sigmoid activation function
	def sigmoid(self, z):
		return 1 / (1 + math.e ** -z)

	def sigmoidPrime(self, z):
		return self.sigmoid(z) * (1 - self.sigmoid(z))

	def draw(self, sample):
		pixelArray = [sample[j:j+20] for j in xrange(0, len(sample), 20)]
		plt.imshow(zip(*pixelArray), cmap = cm.Greys_r, interpolation="nearest")
		plt.show()

	def train(self, trainingDataArray):
		for data in trainingDataArray:
			# Step 2: Forward propagation
			y1 = np.dot(np.mat(self.theta1), np.mat(data['y0']).T)
			sum1 =  y1 + np.mat(self.b1) # Add the bias
			y1 = self.sigmoid(sum1)

			y2 = np.dot(np.array(self.theta2), y1)
			y2 = np.add(y2, self.b2) # Add the bias
			y2 = self.sigmoid(y2)

			# Step 3: Back propagation
			actualVals = [0] * 10
			actualVals[data['label']] = 1
			outputErrors = np.mat(actualVals).T - np.mat(y2)
			hiddenErrors = np.multiply(np.dot(np.mat(self.theta2).T, outputErrors), self.sigmoidPrime(sum1))

			# Step 4: Update weights
			self.theta1 += ocrNN.LEARNING_RATE * np.dot(np.mat(hiddenErrors), np.mat(data['y0']))
			self.theta2 += ocrNN.LEARNING_RATE * np.dot(np.mat(outputErrors), np.mat(y1).T)
			self.b2 += ocrNN.LEARNING_RATE * outputErrors
			self.b1 += ocrNN.LEARNING_RATE * hiddenErrors

	def test(self):
		avgSum = 0
		for j in range(100):
			correctGuessCount = 0
			for i in ocrNN.sampleIndices[3500:]:
				test = ocrNN.dataMatrix[i]
				prediction = self.predict(test)
				if ocrNN.dataLabels[i] == prediction:
					correctGuessCount += 1

			avgSum += (correctGuessCount / float(1500))
		print avgSum / float(100)

	def predict(self, test):
		y1 = np.dot(np.mat(self.theta1), np.mat(test).T)
		y1 =  y1 + np.mat(self.b1) # Add the bias
		y1 = self.sigmoid(y1)

		y2 = np.dot(np.array(self.theta2), y1)
		y2 = np.add(y2, self.b2) # Add the bias
		y2 = self.sigmoid(y2)

		results = y2.T.tolist()[0]
		return results.index(max(results))

	def normalize(self, intensity, newMax, newMin):
		return intensity * (float(newMax - newMin) / float(255)) + newMin

	def save(self):
		nnFile = open(ocrNN.NN_FILE_PATH,'w');
		json.dump({
			"theta1":[npArr.tolist() for npArr in self.theta1],
			"theta2":[npArr.tolist() for npArr in self.theta2],
			"b1":self.b1[0].tolist(),
			"b2":self.b2[0].tolist()
		}, nnFile)
		nnFile.close()

	def load(self):
		nnFile = open(ocrNN.NN_FILE_PATH);
		nn = json.load(nnFile)
		self.theta1 = [np.array(li) for li in nn['theta1']]
		self.theta2 = [np.array(li) for li in nn['theta2']]
		self.b1 = [np.array(nn['b1'][0])]
		self.b2 = [np.array(nn['b2'][0])]
		nnFile.close()

	def __init__(self, numHiddenNodes):
		self.sigmoid = np.vectorize(self.sigmoid)
		self.sigmoidPrime = np.vectorize(self.sigmoidPrime)

		if (not os.path.isfile('nn.json')):
			# Step 1: Initialize weights to small numbers
			self.theta1 = self.randInitializeWeights(400, numHiddenNodes)
			self.theta2 = self.randInitializeWeights(numHiddenNodes, 10)
			self.b1 = self.randInitializeWeights(1, numHiddenNodes)
			self.b2 = self.randInitializeWeights(1, 10)

			# Train using sample data
			self.train([{"y0":self.dataMatrix[i], "label":int(ocrNN.dataLabels[i])} for i in ocrNN.sampleIndices[:3500]])
			self.test()
			self.save()
		else:
			self.load()