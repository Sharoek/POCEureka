.. _example_logic_rules:

===========================
Formulier met logica regels
===========================

In dit voorbeeld maken we een deel-formulier bestaande uit 1 stap, waarbij
de geboorte datum ingevuld door de gebruiker beïnvloedt of het formulier kan worden
ingediend.

.. image:: _assets/logic_rules_2_1.png
    :width: 24%

In dit voorbeeld gaan we er van uit dat u een
:ref:`eenvoudig formulier <example_simple_form>` kan maken.

.. note::

    U kunt dit voorbeeld downloaden en :ref:`importeren <manual_export_import>`
    in Open Formulieren.

    Download: :download:`logic_rules_2.zip <_assets/logic_rules_2.zip>`


Formulier maken
===============

1. Maak een formulier aan met de volgende gegevens:

    * **Naam**: Rijbewijs aanvraag demo

2. Klik op het tabblad **Stappen en velden**.
3. Klik aan de linkerkant op **Stap toevoegen** en selecteer **Maak een nieuwe
   formulierdefinitie**.
4. Onder de sectie **(Herbruikbare) stapgegevens** vul het volgende in:

    * **Naam**: Persoonlijke gegevens

5. Scroll naar de sectie **Velden**.
6. Sleep een **Tekstveld** component op het witte vlak, vul de volgende
   gegevens in en druk daarna op **Opslaan**:

    * **Label**: Naam

7. Herhaal stap 6. maar met:

    * **Label**: Achternaam

8. Sleep een **Datum** component op het witte vlak, vul de volgende
   gegevens in en druk daarna op **Opslaan**:

    * **Label**: Geboorte datum
    * Klik op het tabblad **Validatie** en selecteer **Verplicht**.

9. Onder de formulier velden, klik op **Opmaak**. Sleep een **Vrije tekst** component op het
   witte vlak. Vul de volgende gegevens in en druk daarna op **Opslaan**:

    * Onder **Vrije tekst**: Om een rijbewijs te kunnen aanvragen moet u ouder dan 18 jaar zijn.
    * **Aangepaste CSS class**: Warning.
    * Selecteer **Verborgen**, daarna op **Opslaan**.

.. image:: _assets/logic_rules_2_2.png
    :width: 51%

10. Klik op de **Logica** tab in het formulier menu
11. Klik op **Regel toevoegen**, gevolgd door **Eenvoudig**.
12. Bij **Triggervoorwaarde** selecteer je:

    * Als: **Persoonlijke Gegevens: Geboorte datum (geboorteDatum)**
    * **is groter dan**
    * **vandaag**
    * **Minus**
    * **18** jaren

13. Klik op **Actie Toevoegen**

    * dan **wijzig een attribuut van een veld/component**
    * **Persoonlijke Gegevens: Content (content)** 
    * **verborgen**
    * **Nee**
    
14. Klik op **Actie Toevoegen**

    * en **blokkeer doorgaan naar de volgende stap**

.. image:: _assets/logic_rules_2_3.png
    :width: 51%


.. note::

    Deze twee acties betekenen: als de gebruiker jonger dan 18 is, dan blokkeer
    doorgaan naar de volgende formulier stap en maak de 'Warning component' van stap 9 zichtbaar.

15. Klik onderaan op **Opslaan** om het formulier volledig op te slaan.

U kunt nu het formulier bekijken.
