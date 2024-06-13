# Automated Repository

The Automated Repository is a project developed to enable automatic document collection, filtering, and classification using various tools and GPT-4o. This project includes an RSS Feed Consumer module and a PDF Crawler to efficiently gather documents from various sources. GPT-4o helps in filtering relevant documents according to the intended theme. For each document, it extracts information, organizes it according to several parameters, and generates insights about each one.

## Features

- **RSS Feed Consumer**: Automatically collects documents from subscribed RSS feeds.
- **PDFCrawler**: Extracts documents from PDF files. (Based on [SimFin PDFCrawler GitHub project](https://github.com/SimFin/pdf-crawler/tree/master))
- **Document Filtering**: Filters collected documents to ensure relevance.
- **Document Classification**: Utilizes GPT to classify and extract essential features such as:
  - Title
  - Date
  - Issuer
  - Origin
  - Area
  - Identification of related documents
  - Generation of short, informative abstracts

## Technology Stack

- **Frontend**: Vuetify 3
- **Backend**: Flask
- **Database**: MongoDB

## Project Overview

![Project Architeture](./Images/EsquemaRepoCyberlaw2.png)

## Setup Guide

[Setup instructions will be added here]

## Frontend Screenshots

![Insert Frontend Print 1 Here]
![Insert Frontend Print 2 Here]

## Thesis Information

This project is part of a thesis conducted at the Instituto Politécnico de Leiria.

![Institute Logo]

## Getting Started

To get started with the Automated Repository, follow these steps:

1. Clone the repository.
   ```sh
   git clone https://github.com/yourusername/automated-repository.git

