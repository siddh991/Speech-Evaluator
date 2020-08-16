# Speech Evaluator

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

#### TF Pose Estimation

1. Clone tf-pose-estimation within Speech-Evaluator project directory.
```
git clone https://github.com/ildoonet/tf-pose-estimation.git
```
2. Download Swig-4.0.2 from
```
http://www.swig.org/download.html
```
3. Extract swig-4.0.2.tar.gz into the tf-pose-estimation directory.

4. Add the path of the extracted swig folder to your $PATH variable.

5. Install package.
```
$ cd tf-pose-estimation
$ python setup.py install  # Or, `pip install -e .`
```
5. Download Tensorflow Graph File(pb file)
```
$ cd models/graph/cmu
$ bash download.sh
```
6. Open run_webcam.py and replace 'int' with 'string' on line 24 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
