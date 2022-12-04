<a name="readme-top"></a>

<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

</div>

<br />
<div align="center">
  <a href="https://github.com/aubravo/gxiba">
    <img src="docs/images/mission-logo.png" alt="Mission Logo" width="156" height="180">
  </a>

<h1 align="center">gxiba</h1>


  <p align="center">
<b>gxiba</b> means <b>sky</b> or <b>universe</b> in Zapoteco.

It is also the name of the second and third satellite missions to be launched by UPAEP.

This library was developed as my Data Science and Business Intelligence master's degree thesis. It contains and merges all the data pipeline and data science methods used to build the volcanic ash detection capability for the Gxiba-1 and Gxiba-2 missions.

It is structured in such a way that can allow to build upon further functionalities. If you are interested in participating, please feel free to contribute.
    <br />
    <a href="https://github.com/aubravo/gxiba"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/aubravo/gxiba/issues">Report Bug</a>
    ·
    <a href="https://github.com/aubravo/gxiba/issues">Request Feature</a>
  </p>
</div>

## Contents
<!-- TOC -->
* [About The Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Useful commands](#useful-commands)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgments](#acknowledgments)
<!-- TOC -->

## About The Project

### Built With

[![Python][Python.org]][Python-url]
[![Kubernetes][Kubernetes.io]][Kubernetes-url]
[![Docker][Docker.com]][Docker-url]
[![Google Cloud][cloud.google.com]][cloud-url]
[![Apache Spark][spark.apache.org]][spark-url]
[![TensorFlow][tensorflow.org]][tensorflow-url]
[![Pandas][pandas.pydata.org]][pandas-url]

## Getting Started

### Prerequisites

To get started, you will need a **Google Console account** setup and meet the following requirements:
- a [GCP bucket](https://cloud.google.com/storage/docs/creating-buckets) setup for the project.
- [_gsutil_](https://cloud.google.com/storage/docs/gsutil_install) and [_gcloud_](https://cloud.google.com/sdk/docs/install) installed on your machine
- a [service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts) with at least the following roles:
  - bigquery.user
  - storage.objectAdmin (for security, only allow the service account access to the project bucket)
- **OPTIONAL:** a [GKE cluster](https://cloud.google.com/kubernetes-engine/docs/deploy-app-cluster) if you are interested on running your application on Kubernetes.
- **OPTIONAL:** a [VM]() for a Postgres database hosting.

### Installation 

If you are interested on running the application locally:
```commandline
git clone https://github.com/aubravo/gxiba
```
Move to the new `gxiba` directory:
```commandline
cd ./gxiba
```
and get your service account keys into the project folder by running:
```commandline
gcloud iam service-accounts keys create keys.json --iam-account=your-service-account
```

## Useful commands: ##

```commandline
helm install postgres bitnami/postgresql
```
To get the password for "postgres" run:
```commandline
export POSTGRES_PASSWORD=$(kubectl get secret gxiba-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
```

## Roadmap
See the [open issues](https://github.com/aubravo/gxiba/issues) for a full list of proposed features (and known issues).

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

## License
Distributed under the MIT License. See `LICENSE.txt` for more information.


## Contact
Alvaro U. Bravo - [alvaroubravo@gmail.com](mailto:alvaroubravo@gmail.com); [alvaroulises.bravo@upaep.edu.mx](mailto:alvaroulises.bravo@upaep.edu.mx)

Project Links:
* [Gxiba - GitHub](https://github.com/aubravo/gxiba)
* [Gxiba - UPAEP](https://upaep.mx/gxiba/)

## Acknowledgments

* [UPAEP](https://upaep.mx/)
* [CONACYT](https://conacyt.mx/)
* [Agencia Espacial Mexicana](https://www.gob.mx/aem)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[contributors-shield]: https://img.shields.io/github/contributors/aubravo/gxiba.svg?style=for-the-badge
[contributors-url]: https://github.com/aubravo/gxiba/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/aubravo/gxiba.svg?style=for-the-badge
[forks-url]: https://github.com/aubravo/gxiba/network/members
[stars-shield]: https://img.shields.io/github/stars/aubravo/gxiba.svg?style=for-the-badge
[stars-url]: https://github.com/aubravo/gxiba/stargazers
[issues-shield]: https://img.shields.io/github/issues/aubravo/gxiba.svg?style=for-the-badge
[issues-url]: https://github.com/aubravo/gxiba/issues
[license-shield]: https://img.shields.io/github/license/aubravo/gxiba.svg?style=for-the-badge
[license-url]: https://github.com/aubravo/gxiba/blob/master/LICENSE.txt
[Python.org]: https://img.shields.io/badge/Python3-4B8BBE?style=for-the-badge&logo=Python&logoColor=FFD43B
[Python-url]: https://python.org 
[Kubernetes.io]: https://img.shields.io/badge/Kubernetes-326ce5?style=for-the-badge&logo=Kubernetes&logoColor=white
[Kubernetes-url]: https://kubernetes.io
[Docker.com]: https://img.shields.io/badge/Docker-0db7ed?style=for-the-badge&logo=Docker&logoColor=white
[Docker-url]: https://docker.com
[cloud.google.com]: https://img.shields.io/badge/Google_Cloud-DB4437?style=for-the-badge&logo=GoogleCloud&logoColor=F4B400
[cloud-url]: https://cloud.google.com
[spark.apache.org]: https://img.shields.io/badge/Apache_Spark-white?style=for-the-badge&logo=ApacheSpark&logoColor=E25A1C
[spark-url]: https://spark.apache.org
[tensorflow.org]: https://img.shields.io/badge/TensorFlow-425066?style=for-the-badge&logo=TensorFlow&logoColor=FF6F00
[tensorflow-url]: https://tensorflow.org
[pandas.pydata.org]: https://img.shields.io/badge/Pandas-white?style=for-the-badge&logo=Pandas&logoColor=150458
[pandas-url]: https://pandas.pydata.org/