
![CDAB logo](docs/images/cdab-logo.jpg)

# The Copernicus Sentinels Data Access Benchmark Service

The objective of the Copernicus Sentinels Data Access Worldwide Benchmark is to provide impartial and reliable information on the Sentinels data accessibility from the access points under ESA management, building a comprehensive and objective overview of the conditions actually experienced by users.

In order to achieve its objectives, the benchmarking service encompasses a combination of measurements, interpretation and communication activities that include:
* The systematic execution of benchmarking operations, simulating typical user scenarios from different test sites located in Europe and around the world;
* The cleaning, analysing and interpretation of the results;
* The presentation of the results towards various actors;
* The monitoring of the results and of the benchmark quality over time; and
* The implementation of service evolutions as appropriate.

For the sake of the benchmarking service, "typical" operations performed by the Sentinels users can be sketched according to [Test Scenarios Description](https://github.com/esa-cdab/cdab-testsuite/wiki/Test-Scenarios-Description).

The service operates an independent benchmarking of ESA's hubs and DIASes from a worldwide network of 25+ Test Sites.

The Test Sites are managed remotely as part of a broad architecture designed to provide a regular and automated monitoring of the target sites in an automated way. A complex orchestration of operations from the various test sites to the various Target Sites is operated, whereby each test site issues one or more requests towards one or more target sites, according to a pre-defined test-to-target matrix. The results are systematically stored, analysed and reported.

The main pillars of the benchmarking service architecture are:

* a network of Test Sites, that perform the benchmarking operations towards the pre-defined target sites;
* the Orchestration function, in charge of managing the benchmarking operations;
* the Analysis and Reporting function;
* the Calibration and Validation function, ensuring a continuous monitoring of the service reliability;
* a Public Software Repository service (this repository); and
* the Service Management, in charge of the overall management including possible evolutions.

The service results are captured on different kind of deliverables to different stakeholders with different distribution policies such as:
* The [Service Design Document](https://github.com/esa-cdab/cdab-service/blob/main/docs/Service_Design_Document_V2_2_1_signed.pdf), presenting the main characteristics of the service and providing key information that is needed to interpret the service results. 
* The Service Specific Reports, presenting the service results for a given target site (e.g. the ESA's hubs or the DIAS); and
* The Service Summary Report, presenting an overview of the core benchmarking results to the Copernicus governance.

Further documentaton can be found on:
* [CDAB Quality Of Experience indicators](https://github.com/esa-cdab/cdab-service/wiki)
* [CDAB Software Test Suite](https://github.com/esa-cdab/cdab-testsuite)

A free QoE (Quality Of Experience) calculator plugin can be found at:
* [CDAB QoE calculator plugin](https://github.com/esa-cdab/cdab-service/tree/main/tools/qoe_calculator)

<hr/>
<p align="center">Funded by EU</p>
<p align="center"><img src="copernicus-logo.png" alt="Copernicus" height="125"/><img src="esa-logo.png" alt="ESA" height="125"/></p>
