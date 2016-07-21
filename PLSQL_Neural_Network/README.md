# An example of how to build a neural network scoring engine in PL/SQL

In this you will find the support material for the blog entry:     
This is an example of how to build and deploy a basic artificial neural network scoring engine using PL/SQL. It is intended for learning purposes, in particular for Oracle practitioners who want a hands-on introduction to neural networks.

Author Luca.Canali@cern.ch - July 2016

| File                       | Short description
| -------------------------- | -------------------------------------------------------------------------------------
| [**MNIST_oracle_plsql.ipynb**](MNIST_oracle_plsql.ipynb) | How to deploy the neural network scoring engine in PL/SQL.
| [**MNIST_tensorflow_exp_to_oracle.ipynb**](MNIST_tensorflow_exp_to_oracle.ipynb)| Preparation of the neural network <ul><li>Definition and training of the neural network with tensorFlow</li><li>Extraction of the trained tensors into numpy arrays</li><li>proof of concept of how to run the scoring engine manually in Python</li><li>transfer of the tensors and of the test data to Oracle</li></ul>
| [**MNIST_tables.dmp.gz**](MNIST_tables.dmp.gz) | Tensors and test data produced as described in [MNIST_tensorflow_exp_to_oracle.ipynb](MNIST_tensorflow_exp_to_oracle.ipynb) exported using Oracle datapump utility (expdp version 11.2.0.4)

