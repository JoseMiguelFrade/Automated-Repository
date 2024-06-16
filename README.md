# Automated Repository

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

## Getting Started

To get started with the Automated Repository, follow these steps:

### Pre-requisites

**Recommended:**
- **Windows 11:** 8 GB RAM Minimum.
- **Ubuntu 22.04 Desktop:** 8 GB RAM Minimum.

**Required:**
- **Python 3.x** (3.10+ Recommended) and pip: [Download Python](https://www.python.org/downloads/)
- **MongoDB**: [Download MongoDB](https://www.mongodb.com/) (MongoDB Compass Recommended)
- **Node.js** (20.10 Recommended): [Download Node.js](https://nodejs.org/en/download/package-manager)

**Not required for installation but needed to fully operate the Automated Repository:**
- **Geckodriver** (the .exe needs to be installed in the root folder of the project): [Download Geckodriver](https://github.com/mozilla/geckodriver/releases)
- **Firefox browser**: [Download Firefox](https://www.mozilla.org/pt-PT/firefox/new/)
- **OpenAI API Key**: [Get OpenAI API Key](https://openai.com/api/)

**After fulfilling the pre-requisites, run the following commands depending on the OS:**

**Clone the repository.**
   ```sh
   git clone https://github.com/yourusername/automated-repository.git
```
**Run the following, depending on the OS:**    
   **Windows:**
   - Run the setup script to check pre-requisites, build environment files, and install pip and Node.js dependencies.
     ```sh
     setup_windows.exe
     ```
   - Start the Automated Repository application.
     ```sh
     AutomatedRepository_win.exe
     ```

## Thesis Information

This project is part of a thesis conducted at the Instituto Politécnico de Leiria.

![Institute Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Log%C3%B3tipo_Polit%C3%A9cnico_Leiria_01.png/200px-Log%C3%B3tipo_Polit%C3%A9cnico_Leiria_01.png)



