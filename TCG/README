# TCG

Author: Tommy Lu
Email: <lut@fortinet.com>

## What is TCG?

TCG is an application used to generate API test cases for a given OpenAPI specification file. It generates test cases in the ATF robot framework format, allowing them to be directly executed in the ATF framework.

## How to use TCG?

TCG is a GUI application. To use it, execute the `python main.py` file. This will open the GUI window shown below. Follow the steps below to generate test cases.

## Environment

1. Python 3.7 or above
2. PyQt6

## Installation

1. Clone the repository to your local machine (Make sure you have GUI support in your local machine)
2. Switch to the TCG directory.
3. Install the required packages using the command `pip install -r requirements.txt`
4. Execute the command `python main.py` to start the application.

## Note

1. TCG only supports OpenAPI specification version 3.0.0 or above. If your OpenAPI specification file is in an older version, use the OpenAPI specification converter to convert it to version 3.0.0.

## Steps to generate test cases

1. Import the OpenAPI document using the `Import OpenAPI Doc` button.
2. Import the ATF `Object Mapping File` using the `Import Object Mapping File` button.
    1. If you don't have the `Object Mapping File`, you can generate it using the ATF `schema_handler.py` file available in the ATF repository `./Library/utils/<product_name>_schema_handler.py`.
