# Service Registry PoC

This repository demonstrates a Proof of Concept (PoC) for a service registry implementation using Netflix Eureka. The PoC is structured into three stages, gradually increasing in complexity.

## Overview
This PoC explores the feasibility of using Netflix Eureka as a service registry for applications built with Spring Boot and the Frank!Framework. The final goal is to establish a dynamic service discovery mechanism for multiple services, improving scalability and reliability.

## Stages
### Stage 1: Basic Communication

In this stage, we establish a fundamental setup where:
* Eureka Server is deployed to manage service registration.
* Two Spring Boot services (Service A & Service B) register with Eureka.
* Services communicate with each other through service discover



### Stage 2: Frank!Framework Communication

In this stage, we introduce the Frank!Framework and modify the setup to:
* Replace Spring Boot services with two Frank!Framework services.
* Ensure both Frank!Framework instances can register with Eureka.
* Validate communication between Frank services via Eureka.

### Stage 3: Multi-Service Communication

This stage scales up the architecture:
* Two Frank!Framework services register with Eureka.
* Multiple government services register with Eureka.
* Different services communicate dynamically using Eureka’s discovery capabilities.
* Load balancing and failover handling are tested.

## Prerequisites

Ensure you have the following installed:
* Java 17+ (for Spring Boot & Frank!Framework)
* Maven (for building Java projects)
* Eureka Server (setup provided in this repo)

