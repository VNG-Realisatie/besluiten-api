===========================
besluitregistratiecomponent
===========================

:Version: 1.0.0-rc2
:Source: https://github.com/VNG-Realisatie/gemma-besluitregistratiecomponent
:Keywords: zaken, zaakgericht werken, GEMMA, RGBZ, BRC
:PythonVersion: 3.6

|build-status|

Referentieimplementatie van de Besluiten API als besluitregistratiecomponent
(BRC).

Introduction
============

Binnen het Nederlandse gemeentelandschap wordt zaakgericht werken nagestreefd.
Om dit mogelijk te maken is er gegevensuitwisseling nodig. Er is een behoefte
om besluiten te relateren aan zaken.

Deze referentieimplementatie toont aan dat de API specificatie voor de
besluitregistratiecomponent (hierna BRC) implementeerbaar is, en vormt een
voorbeeld voor andere implementaties indien ergens twijfel bestaat.

Deze component heeft ook een `testomgeving`_ waar leveranciers tegenaan kunnen
testen.

Dit document bevat de technische documentatie voor deze component.


Contents
========

.. toctree::
    :maxdepth: 2

    contents/installation
    contents/usage
    source/brc
    contents/copyright
    contents/changelog


References
============

* `Issues <https://github.com/VNG-Realisatie/gemma-besluitregistratiecomponent/issues>`_
* `Code <https://github.com/VNG-Realisatie/gemma-besluitregistratiecomponent/>`_


.. |build-status| image:: http://jenkins.nlx.io/buildStatus/icon?job=gemma-besluitregistratiecomponent-stable
    :alt: Build status
    :target: http://jenkins.nlx.io/job/gemma-besluitregistratiecomponent-stable

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/gemma-besluitregistratiecomponent/requirements.svg?branch=master
     :target: https://requires.io/github/VNG-Realisatie/gemma-besluitregistratiecomponent/requirements/?branch=master
     :alt: Requirements status

.. _testomgeving: https://besluiten-api.vng.cloud/
