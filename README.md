﻿# Automated Repository

The Automated Repository is a project developed to enable automatic document collection, filtering, and classification using various tools, including GPT-4o. This project counts with an RSS Feed Consumer module and a PDF Crawler to efficiently gather documents from various sources. GPT-4o helps in filtering relevant documents according to the intended theme. For each document, it extracts information, organizes it according to several parameters, and generates insights about each one.
Document information and repository management are facilitated by an intuitive UI featuring various graphs and menus.

## Features

- **RSS Feed Consumer**: Automatically collects documents from subscribed RSS feeds.
- **PDFCrawler**: Extracts PDF documents from online repositories. (Based on [SimFin PDFCrawler GitHub project](https://github.com/SimFin/pdf-crawler/tree/master))
- **Document Filtering**: Filters collected documents to ensure relevance within the defined theme.
- **Document Classification**: Utilizes GPT to classify and extract essential information from documents, such as:
  - Title
  - Date
  - Issuer
  - Origin
  - Area
  - related documents
  - Generation of short, informative abstracts

## Technology Stack

- **Frontend**: Vuetify 3
- **Backend**: Flask
- **Database**: MongoDB

## Project Overview

![Project Architeture](./Images/EsquemaRepoCyberlaw2.png)

## Frontend Screenshots

![Insert Frontend Print 1 Here]
![Insert Frontend Print 2 Here]

## Getting Started

To get started with the Automated Repository, follow these steps:

1. Clone the repository.
   ```sh
   git clone https://github.com/yourusername/automated-repository.git

## Thesis Information

This project is part of a thesis conducted at the Instituto Politécnico de Leiria.

![Institute Logo](https://www.google.com/url?sa=i&url=https%3A%2F%2Fpt.wikipedia.org%2Fwiki%2FInstituto_Polit%25C3%25A9cnico_de_Leiria&psig=AOvVaw0oX-k5h6BU6Fms0ZHY1cDs&ust=1718363011515000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCNj8mJm32IYDFQAAAAAdAAAAABAE)



