StringSheet
===========

.. image:: https://travis-ci.org/Tunous/StringSheet.svg?branch=master
    :target: https://travis-ci.org/Tunous/StringSheet
.. image:: https://badge.fury.io/py/stringsheet.svg
    :target: https://badge.fury.io/py/stringsheet

Script for managing Android translations using Google Spreadsheets.

Usage
=====

create
^^^^^^

Create a new spreadsheet and automatically upload your strings.

.. code-block:: sh

   $ stringsheet create "My project" "~/src/myproject/app/src/main/res"

*Note: The path should point to the res directory of your Android project.*

download
^^^^^^^^

Download translations from spreadsheet.

.. code-block:: sh

   $ stringsheet download spreadsheetId "~/src/myproject/app/src/main/res"

upload
^^^^^^

Upload strings to existing spreadsheet.

.. code-block:: sh

   $ stringsheet upload spreadsheetId "~/src/myproject/app/src/main/res"

Note: This command will override all strings in the spreadsheet. You should first download the spreadsheet using the previous command and commit them to your project before uploading

Installation
============

.. code-block:: sh

   $ pip install stringsheet

Features
========

- Support for all string formats:

  - string
  - string-array
  - plurals

- Automatic spreadsheet formatting durning creation:

  - Protection of informational columns and rows
  - Highlighting of missing translations with conditional formatting

- Support for creating separate sheets for different languages (see `Multi-sheet` section)

Multi-sheet
===========

The create command contains an additional argument called :code:`--multi-sheet` or :code:`-m`. When used the created spreadsheet will consist of multiple sheets, each for a different language.
