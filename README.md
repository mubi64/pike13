# Pike13 Frappe App Documentation

## Introduction

The Pike13 Frappe App is a powerful tool for integrating ERPNext with Pike13. This documentation will guide you through the installation, configuration, and usage of this app to streamline your business processes.

## Table of Contents

1. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Installing the Pike13 App](#installing-the-pike13-app)

2. [Pike13 Settings](#pike13-settings)
    - [Configuration](#configuration)

3. [Pike13 Site](#pike13-site)
    - [Usage](#usage)

## Installation

### Prerequisites

Before you begin, ensure that you have the following prerequisites in place:

- [Frappe Framework](https://frappeframework.com/) is installed and configured.

### Installing the Pike13 App

1. Clone the Pike13 repository to your Frappe app directory:

   ```bash
   git clone https://github.com/mubi64/pike13.git


Certainly, here's a GitHub-flavored Markdown documentation for your Frappe app "Pike13" with two screens: "Pike13 Settings" and "Pike13 Site".

markdown
Copy code
# Pike13 Frappe App Documentation

## Introduction

The Pike13 Frappe App is a powerful tool for integrating ERPNext with Pike13. This documentation will guide you through the installation, configuration, and usage of this app to streamline your business processes.

## Table of Contents

1. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Installing the Pike13 App](#installing-the-pike13-app)

2. [Pike13 Settings](#pike13-settings)
    - [Configuration](#configuration)

3. [Pike13 Site](#pike13-site)
    - [Usage](#usage)

## Installation

### Prerequisites

Before you begin, ensure that you have the following prerequisites in place:

- [Frappe Framework](https://frappeframework.com/) is installed and configured.

### Installing the Pike13 App

1. Clone the Pike13 repository to your Frappe app directory:

   ```bash
   git clone https://github.com/yourusername/Pike13.git

2. Install the app using the Frappe Bench:

  ```bash
  bench --site sitename install-app pike13
```

3. Once installed, migrate your site:

```bash
bench --site sitename migrate
```
4. Finally, restart your Frappe server:

```bash
bench restart
```

The Pike13 app should now be installed and ready to use.
