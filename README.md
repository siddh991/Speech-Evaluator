# Speech Evaluator

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Prerequisites
A step by step guide to installing and  of examples that tell you how to get a development env running

1. Clone repository.
```
$ git clone https://github.com/siddh991/Speech-Evaluator.git
```

#### Installing Dependencies
2. Install required libraries.
```
$ cd Speech-Evaluator
$ pip3 install -r requirements.txt
```

#### Installing TF Pose Estimation

3. Clone tf-pose-estimation within Speech-Evaluator project directory.
```
$ git clone https://github.com/ildoonet/tf-pose-estimation.git
```

4. Download Swig-4.0.2 from
```
http://www.swig.org/download.html
```

5. Extract swig-4.0.2.tar.gz into the tf-pose-estimation directory.

6. Add the path of the extracted swig folder to your $PATH variable using:
```
PATH='path/to/swig-4.0.2/folder':$PATH
```

7. Install package.
```
$ cd tf-pose-estimation
$ python setup.py install  # Or, `pip install -e .`
```

8. Download Tensorflow Graph File(pb file)
```
$ cd models/graph/cmu
$ bash download.sh
```

9. Open run_webcam.py and replace 'int' with 'str' on line 27

## Authors

* **Siddharth Surana** - [siddh991](https://github.com/siddh991)
* **Rishabh Patni** - [rishabh28patni](https://github.com/rishabh28patni)

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
