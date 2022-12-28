<a name="readme-top"></a>

<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

</div>

<div>

<br />
<p align="center">
<a href="https://github.com/aubravo/gxiba">
<img src="docs/images/mission-logo.png" alt="Mission Logo" width="156" height="180">
</a>
<h1 align="center">GXIBA</h1>
</div>

---
<div>
<br />
<p align="center">
<b>Guiranu bíchinu</b> / Todos somos hermanos,
<br />
<b>riní’nu túbisi diidxa’,</b> / hablamos la misma lengua,
<br />
<b>nadxiinu’ guendanabani,</b> / amamos la existencia,
<br />
<b>guibá’ ni rusieepa íquenu,</b> / el cielo que nos cubre,
<br />
<b>ubidxa xiñá’, yudé xti’ neza,</b> / el rojo sol, el polvo del camino,
<br />
<b>ca diidxadú’ xti’ guendarannaxhii.</b> / las palabras tiernas del amor.
<br />
<br />
<b>Esteban Rios Cruz</b> (<b>Laanu’</b> / Nosotros)
<br />
<br />
</p></div>

---

<div><p align="center">
<br />
<b>Gxiba</b> means <b>sky</b> or <b>universe</b> in Zapoteco.
UPAEP's second and third satellite missions are named as such.
This library is part of my Data Science and Business Intelligence master's degree thesis.
It constructs and manages the data pipeline and infrastructure for managing various satellite image inputs, handle and
process them, as well as manage the machine learning training and testing processes.
It is constructed in such way to allow for the coupling of diverse internal SQL Databases, and allow for the introduction
of diverse traditional image pre-processing methods using Python Pillow as a basis.
However, the test setup is configured in such a way as to construct the volcanic ash detection capability for the 
Gxiba-1 and Gxiba-2 missions.
<br />
<br />
If you are interested in participating, please feel free to contribute.
<br />
<a href="https://github.com/aubravo/gxiba"><strong>Explore the docs »</strong></a>
<br />
<br />
<a href="https://github.com/aubravo/gxiba/issues">Report Bug</a>
·
<a href="https://github.com/aubravo/gxiba/issues">Request Feature</a>
</p>
</div>

---
## Contents
<!-- TOC -->
  * [Contents](#contents)
  * [About The Project](#about-the-project)
    * [Built With](#built-with)
  * [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
  * [Useful commands:](#useful-commands-)
  * [Roadmap](#roadmap)
  * [Contributing](#contributing)
  * [License](#license)
  * [Contact](#contact)
  * [Acknowledgments](#acknowledgments)
<!-- TOC --> 

---
## About The Project

### Built With

[![Python 3.11][Python.org]][Python-url]
[![Kubernetes][Kubernetes.io]][Kubernetes-url]
[![Docker][Docker.com]][Docker-url]
[![Google Cloud][cloud.google.com]][cloud-url]
[![TensorFlow][tensorflow.org]][tensorflow-url]
[![Pandas][pandas.pydata.org]][pandas-url]

## Getting Started

### Prerequisites

> IMPORTANT **REQUIRES AT LEAST PYTHON 3.11 TO RUN.**

To get started, you will need a **Google Console account** setup and meet the following requirements:
- a [GCP bucket](https://cloud.google.com/storage/docs/creating-buckets) setup for the project.
- [_gsutil_](https://cloud.google.com/storage/docs/gsutil_install) and [_gcloud_](https://cloud.google.com/sdk/docs/install) installed on your machine
- a [service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts) with at least the following roles:
  - bigquery.user
  - storage.objectAdmin (for security, only allow the service account access to the project bucket)
- **OPTIONAL:** a [GKE cluster](https://cloud.google.com/kubernetes-engine/docs/deploy-app-cluster) if you are interested on running your application on Kubernetes.
- **OPTIONAL:** a Database setup for a production database setup.

### Installation 

If you are interested on running the application locally:
```commandline
git clone https://github.com/aubravo/gxiba
```
and get your service account keys into the project folder by running:
```commandline
gcloud iam service-accounts keys create keys.json --iam-account=your-service-account
```

## Useful commands: ##

<!-- TODO: Add Useful commands -->

## Roadmap
See the [open issues](https://github.com/aubravo/gxiba/issues) for a full list of proposed features (and known issues).

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

## License
Distributed under the MIT License. See `LICENSE` doc for more information.


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
[tensorflow.org]: https://img.shields.io/badge/TensorFlow-425066?style=for-the-badge&logo=TensorFlow&logoColor=FF6F00
[tensorflow-url]: https://tensorflow.org
[pandas.pydata.org]: https://img.shields.io/badge/Pandas-white?style=for-the-badge&logo=Pandas&logoColor=150458
[pandas-url]: https://pandas.pydata.org/