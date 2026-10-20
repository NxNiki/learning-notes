[sagemaker official tuturial](https://docs.aws.amazon.com/sagemaker/)

# udemy-aws-machine_learning

## Section-2 Data Engineering

- S3 (Simple Storage Service) Bucket
- Storage Class
  - Standard
  - Intelligent-Tiering
  - Standard-IA (Infrequent Access)
  - One Zone-IA
  - Glacier
  - Glacier Deep Archive
- Data Encrpytion
- Kinesis
  - Kinesis streams (for real-time machine learning applications)
  - Kinesis data firehose (ingest massive data near real time)
  - Kinesis data analytics (real-time ETL/ML algorithm on streams)
  - Kinesis video stream (real-time video stream to create ML applications)
  - destination: S3, redshift, elastic search, splunk, etc
 
- Glue data catalog
  - crawler:
 

# udacity-aws-machine_learning:
https://www.udacity.com/enrollment/nd189


## course 2: introduction to machine learning

- Data Wrangler
- Ground Truth

### How to run a local Jupyter Notebook on sagemaker studio:

1. login to Amazon SageMaker AI and create a notebook instance (wait till the instance is in service)
2. start jupyterLab
3. Upload Jupyter Notebook using the `up arrow` button in jupyterLab.

amazon sagemaker example: https://github.com/aws/amazon-sagemaker-examples

### AutoGluon:

An easy way to compare performance of different ML models:

https://auto.gluon.ai/stable/index.html

### project: bike sharing

https://github.com/udacity/cd0385-project-starter

## course 3: develop ML workflow:

### resources:

- [xgboost](https://xgboost.readthedocs.io/en/latest/parameter.html)
- [aws doc boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [aws doc blazingtext](https://docs.aws.amazon.com/sagemaker/latest/dg/blazingtext.html)
- [aws doc sagemaker](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html)
- [VSstudio extention](https://marketplace.visualstudio.com/items?itemName=paulshestakov.aws-step-functions-constructor) to construct stepfunctions.


### project and exercise:

https://github.com/NxNiki/udacity-nd009t-C2-Developing-ML-Workflow

### lambda function:

- Lambda is Amazon’s serverless compute service, which is ideal for small tasks that are frequently repeated.

- A lambda function is executed when a playload is delivered to it. A payload is a JSON object which the Lambda function can read from as an input parameter.

- lambda_handler function can return a response, as long as it can be formatted as a JSON object (dict and list).

- With Lambda, as tasks are distributed redundantly across multiple machines.


#### triger a lambda function synchronously and asynchronously.

- use aws CLI:
```
aws lambda invoke --function-name preprocess-helloblze --payload '{"s3-dataset-uri": "udacity-sagemaker-solutiondata2021/l3e1/reviews_Musical_Instruments_5.json.zip"}' response.json
```
- S3 trigger


### step functions:

- task
- state machine: a workflow (an orchestrated and repeatable pattern of activity)
- function orchestration
- branching

> step functions can be expensive to run (> 100x lambda invocations), so it suitable for complex workflow that is not highly frequently used.

https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html

#### toubleshooting:

if has error installing stepfunctions:
```
pip install --upgrade pip setuptools wheel
```

permission issue:

ClientError: An error occurred (AccessDeniedException) when calling the CreateStateMachine operation: User: 
arn:aws:sts::510096416228:assumed-role/AmazonSageMaker-ExecutionRole-20250321T133435/SageMaker is not authorized to
perform: iam:PassRole on resource: arn:aws:iam::510096416228:role/xin-stepfunction because no identity-based policy
allows the iam:PassRole action

Attach the IAMFullAccess and StepFunctionsFullAccess policies to the SageMaker execution role (ExecutionRole-20250321T133435) of the notebook instance.
Also need to attach the CloudWatchEventsFullAccess and SageMakerFullAccess policies to Step Functions role (xin-stepfunction).


## course 4: Deep learning with CV and NLP

### resources:

- [A comparison of DL frameworks](https://thegradient.pub/state-of-ml-frameworks-2019-pytorch-dominates-research-tensorflow-dominates-industry/)
- [loss functions](https://pytorch.org/docs/stable/nn.html#loss-functions)
- [optimizer](https://pytorch.org/docs/stable/optim.html)
- [sagemaker parameter](https://sagemaker.readthedocs.io/en/stable/api/training/parameter.html)
- [sagemaker hyperparameter tuner](https://sagemaker.readthedocs.io/en/stable/api/training/tuner.html)

Loss function and activation function in the output layer:

Obtaining log-probabilities in a neural network is easily achieved by adding a LogSoftmax layer in the last layer of your network. 
You may use CrossEntropyLoss instead, if you prefer not to add an extra layer.

Always pair sigmoid activation with Binary Cross-Entropy (BCE) for classification tasks involving independent probabilities. For regression within 
[0,1], BCE or MSE can work, but BCE is more principled.

The activation function in the output layer determines whether the predicted classes are treated as independent (each class is predicted separately) or mutually exclusive (classes compete, and probabilities sum to 1).

> Sigmoid + BCE: Use when an input can belong to multiple classes simultaneously (e.g., medical diagnoses: a patient might have both "diabetes" and "hypertension").
> Softmax + CCE: Use when classes are mutually exclusive (e.g., handwritten digit recognition: a digit can’t be "2" and "3" at the same time).



## course 5: Operationalizing ML on SageMaker

### resources:
- [data-science-on-aws](https://github.com/data-science-on-aws/data-science-on-aws)

### spot instance:
The idle EC2 instance reserved for other users. Lower cost with lower reliability.

[AWS Official Documents for Splot instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)


### distributed training:

[Pytorch document for distributed training (DDP)](https://docs.pytorch.org/tutorials/intermediate/ddp_tutorial.html)

[AWS Official Document for distributed training](https://docs.aws.amazon.com/sagemaker/latest/dg/distributed-training-get-started.html)

To achieve optimal use of compute resources and faster training speed, you need to configure `instances`, `VPC subset` and `data storage` in the sampe AWS region and Availability Zone.

For instances, it is recommended to use `EFA-enabled GPU instances supported by SageMaker AI` (P4d and P4de instances equipped with NVIDIA A100 GPUs).
> Not all instance types support distributed training with SMDDP. Check AWS official documents for instances supporting SMDDP (SageMaker AI distributed data parallelism).
> pytorch DDP is supported for most of instances.

For data storage, it is recommended to use Amazon FSx for Lustre with high throughput for storing training datasets and model checkpoints.

- AllReduce: synchronize gradients across GPUs at the end of each training iteration.
- AllGather: sharded data parallel training.
  - SageMaker AI model parallelism (SMP)
  - DeepSpeed Zero Redundancy Optimizer (ZeRO)
  - PyTorch Fully Sharded Data Parallelism (FSDP)
- full replicated data
- sharded data

Distributed backend: determines how tensors/gradients are synchronized across devices.

GPU-based backends
- NCCL
- Gloo

High-performance networking backends
- EFA (Elastic Fabric Adapter) with Libfabric
- MPI (Message Passing Interface)

Framework-specific backends
- SMDDP (SageMaker Distributed Data Parallel): Built on top of NCCL + EFA, with extra optimizations for scaling.
- BytePS (less common but supported)
- TensorFlow CollectiveOps

[advanced configuration](https://docs.aws.amazon.com/sagemaker/latest/dg/data-parallel.html)

[talk on distributed ML](https://www.youtube.com/watch?v=eVvjbTZc1CM)

### lambda function：

[beginner tutorial](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)


### auto scaling:


### concurrency:

- reserved concurrency
- provisioned concurrency












