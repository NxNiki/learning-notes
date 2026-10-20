# Report: Predict Bike Sharing Demand with AutoGluon Solution
#### NAME HERE

Xin Niu

## Initial Training
### What did you realize when you tried to submit your predictions? What changes were needed to the output of the predictor to submit your results?
I did not find any negative predictions so I replace the predictions in the submission directly.

### What was the top ranked model that performed?
KNeighborsDist_BAG_L1

## Exploratory data analysis and feature creation
### What did the exploratory analysis find and how did you add additional features?
Most features have a normal distribution.
Extract year, day, hour from the datetime string.

### How much better did your model preform after adding additional features and why do you think that is?
Much better

## Hyper parameter tuning
### How much better did your model preform after trying different hyper parameters?
The r2 score did not improve, but Kaggle score reduced.

### If you were given more time with this dataset, where do you think you would spend more time?
Try more ML models, check outliers, correct distribution with log tranformation.


### Create a table with the models you ran, the hyperparameters modified, and the kaggle score.
|model|hpo1|hpo2|hpo3|score|
|--|--|--|--|--|
|initial|?|?|?|?|
|add_features|?|?|?|?|
|hpo|?|?|?|?|

I am confused about what hyperparameters should I change, so I copied some code from Gluon tutorial.

### Create a line plot showing the top model score for the three (or more) training runs during the project.

<img width="735" alt="image" src="https://github.com/user-attachments/assets/1e4b6262-b288-4ce3-becd-3ef23a3aa72d" />

### Create a line plot showing the top kaggle score for the three (or more) prediction submissions during the project.

<img width="692" alt="image" src="https://github.com/user-attachments/assets/7e0d720d-f74c-40bd-bbb5-9725e4805f27" />


## Summary
TODO: Add your explanation
